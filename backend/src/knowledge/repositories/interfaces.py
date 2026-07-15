import uuid
from abc import ABC, abstractmethod
from typing import List, Optional
from src.knowledge.dtos import VideoKnowledge

class IVideoKnowledgeRepository(ABC):
    """
    Repository for persisting and retrieving immutable VideoKnowledge snapshots.
    """
    
    @abstractmethod
    async def save(self, video_asset_id: uuid.UUID, knowledge: VideoKnowledge) -> None:
        """
        Persist a new immutable snapshot of VideoKnowledge.
        Never overwrites previous snapshots.
        """
        pass

    @abstractmethod
    async def get_latest(self, video_asset_id: uuid.UUID) -> Optional[VideoKnowledge]:
        """
        Retrieve the most recent VideoKnowledge snapshot for a video.
        """
        pass

    @abstractmethod
    async def get_all_snapshots(self, video_asset_id: uuid.UUID) -> List[VideoKnowledge]:
        """
        Retrieve all historical snapshots of VideoKnowledge for a video, ordered by creation time.
        """
        pass

    @abstractmethod
    async def exists(self, video_asset_id: uuid.UUID) -> bool:
        """
        Check if any VideoKnowledge snapshots exist for a video.
        """
        pass
