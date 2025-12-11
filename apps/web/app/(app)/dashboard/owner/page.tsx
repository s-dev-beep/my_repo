'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { 
  Building2, TrendingUp, DollarSign, Users, BarChart3,
  ArrowUpRight, ArrowDownRight, PieChart, LineChart
} from 'lucide-react'
import Link from 'next/link'

const companyStats = {
  totalRevenue: 72000000,
  monthlyRevenue: 12500000,
  totalProperties: 856,
  totalLeads: 1247,
  totalAgents: 45,
  avgDealSize: 2800000,
  growthRate: 28,
  marketShare: 15.3,
}

const departmentPerformance = [
  { name: 'Sales Team A', revenue: 25000000, target: 30000000, agents: 12 },
  { name: 'Sales Team B', revenue: 22000000, target: 25000000, agents: 10 },
  { name: 'Sales Team C', revenue: 18000000, target: 20000000, agents: 8 },
  { name: 'Call Center', leads: 450, conversions: 85, agents: 15 },
]

const revenueByMonth = [
  { month: 'Jul', revenue: 8500000 },
  { month: 'Aug', revenue: 9200000 },
  { month: 'Sep', revenue: 10100000 },
  { month: 'Oct', revenue: 11300000 },
  { month: 'Nov', revenue: 11800000 },
  { month: 'Dec', revenue: 12500000 },
]

export default function OwnerDashboardPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Owner Dashboard</h1>
          <p className="text-gray-500 mt-1">Company-wide performance overview</p>
        </div>
        <div className="flex gap-3">
          <Link href="/analytics">
            <Button variant="outline">
              <BarChart3 className="mr-2 h-4 w-4" />
              Full Reports
            </Button>
          </Link>
          <Link href="/admin/settings">
            <Button>
              <Building2 className="mr-2 h-4 w-4" />
              Company Settings
            </Button>
          </Link>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Revenue (YTD)</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">₺{(companyStats.totalRevenue / 1000000).toFixed(0)}M</div>
            <div className="flex items-center text-xs text-green-600">
              <ArrowUpRight className="h-3 w-3 mr-1" />
              +{companyStats.growthRate}% YoY growth
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Monthly Revenue</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">₺{(companyStats.monthlyRevenue / 1000000).toFixed(1)}M</div>
            <div className="flex items-center text-xs text-green-600">
              <ArrowUpRight className="h-3 w-3 mr-1" />
              +5.9% from last month
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Properties</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{companyStats.totalProperties}</div>
            <p className="text-xs text-muted-foreground">Active listings</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Market Share</CardTitle>
            <PieChart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{companyStats.marketShare}%</div>
            <div className="flex items-center text-xs text-green-600">
              <ArrowUpRight className="h-3 w-3 mr-1" />
              +1.2% from last quarter
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Revenue Chart Placeholder */}
      <Card>
        <CardHeader>
          <CardTitle>Revenue Trend</CardTitle>
          <CardDescription>Monthly revenue for the past 6 months</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-64 flex items-end justify-between gap-4 pt-4">
            {revenueByMonth.map((item) => (
              <div key={item.month} className="flex-1 flex flex-col items-center gap-2">
                <div 
                  className="w-full bg-blue-500 rounded-t-md transition-all hover:bg-blue-600"
                  style={{ height: `${(item.revenue / 15000000) * 200}px` }}
                />
                <span className="text-xs text-muted-foreground">{item.month}</span>
                <span className="text-xs font-medium">₺{(item.revenue / 1000000).toFixed(1)}M</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Department Performance */}
      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Department Performance</CardTitle>
            <CardDescription>Revenue by sales team</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {departmentPerformance.slice(0, 3).map((dept) => (
                <div key={dept.name} className="space-y-2">
                  <div className="flex justify-between">
                    <div>
                      <p className="font-medium">{dept.name}</p>
                      <p className="text-sm text-muted-foreground">{dept.agents} agents</p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">₺{((dept.revenue || 0) / 1000000).toFixed(1)}M</p>
                      <p className="text-sm text-muted-foreground">Target: ₺{((dept.target || 0) / 1000000).toFixed(0)}M</p>
                    </div>
                  </div>
                  <Progress value={((dept.revenue || 0) / (dept.target || 1)) * 100} className="h-2" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Company Metrics</CardTitle>
            <CardDescription>Key performance indicators</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <Users className="h-8 w-8 text-blue-600" />
                  <div>
                    <p className="font-medium">Total Agents</p>
                    <p className="text-sm text-muted-foreground">Active employees</p>
                  </div>
                </div>
                <span className="text-2xl font-bold">{companyStats.totalAgents}</span>
              </div>
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <Users className="h-8 w-8 text-green-600" />
                  <div>
                    <p className="font-medium">Total Leads</p>
                    <p className="text-sm text-muted-foreground">In pipeline</p>
                  </div>
                </div>
                <span className="text-2xl font-bold">{companyStats.totalLeads}</span>
              </div>
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <DollarSign className="h-8 w-8 text-purple-600" />
                  <div>
                    <p className="font-medium">Avg Deal Size</p>
                    <p className="text-sm text-muted-foreground">This year</p>
                  </div>
                </div>
                <span className="text-2xl font-bold">₺{(companyStats.avgDealSize / 1000000).toFixed(1)}M</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Executive Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-3">
            <Link href="/analytics">
              <Button variant="outline">
                <BarChart3 className="mr-2 h-4 w-4" />
                Financial Reports
              </Button>
            </Link>
            <Link href="/admin/users">
              <Button variant="outline">
                <Users className="mr-2 h-4 w-4" />
                Manage Team
              </Button>
            </Link>
            <Link href="/properties/analytics">
              <Button variant="outline">
                <Building2 className="mr-2 h-4 w-4" />
                Property Analytics
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
