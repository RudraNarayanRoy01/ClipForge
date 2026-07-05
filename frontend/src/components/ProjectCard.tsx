import { useState } from 'react';
import { Trash2, Film, Clock, ChevronRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export interface Project {
  id: string;
  name: string;
  description?: string;
  status: string;
  video_count: number;
  created_at: string;
  thumbnail_path?: string;
}

interface ProjectCardProps {
  project: Project;
  onDelete: (id: string) => void;
}

export default function ProjectCard({ project, onDelete }: ProjectCardProps) {
  const navigate = useNavigate();
  const [showConfirm, setShowConfirm] = useState(false);

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (showConfirm) {
      onDelete(project.id);
    } else {
      setShowConfirm(true);
    }
  };

  const cancelDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    setShowConfirm(false);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div 
      onClick={() => navigate(`/projects/${project.id}`)}
      className="bg-[var(--panel)] border border-[var(--border)] rounded-xl overflow-hidden hover:border-[var(--accent)] transition-all cursor-pointer group relative shadow-md"
    >
      <div className="h-32 bg-gradient-to-br from-gray-800 to-black relative">
        {project.thumbnail_path ? (
          <img src={project.thumbnail_path} alt={project.name} className="w-full h-full object-cover opacity-60 group-hover:opacity-100 transition-opacity" />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-700">
            <Film size={48} />
          </div>
        )}
        <div className="absolute top-3 right-3 flex gap-2">
          <span className="px-2 py-1 text-xs font-semibold uppercase tracking-wide bg-black/60 backdrop-blur-sm rounded-md text-gray-300 border border-gray-700">
            {project.status}
          </span>
        </div>
      </div>
      
      <div className="p-5">
        <h3 className="text-xl font-bold text-gray-100 mb-1 truncate">{project.name}</h3>
        <p className="text-sm text-gray-400 mb-4 h-10 line-clamp-2">
          {project.description || "No description provided."}
        </p>
        
        <div className="flex items-center justify-between text-xs text-gray-500 mb-4">
          <div className="flex items-center gap-1.5">
            <Clock size={14} />
            <span>{formatDate(project.created_at)}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Film size={14} />
            <span>{project.video_count} Videos</span>
          </div>
        </div>
        
        <div className="pt-4 border-t border-[var(--border)] flex justify-between items-center">
          {showConfirm ? (
            <div className="flex gap-2 w-full">
              <button 
                onClick={handleDelete}
                className="flex-1 py-1.5 bg-red-600/20 text-red-500 hover:bg-red-600 hover:text-white rounded text-sm font-medium transition-colors border border-red-900"
              >
                Confirm
              </button>
              <button 
                onClick={cancelDelete}
                className="flex-1 py-1.5 bg-gray-800 text-gray-300 hover:bg-gray-700 rounded text-sm font-medium transition-colors"
              >
                Cancel
              </button>
            </div>
          ) : (
            <>
              <button 
                onClick={handleDelete}
                className="p-1.5 text-gray-500 hover:text-red-400 hover:bg-red-400/10 rounded transition-colors"
                title="Delete project"
              >
                <Trash2 size={18} />
              </button>
              <span className="text-[var(--accent)] text-sm font-medium flex items-center group-hover:translate-x-1 transition-transform">
                Open Workspace <ChevronRight size={16} />
              </span>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
