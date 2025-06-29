import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { MessageSquare, Search, Filter, Eye } from 'lucide-react';

export function Conversations() {
  const conversations = [
    {
      id: 1,
      customer: 'أحمد محمد',
      lastMessage: 'أريد معرفة المزيد عن الفستان الأزرق',
      time: '5 دقائق',
      status: 'active',
      unread: 2
    },
    {
      id: 2,
      customer: 'سارة أحمد',
      lastMessage: 'متى سيصل الطلب؟',
      time: '15 دقيقة',
      status: 'waiting',
      unread: 1
    },
    {
      id: 3,
      customer: 'محمد علي',
      lastMessage: 'شكراً لك، الطلب وصل بسلامة',
      time: '1 ساعة',
      status: 'resolved',
      unread: 0
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'waiting': return 'bg-yellow-100 text-yellow-800';
      case 'resolved': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'active': return 'نشط';
      case 'waiting': return 'في الانتظار';
      case 'resolved': return 'محلول';
      default: return status;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Conversations</h1>
          <p className="text-slate-500 mt-1">
            Manage customer conversations and AI responses
          </p>
        </div>
        <Badge variant="outline" className="bg-blue-50 text-blue-700">
          {conversations.filter(c => c.unread > 0).length} رسالة غير مقروءة
        </Badge>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input 
            placeholder="ابحث في المحادثات..." 
            className="pl-10"
          />
        </div>
        <Button variant="outline">
          <Filter className="h-4 w-4 mr-2" />
          تصفية
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5" />
              قائمة المحادثات
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <div className="divide-y">
              {conversations.map((conversation) => (
                <div 
                  key={conversation.id}
                  className="p-4 hover:bg-slate-50 cursor-pointer"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-medium text-slate-900">
                          {conversation.customer}
                        </h3>
                        {conversation.unread > 0 && (
                          <Badge variant="destructive" className="text-xs">
                            {conversation.unread}
                          </Badge>
                        )}
                      </div>
                      <p className="text-sm text-slate-600 mb-2 line-clamp-2">
                        {conversation.lastMessage}
                      </p>
                      <div className="flex items-center justify-between">
                        <Badge 
                          variant="outline"
                          className={getStatusColor(conversation.status)}
                        >
                          {getStatusLabel(conversation.status)}
                        </Badge>
                        <span className="text-xs text-slate-500">
                          {conversation.time}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>تفاصيل المحادثة</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center py-12">
              <MessageSquare className="mx-auto h-12 w-12 text-slate-400 mb-4" />
              <h3 className="text-lg font-medium text-slate-900 mb-2">
                اختر محادثة لعرض التفاصيل
              </h3>
              <p className="text-slate-500">
                انقر على أي محادثة من القائمة لعرض الرسائل والرد عليها
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>إحصائيات المحادثات</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">24</div>
              <div className="text-sm text-slate-500">إجمالي المحادثات</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">18</div>
              <div className="text-sm text-slate-500">ردود الذكي الاصطناعي</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-600">3</div>
              <div className="text-sm text-slate-500">في الانتظار</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-slate-600">95%</div>
              <div className="text-sm text-slate-500">معدل الرضا</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
