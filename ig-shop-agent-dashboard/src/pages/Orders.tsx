import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Package, Search, Filter, Eye, Download, AlertCircle, Loader2 } from 'lucide-react';
import { productionApi, Order } from '../services/productionApi';
import { Alert, AlertDescription } from '../components/ui/alert';

interface OrdersState {
  orders: Order[];
  isLoading: boolean;
  error: string | null;
  searchTerm: string;
}

export function Orders() {
  const [state, setState] = useState<OrdersState>({
    orders: [],
    isLoading: true,
    error: null,
    searchTerm: ''
  });

  // Load orders data from real API
  const loadOrders = async () => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      const response = await productionApi.getOrders();
      
      if (response.error) {
        setState(prev => ({ 
          ...prev, 
          isLoading: false, 
          error: `Failed to load orders: ${response.error}` 
        }));
        return;
      }

      setState(prev => ({
        ...prev,
        orders: response.data || [],
        isLoading: false,
        error: null
      }));
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        isLoading: false, 
        error: 'Network error loading orders' 
      }));
    }
  };

  // Load data on component mount
  useEffect(() => {
    loadOrders();
  }, []);

  // Filter orders based on search term
  const filteredOrders = state.orders.filter(order =>
    order.id.toString().toLowerCase().includes(state.searchTerm.toLowerCase()) ||
    order.customer_name.toLowerCase().includes(state.searchTerm.toLowerCase()) ||
    order.status.toLowerCase().includes(state.searchTerm.toLowerCase())
  );

  // Calculate stats from real data
  const pendingOrders = state.orders.filter(o => o.status === 'pending').length;
  const processingOrders = state.orders.filter(o => o.status === 'processing').length;
  const deliveredOrders = state.orders.filter(o => o.status === 'delivered').length;
  const totalRevenue = state.orders.reduce((sum, o) => sum + o.total_amount, 0);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'confirmed': return 'bg-blue-100 text-blue-800';
      case 'processing': return 'bg-indigo-100 text-indigo-800';
      case 'shipped': return 'bg-green-100 text-green-800';
      case 'delivered': return 'bg-gray-100 text-gray-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'pending': return 'Pending';
      case 'confirmed': return 'Confirmed';
      case 'processing': return 'Processing';
      case 'shipped': return 'Shipped';
      case 'delivered': return 'Delivered';
      case 'cancelled': return 'Cancelled';
      default: return status;
    }
  };

  // Handle order status update
  const handleUpdateStatus = async (orderId: number, newStatus: string) => {
    try {
      const response = await productionApi.updateOrderStatus(orderId, newStatus);
      if (response.error) {
        alert(`Failed to update order status: ${response.error}`);
        return;
      }
      
      // Reload orders after status update
      await loadOrders();
      alert('Order status updated successfully');
    } catch (error) {
      alert('Network error updating order status');
    }
  };

  // Loading state
  if (state.isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-4" />
            <p className="text-slate-600">Loading orders...</p>
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
              onClick={loadOrders}
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
          <h1 className="text-3xl font-bold text-slate-900">Orders</h1>
          <p className="text-slate-500 mt-1">
            Manage customer orders and track shipments ({state.orders.length} orders)
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={loadOrders}>
            <Download className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          {state.orders.length > 0 && (
            <Badge variant="outline" className="bg-green-50 text-green-700">
              {pendingOrders} pending orders
            </Badge>
          )}
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input 
            placeholder="Search orders..." 
            className="pl-10"
            value={state.searchTerm}
            onChange={(e) => setState(prev => ({ ...prev, searchTerm: e.target.value }))}
          />
        </div>
        <Button variant="outline" onClick={loadOrders}>
          <Filter className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Real-time Statistics from API Data */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-blue-600">{pendingOrders}</div>
            <div className="text-sm text-slate-500">Pending Orders</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-yellow-600">{processingOrders}</div>
            <div className="text-sm text-slate-500">Processing</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-green-600">{deliveredOrders}</div>
            <div className="text-sm text-slate-500">Delivered</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-slate-600">{totalRevenue.toFixed(2)} JOD</div>
            <div className="text-sm text-slate-500">Total Revenue</div>
          </CardContent>
        </Card>
      </div>

      {/* Empty state when no orders */}
      {filteredOrders.length === 0 && !state.isLoading ? (
        <Card className="p-12 text-center">
          <Package className="h-16 w-16 text-slate-300 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-slate-600 mb-2">
            {state.searchTerm ? 'No orders found' : 'No orders yet'}
          </h3>
          <p className="text-slate-500 mb-6">
            {state.searchTerm 
              ? `No orders match "${state.searchTerm}". Try a different search term.`
              : 'Orders will appear here when customers place them through Instagram.'
            }
          </p>
        </Card>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Package className="h-5 w-5" />
              Orders List
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {filteredOrders.map((order) => (
                <div 
                  key={order.id}
                  className="border border-slate-200 rounded-lg p-4 hover:bg-slate-50 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-3">
                        <h3 className="font-medium text-slate-900">#{order.id}</h3>
                        <Badge 
                          variant="outline"
                          className={getStatusColor(order.status)}
                        >
                          {getStatusLabel(order.status)}
                        </Badge>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
                        <div>
                          <p className="text-sm text-slate-500">Customer</p>
                          <p className="font-medium">{order.customer_name}</p>
                          {order.instagram_message_id && (
                            <p className="text-sm text-slate-600">Instagram Order</p>
                          )}
                        </div>
                        
                        <div>
                          <p className="text-sm text-slate-500">Items</p>
                          {order.items && order.items.length > 0 ? (
                            order.items.map((item, index) => (
                              <p key={index} className="text-sm">
                                {item.product_name} × {item.quantity} ({item.price.toFixed(2)} JOD each)
                              </p>
                            ))
                          ) : (
                            <p className="text-sm text-slate-400">No items details</p>
                          )}
                        </div>
                        
                        <div>
                          <p className="text-sm text-slate-500">Total</p>
                          <p className="font-bold text-lg">{order.total_amount.toFixed(2)} JOD</p>
                          <p className="text-sm text-slate-600">
                            {new Date(order.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => window.location.href = `/order/${order.id}`}
                      >
                        <Eye className="h-3 w-3 mr-1" />
                        View
                      </Button>
                      <select
                        value={order.status}
                        onChange={(e) => handleUpdateStatus(order.id, e.target.value)}
                        className="text-sm border rounded px-2 py-1"
                      >
                        <option value="pending">Pending</option>
                        <option value="confirmed">Confirmed</option>
                        <option value="processing">Processing</option>
                        <option value="shipped">Shipped</option>
                        <option value="delivered">Delivered</option>
                        <option value="cancelled">Cancelled</option>
                      </select>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
