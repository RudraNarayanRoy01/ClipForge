import os
import subprocess
from typing import List
from ..domain.ports import IVideoProcessor
from ..domain.entities import ClipSegment

class FfmpegVideoProcessor(IVideoProcessor):
    """
    Concrete implementation of the IVideoProcessor using local FFmpeg binaries.
    """
    
    def extract_audio(self, video_path: str, output_path: str) -> None:
        """
        Extracts a 16kHz mono WAV file optimized for Whisper transcription.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video not found: {video_path}")
            
        command = [
            "ffmpeg",
            "-y", # Overwrite
            "-i", video_path,
            "-vn", # Disable video
            "-acodec", "pcm_s16le", # 16-bit PCM
            "-ar", "16000", # 16kHz for Whisper
            "-ac", "1", # Mono
            output_path
        ]
        
        # Execute FFmpeg synchronously. In a real environment, we'd use ffmpeg-python or async subprocess.
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg audio extraction failed: {result.stderr}")
            
    def extract_frames(self, video_path: str, output_dir: str, fps: int = 1) -> None:
        """
        Extracts 1 frame per second as a JPG for the Vision Analyzer to process.
        """
        os.makedirs(output_dir, exist_ok=True)
        command = [
            "ffmpeg",
            "-y",
            "-i", video_path,
            "-vf", f"fps={fps}",
            os.path.join(output_dir, "frame_%04d.jpg")
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg frame extraction failed: {result.stderr}")

    def render_clip(self, clip: ClipSegment, output_path: str) -> None:
        """
        Takes the AI clip boundaries, slices the video, crops it from 16:9 to 9:16, 
        and (theoretically) burns the subtitles.
        """
        # Hardcoded dummy input for scaffolding purposes, since we don't have the original video path in ClipSegment 
        # (It would be fetched from VideoAsset repository during orchestration)
        input_video = "dummy_input.mp4" 
        
        # Center crop math for 16:9 to 9:16
        # Assuming input is 1920x1080. We want 607x1080 (9:16).
        # crop=W:H:X:Y => crop=607:1080:(1920-607)/2:0
        
        crop_filter = "crop=607:1080:656:0"
        
        command = [
            "ffmpeg",
            "-y",
            "-ss", str(clip.boundaries.start_time),
            "-to", str(clip.boundaries.end_time),
            "-i", input_video,
            "-vf", crop_filter,
            "-c:v", "libx264",
            "-preset", "fast",
            "-c:a", "aac",
            output_path
        ]
        
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg clip rendering failed: {result.stderr}")
