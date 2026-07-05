import React, { useRef, useEffect } from 'react';

interface VideoPlayerProps {
  videoUrl: string | null;
  onTimeUpdate?: (currentTime: number) => void;
  seekToTime?: number | null;
}

export const VideoPlayer: React.FC<VideoPlayerProps> = ({ videoUrl, onTimeUpdate, seekToTime }) => {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (seekToTime !== null && seekToTime !== undefined && videoRef.current) {
      videoRef.current.currentTime = seekToTime;
      videoRef.current.play();
    }
  }, [seekToTime]);

  const handleTimeUpdate = () => {
    if (videoRef.current && onTimeUpdate) {
      onTimeUpdate(videoRef.current.currentTime);
    }
  };

  if (!videoUrl) {
    return (
      <div className="flex items-center justify-center w-full h-full bg-slate-900 rounded-lg text-slate-500 shadow-inner">
        <p>No video selected for playback</p>
      </div>
    );
  }

  return (
    <div className="relative w-full h-full rounded-lg overflow-hidden shadow-2xl bg-black border border-slate-700">
      <video
        ref={videoRef}
        src={videoUrl}
        className="w-full h-full object-contain"
        controls
        onTimeUpdate={handleTimeUpdate}
      />
    </div>
  );
};
