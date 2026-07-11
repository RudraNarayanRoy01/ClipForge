import { useState } from 'react';
import { Trash2, FileVideo, Loader2 } from 'lucide-react';
import axios from 'axios';

interface VideoAsset {
  id: string;
  project_id: string;
  file_path: string;
  filename: string;
  original_filename: string;
  file_extension: string;
  file_size_bytes: number;
  duration_seconds: number | null;
  created_at: string;
}

interface VideoCardProps {
  video: VideoAsset;
  onDelete: (id: string) => void;
}

export function VideoCard({ video, onDelete }: VideoCardProps) {
  const [isDeleting, setIsDeleting] = useState(false);

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };
  
  const formatDuration = (seconds: number | null) => {
    if (!seconds) return 'Unknown';
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    return [h, m > 9 ? m : h ? '0' + m : m || '0', s > 9 ? s : '0' + s].filter(Boolean).join(':');
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this video?')) return;
    setIsDeleting(true);
    try {
      await axios.delete(`/api/v1/videos/${video.id}`);
      onDelete(video.id);
    } catch (err) {
      console.error('Failed to delete video', err);
      alert('Failed to delete video');
      setIsDeleting(false);
    }
  };

  return (
    <div className="bg-black/30 border border-gray-800 rounded-xl overflow-hidden hover:border-gray-600 transition-colors group flex items-center p-4">
      <div className="w-16 h-16 bg-gray-900 rounded-lg flex items-center justify-center mr-4 flex-shrink-0">
        <FileVideo className="text-gray-500" size={32} />
      </div>
      
      <div className="flex-1 min-w-0">
        <h4 className="text-white font-medium truncate mb-1" title={video.original_filename}>
          {video.original_filename}
        </h4>
        <div className="flex items-center gap-3 text-xs text-gray-400">
          <span>{formatBytes(video.file_size_bytes)}</span>
          <span>&bull;</span>
          <span>{formatDuration(video.duration_seconds)}</span>
          <span>&bull;</span>
          <span>{new Date(video.created_at).toLocaleDateString()}</span>
          <span>&bull;</span>
          <span className="text-green-400">Ready</span>
        </div>
      </div>
      
      <div className="ml-4 opacity-0 group-hover:opacity-100 transition-opacity">
        <button 
          onClick={handleDelete} 
          disabled={isDeleting}
          className="p-2 text-gray-500 hover:text-red-400 hover:bg-red-400/10 rounded-md transition-colors disabled:opacity-50"
          title="Delete video"
        >
          {isDeleting ? <Loader2 size={18} className="animate-spin" /> : <Trash2 size={18} />}
        </button>
      </div>
    </div>
  );
}
