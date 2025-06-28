import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from './components/ui/toaster';
import { DashboardLayout } from './components/layout/DashboardLayout';
import { Dashboard } from './pages/Dashboard';
import { FunctionalDashboard } from './pages/FunctionalDashboard';
import { Catalog } from './pages/Catalog';
import { Orders } from './pages/Orders';
import { Conversations } from './pages/Conversations';
import { KnowledgeBase } from './pages/KnowledgeBase';
import { BusinessProfile } from './pages/BusinessProfile';
import { Analytics } from './pages/Analytics';
import { Settings } from './pages/Settings';
import { Login } from './pages/Login';
import './App.css'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-slate-50">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<DashboardLayout />}>
            <Route index element={<FunctionalDashboard />} />
            <Route path="mock-dashboard" element={<Dashboard />} />
            <Route path="catalog" element={<Catalog />} />
            <Route path="orders" element={<Orders />} />
            <Route path="conversations" element={<Conversations />} />
            <Route path="knowledge-base" element={<KnowledgeBase />} />
            <Route path="business-profile" element={<BusinessProfile />} />
            <Route path="analytics" element={<Analytics />} />
            <Route path="settings" element={<Settings />} />
          </Route>
        </Routes>
        <Toaster />
      </div>
    </Router>
  );
}

export default App
