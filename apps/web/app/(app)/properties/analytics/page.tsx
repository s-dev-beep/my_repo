'use client'

import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { 
  ArrowLeft, Building2, TrendingUp, TrendingDown, MapPin, 
  Eye, MessageSquare, Clock, DollarSign, BarChart3
} from 'lucide-react'

const stats = {
  totalListings: 856,
  newListingsMonth: 78,
  avgTimeOnMarket: 45,
  avgPricePerSqm: 35000,
  totalViews: 125000,
  totalInquiries: 3400,
  conversionRate: 2.7,
}

const priceByDistrict = [
  { district: 'Oran', avgPrice: 55000, change: 12 },
  { district: 'Bilkent', avgPrice: 48000, change: 8 },
  { district: 'Çankaya', avgPrice: 42000, change: 5 },
  { district: 'Kavaklıdere', avgPrice: 40000, change: 3 },
  { district: 'Kızılay', avgPrice: 38000, change: -2 },
  { district: 'Çayyolu', avgPrice: 35000, change: 7 },
]

const typeDistribution = [
  { type: 'Apartment', count: 520, percentage: 61, color: 'bg-blue-500' },
  { type: 'Villa', count: 156, percentage: 18, color: 'bg-green-500' },
  { type: 'Office', count: 98, percentage: 11, color: 'bg-purple-500' },
  { type: 'Commercial', count: 52, percentage: 6, color: 'bg-orange-500' },
  { type: 'Land', count: 30, percentage: 4, color: 'bg-pink-500' },
]

const topPerformingProperties = [
  { id: 'prop-2', title: 'Luxury Villa with Garden', views: 1245, inquiries: 45, district: 'Oran' },
  { id: 'prop-1', title: 'Modern 3+1 Apartment', views: 980, inquiries: 38, district: 'Çankaya' },
  { id: 'prop-7', title: 'Penthouse with Terrace', views: 856, inquiries: 32, district: 'Çankaya' },
  { id: 'prop-9', title: 'Family Villa in Bilkent', views: 720, inquiries: 28, district: 'Bilkent' },
]

const monthlyData = [
  { month: 'Jul', listings: 65, sold: 12 },
  { month: 'Aug', listings: 72, sold: 15 },
  { month: 'Sep', listings: 68, sold: 18 },
  { month: 'Oct', listings: 75, sold: 14 },
  { month: 'Nov', listings: 82, sold: 20 },
  { month: 'Dec', listings: 78, sold: 22 },
]

export default function PropertyAnalyticsPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/properties">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-5 w-5" />
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold">Property Analytics</h1>
            <p className="text-muted-foreground">Insights and performance metrics</p>
          </div>
        </div>
        <Button variant="outline">
          <BarChart3 className="mr-2 h-4 w-4" />
          Export Report
        </Button>
      </div>

      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Listings</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalListings}</div>
            <div className="flex items-center text-xs text-green-600">
              <TrendingUp className="h-3 w-3 mr-1" />
              +{stats.newListingsMonth} this month
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Price/m²</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">₺{stats.avgPricePerSqm.toLocaleString()}</div>
            <div className="flex items-center text-xs text-green-600">
              <TrendingUp className="h-3 w-3 mr-1" />
              +5.2% from last month
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Views</CardTitle>
            <Eye className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{(stats.totalViews / 1000).toFixed(0)}K</div>
            <p className="text-xs text-muted-foreground">This month</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Days on Market</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.avgTimeOnMarket}</div>
            <div className="flex items-center text-xs text-green-600">
              <TrendingDown className="h-3 w-3 mr-1" />
              -3 days from avg
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Monthly Trend */}
        <Card>
          <CardHeader>
            <CardTitle>Monthly Trend</CardTitle>
            <CardDescription>Listings vs sales over time</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64 flex items-end justify-between gap-2">
              {monthlyData.map((item) => (
                <div key={item.month} className="flex-1 flex flex-col items-center gap-1">
                  <div className="w-full flex flex-col gap-1">
                    <div 
                      className="w-full bg-blue-500 rounded-t"
                      style={{ height: `${item.listings * 2}px` }}
                    />
                    <div 
                      className="w-full bg-green-500 rounded-t"
                      style={{ height: `${item.sold * 6}px` }}
                    />
                  </div>
                  <span className="text-xs text-muted-foreground">{item.month}</span>
                </div>
              ))}
            </div>
            <div className="flex justify-center gap-6 mt-4">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-blue-500 rounded" />
                <span className="text-sm">New Listings</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-green-500 rounded" />
                <span className="text-sm">Sold</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Type Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Property Type Distribution</CardTitle>
            <CardDescription>Breakdown by property type</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {typeDistribution.map((type) => (
                <div key={type.type} className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>{type.type}</span>
                    <span className="font-medium">{type.count} ({type.percentage}%)</span>
                  </div>
                  <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div 
                      className={`h-full ${type.color} rounded-full`}
                      style={{ width: `${type.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Price by District */}
      <Card>
        <CardHeader>
          <CardTitle>Average Price by District</CardTitle>
          <CardDescription>Price per m² by location</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {priceByDistrict.map((district) => (
              <div key={district.district} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <MapPin className="h-5 w-5 text-gray-400" />
                  <div>
                    <p className="font-medium">{district.district}</p>
                    <p className="text-sm text-muted-foreground">Avg: ₺{district.avgPrice.toLocaleString()}/m²</p>
                  </div>
                </div>
                <Badge variant={district.change > 0 ? 'default' : 'destructive'} className={district.change > 0 ? 'bg-green-500' : ''}>
                  {district.change > 0 ? '+' : ''}{district.change}%
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Top Performing Properties */}
      <Card>
        <CardHeader>
          <CardTitle>Top Performing Properties</CardTitle>
          <CardDescription>Most viewed and inquired listings</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {topPerformingProperties.map((property, index) => (
              <Link key={property.id} href={`/properties/${property.id}`}>
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer">
                  <div className="flex items-center gap-4">
                    <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold">
                      {index + 1}
                    </div>
                    <div>
                      <p className="font-medium">{property.title}</p>
                      <p className="text-sm text-muted-foreground">{property.district}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-6">
                    <div className="text-center">
                      <div className="flex items-center gap-1">
                        <Eye className="h-4 w-4 text-gray-400" />
                        <span className="font-medium">{property.views.toLocaleString()}</span>
                      </div>
                      <p className="text-xs text-muted-foreground">Views</p>
                    </div>
                    <div className="text-center">
                      <div className="flex items-center gap-1">
                        <MessageSquare className="h-4 w-4 text-gray-400" />
                        <span className="font-medium">{property.inquiries}</span>
                      </div>
                      <p className="text-xs text-muted-foreground">Inquiries</p>
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
