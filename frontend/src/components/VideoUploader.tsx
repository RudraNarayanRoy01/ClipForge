import React, { useCallback, useState } from 'react';
import { Upload, X, FileVideo } from 'lucide-react';
import axios from 'axios';

interface VideoUploaderProps {
  projectId: string;
  onUploadSuccess: (video: any) => void;
}

export function VideoUploader({ projectId, onUploadSuccess }: VideoUploaderProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const uploadFile = async (file: File) => {
    if (!file) return;
    
    setIsUploading(true);
    setProgress(0);
    setError(null);
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const res = await axios.post(`/api/v1/projects/${projectId}/videos`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setProgress(percentCompleted);
          }
        }
      });
      onUploadSuccess(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to upload video');
    } finally {
      setIsUploading(false);
      setProgress(0);
    }
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      uploadFile(e.dataTransfer.files[0]);
    }
  }, [projectId, onUploadSuccess]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      uploadFile(e.target.files[0]);
    }
  };

  return (
    <div className="w-full">
      <div 
        className={`border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center transition-colors ${isDragging ? 'border-[var(--accent)] bg-[var(--accent)]/10' : 'border-gray-700 hover:border-gray-500 bg-black/20'}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        {isUploading ? (
          <div className="w-full max-w-xs flex flex-col items-center">
            <div className="text-gray-300 mb-4 flex items-center gap-2">
              <Upload className="animate-bounce text-[var(--accent)]" size={24} />
              <span>Uploading {progress}%</span>
            </div>
            <div className="w-full bg-gray-800 rounded-full h-2.5">
              <div className="bg-[var(--accent)] h-2.5 rounded-full transition-all duration-300" style={{ width: `${progress}%` }}></div>
            </div>
          </div>
        ) : (
          <>
            <FileVideo className="text-gray-500 mb-4" size={48} />
            <h3 className="text-lg font-medium text-white mb-2">Drag & drop a video file here</h3>
            <p className="text-sm text-gray-400 mb-6 text-center max-w-sm">
              Supports MP4, MOV, MKV, AVI, and WebM files.
            </p>
            <label className="cursor-pointer px-6 py-2 bg-[var(--accent)] text-white hover:bg-[var(--accent)]/80 rounded-md transition-colors shadow-lg">
              Browse Files
              <input type="file" className="hidden" accept=".mp4,.mov,.mkv,.avi,.webm" onChange={handleFileChange} />
            </label>
          </>
        )}
      </div>
      
      {error && (
        <div className="mt-4 p-4 bg-red-900/30 border border-red-500/50 rounded-lg flex items-start justify-between text-red-200">
          <p className="text-sm">{error}</p>
          <button onClick={() => setError(null)} className="text-red-400 hover:text-red-200"><X size={16} /></button>
        </div>
      )}
    </div>
  );
}
