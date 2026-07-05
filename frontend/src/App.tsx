import { useEffect, useState } from 'react';
import axios from 'axios';

function App() {
  const [healthStatus, setHealthStatus] = useState<string>('Checking backend connection...');

  useEffect(() => {
    axios.get('/api/v1/health')
      .then(res => setHealthStatus(res.data.message))
      .catch(err => setHealthStatus('Failed to connect to backend API: ' + err.message));
  }, []);

  return (
    <div className="min-h-screen bg-[var(--background)] flex items-center justify-center text-white">
      <div className="bg-[var(--panel)] p-8 rounded-xl border border-[var(--border)] shadow-lg max-w-xl text-center space-y-4">
        <h1 className="text-3xl font-bold text-[var(--accent)]">AI Clipping Platform</h1>
        <p className="text-gray-400">Milestone 1: API Bridge & React Scaffold</p>
        
        <div className="mt-6 p-4 bg-black/30 rounded-lg">
          <p className="font-mono text-sm">Backend Status: 
            <span className={healthStatus.includes('Failed') ? 'text-red-400 ml-2' : 'text-green-400 ml-2'}>
              {healthStatus}
            </span>
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;
