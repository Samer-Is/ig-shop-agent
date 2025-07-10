import { Link, useLocation } from 'react-router-dom';
import { cn } from '../../lib/utils';
import { 
  LayoutDashboard, 
  Package, 
  ShoppingCart, 
  MessageCircle, 
  BookOpen, 
  User, 
  BarChart3, 
  Settings,
  Instagram,
  Bot
} from 'lucide-react';

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Catalog', href: '/catalog', icon: Package },
  { name: 'Orders', href: '/orders', icon: ShoppingCart },
  { name: 'Conversations', href: '/conversations', icon: MessageCircle },
  { name: 'Knowledge Base', href: '/knowledge-base', icon: BookOpen },
  { name: 'Business Profile', href: '/business-profile', icon: User },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export function Sidebar() {
  const location = useLocation();

  return (
    <div className="w-64 bg-white border-r border-slate-200 flex flex-col">
      {/* Logo */}
      <div className="flex items-center gap-3 px-6 py-6 border-b border-slate-200">
        <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-br from-purple-600 to-blue-600 rounded-lg">
          <Bot className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-slate-900">IG Shop Agent</h1>
          <p className="text-sm text-slate-500">Instagram DM Automation</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-2">
        {navigation.map((item) => {
          const isActive = location.pathname === item.href;
          return (
            <Link
              key={item.name}
              to={item.href}
              className={cn(
                'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-blue-50 text-blue-700 border border-blue-200'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              )}
            >
              <item.icon className="w-5 h-5" />
              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* Bottom section */}
      <div className="px-4 py-4 border-t border-slate-200">
        <div className="flex items-center gap-3 px-3 py-2 bg-slate-50 rounded-lg">
          <div className="flex items-center justify-center w-8 h-8 bg-gradient-to-br from-pink-500 to-orange-500 rounded-lg">
            <Instagram className="w-4 h-4 text-white" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-slate-900 truncate">
              @jordanfashion_store
            </p>
            <p className="text-xs text-slate-500">Professional Plan</p>
          </div>
        </div>
      </div>
    </div>
  );
}
