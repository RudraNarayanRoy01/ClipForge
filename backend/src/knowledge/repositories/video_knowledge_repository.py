import uuid
import json
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.knowledge.repositories.interfaces import IVideoKnowledgeRepository
from src.knowledge.dtos import VideoKnowledge
from src.infrastructure.models import VideoKnowledgeModel

class VideoKnowledgeRepository(IVideoKnowledgeRepository):
    """
    SQLAlchemy implementation of the VideoKnowledge snapshot repository.
    Persists VideoKnowledge as immutable JSON snapshots.
    """
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def save(self, video_asset_id: uuid.UUID, knowledge: VideoKnowledge) -> None:
        """
        Persist a new immutable snapshot of VideoKnowledge.
        """
        # Serialize the Pydantic model to a dict, which will be stored as JSON
        knowledge_dict = json.loads(knowledge.json())
        
        db_snapshot = VideoKnowledgeModel(
            video_asset_id=str(video_asset_id),
            knowledge_json=knowledge_dict
        )
        
        self.db.add(db_snapshot)
        await self.db.commit()

    async def get_latest(self, video_asset_id: uuid.UUID) -> Optional[VideoKnowledge]:
        """
        Retrieve the most recent VideoKnowledge snapshot for a video.
        """
        stmt = (
            select(VideoKnowledgeModel)
            .where(VideoKnowledgeModel.video_asset_id == str(video_asset_id))
            .order_by(VideoKnowledgeModel.created_at.desc())
            .limit(1)
        )
        
        result = await self.db.execute(stmt)
        db_snapshot = result.scalars().first()
        
        if not db_snapshot:
            return None
            
        return VideoKnowledge.parse_obj(db_snapshot.knowledge_json)

    async def get_all_snapshots(self, video_asset_id: uuid.UUID) -> List[VideoKnowledge]:
        """
        Retrieve all historical snapshots of VideoKnowledge for a video, ordered by creation time.
        """
        stmt = (
            select(VideoKnowledgeModel)
            .where(VideoKnowledgeModel.video_asset_id == str(video_asset_id))
            .order_by(VideoKnowledgeModel.created_at.asc())
        )
        
        result = await self.db.execute(stmt)
        db_snapshots = result.scalars().all()
        
        return [VideoKnowledge.parse_obj(snap.knowledge_json) for snap in db_snapshots]

    async def exists(self, video_asset_id: uuid.UUID) -> bool:
        """
        Check if any VideoKnowledge snapshots exist for a video.
        """
        stmt = (
            select(VideoKnowledgeModel.id)
            .where(VideoKnowledgeModel.video_asset_id == str(video_asset_id))
            .limit(1)
        )
        
        result = await self.db.execute(stmt)
        return result.scalars().first() is not None
