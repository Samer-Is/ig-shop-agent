import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { BookOpen, Search, Plus, Edit, Trash2 } from 'lucide-react';

export function KnowledgeBase() {
  const knowledgeItems = [
    {
      id: 1,
      title: 'معلومات الشحن والتوصيل',
      category: 'Shipping',
      content: 'يتم التوصيل خلال 2-3 أيام عمل داخل عمان، و3-5 أيام للمحافظات',
      lastUpdated: '2024-01-15'
    },
    {
      id: 2,
      title: 'سياسة الإرجاع والاستبدال',
      category: 'Returns',
      content: 'يمكن إرجاع أو استبدال المنتجات خلال 14 يوم من تاريخ الاستلام',
      lastUpdated: '2024-01-10'
    },
    {
      id: 3,
      title: 'طرق الدفع المتاحة',
      category: 'Payment',
      content: 'نقبل الدفع نقداً عند التسليم، أو عبر البطاقات الائتمانية',
      lastUpdated: '2024-01-08'
    }
  ];

  const getCategoryColor = (category: string) => {
    const colors = {
      'Shipping': 'bg-blue-100 text-blue-800',
      'Returns': 'bg-green-100 text-green-800',
      'Payment': 'bg-purple-100 text-purple-800',
      'Products': 'bg-orange-100 text-orange-800'
    };
    return colors[category as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Knowledge Base</h1>
          <p className="text-slate-500 mt-1">
            Manage AI responses and business information
          </p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Add Knowledge
        </Button>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input 
            placeholder="ابحث في قاعدة المعرفة..." 
            className="pl-10"
          />
        </div>
        <Button variant="outline">
          تصفية حسب الفئة
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BookOpen className="h-5 w-5" />
              قاعدة المعرفة
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {knowledgeItems.map((item) => (
              <div 
                key={item.id}
                className="border border-slate-200 rounded-lg p-4 hover:bg-slate-50 transition-colors"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="font-medium text-slate-900">{item.title}</h3>
                      <Badge 
                        variant="outline"
                        className={getCategoryColor(item.category)}
                      >
                        {item.category}
                      </Badge>
                    </div>
                    <p className="text-sm text-slate-600 mb-2">
                      {item.content}
                    </p>
                    <p className="text-xs text-slate-500">
                      آخر تحديث: {item.lastUpdated}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button size="sm" variant="outline">
                      <Edit className="h-3 w-3" />
                    </Button>
                    <Button size="sm" variant="outline">
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>إحصائيات الاستخدام</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">127</div>
              <div className="text-sm text-slate-500">إجمالي المقالات</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">89%</div>
              <div className="text-sm text-slate-500">معدل الإجابة الصحيحة</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">45</div>
              <div className="text-sm text-slate-500">استفسارات اليوم</div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>الأسئلة الشائعة</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="border border-slate-200 rounded p-3">
              <h4 className="font-medium mb-1">كم يستغرق وقت التوصيل؟</h4>
              <p className="text-sm text-slate-600">2-3 أيام عمل داخل عمان</p>
            </div>
            <div className="border border-slate-200 rounded p-3">
              <h4 className="font-medium mb-1">هل يمكن الإرجاع؟</h4>
              <p className="text-sm text-slate-600">نعم، خلال 14 يوم من الاستلام</p>
            </div>
            <div className="border border-slate-200 rounded p-3">
              <h4 className="font-medium mb-1">ما هي طرق الدفع؟</h4>
              <p className="text-sm text-slate-600">نقداً عند التسليم أو بطاقة ائتمانية</p>
            </div>
            <div className="border border-slate-200 rounded p-3">
              <h4 className="font-medium mb-1">هل التوصيل مجاني؟</h4>
              <p className="text-sm text-slate-600">مجاني للطلبات أكثر من 50 دينار</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
