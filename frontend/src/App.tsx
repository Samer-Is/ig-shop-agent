import React, { useState, useEffect } from 'react';
import MinimalDashboard from './components/MinimalDashboard';
import { productionApi } from './utils/api';

interface User {
  id: string;
  instagram_handle: string;
  instagram_connected: boolean;
}

const App: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isConnecting, setIsConnecting] = useState(false);

  useEffect(() => {
    // Check if user is already logged in
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      try {
        setUser(JSON.parse(savedUser));
      } catch (error) {
        console.error('Error parsing saved user:', error);
        localStorage.removeItem('user');
      }
    }
    setIsLoading(false);
  }, []);

  const handleInstagramConnect = async () => {
    try {
      setIsConnecting(true);
      const response = await productionApi.getInstagramAuthUrl();
      
      if (response.auth_url) {
        // Redirect to Instagram OAuth
        window.location.href = response.auth_url;
      } else {
        throw new Error('Failed to get Instagram auth URL');
      }
    } catch (error) {
      console.error('Instagram connect error:', error);
      alert('Failed to connect to Instagram. Please try again.');
    } finally {
      setIsConnecting(false);
    }
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('user');
  };

  // Handle Instagram OAuth callback
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const state = urlParams.get('state');

    if (code && state) {
      handleInstagramCallback(code, state);
    }
  }, []);

  const handleInstagramCallback = async (code: string, state: string) => {
    try {
      setIsConnecting(true);
      const response = await productionApi.handleInstagramCallback({ code, state });
      
      if (response.success && response.user) {
        const userData = {
          id: response.user.id,
          instagram_handle: response.instagram_handle || response.user.instagram_handle,
          instagram_connected: response.user.instagram_connected
        };
        
        setUser(userData);
        localStorage.setItem('user', JSON.stringify(userData));
        
        // Clean up URL
        window.history.replaceState({}, document.title, window.location.pathname);
        
        alert('Instagram connected successfully!');
      } else {
        throw new Error(response.message || 'Failed to connect Instagram');
      }
    } catch (error) {
      console.error('Instagram callback error:', error);
      alert('Failed to complete Instagram connection. Please try again.');
    } finally {
      setIsConnecting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user || !user.instagram_connected) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full bg-white rounded-lg shadow-md p-8">
          <div className="text-center">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">IG Shop Agent</h1>
            <p className="text-gray-600 mb-8">
              AI-powered Instagram DM management for your business
            </p>
            
            {isConnecting ? (
              <div className="text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-600">Connecting to Instagram...</p>
              </div>
            ) : (
              <button
                onClick={handleInstagramConnect}
                className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold py-3 px-6 rounded-lg hover:from-purple-700 hover:to-pink-700 transition duration-200 flex items-center justify-center"
              >
                <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
                </svg>
                Connect Instagram Account
              </button>
            )}
            
            <p className="text-xs text-gray-500 mt-4">
              Connect your Instagram Business account to start managing DMs with AI
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Simple top bar with user info and logout */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-3 flex justify-between items-center">
          <div className="flex items-center">
            <h1 className="text-xl font-bold text-gray-900">IG Shop Agent</h1>
            <span className="ml-4 text-sm text-gray-600">
              Connected: @{user.instagram_handle}
            </span>
          </div>
          <button
            onClick={handleLogout}
            className="text-gray-600 hover:text-gray-900 text-sm"
          >
            Logout
          </button>
        </div>
      </div>
      
      {/* Main dashboard */}
      <MinimalDashboard />
    </div>
  );
};

export default App; 