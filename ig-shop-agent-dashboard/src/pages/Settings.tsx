import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Switch } from '../components/ui/switch';
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
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '../components/ui/alert-dialog';
import { 
  Settings as SettingsIcon, 
  Instagram, 
  Key, 
  Bell,
  Shield,
  Trash2,
  Save,
  Copy,
  Eye,
  EyeOff,
  Webhook,
  Zap
} from 'lucide-react';

export function Settings() {
  const [showApiKey, setShowApiKey] = useState(false);
  const [settings, setSettings] = useState({
    notifications: {
      newOrders: true,
      aiResponses: false,
      lowStock: true,
      dailyReports: true
    },
    ai: {
      autoResponse: true,
      handoffThreshold: 3,
      maxTokensPerResponse: 150,
      temperature: 0.7
    },
    instagram: {
      accessToken: 'IG_••••••••••••••••••••••••••••••••••••••••••••••',
      webhookUrl: 'https://api.ig-shop-agent.com/webhooks/instagram',
      verifyToken: 'verify_••••••••••••••••••••••••••••••••••••••••••'
    }
  });

  const handleNotificationChange = (key: string, value: boolean) => {
    setSettings(prev => ({
      ...prev,
      notifications: {
        ...prev.notifications,
        [key]: value
      }
    }));
  };

  const handleAIChange = (key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      ai: {
        ...prev.ai,
        [key]: value
      }
    }));
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    // You would show a toast notification here
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Settings</h1>
          <p className="text-slate-500 mt-1">
            Configure your account, integrations, and system preferences
          </p>
        </div>
        <Button>
          <Save className="w-4 h-4 mr-2" />
          Save All Changes
        </Button>
      </div>

      <Tabs defaultValue="notifications" className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="notifications" className="flex items-center gap-2">
            <Bell className="w-4 h-4" />
            Notifications
          </TabsTrigger>
          <TabsTrigger value="ai" className="flex items-center gap-2">
            <Zap className="w-4 h-4" />
            AI Settings
          </TabsTrigger>
          <TabsTrigger value="instagram" className="flex items-center gap-2">
            <Instagram className="w-4 h-4" />
            Instagram
          </TabsTrigger>
          <TabsTrigger value="security" className="flex items-center gap-2">
            <Shield className="w-4 h-4" />
            Security
          </TabsTrigger>
          <TabsTrigger value="danger" className="flex items-center gap-2">
            <Trash2 className="w-4 h-4" />
            Danger Zone
          </TabsTrigger>
        </TabsList>

        {/* Notifications */}
        <TabsContent value="notifications" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="w-5 h-5" />
                Notification Preferences
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="new-orders">New Orders</Label>
                    <p className="text-sm text-slate-500">Get notified when new orders are placed</p>
                  </div>
                  <Switch
                    id="new-orders"
                    checked={settings.notifications.newOrders}
                    onCheckedChange={(value) => handleNotificationChange('newOrders', value)}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="ai-responses">AI Responses</Label>
                    <p className="text-sm text-slate-500">Get notified when AI generates responses</p>
                  </div>
                  <Switch
                    id="ai-responses"
                    checked={settings.notifications.aiResponses}
                    onCheckedChange={(value) => handleNotificationChange('aiResponses', value)}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="low-stock">Low Stock Alerts</Label>
                    <p className="text-sm text-slate-500">Get alerted when products are running low</p>
                  </div>
                  <Switch
                    id="low-stock"
                    checked={settings.notifications.lowStock}
                    onCheckedChange={(value) => handleNotificationChange('lowStock', value)}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="daily-reports">Daily Reports</Label>
                    <p className="text-sm text-slate-500">Receive daily performance summaries</p>
                  </div>
                  <Switch
                    id="daily-reports"
                    checked={settings.notifications.dailyReports}
                    onCheckedChange={(value) => handleNotificationChange('dailyReports', value)}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* AI Settings */}
        <TabsContent value="ai" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="w-5 h-5" />
                AI Agent Configuration
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <Label htmlFor="auto-response">Auto Response</Label>
                  <p className="text-sm text-slate-500">Enable automatic AI responses to customer messages</p>
                </div>
                <Switch
                  id="auto-response"
                  checked={settings.ai.autoResponse}
                  onCheckedChange={(value) => handleAIChange('autoResponse', value)}
                />
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="handoff-threshold">Handoff Threshold</Label>
                  <Select
                    value={settings.ai.handoffThreshold.toString()}
                    onValueChange={(value) => handleAIChange('handoffThreshold', parseInt(value))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1">1 failed attempt</SelectItem>
                      <SelectItem value="2">2 failed attempts</SelectItem>
                      <SelectItem value="3">3 failed attempts</SelectItem>
                      <SelectItem value="5">5 failed attempts</SelectItem>
                    </SelectContent>
                  </Select>
                  <p className="text-xs text-slate-500">Number of AI failures before human handoff</p>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="max-tokens">Max Tokens per Response</Label>
                  <Input
                    id="max-tokens"
                    type="number"
                    value={settings.ai.maxTokensPerResponse}
                    onChange={(e) => handleAIChange('maxTokensPerResponse', parseInt(e.target.value))}
                    min="50"
                    max="500"
                  />
                  <p className="text-xs text-slate-500">Maximum length of AI responses</p>
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="temperature">AI Creativity (Temperature)</Label>
                <Input
                  id="temperature"
                  type="number"
                  value={settings.ai.temperature}
                  onChange={(e) => handleAIChange('temperature', parseFloat(e.target.value))}
                  min="0"
                  max="1"
                  step="0.1"
                />
                <p className="text-xs text-slate-500">0 = more focused, 1 = more creative</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Instagram Integration */}
        <TabsContent value="instagram" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Instagram className="w-5 h-5" />
                Instagram Integration
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center gap-2 p-4 bg-green-50 border border-green-200 rounded-lg">
                <Badge variant="default" className="bg-green-600">Connected</Badge>
                <span className="text-sm text-green-800">@jordanfashion_store</span>
              </div>
              
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="access-token">Access Token</Label>
                  <div className="flex gap-2">
                    <Input
                      id="access-token"
                      type={showApiKey ? 'text' : 'password'}
                      value={settings.instagram.accessToken}
                      readOnly
                      className="font-mono text-sm"
                    />
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setShowApiKey(!showApiKey)}
                    >
                      {showApiKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => copyToClipboard(settings.instagram.accessToken)}
                    >
                      <Copy className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="webhook-url">Webhook URL</Label>
                  <div className="flex gap-2">
                    <Input
                      id="webhook-url"
                      value={settings.instagram.webhookUrl}
                      readOnly
                      className="font-mono text-sm"
                    />
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => copyToClipboard(settings.instagram.webhookUrl)}
                    >
                      <Copy className="w-4 h-4" />
                    </Button>
                  </div>
                  <p className="text-xs text-slate-500">Use this URL in your Meta App webhook configuration</p>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="verify-token">Verify Token</Label>
                  <div className="flex gap-2">
                    <Input
                      id="verify-token"
                      type="password"
                      value={settings.instagram.verifyToken}
                      readOnly
                      className="font-mono text-sm"
                    />
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => copyToClipboard(settings.instagram.verifyToken)}
                    >
                      <Copy className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </div>
              
              <div className="flex gap-2">
                <Button variant="outline">
                  <Webhook className="w-4 h-4 mr-2" />
                  Test Webhook
                </Button>
                <Button variant="outline">Reconnect Instagram</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Security */}
        <TabsContent value="security" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="w-5 h-5" />
                Security Settings
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="current-password">Current Password</Label>
                  <Input
                    id="current-password"
                    type="password"
                    placeholder="Enter current password"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="new-password">New Password</Label>
                  <Input
                    id="new-password"
                    type="password"
                    placeholder="Enter new password"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="confirm-password">Confirm New Password</Label>
                  <Input
                    id="confirm-password"
                    type="password"
                    placeholder="Confirm new password"
                  />
                </div>
                
                <Button>Update Password</Button>
              </div>
              
              <div className="border-t pt-6">
                <h4 className="font-medium text-slate-900 mb-4">Two-Factor Authentication</h4>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-slate-700">2FA Status</p>
                    <p className="text-sm text-slate-500">Add an extra layer of security to your account</p>
                  </div>
                  <Badge variant="secondary">Disabled</Badge>
                </div>
                <Button variant="outline" className="mt-4">
                  <Key className="w-4 h-4 mr-2" />
                  Enable 2FA
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Danger Zone */}
        <TabsContent value="danger" className="space-y-6">
          <Card className="border-red-200">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-red-700">
                <Trash2 className="w-5 h-5" />
                Danger Zone
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="p-4 border border-red-200 rounded-lg bg-red-50">
                  <h4 className="font-medium text-red-900 mb-2">Delete Account</h4>
                  <p className="text-sm text-red-700 mb-4">
                    Permanently delete your account and all associated data. This action cannot be undone.
                  </p>
                  <AlertDialog>
                    <AlertDialogTrigger asChild>
                      <Button variant="destructive">Delete Account</Button>
                    </AlertDialogTrigger>
                    <AlertDialogContent>
                      <AlertDialogHeader>
                        <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                        <AlertDialogDescription>
                          This action cannot be undone. This will permanently delete your account
                          and remove all your data from our servers.
                        </AlertDialogDescription>
                      </AlertDialogHeader>
                      <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction className="bg-red-600 hover:bg-red-700">
                          Yes, delete account
                        </AlertDialogAction>
                      </AlertDialogFooter>
                    </AlertDialogContent>
                  </AlertDialog>
                </div>
                
                <div className="p-4 border border-orange-200 rounded-lg bg-orange-50">
                  <h4 className="font-medium text-orange-900 mb-2">Reset All Data</h4>
                  <p className="text-sm text-orange-700 mb-4">
                    Clear all conversations, orders, and analytics data while keeping your account.
                  </p>
                  <Button variant="outline" className="border-orange-300 text-orange-700">
                    Reset Data
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
