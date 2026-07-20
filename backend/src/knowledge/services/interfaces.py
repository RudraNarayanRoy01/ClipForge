import uuid
from abc import ABC, abstractmethod
from src.knowledge.dtos import VideoKnowledge

class IVideoKnowledgeAccessService(ABC):
    """
    Service for retrieving VideoKnowledge snapshots.
    Hides repository details and provides canonical domain access.
    """
    
    @abstractmethod
    async def get_latest(self, video_asset_id: uuid.UUID) -> VideoKnowledge:
        """
        Retrieve the most recent VideoKnowledge snapshot for a video.
        Raises KnowledgeNotFound if no snapshots exist.
        """
        pass
        
    @abstractmethod
    async def get_version(self, video_asset_id: uuid.UUID, version: str) -> VideoKnowledge:
        """
        Retrieve a specific version of the VideoKnowledge snapshot for a video.
        
        The 'version' parameter specifically corresponds to the 'knowledge_version' 
        (the version of the knowledge extraction logic), NOT the schema_version or 
        source_version.

        Raises KnowledgeNotFound if no snapshots exist.
        Raises KnowledgeVersionNotFound if the specific version does not exist.
        """
        pass
        
    @abstractmethod
    async def exists(self, video_asset_id: uuid.UUID) -> bool:
        """
        Check if any VideoKnowledge snapshots exist for a video.
        """
        pass
