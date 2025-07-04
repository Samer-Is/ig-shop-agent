import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Badge } from '../components/ui/badge';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Progress } from '../components/ui/progress';
import { CheckCircle, Instagram, Upload, FileText, Settings, ArrowRight, AlertCircle } from 'lucide-react';
import { apiService } from '../services/apiService';
import { useAuth } from '../contexts/AuthContext';

interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  completed: boolean;
}

interface BusinessProfile {
  instagram_handle: string;
  business_name: string;
  intro_message: string;
  delivery_info: string;
  return_policy: string;
  special_offers: string;
  brand_voice: string;
  business_hours: string;
  contact_phone: string;
}

export function OnboardingWizard() {
  const { user, login } = useAuth();
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [instagramConnected, setInstagramConnected] = useState(false);
  const [catalogUploaded, setCatalogUploaded] = useState(false);
  const [knowledgeBaseUploaded, setKnowledgeBaseUploaded] = useState(false);
  const [businessProfile, setBusinessProfile] = useState<BusinessProfile>({
    instagram_handle: '',
    business_name: '',
    intro_message: '',
    delivery_info: '',
    return_policy: '',
    special_offers: '',
    brand_voice: '',
    business_hours: '',
    contact_phone: ''
  });

  const steps: OnboardingStep[] = [
    {
      id: 'instagram',
      title: 'Connect Instagram',
      description: 'Link your Instagram Business account with Meta OAuth',
      completed: instagramConnected
    },
    {
      id: 'catalog',
      title: 'Upload Product Catalog',
      description: 'Import your products via CSV file',
      completed: catalogUploaded
    },
    {
      id: 'knowledge',
      title: 'Knowledge Base',
      description: 'Upload business documents and FAQs',
      completed: knowledgeBaseUploaded
    },
    {
      id: 'profile',
      title: 'Business Profile',
      description: 'Configure AI personality and responses',
      completed: Object.values(businessProfile).every((v: string) => v && v.length > 0)
    }
  ];

  const progress = (steps.filter(s => s.completed).length / steps.length) * 100;

  // Instagram OAuth Integration
  const handleInstagramConnect = async () => {
    setLoading(true);
    setError(null);

    try {
      // Get auth URL from our backend
      const response = await apiService.getInstagramAuthUrl();
      
      if (response.error) {
        setError(response.error);
        setLoading(false);
        return;
      }

      const { auth_url, state } = response.data;
      
      // Store state in localStorage for verification
      localStorage.setItem('oauth_state', state);

      // Open OAuth popup
      const popup = window.open(
        auth_url,
        'instagram-oauth',
        'width=600,height=800,scrollbars=yes'
      );

      if (!popup) {
        throw new Error('Popup blocked. Please allow popups for this site.');
      }

      // Listen for OAuth completion
      const handleMessage = async (event: MessageEvent) => {
        if (event.origin !== window.location.origin) return;

        if (event.data.type === 'INSTAGRAM_OAUTH_SUCCESS') {
          const { code, state: returnedState } = event.data;
          
          // Verify state
          const storedState = localStorage.getItem('oauth_state');
          if (!storedState || storedState !== returnedState) {
            setError('Invalid authentication response. Please try again.');
            setLoading(false);
            return;
          }

          try {
            // Exchange code for token
            const authResponse = await apiService.handleInstagramCallback(code, returnedState);
            
            if (authResponse.error) {
              setError(authResponse.error);
              setLoading(false);
              return;
            }

            // Update user context with Instagram data
            if (user) {
              const updatedUser = {
                ...user,
                instagram_connected: true,
                instagram_handle: authResponse.data.instagram_handle
              };
              login(localStorage.getItem('ig_session_token') || '', updatedUser);
            }

            // Clear state
            localStorage.removeItem('oauth_state');
            
            // Close popup and proceed
            popup.close();
            setInstagramConnected(true);
            setLoading(false);
            if (currentStep === 0) {
              setCurrentStep(1);
            }

          } catch (error) {
            console.error('Failed to complete Instagram authentication:', error);
            setError('Failed to complete Instagram authentication. Please try again.');
            setLoading(false);
          }
        } else if (event.data.type === 'INSTAGRAM_OAUTH_ERROR') {
          popup.close();
          setError(event.data.error_description || 'Instagram connection failed');
          setLoading(false);
        }
      };

      window.addEventListener('message', handleMessage);

      // Handle popup closed without completion
      const checkClosed = setInterval(() => {
        if (popup.closed) {
          clearInterval(checkClosed);
          window.removeEventListener('message', handleMessage);
          if (!instagramConnected) {
            setError('Instagram connection cancelled');
            setLoading(false);
          }
        }
      }, 1000);

    } catch (error) {
      console.error('Instagram connection error:', error);
      setError('Failed to connect to Instagram. Please try again.');
      setLoading(false);
    }
  };

  // Catalog Upload
  const handleCatalogUpload = async (file: File) => {
    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('catalog', file);

      const response = await fetch('https://igshop-dev-functions-v2.azurewebsites.net/api/catalog/upload', {
        method: 'POST',
        body: formData
      });

      const result = await response.json();

      if (response.ok) {
        setCatalogUploaded(true);
      } else {
        throw new Error(result.error || 'Failed to upload catalog');
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to upload catalog');
    } finally {
      setLoading(false);
    }
  };

  // Knowledge Base Upload
  const handleKnowledgeUpload = async (files: File[]) => {
    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      files.forEach((file, index) => {
        formData.append(`document_${index}`, file);
      });

      const response = await fetch('https://igshop-dev-functions-v2.azurewebsites.net/api/knowledge-base/upload', {
        method: 'POST',
        body: formData
      });

      const result = await response.json();

      if (response.ok) {
        setKnowledgeBaseUploaded(true);
      } else {
        throw new Error(result.error || 'Failed to upload knowledge base');
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to upload knowledge base');
    } finally {
      setLoading(false);
    }
  };

  // Business Profile Save
  const handleProfileSave = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('https://igshop-dev-functions-v2.azurewebsites.net/api/business-profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(businessProfile)
      });

      const result = await response.json();

      if (response.ok) {
        // Profile saved successfully
        alert('🎉 IG Shop Agent setup complete! Your AI assistant is now ready to handle Instagram DMs.');
        window.location.href = '/'; // Redirect to main dashboard
      } else {
        throw new Error(result.error || 'Failed to save business profile');
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to save profile');
    } finally {
      setLoading(false);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 0: // Instagram Connection
        return (
          <div className="space-y-6">
            <div className="text-center">
              <Instagram className="h-16 w-16 mx-auto mb-4 text-pink-600" />
              <h3 className="text-xl font-semibold mb-2">Connect Your Instagram Business Account</h3>
              <p className="text-gray-600 mb-6">
                Link your Instagram Business page to enable DM automation and AI responses.
              </p>
            </div>

            {instagramConnected ? (
              <div className="text-center">
                <CheckCircle className="h-12 w-12 mx-auto mb-4 text-green-600" />
                <p className="text-green-600 font-semibold">Instagram Connected Successfully!</p>
                <p className="text-sm text-gray-600">Handle: @{businessProfile.instagram_handle}</p>
              </div>
            ) : (
              <div className="text-center">
                <Button 
                  onClick={handleInstagramConnect} 
                  disabled={loading}
                  className="bg-pink-600 hover:bg-pink-700"
                >
                  {loading ? 'Connecting...' : 'Connect with Instagram'}
                </Button>
                <p className="text-xs text-gray-500 mt-2">
                  You'll be redirected to Instagram to authorize access
                </p>
              </div>
            )}
          </div>
        );

      case 1: // Catalog Upload
        return (
          <div className="space-y-6">
            <div className="text-center">
              <Upload className="h-16 w-16 mx-auto mb-4 text-blue-600" />
              <h3 className="text-xl font-semibold mb-2">Upload Product Catalog</h3>
              <p className="text-gray-600 mb-6">
                Upload a CSV file with your product catalog (name, price, description, etc.)
              </p>
            </div>

            {catalogUploaded ? (
              <div className="text-center">
                <CheckCircle className="h-12 w-12 mx-auto mb-4 text-green-600" />
                <p className="text-green-600 font-semibold">Catalog Uploaded Successfully!</p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                  <input
                    type="file"
                    accept=".csv"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) handleCatalogUpload(file);
                    }}
                    className="hidden"
                    id="catalog-upload"
                  />
                  <label htmlFor="catalog-upload" className="cursor-pointer">
                    <Upload className="h-8 w-8 mx-auto mb-2 text-gray-400" />
                    <p className="text-gray-600">Click to upload CSV file</p>
                    <p className="text-xs text-gray-400">Required columns: name, price, description</p>
                  </label>
                </div>
              </div>
            )}
          </div>
        );

      case 2: // Knowledge Base
        return (
          <div className="space-y-6">
            <div className="text-center">
              <FileText className="h-16 w-16 mx-auto mb-4 text-green-600" />
              <h3 className="text-xl font-semibold mb-2">Knowledge Base</h3>
              <p className="text-gray-600 mb-6">
                Upload business documents, FAQs, and policies for the AI to reference
              </p>
            </div>

            {knowledgeBaseUploaded ? (
              <div className="text-center">
                <CheckCircle className="h-12 w-12 mx-auto mb-4 text-green-600" />
                <p className="text-green-600 font-semibold">Knowledge Base Uploaded!</p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                  <input
                    type="file"
                    multiple
                    accept=".pdf,.doc,.docx,.txt"
                    onChange={(e) => {
                      const files = Array.from(e.target.files || []);
                      if (files.length > 0) handleKnowledgeUpload(files);
                    }}
                    className="hidden"
                    id="knowledge-upload"
                  />
                  <label htmlFor="knowledge-upload" className="cursor-pointer">
                    <FileText className="h-8 w-8 mx-auto mb-2 text-gray-400" />
                    <p className="text-gray-600">Click to upload documents</p>
                    <p className="text-xs text-gray-400">PDF, DOC, DOCX, TXT files</p>
                  </label>
                </div>
                <Button 
                  onClick={() => setKnowledgeBaseUploaded(true)}
                  variant="outline"
                  className="w-full"
                >
                  Skip for now
                </Button>
              </div>
            )}
          </div>
        );

      case 3: // Business Profile
        return (
          <div className="space-y-6">
            <div className="text-center">
              <Settings className="h-16 w-16 mx-auto mb-4 text-purple-600" />
              <h3 className="text-xl font-semibold mb-2">Business Profile</h3>
              <p className="text-gray-600 mb-6">
                Configure your AI assistant's personality and responses
              </p>
            </div>

            <div className="space-y-4">
              <div>
                <Label htmlFor="business_name">Business Name</Label>
                <Input
                  id="business_name"
                  value={businessProfile.business_name}
                  onChange={(e) => setBusinessProfile(prev => ({ ...prev, business_name: e.target.value }))}
                  placeholder="e.g., Racing Jackets Jordan"
                />
              </div>

              <div>
                <Label htmlFor="intro_message">Welcome Message (Arabic)</Label>
                <Textarea
                  id="intro_message"
                  value={businessProfile.intro_message}
                  onChange={(e) => setBusinessProfile(prev => ({ ...prev, intro_message: e.target.value }))}
                  placeholder="أهلاً وسهلاً! أنا مساعد متجر..."
                  rows={3}
                />
              </div>

              <div>
                <Label htmlFor="delivery_info">Delivery Information</Label>
                <Textarea
                  id="delivery_info"
                  value={businessProfile.delivery_info}
                  onChange={(e) => setBusinessProfile(prev => ({ ...prev, delivery_info: e.target.value }))}
                  rows={2}
                />
              </div>

              <div>
                <Label htmlFor="contact_phone">Contact Phone</Label>
                <Input
                  id="contact_phone"
                  value={businessProfile.contact_phone}
                  onChange={(e) => setBusinessProfile(prev => ({ ...prev, contact_phone: e.target.value }))}
                  placeholder="+962 X XXXX XXXX"
                />
              </div>

              <div>
                <Label htmlFor="business_hours">Business Hours</Label>
                <Input
                  id="business_hours"
                  value={businessProfile.business_hours}
                  onChange={(e) => setBusinessProfile(prev => ({ ...prev, business_hours: e.target.value }))}
                />
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">IG Shop Agent Setup</h1>
          <p className="text-gray-600">Set up your Instagram DM automation in 4 simple steps</p>
        </div>

        {/* Progress */}
        <Card className="mb-8">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm font-medium">Setup Progress</span>
              <span className="text-sm text-gray-500">{Math.round(progress)}% Complete</span>
            </div>
            <Progress value={progress} className="mb-4" />
            <div className="grid grid-cols-4 gap-4">
              {steps.map((step, index) => (
                <div key={step.id} className="text-center">
                  <div className={`w-8 h-8 mx-auto mb-2 rounded-full flex items-center justify-center text-sm ${
                    step.completed ? 'bg-green-500 text-white' : 
                    index === currentStep ? 'bg-blue-500 text-white' : 
                    'bg-gray-200 text-gray-600'
                  }`}>
                    {step.completed ? <CheckCircle className="h-4 w-4" /> : index + 1}
                  </div>
                  <p className="text-xs text-gray-600">{step.title}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Current Step */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>{steps[currentStep].title}</CardTitle>
            <CardDescription>{steps[currentStep].description}</CardDescription>
          </CardHeader>
          <CardContent>
            {error && (
              <Alert className="mb-6">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
            
            {renderStepContent()}
          </CardContent>
        </Card>

        {/* Navigation */}
        <div className="flex justify-between">
          <Button
            variant="outline"
            onClick={() => setCurrentStep(Math.max(0, currentStep - 1))}
            disabled={currentStep === 0}
          >
            Previous
          </Button>

          {currentStep === steps.length - 1 ? (
            <Button
              onClick={handleProfileSave}
              disabled={loading || !steps[currentStep].completed}
              className="bg-green-600 hover:bg-green-700"
            >
              {loading ? 'Finishing Setup...' : 'Complete Setup'}
            </Button>
          ) : (
            <Button
              onClick={() => setCurrentStep(Math.min(steps.length - 1, currentStep + 1))}
              disabled={!steps[currentStep].completed}
            >
              Next
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          )}
        </div>
      </div>
    </div>
  );
} 