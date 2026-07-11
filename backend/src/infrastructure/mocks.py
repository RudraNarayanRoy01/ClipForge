import uuid
from typing import List
from src.domain.ports import IAudioAnalyzer, IVisionAnalyzer, ILLMReasoningEngine
from src.domain.entities import (
    WordLevelTimestamp, SpeakerSegment, EnergySegment, SilenceSegment,
    SceneBoundary, FaceBoundingBox, EmotionSegment, GestureEvent,
    ObjectDetection, OCREvent, TopicSegment, TimelineContext, ClipSegment,
    TimeRange, AiConfidenceScore, GeneratedCaption
)

class MockAudioAnalyzer(IAudioAnalyzer):
    """Mocks the extraction of audio modalities without running neural networks."""
    
    def transcribe(self, audio_path: str) -> List[WordLevelTimestamp]:
        return [
            WordLevelTimestamp("Welcome", TimeRange(0.0, 0.5)),
            WordLevelTimestamp("to", TimeRange(0.5, 0.7)),
            WordLevelTimestamp("the", TimeRange(0.7, 0.9)),
            WordLevelTimestamp("podcast", TimeRange(0.9, 1.5)),
        ]
        
    def detect_speakers(self, audio_path: str) -> List[SpeakerSegment]:
        return [SpeakerSegment("Speaker_A", TimeRange(0.0, 1.5))]
        
    def measure_energy(self, audio_path: str) -> List[EnergySegment]:
        return [EnergySegment(TimeRange(0.0, 1.5), 0.8)]
        
    def detect_silence(self, audio_path: str) -> List[SilenceSegment]:
        return []

class MockVisionAnalyzer(IVisionAnalyzer):
    """Mocks vision pipeline."""
    def detect_scenes(self, video_path: str) -> List[SceneBoundary]:
        return [SceneBoundary("scene_1", TimeRange(0.0, 1.5))]
    def detect_faces(self, video_path: str, fps: int = 1) -> List[FaceBoundingBox]:
        return [FaceBoundingBox(0.0, 100, 100, 200, 200, "Speaker_A")]
    def detect_emotions(self, video_path: str, fps: int = 1) -> List[EmotionSegment]:
        return [EmotionSegment(TimeRange(0.0, 1.5), "happy", AiConfidenceScore(0.9))]
    def detect_gestures(self, video_path: str, fps: int = 1) -> List[GestureEvent]:
        return []
    def detect_objects(self, video_path: str, fps: int = 1) -> List[ObjectDetection]:
        return []
    def read_text_ocr(self, video_path: str, fps: int = 1) -> List[OCREvent]:
        return []

class MockLLMReasoningEngine(ILLMReasoningEngine):
    """Mocks the heavy Gemma 4 reasoning process."""
    
    def detect_topics(self, text_transcript: str) -> List[TopicSegment]:
        return [TopicSegment(TimeRange(0.0, 1.5), "Intro", "The host introduces the podcast.")]
        
    def generate_clips(self, context: TimelineContext) -> List[ClipSegment]:
        # Generate a fake clip based on the context
        clip = ClipSegment(
            id=uuid.uuid4(),
            project_id=uuid.uuid4(), # Would be set by orchestrator
            video_asset_id=context.video_asset_id,
            boundaries=TimeRange(0.0, 1.5),
            title="The Best Podcast Intro",
            hook_text="Wait until you hear this...",
            hashtags=["#podcast", "#viral"],
            captions=[
                GeneratedCaption(TimeRange(0.0, 1.5), "Welcome to the podcast!", {})
            ],
            virality_score=95,
            ai_rationale="High energy intro with a happy emotion.",
            user_approved=False
        )
        return [clip]
        
    def rank_clips(self, clips: List[ClipSegment], context: TimelineContext) -> List[ClipSegment]:
        return sorted(clips, key=lambda c: c.virality_score, reverse=True)
