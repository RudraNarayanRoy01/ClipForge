import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.transcription.interfaces import ITranscriptRepository
from src.transcription.dtos import Transcript, TranscriptionSegment, TranscriptionWord
from src.infrastructure.models import TranscriptModel, TranscriptSegmentModel, TranscriptWordModel

class TranscriptRepository(ITranscriptRepository):
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def save_transcript(self, video_asset_id: uuid.UUID, transcript: Transcript) -> None:
        # Delete existing transcript if any to ensure clean replacement
        result = await self.db.execute(select(TranscriptModel).filter(TranscriptModel.video_asset_id == str(video_asset_id)))
        existing_transcript = result.scalars().first()
        if existing_transcript:
            await self.db.delete(existing_transcript)
            await self.db.flush()

        db_transcript = TranscriptModel(
            video_asset_id=str(video_asset_id),
            full_text=transcript.full_text,
            language=transcript.language,
            metadata_json=transcript.metadata
        )

        for s_idx, segment in enumerate(transcript.segments):
            db_segment = TranscriptSegmentModel(
                video_asset_id=str(video_asset_id),
                segment_index=s_idx,
                text=segment.text,
                start_time=segment.start_time,
                end_time=segment.end_time,
                language=segment.language,
                speaker=segment.speaker,
                confidence=segment.confidence,
                transcript=db_transcript
            )

            for w_idx, word in enumerate(segment.words):
                db_word = TranscriptWordModel(
                    word_index=w_idx,
                    text=word.text,
                    start_time=word.start_time,
                    end_time=word.end_time,
                    confidence=word.confidence,
                    speaker=word.speaker,
                    segment=db_segment
                )
                db_segment.words.append(db_word)
                
            db_transcript.segments.append(db_segment)

        self.db.add(db_transcript)
        await self.db.commit()

    async def get_transcript(self, video_asset_id: uuid.UUID) -> Transcript:
        result = await self.db.execute(select(TranscriptModel).filter(TranscriptModel.video_asset_id == str(video_asset_id)))
        db_transcript = result.scalars().first()

        if not db_transcript:
            raise ValueError(f"Transcript for video asset {video_asset_id} not found")

        segments = []
        for db_segment in db_transcript.segments:
            words = []
            for db_word in db_segment.words:
                words.append(TranscriptionWord(
                    text=db_word.text,
                    start_time=db_word.start_time,
                    end_time=db_word.end_time,
                    confidence=db_word.confidence,
                    speaker=db_word.speaker
                ))

            segments.append(TranscriptionSegment(
                text=db_segment.text,
                start_time=db_segment.start_time,
                end_time=db_segment.end_time,
                words=words,
                language=db_segment.language,
                speaker=db_segment.speaker,
                confidence=db_segment.confidence
            ))

        # Extract ORM attributes into plain Python variables to satisfy Pyrefly
        # without changing runtime behavior or using casts/type: ignores
        full_text_val = str(db_transcript.full_text)
        language_val = str(db_transcript.language) if db_transcript.language else None
        
        metadata_dict = db_transcript.metadata_json
        metadata_val = dict(metadata_dict) if isinstance(metadata_dict, dict) else {}

        return Transcript(
            full_text=full_text_val,
            segments=segments,
            language=language_val,
            metadata=metadata_val
        )
