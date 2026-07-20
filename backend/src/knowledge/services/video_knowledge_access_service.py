import uuid

from src.knowledge.dtos import VideoKnowledge
from src.knowledge.repositories.interfaces import IVideoKnowledgeRepository
from src.knowledge.services.interfaces import IVideoKnowledgeAccessService
from src.knowledge.exceptions import KnowledgeNotFound, KnowledgeVersionNotFound, KnowledgeUnavailable

class VideoKnowledgeAccessService(IVideoKnowledgeAccessService):
    """
    Implementation of the VideoKnowledgeAccessService.
    Provides a provider-independent access point for retrieved VideoKnowledge snapshots.
    """
    
    def __init__(self, repository: IVideoKnowledgeRepository):
        self._repository = repository

    async def get_latest(self, video_asset_id: uuid.UUID) -> VideoKnowledge:
        """
        Retrieve the most recent VideoKnowledge snapshot for a video.
        Raises KnowledgeNotFound if no snapshots exist.
        """
        try:
            snapshot = await self._repository.get_latest(video_asset_id)
        except Exception as e:
            raise KnowledgeUnavailable(f"An error occurred while retrieving knowledge for video {video_asset_id}.") from e

        if not snapshot:
            raise KnowledgeNotFound(f"No knowledge snapshots found for video {video_asset_id}.")
            
        return snapshot

    async def get_version(self, video_asset_id: uuid.UUID, version: str) -> VideoKnowledge:
        """
        Retrieve a specific version of the VideoKnowledge snapshot for a video.
        Raises KnowledgeNotFound if no snapshots exist.
        Raises KnowledgeVersionNotFound if the specific version does not exist.
        """
        try:
            snapshots = await self._repository.get_all_snapshots(video_asset_id)
        except Exception as e:
            raise KnowledgeUnavailable(f"An error occurred while retrieving knowledge for video {video_asset_id}.") from e

        if not snapshots:
            raise KnowledgeNotFound(f"No knowledge snapshots found for video {video_asset_id}.")
            
        # Iterate from most recent to oldest to get the latest snapshot of the requested version
        snapshots.sort(key=lambda s: s.metadata.processing_timestamp, reverse=True)
        for snapshot in snapshots:
            if snapshot.metadata.knowledge_version == version:
                return snapshot
                
        raise KnowledgeVersionNotFound(f"Knowledge version '{version}' not found for video {video_asset_id}.")

    async def exists(self, video_asset_id: uuid.UUID) -> bool:
        """
        Check if any VideoKnowledge snapshots exist for a video.
        """
        try:
            return await self._repository.exists(video_asset_id)
        except Exception as e:
            raise KnowledgeUnavailable(f"An error occurred while checking knowledge existence for video {video_asset_id}.") from e
