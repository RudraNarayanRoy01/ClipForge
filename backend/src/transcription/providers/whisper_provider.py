import os
import asyncio
import threading
from typing import TYPE_CHECKING, List, Optional, Any

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



class WhisperTranscriptionService(ITranscriptionService):
    """
    Concrete implementation of ITranscriptionService using Faster-Whisper.
    """
    
    def __init__(self, beam_size: int, default_language: str):
        self._beam_size = beam_size
        self._default_language = default_language
        
        self._model: Optional["WhisperModel"] = None
        self._model_lock = threading.Lock()
        
        # Track currently loaded configuration
        self._current_model: Optional[str] = None
        self._current_device: Optional[str] = None
        self._current_compute_class: Optional[str] = None
        
    async def _ensure_model_loaded(self, model: str, device: str, compute_class: str) -> None:
        """
        Lazily load the Whisper model once. 
        Reuse it for subsequent requests to avoid high loading overhead,
        but reload if the Runtime requests a different model/device/compute configuration.
        """
        if (self._model is not None and 
            self._current_model == model and 
            self._current_device == device and 
            self._current_compute_class == compute_class):
            return
            
        def _sync_ensure_loaded() -> None:
            with self._model_lock:
                # Double-check pattern to prevent race conditions
                if (self._model is not None and 
                    self._current_model == model and 
                    self._current_device == device and 
                    self._current_compute_class == compute_class):
                    return
                    
                try:
                    from faster_whisper import WhisperModel  # type: ignore
                    self._model = WhisperModel(
                        model_size_or_path=model,
                        device=device,
                        compute_type=compute_class,
                    )
                    
                    # Update tracked state
                    self._current_model = model
                    self._current_device = device
                    self._current_compute_class = compute_class
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
                    
        await asyncio.to_thread(_sync_ensure_loaded)

    async def transcribe(self, request: TranscriptionRequest, **kwargs: Any) -> Transcript:
        """
        Transcribe the provided media file.
        """
        if not os.path.isfile(request.media_path):
            raise TranscriptionProcessingError(f"Media file not found: {request.media_path}")
            
        model = kwargs.get("model", "base")
        device = kwargs.get("device", "cpu")
        compute_class = kwargs.get("compute_class", "default")
            
        await self._ensure_model_loaded(model, device, compute_class)
        
        language = request.language_hint or self._default_language
        beam_size = self._beam_size
        
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
                    "model": model
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
