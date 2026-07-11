import os
import uuid
import shutil
from typing import List
from fastapi import UploadFile, HTTPException

from src.domain.entities import VideoAsset
from src.domain.ports import IVideoRepository, IVideoProcessor
from src.repositories.project_repository import ProjectRepository

ALLOWED_EXTENSIONS = {'.mp4', '.mov', '.mkv', '.avi', '.webm'}

class VideoService:
    def __init__(
        self, 
        video_repo: IVideoRepository,
        project_repo: ProjectRepository,
        video_processor: IVideoProcessor
    ):
        self.video_repo = video_repo
        self.project_repo = project_repo
        self.video_processor = video_processor

    async def upload_video(self, project_id: str, file: UploadFile) -> VideoAsset:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Empty filename")
            
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")
            
        try:
            # Verify project exists
            project_uuid = uuid.UUID(project_id)
            project = await self.project_repo.get_by_id(str(project_uuid))
            if not project:
                raise ValueError("Project not found")
        except ValueError as e:
             raise HTTPException(status_code=404, detail="Project not found")
            
        # Create storage path
        storage_dir = os.path.join("backend", "storage", "projects", project_id, "videos")
        os.makedirs(storage_dir, exist_ok=True)
        
        # Generate unique filename to avoid collisions
        unique_id = str(uuid.uuid4())
        new_filename = f"{unique_id}{file_ext}"
        storage_path = os.path.join(storage_dir, new_filename)
        
        # Save file to disk
        file_size = 0
        try:
            with open(storage_path, "wb") as buffer:
                while content := await file.read(1024 * 1024): # 1MB chunks
                    buffer.write(content)
                    file_size += len(content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
            
        if file_size == 0:
            os.remove(storage_path)
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
            
        # Extract metadata
        metadata = {}
        try:
            metadata = self.video_processor.get_video_metadata(storage_path)
        except Exception as e:
            # Log error but don't fail upload completely?
            # For this MVP we can allow it to proceed with missing metadata
            pass
            
        # Create VideoAsset
        video_asset = VideoAsset(
            id=uuid.UUID(unique_id),
            project_id=project_uuid,
            file_path=storage_path,
            filename=new_filename,
            original_filename=file.filename,
            file_extension=file_ext,
            mime_type=file.content_type or "video/mp4",
            file_size_bytes=file_size,
            duration=metadata.get("duration_seconds") or 0.0,
            duration_seconds=metadata.get("duration_seconds"),
            width=metadata.get("width"),
            height=metadata.get("height"),
            fps=metadata.get("fps"),
            storage_path=storage_path
        )
        
        await self.video_repo.save_video(video_asset)
        return video_asset

    async def list_videos(self, project_id: str) -> List[VideoAsset]:
        try:
            project_uuid = uuid.UUID(project_id)
            # Verify project exists
            project = await self.project_repo.get_by_id(str(project_uuid))
            if not project:
                raise ValueError("Project not found")
            return await self.video_repo.get_videos_for_project(project_uuid)
        except ValueError:
            raise HTTPException(status_code=404, detail="Project not found")

    async def delete_video(self, video_id: str) -> None:
        try:
            video_uuid = uuid.UUID(video_id)
            video = await self.video_repo.get_video(video_uuid)
            
            # Delete physical file
            if os.path.exists(video.storage_path):
                os.remove(video.storage_path)
                
            # Delete database record
            await self.video_repo.delete_video(video_uuid)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
