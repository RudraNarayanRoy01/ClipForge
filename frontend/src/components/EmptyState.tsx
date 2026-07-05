import { FolderPlus } from 'lucide-react';

interface EmptyStateProps {
  onCreateClick: () => void;
}

export default function EmptyState({ onCreateClick }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-20 px-4 text-center">
      <div className="bg-[var(--panel)] p-6 rounded-full border border-[var(--border)] mb-6 shadow-xl">
        <FolderPlus size={48} className="text-[var(--accent)]" />
      </div>
      <h2 className="text-2xl font-semibold text-white mb-2">No projects yet</h2>
      <p className="text-gray-400 max-w-md mb-8">
        Get started by creating a new video clipping workspace. You'll be able to import footage, run AI analysis, and generate viral clips.
      </p>
      <button 
        onClick={onCreateClick}
        className="px-6 py-3 bg-[var(--accent)] text-white font-medium rounded-lg hover:bg-opacity-90 transition-all active:scale-95 flex items-center gap-2"
      >
        <FolderPlus size={20} />
        Create Project
      </button>
    </div>
  );
}
