'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  Store, Package, ShoppingCart, TrendingUp, Star, Users,
  DollarSign, BarChart3
} from 'lucide-react'
import Link from 'next/link'

const marketplaceStats = {
  totalListings: 120,
  activeOrders: 15,
  totalSales: 45000,
  avgRating: 4.7,
  monthlyGrowth: 18,
}

const featuredProducts = [
  { id: 'mp-1', title: 'Lead Package - 50 Qualified Leads', price: 5000, seller: 'LeadGen Pro', rating: 4.8, sales: 156, category: 'Leads' },
  { id: 'mp-2', title: 'Property Photography Service', price: 1500, seller: 'ProPhoto', rating: 4.9, sales: 89, category: 'Services' },
  { id: 'mp-3', title: 'Virtual Tour Package', price: 2500, seller: '360 Tours', rating: 4.7, sales: 45, category: 'Services' },
  { id: 'mp-4', title: 'CRM Training Course', price: 3000, seller: 'CRM Academy', rating: 4.6, sales: 234, category: 'Training' },
]

const categories = [
  { name: 'Leads', count: 25, icon: Users, color: 'bg-blue-500' },
  { name: 'Services', count: 48, icon: Package, color: 'bg-green-500' },
  { name: 'Training', count: 15, icon: BarChart3, color: 'bg-purple-500' },
  { name: 'Tools', count: 32, icon: Store, color: 'bg-orange-500' },
]

const recentOrders = [
  { id: 1, product: 'Lead Package - 50 Leads', buyer: 'Ahmet Yılmaz', price: 5000, status: 'completed', date: '2 hours ago' },
  { id: 2, product: 'Property Photography', buyer: 'Fatma Demir', price: 1500, status: 'in_progress', date: '5 hours ago' },
  { id: 3, product: 'CRM Training Course', buyer: 'Ali Öztürk', price: 3000, status: 'pending', date: '1 day ago' },
]

const statusColors: Record<string, string> = {
  completed: 'bg-green-500',
  in_progress: 'bg-blue-500',
  pending: 'bg-yellow-500',
  cancelled: 'bg-red-500',
}

export default function MarketplaceDashboardPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Marketplace Dashboard</h1>
          <p className="text-gray-500 mt-1">Browse and manage marketplace activity</p>
        </div>
        <div className="flex gap-3">
          <Link href="/marketplace">
            <Button variant="outline">
              <Store className="mr-2 h-4 w-4" />
              Browse Marketplace
            </Button>
          </Link>
          <Button>
            <Package className="mr-2 h-4 w-4" />
            List Product
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Listings</CardTitle>
            <Package className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{marketplaceStats.totalListings}</div>
            <p className="text-xs text-muted-foreground">Active products</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Orders</CardTitle>
            <ShoppingCart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{marketplaceStats.activeOrders}</div>
            <p className="text-xs text-muted-foreground">In progress</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Sales</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">₺{marketplaceStats.totalSales.toLocaleString()}</div>
            <div className="flex items-center text-xs text-green-600">
              <TrendingUp className="h-3 w-3 mr-1" />
              +{marketplaceStats.monthlyGrowth}% this month
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Rating</CardTitle>
            <Star className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{marketplaceStats.avgRating}</div>
            <div className="flex items-center">
              {[1, 2, 3, 4, 5].map((star) => (
                <Star
                  key={star}
                  className={`h-3 w-3 ${star <= Math.round(marketplaceStats.avgRating) ? 'text-yellow-500 fill-yellow-500' : 'text-gray-300'}`}
                />
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Categories */}
      <Card>
        <CardHeader>
          <CardTitle>Categories</CardTitle>
          <CardDescription>Browse by category</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {categories.map((category) => (
              <Link key={category.name} href={`/marketplace?category=${category.name.toLowerCase()}`}>
                <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer">
                  <div className={`p-3 rounded-lg ${category.color}`}>
                    <category.icon className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <p className="font-medium">{category.name}</p>
                    <p className="text-sm text-muted-foreground">{category.count} items</p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Featured Products */}
        <Card>
          <CardHeader>
            <CardTitle>Featured Products</CardTitle>
            <CardDescription>Top-rated marketplace listings</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {featuredProducts.map((product) => (
                <Link key={product.id} href={`/marketplace/${product.id}`}>
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer">
                    <div>
                      <p className="font-medium">{product.title}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-sm text-muted-foreground">{product.seller}</span>
                        <span className="text-sm text-muted-foreground">•</span>
                        <div className="flex items-center">
                          <Star className="h-3 w-3 text-yellow-500 fill-yellow-500 mr-1" />
                          <span className="text-sm">{product.rating}</span>
                        </div>
                        <span className="text-sm text-muted-foreground">({product.sales} sales)</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-bold">₺{product.price.toLocaleString()}</p>
                      <Badge variant="outline">{product.category}</Badge>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
            <Link href="/marketplace">
              <Button variant="link" className="w-full mt-4">View all products</Button>
            </Link>
          </CardContent>
        </Card>

        {/* Recent Orders */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Orders</CardTitle>
            <CardDescription>Your latest marketplace activity</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentOrders.map((order) => (
                <div key={order.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium">{order.product}</p>
                    <p className="text-sm text-muted-foreground">Buyer: {order.buyer}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">₺{order.price.toLocaleString()}</p>
                    <Badge className={statusColors[order.status]}>{order.status.replace('_', ' ')}</Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
