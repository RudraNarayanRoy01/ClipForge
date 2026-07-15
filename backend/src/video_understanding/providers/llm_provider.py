import logging
from typing import Any, Dict
from datetime import datetime, timezone

from src.intelligence.interfaces.ai_service import IAIService
from src.intelligence.schemas.ai_models import AIExecutionCommand
from src.intelligence.exceptions.ai import (
    AIProviderError,
    AIConnectionError,
    AITimeoutError,
    AIConfigurationError,
    AIResponseValidationError
)
from src.video_understanding.interfaces import IVideoUnderstandingService
from src.video_understanding.dtos import (
    VideoAnalysisRequest,
    VideoUnderstandingResult,
    Topic,
    Entity,
    Hook,
    Highlight,
    UnderstandingMetadata
)
from src.video_understanding.exceptions import (
    VideoUnderstandingError,
    ProviderConnectionError,
    ProviderTimeoutError,
    ProviderConfigurationError,
    VideoUnderstandingProcessingError,
    VideoUnderstandingValidationError,
    ContextLengthExceededError
)

logger = logging.getLogger(__name__)

class LLMVideoUnderstandingService(IVideoUnderstandingService):
    """
    Concrete implementation of IVideoUnderstandingService using the standard AI pipeline.
    """
    def __init__(self, ai_service: IAIService):
        self._ai_service = ai_service

    def _normalize_confidence(self, confidence: float) -> float:
        if confidence < 0.0:
            return 0.0
        if confidence > 1.0:
            return 1.0
        return confidence

    def _normalize_timestamps(self, start: float, end: float) -> tuple[float, float]:
        if start > end:
            return end, start
        return max(0.0, start), max(0.0, end)

    def _normalize_result(self, result: VideoUnderstandingResult, provider_id: str) -> VideoUnderstandingResult:
        # 1. Normalize and deduplicate Topics
        topic_map = {}
        for t in result.topics or []:
            name_key = t.name.strip().lower()
            conf = self._normalize_confidence(t.confidence)
            st, et = self._normalize_timestamps(t.start_time, t.end_time)
            if name_key not in topic_map or topic_map[name_key].confidence < conf:
                topic_map[name_key] = Topic(
                    name=t.name,
                    description=t.description,
                    confidence=conf,
                    start_time=st,
                    end_time=et,
                    reasoning=t.reasoning
                )
        unique_topics = sorted(topic_map.values(), key=lambda x: x.confidence, reverse=True)

        # 2. Normalize and deduplicate Entities
        entity_map = {}
        for e in result.entities or []:
            key = (e.name.strip().lower(), e.entity_type.strip().lower())
            conf = self._normalize_confidence(e.confidence)
            if key not in entity_map or entity_map[key].confidence < conf:
                entity_map[key] = Entity(
                    name=e.name,
                    entity_type=e.entity_type,
                    confidence=conf,
                    reasoning=e.reasoning
                )
        unique_entities = sorted(entity_map.values(), key=lambda x: x.confidence, reverse=True)

        # 3. Normalize Hooks
        hook_map = {}
        for h in result.hooks or []:
            text_key = h.text.strip().lower()
            conf = self._normalize_confidence(h.confidence)
            st = h.start_time
            et = h.end_time
            if st is not None and et is not None:
                st, et = self._normalize_timestamps(st, et)
            elif st is not None:
                st = max(0.0, st)
            elif et is not None:
                et = max(0.0, et)
            
            if text_key not in hook_map or hook_map[text_key].confidence < conf:
                hook_map[text_key] = Hook(
                    text=h.text,
                    start_time=st,
                    end_time=et,
                    confidence=conf,
                    reasoning=h.reasoning
                )
        hooks = list(hook_map.values())
        hooks.sort(key=lambda x: x.start_time if x.start_time is not None else 0.0)

        # 4. Normalize Highlights
        highlight_map = {}
        for hl in result.highlights or []:
            text_key = hl.text.strip().lower()
            conf = self._normalize_confidence(hl.confidence)
            st, et = self._normalize_timestamps(hl.start_time, hl.end_time)
            
            if text_key not in highlight_map or highlight_map[text_key].confidence < conf:
                highlight_map[text_key] = Highlight(
                    text=hl.text,
                    start_time=st,
                    end_time=et,
                    confidence=conf,
                    reasoning=hl.reasoning
                )
        highlights = list(highlight_map.values())
        highlights.sort(key=lambda x: x.start_time)

        # 5. Metadata
        metadata = UnderstandingMetadata(
            analysis_version="1.0",
            schema_version="1.0",
            processing_timestamp=datetime.now(timezone.utc),
            provider_identifier=provider_id
        )

        return VideoUnderstandingResult(
            topics=unique_topics,
            entities=unique_entities,
            hooks=hooks,
            highlights=highlights,
            overall_sentiment=result.overall_sentiment,
            summary=result.summary,
            metadata=metadata
        )

    async def analyze_video(self, request: VideoAnalysisRequest) -> VideoUnderstandingResult:
        """
        Analyze the provided video transcript and extract rich understanding metadata
        using the configured AI service.
        """
        # Sanitize transcript text slightly to avoid completely broken inputs
        clean_transcript = request.transcript_text.strip()
        
        target_audiences_str = ", ".join(request.target_audiences) if request.target_audiences else "General Audience"
        custom_instructions_str = request.custom_instructions if request.custom_instructions else "None provided"

        command = AIExecutionCommand(
            prompt_identifier="video_understanding/analyze_video",
            template_variables={
                "transcript_text": clean_transcript,
                "target_audiences": target_audiences_str,
                "custom_instructions": custom_instructions_str
            },
            response_schema=VideoUnderstandingResult
        )

        try:
            response = await self._ai_service.execute(command)
            
            if not isinstance(response.structured_output, VideoUnderstandingResult):
                if isinstance(response.structured_output, dict):
                    result = VideoUnderstandingResult.parse_obj(response.structured_output)
                else:
                    raise VideoUnderstandingValidationError("AI Service did not return the expected structured output type.")
            else:
                result = response.structured_output
                
            # Perform deterministic normalization
            provider_id = response.provider
            normalized_result = self._normalize_result(result, provider_id)

            return normalized_result

        except AIConnectionError as e:
            logger.error(f"Connection error analyzing video {request.video_id}: {e}")
            raise ProviderConnectionError(f"Failed to connect to AI provider: {e}") from e
        except AITimeoutError as e:
            logger.error(f"Timeout analyzing video {request.video_id}: {e}")
            raise ProviderTimeoutError(f"AI provider request timed out: {e}") from e
        except AIConfigurationError as e:
            logger.error(f"Configuration error analyzing video {request.video_id}: {e}")
            raise ProviderConfigurationError(f"AI provider configuration error: {e}") from e
        except AIResponseValidationError as e:
            logger.error(f"Validation error from AI response for video {request.video_id}: {e}")
            raise VideoUnderstandingValidationError(f"Invalid structured output from AI provider: {e}") from e
        except AIProviderError as e:
            logger.error(f"General AI provider error for video {request.video_id}: {e}")
            if "context length" in str(e).lower() or "token limit" in str(e).lower():
                raise ContextLengthExceededError(f"Transcript exceeds provider token limit: {e}") from e
            raise VideoUnderstandingProcessingError(f"AI provider failed to process request: {e}") from e
        except VideoUnderstandingError:
            # Re-raise already mapped exceptions
            raise
        except Exception as e:
            logger.error(f"Unexpected error analyzing video {request.video_id}: {e}")
            raise VideoUnderstandingError(f"An unexpected error occurred during video understanding: {e}") from e
