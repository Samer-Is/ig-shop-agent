import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Alert, AlertDescription } from '../components/ui/alert';
import { apiService } from '../services/api';
import { 
  Bot, 
  Instagram,
  Loader2,
  AlertCircle
} from 'lucide-react';

export function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const { login, isAuthenticated } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      const from = location.state?.from?.pathname || '/';
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, navigate, location]);

  // Handle Instagram OAuth callback
  useEffect(() => {
    const code = searchParams.get('code');
    const error = searchParams.get('error');
    const error_description = searchParams.get('error_description');
    const state = searchParams.get('state');

    if (error) {
      setError(`Instagram OAuth error: ${error_description || error}`);
      return;
    }

    if (code && state) {
      handleInstagramCallback(code, state);
    }
  }, [searchParams, isAuthenticated, navigate]);

  const handleInstagramCallback = async (code: string, state: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await apiService.handleInstagramCallback(code, state);
      
      if (response.data?.token && response.data?.user) {
        // Successfully connected Instagram and got auth token
        login(response.data.token, response.data.user);
        navigate('/dashboard');
      } else {
        setError(response.error || 'Failed to connect Instagram');
      }
    } catch (err) {
      console.error('Instagram callback error:', err);
      setError('Network error while connecting Instagram');
    } finally {
      setIsLoading(false);
    }
  };

  const handleInstagramLogin = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiService.getInstagramAuthUrl();
      
      if (response.data?.auth_url) {
        // Store current URL for redirect back after auth
        sessionStorage.setItem('auth_redirect', window.location.href);
        
        // Redirect to Instagram OAuth
        window.location.href = response.data.auth_url;
      } else {
        setError(response.error || 'Failed to get Instagram login URL');
      }
    } catch (err) {
      console.error('Instagram login error:', err);
      setError('Network error while starting Instagram login');
    } finally {
      setIsLoading(false);
    }
  };

  const features = [
    'AI-powered Instagram DM automation',
    'Real-time conversation management',
    'Automated order processing',
    'Advanced analytics and reporting',
    'Multi-tenant architecture',
    'Enterprise-grade security'
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-4">
      <div className="w-full max-w-6xl grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
        {/* Left Side - Branding & Features */}
        <div className="hidden lg:block space-y-8">
          <div className="space-y-6">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-12 h-12 bg-gradient-to-br from-purple-600 to-blue-600 rounded-lg">
                <Bot className="w-7 h-7 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-slate-900">IG Shop Agent</h1>
                <p className="text-slate-600">Instagram DM Automation Platform</p>
              </div>
            </div>
            
            <div className="space-y-4">
              <h2 className="text-2xl font-semibold text-slate-800">
                Transform Your Instagram Shop
              </h2>
              <p className="text-slate-600">
                Connect your Instagram business account to automate customer service, 
                process orders, and grow your business with AI-powered conversations.
              </p>
            </div>

            <div className="space-y-3">
              {features.map((feature, index) => (
                <div key={index} className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-purple-600" />
                  <span className="text-slate-700">{feature}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Side - Login Form */}
        <div className="w-full max-w-md mx-auto">
          <Card className="border-0 shadow-xl bg-white/80 backdrop-blur">
            <CardHeader className="space-y-1 text-center">
              <CardTitle className="text-2xl font-bold">Welcome Back</CardTitle>
              <p className="text-slate-600">
                Connect your Instagram account to get started
              </p>
            </CardHeader>
            <CardContent className="space-y-4">
              {error && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <Button
                className="w-full h-11 text-base"
                onClick={handleInstagramLogin}
                disabled={isLoading}
              >
                {isLoading ? (
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                ) : (
                  <Instagram className="mr-2 h-5 w-5" />
                )}
                Connect with Instagram
              </Button>

              <div className="text-center text-sm text-slate-600">
                By connecting, you agree to our Terms of Service and Privacy Policy
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
