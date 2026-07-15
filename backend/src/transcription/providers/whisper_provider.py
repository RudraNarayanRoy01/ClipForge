import os
import asyncio
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from faster_whisper import WhisperModel  # type: ignore

from src.transcription.interfaces import ITranscriptionService
from src.transcription.dtos import (
    TranscriptionRequest,
    Transcript,
    TranscriptionSegment,
    TranscriptionWord
)
from src.transcription.exceptions import (
    TranscriptionError,
    TranscriptionProcessingError,
    TranscriptionConfigurationError
)
from src.config.transcription_settings import TranscriptionSettings


class WhisperTranscriptionService(ITranscriptionService):
    """
    Concrete implementation of ITranscriptionService using Faster-Whisper.
    """
    
    def __init__(self, settings: TranscriptionSettings):
        self._settings = settings
        self._model: Optional["WhisperModel"] = None
        self._model_lock = asyncio.Lock()
        
    async def _ensure_model_loaded(self) -> None:
        """
        Lazily load the Whisper model once. 
        Reuse it for subsequent requests to avoid high loading overhead.
        """
        if self._model is not None:
            return
            
        async with self._model_lock:
            # Double-check pattern to prevent race conditions
            if self._model is not None:
                return
                
            try:
                # Loading the model is CPU intensive and blocking, so we run it in a thread
                def load_model() -> "WhisperModel":
                    from faster_whisper import WhisperModel  # type: ignore
                    return WhisperModel(
                        model_size_or_path=self._settings.transcription_model,
                        device=self._settings.transcription_device,
                        compute_type=self._settings.transcription_compute_type,
                    )
                self._model = await asyncio.to_thread(load_model)
            except ValueError as e:
                # Typically happens if device or compute_type are invalid
                raise TranscriptionConfigurationError(
                    f"Invalid Faster-Whisper configuration: {str(e)}"
                ) from e
            except Exception as e:
                # General failures (e.g., model file not found, missing dependencies)
                raise TranscriptionError(
                    f"Failed to load Faster-Whisper model: {str(e)}"
                ) from e

    async def transcribe(self, request: TranscriptionRequest) -> Transcript:
        """
        Transcribe the provided media file.
        """
        if not os.path.isfile(request.media_path):
            raise TranscriptionProcessingError(f"Media file not found: {request.media_path}")
            
        await self._ensure_model_loaded()
        
        language = request.language_hint or self._settings.transcription_language
        beam_size = self._settings.transcription_beam_size
        
        try:
            # Both transcribe() and iterating over the segments block the thread.
            # We encapsulate the whole process and execute it in a thread pool.
            def run_transcription() -> Transcript:
                assert self._model is not None, "Whisper model not initialized"
                
                segments_gen, info = self._model.transcribe(
                    request.media_path,
                    language=language,
                    beam_size=beam_size,
                    initial_prompt=request.prompt,
                    word_timestamps=True
                )
                
                result_segments: List[TranscriptionSegment] = []
                full_text_parts: List[str] = []
                
                # Consuming the generator evaluates the transcription model
                for segment in segments_gen:
                    words = []
                    # Process words if word timestamps were successfully generated
                    if getattr(segment, "words", None):
                        for word in segment.words:
                            words.append(
                                TranscriptionWord(
                                    text=word.word,
                                    start_time=word.start,
                                    end_time=word.end,
                                    confidence=word.probability
                                )
                            )
                    
                    seg_text = segment.text.strip()
                    full_text_parts.append(seg_text)
                    
                    result_segments.append(
                        TranscriptionSegment(
                            text=seg_text,
                            start_time=segment.start,
                            end_time=segment.end,
                            words=words,
                            language=info.language,
                            confidence=getattr(segment, "avg_logprob", None)
                        )
                    )
                    
                full_text = " ".join(full_text_parts)
                
                # Build metadata dictionary with whatever Faster-Whisper provides
                metadata = {
                    "language_probability": getattr(info, "language_probability", None),
                    "duration": getattr(info, "duration", None),
                    "provider": "faster-whisper",
                    "model": self._settings.transcription_model
                }
                
                return Transcript(
                    full_text=full_text,
                    segments=result_segments,
                    language=info.language,
                    metadata=metadata
                )
                
            return await asyncio.to_thread(run_transcription)
            
        except ValueError as e:
            # Faster-Whisper raises ValueError for unsupported configurations during transcribing
            raise TranscriptionConfigurationError(f"Transcription configuration error: {str(e)}") from e
        except Exception as e:
            # General runtime errors or corrupt media files
            raise TranscriptionProcessingError(f"Whisper transcription failed: {str(e)}") from e
