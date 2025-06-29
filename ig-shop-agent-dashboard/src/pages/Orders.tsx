import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { 
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../components/ui/dialog';
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '../components/ui/dropdown-menu';
import { 
  Search, 
  Filter, 
  Download, 
  MoreVertical,
  Edit,
  Truck,
  CheckCircle,
  XCircle,
  Clock,
  ShoppingCart,
  Phone,
  MapPin,
  Loader2,
  AlertCircle
} from 'lucide-react';
import { apiService } from '../services/api';
import { Order } from '../types';

export function Orders() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [orderList, setOrderList] = useState<Order[]>([]);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load orders from API
  useEffect(() => {
    const loadOrders = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const response = await apiService.getOrders(100, 0, selectedStatus === 'all' ? undefined : selectedStatus);
        
        if (response.data && response.data.orders) {
          setOrderList(response.data.orders);
        } else {
          setError(response.error || 'Failed to load orders');
          setOrderList([]); // Set empty array on error
        }
      } catch (err) {
        setError('Failed to load orders');
        setOrderList([]); // Set empty array on error
      } finally {
        setIsLoading(false);
      }
    };

    loadOrders();
  }, [selectedStatus]);

  const statuses = ['all', 'pending', 'confirmed', 'shipped', 'delivered', 'cancelled'];

  const filteredOrders = orderList.filter(order => {
    const matchesSearch = order.customer.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         order.phone.includes(searchTerm) ||
                         order.sku.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = selectedStatus === 'all' || order.status === selectedStatus;
    return matchesSearch && matchesStatus;
  });

  const getStatusConfig = (status: string) => {
    switch (status) {
      case 'pending':
        return { 
          label: 'Pending', 
          variant: 'secondary' as const, 
          icon: Clock,
          color: 'text-orange-600' 
        };
      case 'confirmed':
        return { 
          label: 'Confirmed', 
          variant: 'default' as const, 
          icon: CheckCircle,
          color: 'text-blue-600' 
        };
      case 'shipped':
        return { 
          label: 'Shipped', 
          variant: 'outline' as const, 
          icon: Truck,
          color: 'text-purple-600' 
        };
      case 'delivered':
        return { 
          label: 'Delivered', 
          variant: 'default' as const, 
          icon: CheckCircle,
          color: 'text-green-600' 
        };
      case 'cancelled':
        return { 
          label: 'Cancelled', 
          variant: 'destructive' as const, 
          icon: XCircle,
          color: 'text-red-600' 
        };
      default:
        return { 
          label: status, 
          variant: 'outline' as const, 
          icon: Clock,
          color: 'text-slate-600' 
        };
    }
  };

  const getOrderStats = () => {
    const totalRevenue = orderList
      .filter(o => o.status === 'delivered')
      .reduce((sum, order) => sum + order.total_amount, 0);
    
    return {
      total: orderList.length,
      pending: orderList.filter(o => o.status === 'pending').length,
      confirmed: orderList.filter(o => o.status === 'confirmed').length,
      shipped: orderList.filter(o => o.status === 'shipped').length,
      delivered: orderList.filter(o => o.status === 'delivered').length,
      revenue: totalRevenue
    };
  };

  const stats = getOrderStats();

  // Loading state
  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">Orders</h1>
            <p className="text-slate-500 mt-1">Loading orders...</p>
          </div>
        </div>
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          <span className="ml-3 text-slate-600">Loading orders...</span>
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
            <h1 className="text-3xl font-bold text-slate-900">Orders</h1>
            <p className="text-slate-500 mt-1">Manage and track your customer orders</p>
          </div>
        </div>
        <Card>
          <CardContent className="p-6">
            <div className="text-center">
              <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-slate-900 mb-2">Failed to Load Orders</h3>
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Orders</h1>
          <p className="text-slate-500 mt-1">
            Manage and track your customer orders
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Export Orders
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="text-center">
              <p className="text-sm font-medium text-slate-500">Total Orders</p>
              <p className="text-2xl font-bold text-slate-900">{stats.total}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-center">
              <p className="text-sm font-medium text-orange-600">Pending</p>
              <p className="text-2xl font-bold text-orange-600">{stats.pending}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-center">
              <p className="text-sm font-medium text-blue-600">Confirmed</p>
              <p className="text-2xl font-bold text-blue-600">{stats.confirmed}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-center">
              <p className="text-sm font-medium text-purple-600">Shipped</p>
              <p className="text-2xl font-bold text-purple-600">{stats.shipped}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-center">
              <p className="text-sm font-medium text-green-600">Delivered</p>
              <p className="text-2xl font-bold text-green-600">{stats.delivered}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-center">
              <p className="text-sm font-medium text-slate-500">Revenue</p>
              <p className="text-2xl font-bold text-green-600">{stats.revenue.toLocaleString()} JOD</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
              <Input
                placeholder="Search orders by customer, phone, or SKU..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline">
                  <Filter className="w-4 h-4 mr-2" />
                  {selectedStatus === 'all' ? 'All Status' : getStatusConfig(selectedStatus).label}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                {statuses.map((status) => (
                  <DropdownMenuItem
                    key={status}
                    onClick={() => setSelectedStatus(status)}
                  >
                    {status === 'all' ? 'All Status' : getStatusConfig(status).label}
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </CardContent>
      </Card>

      {/* Orders Table */}
      <Card>
        <CardHeader>
          <CardTitle>Orders ({filteredOrders.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Order ID</TableHead>
                <TableHead>Customer</TableHead>
                <TableHead>Product</TableHead>
                <TableHead>Quantity</TableHead>
                <TableHead>Total</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredOrders.map((order) => {
                const statusConfig = getStatusConfig(order.status);
                return (
                  <TableRow key={order.id}>
                    <TableCell className="font-mono text-sm">{order.id.substring(0, 8)}</TableCell>
                    <TableCell>
                      <div>
                        <p className="font-medium text-slate-900">{order.customer}</p>
                        <p className="text-sm text-slate-500 flex items-center gap-1">
                          <Phone className="w-3 h-3" />
                          {order.phone}
                        </p>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div>
                        <p className="font-medium text-slate-900">{order.sku}</p>
                      </div>
                    </TableCell>
                    <TableCell>{order.qty}</TableCell>
                    <TableCell className="font-medium">{order.total_amount} JOD</TableCell>
                    <TableCell>
                      <Badge variant={statusConfig.variant} className="flex items-center gap-1 w-fit">
                        <statusConfig.icon className="w-3 h-3" />
                        {statusConfig.label}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {new Date(order.created_at).toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        year: 'numeric'
                      })}
                    </TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm">
                            <MoreVertical className="w-4 h-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => setSelectedOrder(order)}>
                            View Details
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            <Edit className="w-4 h-4 mr-2" />
                            Edit Order
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            <Truck className="w-4 h-4 mr-2" />
                            Update Status
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Order Details Dialog */}
      <Dialog open={!!selectedOrder} onOpenChange={() => setSelectedOrder(null)}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Order Details</DialogTitle>
            <DialogDescription>
              Complete information for order #{selectedOrder?.id.substring(0, 8)}
            </DialogDescription>
          </DialogHeader>
          {selectedOrder && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <h4 className="font-medium text-slate-900 mb-2">Customer Information</h4>
                    <div className="space-y-2 text-sm">
                      <p><span className="font-medium">Name:</span> {selectedOrder.customer}</p>
                      <p className="flex items-center gap-1">
                        <Phone className="w-3 h-3" />
                        <span className="font-medium">Phone:</span> {selectedOrder.phone}
                      </p>
                      {selectedOrder.delivery_address && (
                        <p className="flex items-start gap-1">
                          <MapPin className="w-3 h-3 mt-0.5" />
                          <span className="font-medium">Address:</span> {selectedOrder.delivery_address}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
                <div className="space-y-4">
                  <div>
                    <h4 className="font-medium text-slate-900 mb-2">Order Information</h4>
                    <div className="space-y-2 text-sm">
                      <p><span className="font-medium">SKU:</span> {selectedOrder.sku}</p>
                      <p><span className="font-medium">Quantity:</span> {selectedOrder.qty}</p>
                      <p><span className="font-medium">Total:</span> {selectedOrder.total_amount} JOD</p>
                      <p className="flex items-center gap-1">
                        <span className="font-medium">Status:</span>
                        <Badge variant={getStatusConfig(selectedOrder.status).variant}>
                          {getStatusConfig(selectedOrder.status).label}
                        </Badge>
                      </p>
                    </div>
                  </div>
                </div>
              </div>
              {selectedOrder.notes && (
                <div>
                  <h4 className="font-medium text-slate-900 mb-2">Notes</h4>
                  <p className="text-sm text-slate-600 bg-slate-50 p-3 rounded-lg">
                    {selectedOrder.notes}
                  </p>
                </div>
              )}
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setSelectedOrder(null)}>
                  Close
                </Button>
                <Button>
                  Update Status
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
