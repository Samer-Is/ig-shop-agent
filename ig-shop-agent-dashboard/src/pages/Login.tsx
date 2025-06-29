import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Badge } from '../components/ui/badge';
import { Alert, AlertDescription } from '../components/ui/alert';
import { apiService } from '../services/api';
import { 
  Bot, 
  Instagram, 
  Shield, 
  ArrowRight,
  CheckCircle,
  AlertCircle,
  Loader2
} from 'lucide-react';

export function Login() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [businessName, setBusinessName] = useState('');

  // Handle Instagram OAuth callback
  useEffect(() => {
    const code = searchParams.get('code');
    const state = searchParams.get('state');
    const error = searchParams.get('error');

    if (error) {
      setError(`Instagram OAuth error: ${error}`);
      return;
    }

    if (code && state) {
      handleInstagramCallback(code, state);
    }
  }, [searchParams]);

  const handleInstagramCallback = async (code: string, state: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiService.handleInstagramCallback(
        code, 
        state, 
        `${window.location.origin}/login`
      );

      if (response.data?.success) {
        // Store the session token
        apiService.setAuthToken(response.data.session_token);
        
        // Store user info in localStorage for easy access
        localStorage.setItem('ig_user', JSON.stringify(response.data.user));
        localStorage.setItem('ig_tenant_id', response.data.tenant_id);
        
        // Navigate to dashboard
        navigate('/');
      } else {
        setError(response.error || 'Authentication failed');
      }
    } catch (err) {
      setError('Network error during authentication');
    } finally {
      setIsLoading(false);
    }
  };

  const handleInstagramLogin = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiService.getInstagramAuthUrl(
        businessName, 
        `${window.location.origin}/login`
      );

      if (response.data?.auth_url) {
        // Redirect to Instagram OAuth
        window.location.href = response.data.auth_url;
      } else {
        setError(response.error || 'Failed to generate Instagram auth URL');
        setIsLoading(false);
      }
    } catch (err) {
      setError('Network error. Please try again.');
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
              <h2 className="text-2xl font-bold text-slate-900">
                Automate Your Instagram Business
              </h2>
              <p className="text-slate-600 text-lg">
                Transform your Instagram DMs into a powerful sales channel with AI-driven automation
              </p>
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-slate-900">Key Features:</h3>
            <div className="space-y-3">
              {features.map((feature, index) => (
                <div key={index} className="flex items-center gap-3">
                  <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
                  <span className="text-slate-700">{feature}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-4">
            <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
              <Instagram className="w-3 h-3 mr-1" />
              Instagram Official API
            </Badge>
            <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
              <Shield className="w-3 h-3 mr-1" />
              Enterprise Security
            </Badge>
          </div>
        </div>

        {/* Right Side - Login Form */}
        <div className="w-full max-w-md mx-auto">
          <Card className="shadow-xl border-0">
            <CardHeader className="space-y-1 pb-6">
              <div className="flex items-center justify-center lg:hidden mb-6">
                <div className="flex items-center gap-3">
                  <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-br from-purple-600 to-blue-600 rounded-lg">
                    <Bot className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h1 className="text-xl font-bold text-slate-900">IG Shop Agent</h1>
                    <p className="text-sm text-slate-500">Instagram DM Automation</p>
                  </div>
                </div>
              </div>
              <CardTitle className="text-2xl font-bold text-center">Connect Your Instagram</CardTitle>
              <p className="text-slate-600 text-center">
                Link your Instagram Business account to get started
              </p>
            </CardHeader>
            <CardContent>
              {error && (
                <Alert className="mb-6 border-red-200 bg-red-50">
                  <AlertCircle className="h-4 w-4 text-red-600" />
                  <AlertDescription className="text-red-700">
                    {error}
                  </AlertDescription>
                </Alert>
              )}

              <div className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="businessName">Business Name (Optional)</Label>
                  <Input
                    id="businessName"
                    type="text"
                    placeholder="e.g., Jordan Fashion Store"
                    value={businessName}
                    onChange={(e) => setBusinessName(e.target.value)}
                    disabled={isLoading}
                  />
                  <p className="text-xs text-slate-500">
                    This helps us identify your store during setup
                  </p>
                </div>
                
                <Button 
                  onClick={handleInstagramLogin}
                  className="w-full bg-gradient-to-r from-pink-600 to-purple-600 hover:from-pink-700 hover:to-purple-700"
                  disabled={isLoading}
                  size="lg"
                >
                  {isLoading ? (
                    <div className="flex items-center gap-2">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Connecting to Instagram...
                    </div>
                  ) : (
                    <div className="flex items-center gap-2">
                      <Instagram className="w-5 h-5" />
                      Connect with Instagram
                      <ArrowRight className="w-4 h-4" />
                    </div>
                  )}
                </Button>

                <div className="text-center">
                  <div className="relative">
                    <div className="absolute inset-0 flex items-center">
                      <span className="w-full border-t border-slate-200" />
                    </div>
                    <div className="relative flex justify-center text-xs uppercase">
                      <span className="bg-white px-2 text-slate-500">How it works</span>
                    </div>
                  </div>
                </div>

                <div className="space-y-3 text-sm text-slate-600">
                  <div className="flex items-start gap-2">
                    <div className="w-5 h-5 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-xs font-bold mt-0.5">1</div>
                    <p>Connect your Instagram Business account</p>
                  </div>
                  <div className="flex items-start gap-2">
                    <div className="w-5 h-5 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-xs font-bold mt-0.5">2</div>
                    <p>Upload your product catalog and business info</p>
                  </div>
                  <div className="flex items-start gap-2">
                    <div className="w-5 h-5 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-xs font-bold mt-0.5">3</div>
                    <p>Start receiving AI-powered Instagram DM responses</p>
                  </div>
                </div>
              </div>
              
              <div className="mt-6 pt-6 border-t border-slate-200">
                <p className="text-center text-sm text-slate-600">
                  Don't have an account?{' '}
                  <Button variant="link" className="px-0 text-sm font-medium">
                    Contact sales
                  </Button>
                </p>
              </div>
            </CardContent>
          </Card>
          
          <div className="mt-6 text-center">
            <p className="text-xs text-slate-500">
              By signing in, you agree to our{' '}
              <Button variant="link" className="px-0 text-xs h-auto">
                Terms of Service
              </Button>{' '}
              and{' '}
              <Button variant="link" className="px-0 text-xs h-auto">
                Privacy Policy
              </Button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
