import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiService } from '../services/api';
import type { User } from '../types';

// Remove local User interface to use the one from types/index.ts

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string, userData: User) => void;
  logout: () => void;
  checkAuth: () => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!user;

  const login = (token: string, userData: User) => {
    apiService.setAuthToken(token);
    setUser(userData);
    localStorage.setItem('ig_user', JSON.stringify(userData));
    localStorage.setItem('ig_session_token', token);
  };

  const logout = () => {
    apiService.clearAuthToken();
    setUser(null);
    localStorage.removeItem('ig_user');
    localStorage.removeItem('ig_session_token');
    localStorage.removeItem('ig_tenant_id');
  };

  const checkAuth = async (): Promise<boolean> => {
    try {
      const token = localStorage.getItem('ig_session_token');
      const userData = localStorage.getItem('ig_user');

      if (!token || !userData) {
        setIsLoading(false);
        return false;
      }

      // Set token for API calls
      apiService.setAuthToken(token);

      // Verify token is still valid
      const response = await apiService.verifyToken();
      
      if (response.data?.valid) {
        setUser(JSON.parse(userData));
        setIsLoading(false);
        return true;
      } else {
        // Token invalid, clear everything
        logout();
        setIsLoading(false);
        return false;
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      logout();
      setIsLoading(false);
      return false;
    }
  };

  useEffect(() => {
    checkAuth();
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        isLoading,
        login,
        logout,
        checkAuth,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
} 