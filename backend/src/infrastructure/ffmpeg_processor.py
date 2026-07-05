import os
import subprocess
import json
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

    def get_video_metadata(self, video_path: str) -> dict:
        """
        Extracts duration, width, height, and fps using ffprobe.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video not found: {video_path}")
            
        command = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            video_path
        ]
        
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFprobe metadata extraction failed: {result.stderr}")
            
        data = json.loads(result.stdout)
        
        metadata = {
            "duration_seconds": None,
            "width": None,
            "height": None,
            "fps": None
        }
        
        # Format duration
        if "format" in data and "duration" in data["format"]:
            try:
                metadata["duration_seconds"] = float(data["format"]["duration"])
            except ValueError:
                pass
                
        # Stream properties
        if "streams" in data:
            for stream in data["streams"]:
                if stream.get("codec_type") == "video":
                    metadata["width"] = stream.get("width")
                    metadata["height"] = stream.get("height")
                    
                    # fps is often like "30000/1001" or "30/1"
                    r_frame_rate = stream.get("r_frame_rate", "0/0")
                    try:
                        num, den = r_frame_rate.split("/")
                        if int(den) > 0:
                            metadata["fps"] = float(num) / float(den)
                    except (ValueError, ZeroDivisionError):
                        pass
                    break # just need the first video stream
                    
        return metadata
