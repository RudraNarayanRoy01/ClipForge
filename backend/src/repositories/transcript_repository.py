import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.transcription.interfaces import ITranscriptRepository
from src.transcription.dtos import Transcript, TranscriptionSegment, TranscriptionWord, TranscriptSearchResult
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

    async def search_transcripts(self, query: str, video_asset_id: Optional[uuid.UUID] = None, limit: int = 50) -> List[TranscriptSearchResult]:
        if not query or not query.strip():
            raise ValueError("Search query cannot be empty")
        
        # Limit the query length to prevent absurdly large queries
        if len(query) > 200:
            raise ValueError("Search query is too long")

        # Start building the SQLAlchemy query for segments
        stmt = select(TranscriptSegmentModel)

        # Apply keyword search using case-insensitive LIKE
        # By default, SQLAlchemy `ilike` maps to `ILIKE` on PostgreSQL and `LIKE` on SQLite.
        stmt = stmt.where(TranscriptSegmentModel.text.ilike(f"%{query}%"))

        if video_asset_id:
            stmt = stmt.where(TranscriptSegmentModel.video_asset_id == str(video_asset_id))

        # Order by video and then by start_time so sequential results appear in order
        stmt = stmt.order_by(TranscriptSegmentModel.video_asset_id, TranscriptSegmentModel.start_time)
        stmt = stmt.limit(limit)

        result = await self.db.execute(stmt)
        db_segments = result.scalars().all()

        search_results = []
        for db_segment in db_segments:
            words = []
            for db_word in db_segment.words:
                words.append(TranscriptionWord(
                    text=db_word.text,
                    start_time=db_word.start_time,
                    end_time=db_word.end_time,
                    confidence=db_word.confidence,
                    speaker=db_word.speaker
                ))

            segment_dto = TranscriptionSegment(
                text=db_segment.text,
                start_time=db_segment.start_time,
                end_time=db_segment.end_time,
                words=words,
                language=db_segment.language,
                speaker=db_segment.speaker,
                confidence=db_segment.confidence
            )

            search_results.append(TranscriptSearchResult(
                video_asset_id=uuid.UUID(db_segment.video_asset_id),
                segment=segment_dto
            ))

        return search_results
