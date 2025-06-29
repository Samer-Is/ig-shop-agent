import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Package, Search, Filter, Eye, Download } from 'lucide-react';

export function Orders() {
  const orders = [
    {
      id: 'ORD-001',
      customer: 'أحمد محمد',
      items: [
        { name: 'فستان أزرق', quantity: 1, price: 45 }
      ],
      total: 45,
      status: 'pending',
      date: '2024-01-15',
      phone: '+962791234567'
    },
    {
      id: 'ORD-002',
      customer: 'سارة أحمد',
      items: [
        { name: 'حذاء كعب عالي', quantity: 2, price: 35 }
      ],
      total: 70,
      status: 'confirmed',
      date: '2024-01-14',
      phone: '+962791234568'
    },
    {
      id: 'ORD-003',
      customer: 'محمد علي',
      items: [
        { name: 'بلوزة بيضاء', quantity: 1, price: 25 },
        { name: 'جينز أسود', quantity: 1, price: 40 }
      ],
      total: 65,
      status: 'shipped',
      date: '2024-01-13',
      phone: '+962791234569'
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'confirmed': return 'bg-blue-100 text-blue-800';
      case 'shipped': return 'bg-green-100 text-green-800';
      case 'delivered': return 'bg-gray-100 text-gray-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'pending': return 'في الانتظار';
      case 'confirmed': return 'مؤكد';
      case 'shipped': return 'تم الشحن';
      case 'delivered': return 'تم التسليم';
      case 'cancelled': return 'ملغي';
      default: return status;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Orders</h1>
          <p className="text-slate-500 mt-1">
            Manage customer orders and track shipments
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            تصدير
          </Button>
          <Badge variant="outline" className="bg-green-50 text-green-700">
            {orders.length} طلب جديد
          </Badge>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input 
            placeholder="ابحث في الطلبات..." 
            className="pl-10"
          />
        </div>
        <Button variant="outline">
          <Filter className="h-4 w-4 mr-2" />
          تصفية
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-blue-600">12</div>
            <div className="text-sm text-slate-500">طلبات جديدة</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-yellow-600">8</div>
            <div className="text-sm text-slate-500">قيد المعالجة</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-green-600">45</div>
            <div className="text-sm text-slate-500">تم التسليم</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-slate-600">1,234 JOD</div>
            <div className="text-sm text-slate-500">إجمالي المبيعات</div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Package className="h-5 w-5" />
            قائمة الطلبات
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {orders.map((order) => (
              <div 
                key={order.id}
                className="border border-slate-200 rounded-lg p-4 hover:bg-slate-50 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-3">
                      <h3 className="font-medium text-slate-900">{order.id}</h3>
                      <Badge 
                        variant="outline"
                        className={getStatusColor(order.status)}
                      >
                        {getStatusLabel(order.status)}
                      </Badge>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
                      <div>
                        <p className="text-sm text-slate-500">العميل</p>
                        <p className="font-medium">{order.customer}</p>
                        <p className="text-sm text-slate-600">{order.phone}</p>
                      </div>
                      
                      <div>
                        <p className="text-sm text-slate-500">المنتجات</p>
                        {order.items.map((item, index) => (
                          <p key={index} className="text-sm">
                            {item.name} × {item.quantity}
                          </p>
                        ))}
                      </div>
                      
                      <div>
                        <p className="text-sm text-slate-500">الإجمالي</p>
                        <p className="font-bold text-lg">{order.total} JOD</p>
                        <p className="text-sm text-slate-600">{order.date}</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <Button size="sm" variant="outline">
                      <Eye className="h-3 w-3 mr-1" />
                      عرض
                    </Button>
                    <Button size="sm">
                      تحديث الحالة
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
