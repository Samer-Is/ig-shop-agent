import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Package, Search, Plus, Edit, Trash2, Filter } from 'lucide-react';

export function Catalog() {
  const products = [
    {
      id: 1,
      name: 'فستان أزرق أنيق',
      description: 'فستان رائع للمناسبات الخاصة',
      price: 45,
      category: 'Dresses',
      stock: 12,
      image: '/images/dress-1.jpg',
      status: 'active'
    },
    {
      id: 2,
      name: 'حذاء كعب عالي',
      description: 'حذاء مريح وعملي',
      price: 35,
      category: 'Shoes',
      stock: 8,
      image: '/images/heels-1.jpeg',
      status: 'active'
    },
    {
      id: 3,
      name: 'بلوزة بيضاء كلاسيكية',
      description: 'بلوزة عملية لجميع المناسبات',
      price: 25,
      category: 'Tops',
      stock: 15,
      image: '/images/top-1.jpeg',
      status: 'active'
    },
    {
      id: 4,
      name: 'حقيبة يد جلدية',
      description: 'حقيبة عملية وأنيقة',
      price: 60,
      category: 'Bags',
      stock: 5,
      image: '/images/bag-1.jpg',
      status: 'active'
    }
  ];

  const getCategoryColor = (category: string) => {
    const colors = {
      'Dresses': 'bg-pink-100 text-pink-800',
      'Shoes': 'bg-blue-100 text-blue-800',
      'Tops': 'bg-green-100 text-green-800',
      'Bags': 'bg-purple-100 text-purple-800'
    };
    return colors[category as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  const getStockColor = (stock: number) => {
    if (stock === 0) return 'bg-red-100 text-red-800';
    if (stock < 5) return 'bg-yellow-100 text-yellow-800';
    return 'bg-green-100 text-green-800';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Product Catalog</h1>
          <p className="text-slate-500 mt-1">
            Manage your product inventory and pricing
          </p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Add Product
        </Button>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input 
            placeholder="ابحث في المنتجات..." 
            className="pl-10"
          />
        </div>
        <Button variant="outline">
          <Filter className="h-4 w-4 mr-2" />
          تصفية حسب الفئة
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-blue-600">{products.length}</div>
            <div className="text-sm text-slate-500">إجمالي المنتجات</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-green-600">{products.filter(p => p.status === 'active').length}</div>
            <div className="text-sm text-slate-500">منتجات نشطة</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-yellow-600">{products.filter(p => p.stock < 5).length}</div>
            <div className="text-sm text-slate-500">مخزون منخفض</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-slate-600">{products.reduce((sum, p) => sum + (p.price * p.stock), 0)} JOD</div>
            <div className="text-sm text-slate-500">قيمة المخزون</div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {products.map((product) => (
          <Card key={product.id} className="overflow-hidden hover:shadow-lg transition-shadow">
            <div className="aspect-square overflow-hidden bg-slate-100">
              <img 
                src={product.image} 
                alt={product.name}
                className="w-full h-full object-cover"
                onError={(e) => {
                  e.currentTarget.src = 'https://via.placeholder.com/300x300?text=No+Image';
                }}
              />
            </div>
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <CardTitle className="text-lg line-clamp-2">{product.name}</CardTitle>
                <div className="flex gap-1">
                  <Button size="sm" variant="outline">
                    <Edit className="h-3 w-3" />
                  </Button>
                  <Button size="sm" variant="outline">
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              <p className="text-sm text-slate-600 mb-3 line-clamp-2">
                {product.description}
              </p>
              
              <div className="flex items-center gap-2 mb-3">
                <Badge 
                  variant="outline"
                  className={getCategoryColor(product.category)}
                >
                  {product.category}
                </Badge>
                <Badge 
                  variant="outline"
                  className={getStockColor(product.stock)}
                >
                  {product.stock} في المخزون
                </Badge>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="text-xl font-bold text-slate-900">
                  {product.price} JOD
                </div>
                <Button size="sm">
                  تعديل
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Package className="h-5 w-5" />
            إحصائيات سريعة
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <h4 className="font-medium mb-2">الفئات الأكثر مبيعاً</h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span>Dresses</span>
                  <span className="text-blue-600">65%</span>
                </div>
                <div className="flex justify-between">
                  <span>Shoes</span>
                  <span className="text-green-600">20%</span>
                </div>
                <div className="flex justify-between">
                  <span>Bags</span>
                  <span className="text-purple-600">15%</span>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="font-medium mb-2">المنتجات الأكثر طلباً</h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span>فستان أزرق أنيق</span>
                  <span className="text-blue-600">24 طلب</span>
                </div>
                <div className="flex justify-between">
                  <span>حذاء كعب عالي</span>
                  <span className="text-green-600">18 طلب</span>
                </div>
                <div className="flex justify-between">
                  <span>حقيبة يد جلدية</span>
                  <span className="text-purple-600">12 طلب</span>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="font-medium mb-2">تنبيهات المخزون</h4>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                  <span className="text-sm">منتجات نفدت من المخزون: 0</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                  <span className="text-sm">مخزون منخفض: {products.filter(p => p.stock < 5).length}</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-sm">مخزون جيد: {products.filter(p => p.stock >= 5).length}</span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
