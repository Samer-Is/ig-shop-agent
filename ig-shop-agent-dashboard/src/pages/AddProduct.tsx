import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { ArrowLeft, Package, Save, Loader2, AlertCircle, CheckCircle } from 'lucide-react';
import { productionApi } from '../services/productionApi';
import { Alert, AlertDescription } from '../components/ui/alert';

interface ProductForm {
  name: string;
  description: string;
  price_jod: string;
  category: string;
  stock_quantity: string;
  image_url: string;
}

interface AddProductState {
  form: ProductForm;
  isSubmitting: boolean;
  error: string | null;
  success: string | null;
}

export function AddProduct() {
  const [state, setState] = useState<AddProductState>({
    form: {
      name: '',
      description: '',
      price_jod: '',
      category: '',
      stock_quantity: '',
      image_url: ''
    },
    isSubmitting: false,
    error: null,
    success: null
  });

  const categories = [
    'Fashion',
    'Electronics',
    'Dresses',
    'Shoes',
    'Tops',
    'Bags',
    'Accessories',
    'Beauty',
    'Home',
    'Sports',
    'Other'
  ];

  const handleInputChange = (field: keyof ProductForm, value: string) => {
    setState(prev => ({
      ...prev,
      form: { ...prev.form, [field]: value },
      error: null,
      success: null
    }));
  };

  const validateForm = (): boolean => {
    const { name, price_jod, stock_quantity } = state.form;
    
    if (!name.trim()) {
      setState(prev => ({ ...prev, error: 'Product name is required' }));
      return false;
    }
    
    if (!price_jod || isNaN(Number(price_jod)) || Number(price_jod) <= 0) {
      setState(prev => ({ ...prev, error: 'Valid price is required' }));
      return false;
    }
    
    if (!stock_quantity || isNaN(Number(stock_quantity)) || Number(stock_quantity) < 0) {
      setState(prev => ({ ...prev, error: 'Valid stock quantity is required' }));
      return false;
    }
    
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    setState(prev => ({ ...prev, isSubmitting: true, error: null }));
    
    try {
      const productData = {
        name: state.form.name.trim(),
        description: state.form.description.trim() || undefined,
        price_jod: Number(state.form.price_jod),
        category: state.form.category || undefined,
        stock_quantity: Number(state.form.stock_quantity),
        image_url: state.form.image_url.trim() || undefined
      };
      
      const response = await productionApi.addCatalogItem(productData);
      
      if (response.error) {
        setState(prev => ({ 
          ...prev, 
          isSubmitting: false, 
          error: `Failed to add product: ${response.error}` 
        }));
        return;
      }
      
      setState(prev => ({ 
        ...prev, 
        isSubmitting: false, 
        success: `Product "${state.form.name}" added successfully!` 
      }));
      
      // Reset form after successful submission
      setTimeout(() => {
        setState(prev => ({
          ...prev,
          form: {
            name: '',
            description: '',
            price_jod: '',
            category: '',
            stock_quantity: '',
            image_url: ''
          },
          success: null
        }));
      }, 2000);
      
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        isSubmitting: false, 
        error: 'Network error adding product' 
      }));
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6 p-6">
      <div className="flex items-center gap-4">
        <Button 
          variant="outline" 
          onClick={() => window.history.back()}
          className="flex items-center gap-2"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Catalog
        </Button>
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Add New Product</h1>
          <p className="text-slate-500 mt-1">Add a product to your catalog</p>
        </div>
      </div>

      {/* Success Message */}
      {state.success && (
        <Alert className="border-green-200 bg-green-50">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">
            {state.success}
          </AlertDescription>
        </Alert>
      )}

      {/* Error Message */}
      {state.error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {state.error}
          </AlertDescription>
        </Alert>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Package className="h-5 w-5" />
            Product Information
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Product Name */}
            <div className="space-y-2">
              <Label htmlFor="name">Product Name *</Label>
              <Input
                id="name"
                value={state.form.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                placeholder="Enter product name"
                required
                disabled={state.isSubmitting}
              />
            </div>

            {/* Description */}
            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={state.form.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                placeholder="Enter product description"
                rows={3}
                disabled={state.isSubmitting}
              />
            </div>

            {/* Price and Stock in a row */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="price">Price (JOD) *</Label>
                <Input
                  id="price"
                  type="number"
                  step="0.01"
                  min="0"
                  value={state.form.price_jod}
                  onChange={(e) => handleInputChange('price_jod', e.target.value)}
                  placeholder="0.00"
                  required
                  disabled={state.isSubmitting}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="stock">Stock Quantity *</Label>
                <Input
                  id="stock"
                  type="number"
                  min="0"
                  value={state.form.stock_quantity}
                  onChange={(e) => handleInputChange('stock_quantity', e.target.value)}
                  placeholder="0"
                  required
                  disabled={state.isSubmitting}
                />
              </div>
            </div>

            {/* Category */}
            <div className="space-y-2">
              <Label htmlFor="category">Category</Label>
              <Select
                value={state.form.category}
                onValueChange={(value) => handleInputChange('category', value)}
                disabled={state.isSubmitting}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a category" />
                </SelectTrigger>
                <SelectContent>
                  {categories.map((category) => (
                    <SelectItem key={category} value={category}>
                      {category}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Image URL */}
            <div className="space-y-2">
              <Label htmlFor="image">Image URL</Label>
              <Input
                id="image"
                type="url"
                value={state.form.image_url}
                onChange={(e) => handleInputChange('image_url', e.target.value)}
                placeholder="https://example.com/image.jpg"
                disabled={state.isSubmitting}
              />
              <p className="text-sm text-slate-500">
                Optional: Add a URL for the product image
              </p>
            </div>

            {/* Submit Button */}
            <div className="flex items-center gap-4 pt-4">
              <Button 
                type="submit" 
                disabled={state.isSubmitting}
                className="flex items-center gap-2"
              >
                {state.isSubmitting ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Save className="h-4 w-4" />
                )}
                {state.isSubmitting ? 'Adding Product...' : 'Add Product'}
              </Button>
              
              <Button 
                type="button" 
                variant="outline"
                onClick={() => window.history.back()}
                disabled={state.isSubmitting}
              >
                Cancel
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Preview Card */}
      {state.form.name && (
        <Card>
          <CardHeader>
            <CardTitle>Preview</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="border rounded-lg p-4 bg-slate-50">
              <div className="flex items-start gap-4">
                <div className="w-20 h-20 bg-slate-200 rounded-lg flex items-center justify-center overflow-hidden">
                  {state.form.image_url ? (
                    <img 
                      src={state.form.image_url} 
                      alt={state.form.name}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        e.currentTarget.src = '';
                        e.currentTarget.style.display = 'none';
                      }}
                    />
                  ) : (
                    <Package className="h-8 w-8 text-slate-400" />
                  )}
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-slate-900">{state.form.name}</h3>
                  {state.form.description && (
                    <p className="text-sm text-slate-600 mt-1">{state.form.description}</p>
                  )}
                  <div className="flex items-center gap-2 mt-2">
                    {state.form.price_jod && (
                      <span className="font-bold text-slate-900">{state.form.price_jod} JOD</span>
                    )}
                    {state.form.category && (
                      <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                        {state.form.category}
                      </span>
                    )}
                    {state.form.stock_quantity && (
                      <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                        {state.form.stock_quantity} in stock
                      </span>
                    )}
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