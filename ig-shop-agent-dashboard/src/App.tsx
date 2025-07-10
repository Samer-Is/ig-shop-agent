import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { Toaster } from './components/ui/toaster';
import { ErrorBoundary } from './components/ErrorBoundary';
import { ProtectedRoute } from './components/ProtectedRoute';
import { DashboardLayout } from './components/layout/DashboardLayout';

// Import pages
import { Login } from './pages/Login';
import ProductionDashboard from './components/ProductionDashboard';
import { Catalog } from './pages/Catalog';
import { AddProduct } from './pages/AddProduct';
import { Orders } from './pages/Orders';
import { Conversations } from './pages/Conversations';
import { Analytics } from './pages/Analytics';
import { BusinessProfile } from './pages/BusinessProfile';
import { Settings } from './pages/Settings';
import { KnowledgeBase } from './pages/KnowledgeBase';
import { InstagramAgent } from './pages/InstagramAgent';
import { OnboardingWizard } from './pages/OnboardingWizard';

import './App.css';

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Router>
          <div className="App">
            <Routes>
              {/* Public routes */}
              <Route path="/login" element={<Login />} />
              
              {/* Protected routes with layout */}
              <Route
                path="/"
                element={
                  <ProtectedRoute>
                    <DashboardLayout />
                  </ProtectedRoute>
                }
              >
                {/* Production Dashboard as default */}
                <Route index element={<ProductionDashboard />} />
                <Route path="dashboard" element={<ProductionDashboard />} />
                <Route path="catalog" element={<Catalog />} />
                <Route path="add-product" element={<AddProduct />} />
                <Route path="orders" element={<Orders />} />
                <Route path="conversations" element={<Conversations />} />
                <Route path="analytics" element={<Analytics />} />
                <Route path="business-profile" element={<BusinessProfile />} />
                <Route path="settings" element={<Settings />} />
                <Route path="knowledge-base" element={<KnowledgeBase />} />
                <Route path="instagram-agent" element={<InstagramAgent />} />
                <Route path="onboarding" element={<OnboardingWizard />} />
              </Route>

              {/* Redirect any unknown routes to dashboard */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
            <Toaster />
          </div>
        </Router>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;
