import React, { useState } from 'react';
import { useCampaignStore } from '../../store/useCampaignStore';
import { FileText, Link, File, AlertCircle, Loader2 } from 'lucide-react';

export const CampaignImportCard: React.FC = () => {
  const { importCampaign, isImporting, importProgressText, error, clearError } = useCampaignStore();
  const [contentType, setContentType] = useState<'url' | 'text'>('url');
  const [source, setSource] = useState('');

  const handleImport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!source.trim()) return;
    await importCampaign(contentType, source);
    if (!useCampaignStore.getState().error) {
      setSource('');
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
      <h2 className="text-lg font-semibold text-slate-200 mb-4 flex items-center gap-2">
        <span>Import Campaign</span>
      </h2>
      
      {error && (
        <div className="mb-4 p-3 bg-rose-950/50 border-l-4 border-rose-500 rounded text-rose-200 text-sm flex items-start justify-between">
          <div className="flex gap-2">
            <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
            <p>{error}</p>
          </div>
          <button onClick={clearError} className="text-rose-400 hover:text-rose-200">&times;</button>
        </div>
      )}

      <form onSubmit={handleImport} className="space-y-4">
        <div className="flex gap-2 bg-slate-950 p-1 rounded-lg border border-slate-800 w-fit">
          <button
            type="button"
            disabled={isImporting}
            onClick={() => setContentType('url')}
            className={`flex items-center gap-2 px-3 py-1.5 text-sm rounded-md transition-colors ${
              contentType === 'url' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Link className="w-4 h-4" /> URL
          </button>
          <button
            type="button"
            disabled={isImporting}
            onClick={() => setContentType('text')}
            className={`flex items-center gap-2 px-3 py-1.5 text-sm rounded-md transition-colors ${
              contentType === 'text' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <FileText className="w-4 h-4" /> Raw Text
          </button>
          <button
            type="button"
            disabled
            className="flex items-center gap-2 px-3 py-1.5 text-sm rounded-md text-slate-600 cursor-not-allowed opacity-50 relative group"
            title="PDF Support Coming Soon"
          >
            <File className="w-4 h-4" /> PDF
            <span className="absolute -top-8 left-1/2 -translate-x-1/2 bg-slate-800 text-slate-300 text-xs px-2 py-1 rounded hidden group-hover:block whitespace-nowrap">
              Coming Soon
            </span>
          </button>
        </div>

        <div>
          {contentType === 'url' ? (
            <input
              type="url"
              required
              disabled={isImporting}
              placeholder="https://example.com/campaign-brief"
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-2 text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50 transition-shadow"
              value={source}
              onChange={(e) => setSource(e.target.value)}
            />
          ) : (
            <textarea
              required
              disabled={isImporting}
              placeholder="Paste campaign requirements and brief here..."
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-2 text-slate-200 h-32 resize-none focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50 transition-shadow font-mono text-sm"
              value={source}
              onChange={(e) => setSource(e.target.value)}
            />
          )}
        </div>

        <div className="flex justify-end items-center gap-4">
          {isImporting && (
            <span className="text-sm text-indigo-400 flex items-center gap-2 animate-pulse">
              {importProgressText}
            </span>
          )}
          <button
            type="submit"
            disabled={isImporting || !source.trim()}
            className="bg-indigo-600 hover:bg-indigo-500 text-white px-5 py-2 rounded-lg font-medium transition-all disabled:opacity-50 flex items-center gap-2 shadow-sm shadow-indigo-900/50"
          >
            {isImporting ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
            {isImporting ? 'Importing...' : 'Extract Intelligence'}
          </button>
        </div>
      </form>
    </div>
  );
};
