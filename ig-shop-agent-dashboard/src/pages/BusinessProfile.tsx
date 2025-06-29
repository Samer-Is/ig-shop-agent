import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Label } from '../components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Badge } from '../components/ui/badge';
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import { 
  User, 
  Clock, 
  Phone, 
  Mail, 
  MapPin, 
  Bot,
  Save,
  RotateCcw,
  CheckCircle,
  AlertCircle,
  Loader2
} from 'lucide-react';
import { apiService } from '../services/api';
import { BusinessProfile as BusinessProfileType } from '../types';

export function BusinessProfile() {
  const [profile, setProfile] = useState<BusinessProfileType | null>(null);
  const [hasChanges, setHasChanges] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load profile from API
  useEffect(() => {
    const loadProfile = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        // Create default profile structure for now
        const defaultProfile: BusinessProfileType = {
          tenant_id: 'current',
          yaml_profile: {
            business_name: 'Your Business',
            description: '',
            contact_info: {
              email: '',
              phone: '',
              address: ''
            },
            operating_hours: {
              sunday: '9:00 AM - 6:00 PM',
              monday: '9:00 AM - 6:00 PM',
              tuesday: '9:00 AM - 6:00 PM',
              wednesday: '9:00 AM - 6:00 PM',
              thursday: '9:00 AM - 6:00 PM',
              friday: '9:00 AM - 6:00 PM',
              saturday: '9:00 AM - 6:00 PM'
            },
            policies: {
              shipping: '',
              returns: '',
              payment: ''
            },
            ai_personality: {
              tone: 'friendly',
              language: 'arabic',
              greeting: 'أهلاً وسهلاً!'
            }
          }
        };
        
        setProfile(defaultProfile);
      } catch (err) {
        setError('Failed to load business profile');
      } finally {
        setIsLoading(false);
      }
    };

    loadProfile();
  }, []);

  const handleSave = async () => {
    if (!profile) return;
    try {
      // TODO: Implement API call to save profile
      console.log('Saving profile:', profile);
      setHasChanges(false);
    } catch (err) {
      setError('Failed to save profile');
    }
  };

  const handleReset = () => {
    if (profile) {
      // Reset to original loaded state
      setHasChanges(false);
    }
  };

  const updateProfile = (section: string, field: string, value: any) => {
    setProfile(prev => {
      if (!prev) return prev;
      return {
        ...prev,
        yaml_profile: {
          ...prev.yaml_profile,
          [section]: {
            ...prev.yaml_profile[section],
            [field]: value
          }
        }
      };
    });
    setHasChanges(true);
  };

  const updateBasicInfo = (field: string, value: string) => {
    setProfile(prev => {
      if (!prev) return prev;
      return {
        ...prev,
        yaml_profile: {
          ...prev.yaml_profile,
          [field]: value
        }
      };
    });
    setHasChanges(true);
  };

  const updateOperatingHours = (day: string, hours: string) => {
    setProfile(prev => {
      if (!prev) return prev;
      return {
        ...prev,
        yaml_profile: {
          ...prev.yaml_profile,
          operating_hours: {
            ...prev.yaml_profile.operating_hours,
            [day]: hours
          }
        }
      };
    });
    setHasChanges(true);
  };

  const weekdays = [
    'الأحد', 'الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت'
  ];

  // Loading state
  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">Business Profile</h1>
            <p className="text-slate-500 mt-1">Loading profile...</p>
          </div>
        </div>
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          <span className="ml-3 text-slate-600">Loading business profile...</span>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">Business Profile</h1>
            <p className="text-slate-500 mt-1">Configure your business information and AI agent personality</p>
          </div>
        </div>
        <Card>
          <CardContent className="p-6">
            <div className="text-center">
              <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-slate-900 mb-2">Failed to Load Profile</h3>
              <p className="text-slate-500 mb-4">{error}</p>
              <Button onClick={() => window.location.reload()}>
                Try Again
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Null check
  if (!profile) {
    return null;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Business Profile</h1>
          <p className="text-slate-500 mt-1">
            Configure your business information and AI agent personality
          </p>
        </div>
        <div className="flex items-center gap-3">
          {hasChanges && (
            <Badge variant="secondary" className="bg-orange-50 text-orange-700">
              <AlertCircle className="w-3 h-3 mr-1" />
              Unsaved Changes
            </Badge>
          )}
          <Button variant="outline" onClick={handleReset} disabled={!hasChanges}>
            <RotateCcw className="w-4 h-4 mr-2" />
            Reset
          </Button>
          <Button onClick={handleSave} disabled={!hasChanges}>
            <Save className="w-4 h-4 mr-2" />
            Save Profile
          </Button>
        </div>
      </div>

      <Tabs defaultValue="basic" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="basic" className="flex items-center gap-2">
            <User className="w-4 h-4" />
            Basic Info
          </TabsTrigger>
          <TabsTrigger value="hours" className="flex items-center gap-2">
            <Clock className="w-4 h-4" />
            Operating Hours
          </TabsTrigger>
          <TabsTrigger value="policies" className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4" />
            Policies
          </TabsTrigger>
          <TabsTrigger value="ai" className="flex items-center gap-2">
            <Bot className="w-4 h-4" />
            AI Personality
          </TabsTrigger>
        </TabsList>

        {/* Basic Information */}
        <TabsContent value="basic" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="w-5 h-5" />
                Business Information
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="business_name">Business Name</Label>
                  <Input
                    id="business_name"
                    value={profile.yaml_profile.business_name}
                    onChange={(e) => updateBasicInfo('business_name', e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={profile.yaml_profile.contact_info.email}
                    onChange={(e) => updateProfile('contact_info', 'email', e.target.value)}
                    placeholder="business@example.com"
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="description">Business Description</Label>
                <Textarea
                  id="description"
                  value={profile.yaml_profile.description}
                  onChange={(e) => updateBasicInfo('description', e.target.value)}
                  placeholder="Describe your business..."
                  rows={4}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="phone">Phone Number</Label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                    <Input
                      id="phone"
                      value={profile.yaml_profile.contact_info.phone}
                      onChange={(e) => updateProfile('contact_info', 'phone', e.target.value)}
                      className="pl-10"
                      placeholder="+962791234567"
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="address">Address</Label>
                  <div className="relative">
                    <MapPin className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                    <Input
                      id="address"
                      value={profile.yaml_profile.contact_info.address}
                      onChange={(e) => updateProfile('contact_info', 'address', e.target.value)}
                      className="pl-10"
                      placeholder="Business address"
                    />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Operating Hours */}
        <TabsContent value="hours" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="w-5 h-5" />
                Operating Hours
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {weekdays.map((day) => (
                  <div key={day} className="flex items-center gap-4">
                    <div className="w-20 text-sm font-medium text-slate-700">
                      {day}
                    </div>
                    <Input
                      value={profile.yaml_profile.operating_hours[day] || ''}
                      onChange={(e) => updateOperatingHours(day, e.target.value)}
                      placeholder="10:00 - 22:00"
                      className="flex-1"
                    />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Policies */}
        <TabsContent value="policies" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5" />
                Business Policies
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="shipping">Shipping Policy</Label>
                <Textarea
                  id="shipping"
                  value={profile.yaml_profile.policies.shipping}
                  onChange={(e) => updateProfile('policies', 'shipping', e.target.value)}
                  placeholder="Describe your shipping policy..."
                  rows={3}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="returns">Return Policy</Label>
                <Textarea
                  id="returns"
                  value={profile.yaml_profile.policies.returns}
                  onChange={(e) => updateProfile('policies', 'returns', e.target.value)}
                  placeholder="Describe your return policy..."
                  rows={3}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="payment">Payment Policy</Label>
                <Textarea
                  id="payment"
                  value={profile.yaml_profile.policies.payment}
                  onChange={(e) => updateProfile('policies', 'payment', e.target.value)}
                  placeholder="Describe your payment policy..."
                  rows={3}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* AI Personality */}
        <TabsContent value="ai" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bot className="w-5 h-5" />
                AI Agent Personality
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="tone">Tone</Label>
                  <Select
                    value={profile.yaml_profile.ai_personality.tone}
                    onValueChange={(value) => updateProfile('ai_personality', 'tone', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="ودود ومهني">ودود ومهني</SelectItem>
                      <SelectItem value="رسمي">رسمي</SelectItem>
                      <SelectItem value="كاجوال">كاجوال</SelectItem>
                      <SelectItem value="حماسي">حماسي</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="language">Language</Label>
                  <Select
                    value={profile.yaml_profile.ai_personality.language}
                    onValueChange={(value) => updateProfile('ai_personality', 'language', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="العربية الأردنية">العربية الأردنية</SelectItem>
                      <SelectItem value="العربية الفصحى">العربية الفصحى</SelectItem>
                      <SelectItem value="English">English</SelectItem>
                      <SelectItem value="Mixed">Mixed (Arabic/English)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="response_style">Response Style</Label>
                <Textarea
                  id="response_style"
                  value={profile.yaml_profile.ai_personality.response_style || ''}
                  onChange={(e) => updateProfile('ai_personality', 'response_style', e.target.value)}
                  placeholder="Describe how the AI should respond to customers..."
                  rows={3}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="greeting">Greeting Message</Label>
                <Input
                  id="greeting"
                  value={profile.yaml_profile.ai_personality.greeting}
                  onChange={(e) => updateProfile('ai_personality', 'greeting', e.target.value)}
                  placeholder="أهلاً وسهلاً! كيف يمكنني مساعدتك؟"
                />
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="font-medium text-blue-900 mb-2">AI Behavior Guidelines</h4>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>• Always greet customers in a friendly manner</li>
                  <li>• Use Jordanian Arabic dialect when appropriate</li>
                  <li>• Be helpful and provide detailed product information</li>
                  <li>• Ask clarifying questions when orders are unclear</li>
                  <li>• Escalate complex issues to human agents</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
