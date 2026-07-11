import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import ProjectsPage from './pages/ProjectsPage';
import ProjectWorkspace from './pages/ProjectWorkspace';
import CampaignsPage from './pages/CampaignsPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/projects" replace />} />
        <Route path="/projects" element={<ProjectsPage />} />
        <Route path="/projects/:id" element={<ProjectWorkspace />} />
        <Route path="/campaigns" element={<CampaignsPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
