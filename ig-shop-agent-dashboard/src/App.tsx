import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from './components/ui/toaster';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { DashboardLayout } from './components/layout/DashboardLayout';
import { Dashboard } from './pages/Dashboard';
import { WorkingDashboard } from './pages/WorkingDashboard';
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
      <AuthProvider>
        <div className="min-h-screen bg-slate-50">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/" element={
              <ProtectedRoute>
                <DashboardLayout />
              </ProtectedRoute>
            }>
              <Route index element={<WorkingDashboard />} />
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
      </AuthProvider>
    </Router>
  );
}

export default App
