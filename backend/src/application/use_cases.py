import uuid
import asyncio
from typing import List
from src.domain.ports import (
    IAudioAnalyzer, IVisionAnalyzer, ILLMReasoningEngine, 
    ITimelineContextRepository, IVideoProcessor
)
from src.domain.entities import TimelineContext, ClipSegment
from src.domain.ports import IProjectRepository
from src.knowledge.builders.video_knowledge_builder import VideoKnowledgeBuilder
from src.media.dtos import MediaMetadata
from src.transcription.dtos import Transcript, TranscriptionSegment, TranscriptionWord
from src.video_understanding.dtos import VideoUnderstandingResult, Topic

class GenerateClipsUseCase:
    """
    Orchestrates the massive AI pipeline asynchronously.
    """
    def __init__(
        self,
        audio_analyzer: IAudioAnalyzer,
        vision_analyzer: IVisionAnalyzer,
        llm_engine: ILLMReasoningEngine,
        timeline_repo: ITimelineContextRepository,
        project_repo: IProjectRepository,
        video_processor: IVideoProcessor
    ):
        self.audio = audio_analyzer
        self.vision = vision_analyzer
        self.llm = llm_engine
        self.timeline_repo = timeline_repo
        self.project_repo = project_repo
        self.video = video_processor

    async def execute(self, project_id: uuid.UUID, video_asset_id: uuid.UUID, video_path: str) -> List[ClipSegment]:
        audio_path = "temp_audio.wav"
        
        # Offload synchronous blocking subprocess to threadpool
        await asyncio.to_thread(self.video.extract_audio, video_path, audio_path)
        
        # In a real scenario, these would also be async or offloaded
        words = await asyncio.to_thread(self.audio.transcribe, audio_path)
        speakers = await asyncio.to_thread(self.audio.detect_speakers, audio_path)
        energy = await asyncio.to_thread(self.audio.measure_energy, audio_path)
        silences = await asyncio.to_thread(self.audio.detect_silence, audio_path)
        
        scenes = await asyncio.to_thread(self.vision.detect_scenes, video_path)
        faces = await asyncio.to_thread(self.vision.detect_faces, video_path)
        emotions = await asyncio.to_thread(self.vision.detect_emotions, video_path)
        gestures = await asyncio.to_thread(self.vision.detect_gestures, video_path)
        objects = await asyncio.to_thread(self.vision.detect_objects, video_path)
        ocr = await asyncio.to_thread(self.vision.read_text_ocr, video_path)
        
        full_text = " ".join([w.word for w in words])
        topics = await asyncio.to_thread(self.llm.detect_topics, full_text)
        
        context = TimelineContext(
            video_asset_id=video_asset_id,
            words=words, speakers=speakers, energy=energy, silences=silences,
            scenes=scenes, faces=faces, emotions=emotions, gestures=gestures,
            objects=objects, ocr_texts=ocr, topics=topics
        )
        
        # Knowledge Extraction (Transformation)
        knowledge_builder = VideoKnowledgeBuilder()
        
        # Mappings from internal entities to DTOs for Knowledge Builder
        transcript_dto = Transcript(
            full_text=full_text,
            segments=[
                TranscriptionSegment(
                    text=" ".join(w.word for w in words),
                    start_time=words[0].timestamp if words else 0.0,
                    end_time=words[-1].timestamp if words else 0.0,
                    words=[TranscriptionWord(text=w.word, start_time=w.timestamp, end_time=w.timestamp, confidence=1.0) for w in words]
                )
            ]
        )
        media_meta_dto = MediaMetadata(video_id=str(video_asset_id), duration_seconds=120.0, width=1920, height=1080, fps=30.0)
        understanding_dto = VideoUnderstandingResult(
            video_id=str(video_asset_id),
            topics=[Topic(name=t.topic, start_time=t.start_time, end_time=t.end_time) for t in topics],
            highlights=[]
        )
        
        video_knowledge = (
            knowledge_builder
            .with_media_metadata(media_meta_dto)
            .with_transcript(transcript_dto)
            .with_understanding(understanding_dto)
            .build()
        )
        
        # Persist Timeline Context (Timeline Generation)
        self.timeline_repo.save_context(context)
        
        candidates = await asyncio.to_thread(self.llm.generate_clips, context)
        ranked_clips = await asyncio.to_thread(self.llm.rank_clips, candidates, context)
        
        for clip in ranked_clips:
            clip.project_id = project_id
            
        # Async DB persistence
        await self.project_repo.save_clips(ranked_clips)
        
        return ranked_clips
