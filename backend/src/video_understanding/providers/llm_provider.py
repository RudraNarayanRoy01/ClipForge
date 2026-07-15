import logging
from typing import Any, Dict

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
from src.video_understanding.dtos import VideoAnalysisRequest, VideoUnderstandingResult
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
                
            # Post-process: ensure deduplication of topics (case-insensitive)
            seen_topic_names = set()
            unique_topics = []
            for t in result.topics:
                t_name_lower = t.name.strip().lower()
                if t_name_lower not in seen_topic_names:
                    seen_topic_names.add(t_name_lower)
                    unique_topics.append(t)

            if len(unique_topics) != len(result.topics):
                result = VideoUnderstandingResult(
                    topics=unique_topics,
                    entities=result.entities,
                    hooks=result.hooks,
                    highlights=result.highlights,
                    overall_sentiment=result.overall_sentiment,
                    summary=result.summary
                )

            return result

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
