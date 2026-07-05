import uuid
from typing import List
from backend.src.intelligence.timeline.models import TranscriptEvent
from backend.src.infrastructure.timeline.store import temporal_store

class IngestionPipeline:
    def process_video(self, video_id: str, video_path: str) -> None:
        """
        Mock ingestion pipeline. In a real scenario, this would:
        1. Call FFmpeg to extract audio.
        2. Run Whisper on the audio to get transcript segments.
        3. Emit TranscriptEvents to the temporal store.
        """
        # Simulate Whisper transcript segments
        mock_segments = [
            {"start_ms": 0, "end_ms": 5000, "text": "Welcome back to the channel."},
            {"start_ms": 5000, "end_ms": 10000, "text": "Today we are talking about AI architecture."},
            {"start_ms": 10000, "end_ms": 15000, "text": "Let's dive right into the semantic event stream."},
        ]

        # Emit events to the store
        for segment in mock_segments:
            event = TranscriptEvent(
                id=uuid.uuid4(),
                stream_id=video_id,
                start_time_ms=segment["start_ms"],
                end_time_ms=segment["end_ms"],
                confidence=0.99,
                text=str(segment["text"])
            )
            temporal_store.insert(event)

# Example usage
# pipeline = IngestionPipeline()
# pipeline.process_video("vid_123", "/path/to/video.mp4")
