import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Package, Search, Plus, Edit, Trash2, Filter, AlertCircle, Loader2 } from 'lucide-react';
import { productionApi, CatalogItem } from '../services/productionApi';
import { Alert, AlertDescription } from '../components/ui/alert';

interface CatalogState {
  products: CatalogItem[];
  isLoading: boolean;
  error: string | null;
  searchTerm: string;
}

export function Catalog() {
  const [state, setState] = useState<CatalogState>({
    products: [],
    isLoading: true,
    error: null,
    searchTerm: ''
  });

  // Load catalog data from real API
  const loadCatalog = async () => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      const response = await productionApi.getCatalog();
      
      if (response.error) {
        setState(prev => ({ 
          ...prev, 
          isLoading: false, 
          error: `Failed to load catalog: ${response.error}` 
        }));
        return;
      }

      setState(prev => ({
        ...prev,
        products: response.data || [],
        isLoading: false,
        error: null
      }));
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        isLoading: false, 
        error: 'Network error loading catalog' 
      }));
    }
  };

  // Load data on component mount
  useEffect(() => {
    loadCatalog();
  }, []);

  // Filter products based on search term
  const filteredProducts = state.products.filter(product =>
    product.name.toLowerCase().includes(state.searchTerm.toLowerCase()) ||
    product.description?.toLowerCase().includes(state.searchTerm.toLowerCase()) ||
    product.category?.toLowerCase().includes(state.searchTerm.toLowerCase())
  );

  // Calculate stats from real data
  const totalProducts = state.products.length;
  const activeProducts = state.products.filter(p => p.is_active).length;
  const lowStockProducts = state.products.filter(p => p.stock_quantity < 5).length;
  const totalInventoryValue = state.products.reduce((sum, p) => sum + (p.price_jod * p.stock_quantity), 0);

  const getCategoryColor = (category: string) => {
    const colors = {
      'Dresses': 'bg-pink-100 text-pink-800',
      'Shoes': 'bg-blue-100 text-blue-800',
      'Tops': 'bg-green-100 text-green-800',
      'Bags': 'bg-purple-100 text-purple-800',
      'Electronics': 'bg-indigo-100 text-indigo-800',
      'Fashion': 'bg-rose-100 text-rose-800'
    };
    return colors[category as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  const getStockColor = (stock: number) => {
    if (stock === 0) return 'bg-red-100 text-red-800';
    if (stock < 5) return 'bg-yellow-100 text-yellow-800';
    return 'bg-green-100 text-green-800';
  };

  // Handle product deletion
  const handleDeleteProduct = async (productId: string) => {
    if (!confirm('Are you sure you want to delete this product?')) return;
    
    try {
      const response = await productionApi.deleteCatalogItem(Number(productId));
      if (response.error) {
        alert(`Failed to delete product: ${response.error}`);
        return;
      }
      
      // Reload catalog after deletion
      await loadCatalog();
      alert('Product deleted successfully');
    } catch (error) {
      alert('Network error deleting product');
    }
  };

  // Loading state
  if (state.isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-4" />
            <p className="text-slate-600">Loading catalog...</p>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (state.error) {
    return (
      <div className="space-y-6">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {state.error}
            <Button 
              variant="outline" 
              size="sm" 
              className="ml-4"
              onClick={loadCatalog}
            >
              Retry
            </Button>
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Product Catalog</h1>
          <p className="text-slate-500 mt-1">
            Manage your product inventory and pricing ({totalProducts} products)
          </p>
        </div>
        <Button onClick={() => window.location.href = '/add-product'}>
          <Plus className="h-4 w-4 mr-2" />
          Add Product
        </Button>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input 
            placeholder="Search products..." 
            className="pl-10"
            value={state.searchTerm}
            onChange={(e) => setState(prev => ({ ...prev, searchTerm: e.target.value }))}
          />
        </div>
        <Button variant="outline" onClick={loadCatalog}>
          <Filter className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Real-time Statistics from API Data */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-blue-600">{totalProducts}</div>
            <div className="text-sm text-slate-500">Total Products</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-green-600">{activeProducts}</div>
            <div className="text-sm text-slate-500">Active Products</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-yellow-600">{lowStockProducts}</div>
            <div className="text-sm text-slate-500">Low Stock</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-slate-600">{totalInventoryValue.toFixed(2)} JOD</div>
            <div className="text-sm text-slate-500">Inventory Value</div>
          </CardContent>
        </Card>
      </div>

      {/* Empty state when no products */}
      {filteredProducts.length === 0 && !state.isLoading ? (
        <Card className="p-12 text-center">
          <Package className="h-16 w-16 text-slate-300 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-slate-600 mb-2">
            {state.searchTerm ? 'No products found' : 'No products yet'}
          </h3>
          <p className="text-slate-500 mb-6">
            {state.searchTerm 
              ? `No products match "${state.searchTerm}". Try a different search term.`
              : 'Add your first product to get started with your catalog.'
            }
          </p>
          {!state.searchTerm && (
            <Button onClick={() => window.location.href = '/add-product'}>
              <Plus className="h-4 w-4 mr-2" />
              Add Your First Product
            </Button>
          )}
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredProducts.map((product) => (
            <Card key={product.id} className="overflow-hidden hover:shadow-lg transition-shadow">
              <div className="aspect-square overflow-hidden bg-slate-100">
                <img 
                  src={product.image_url || 'https://via.placeholder.com/300x300?text=No+Image'} 
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
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={() => window.location.href = `/edit-product/${product.id}`}
                    >
                      <Edit className="h-3 w-3" />
                    </Button>
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={() => handleDeleteProduct(product.id)}
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="pt-0">
                <p className="text-sm text-slate-600 mb-3 line-clamp-2">
                  {product.description || 'No description available'}
                </p>
                
                <div className="flex items-center gap-2 mb-3">
                  <Badge 
                    variant="outline"
                    className={getCategoryColor(product.category || 'Other')}
                  >
                    {product.category || 'Uncategorized'}
                  </Badge>
                  <Badge 
                    variant="outline"
                    className={getStockColor(product.stock_quantity)}
                  >
                    {product.stock_quantity} in stock
                  </Badge>
                  {!product.is_active && (
                    <Badge variant="outline" className="bg-red-100 text-red-800">
                      Inactive
                    </Badge>
                  )}
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="text-xl font-bold text-slate-900">
                    {product.price_jod} JOD
                  </div>
                  <Button 
                    size="sm"
                    onClick={() => window.location.href = `/edit-product/${product.id}`}
                  >
                    Edit
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Real Statistics Card - Only show if we have products */}
      {state.products.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Package className="h-5 w-5" />
              Catalog Statistics
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <h4 className="font-medium mb-2">Stock Status</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>In Stock</span>
                    <span className="text-green-600">{state.products.filter(p => p.stock_quantity > 0).length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Out of Stock</span>
                    <span className="text-red-600">{state.products.filter(p => p.stock_quantity === 0).length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Low Stock</span>
                    <span className="text-yellow-600">{lowStockProducts}</span>
                  </div>
                </div>
              </div>
              <div>
                <h4 className="font-medium mb-2">Product Status</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Active</span>
                    <span className="text-green-600">{activeProducts}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Inactive</span>
                    <span className="text-gray-600">{totalProducts - activeProducts}</span>
                  </div>
                </div>
              </div>
              <div>
                <h4 className="font-medium mb-2">Price Range</h4>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Highest</span>
                    <span className="text-blue-600">{Math.max(...state.products.map(p => p.price_jod)).toFixed(2)} JOD</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Lowest</span>
                    <span className="text-blue-600">{Math.min(...state.products.map(p => p.price_jod)).toFixed(2)} JOD</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Average</span>
                    <span className="text-blue-600">{(state.products.reduce((sum, p) => sum + p.price_jod, 0) / state.products.length).toFixed(2)} JOD</span>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
