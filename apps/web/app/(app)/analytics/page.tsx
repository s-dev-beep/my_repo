'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { BarChart3, TrendingUp, TrendingDown, Users, Building2, DollarSign, Target, Download } from 'lucide-react'

const kpis = [
  { label: 'Total Revenue', value: '₺72M', change: 28, trend: 'up' },
  { label: 'Leads Generated', value: '1,247', change: 15, trend: 'up' },
  { label: 'Properties Sold', value: '156', change: 12, trend: 'up' },
  { label: 'Conversion Rate', value: '18.5%', change: -2, trend: 'down' },
]

const salesByMonth = [
  { month: 'Jan', revenue: 18500000, deals: 8 },
  { month: 'Feb', revenue: 25000000, deals: 12 },
  { month: 'Mar', revenue: 32000000, deals: 15 },
  { month: 'Apr', revenue: 22000000, deals: 10 },
  { month: 'May', revenue: 38000000, deals: 18 },
  { month: 'Jun', revenue: 29000000, deals: 14 },
]

const leadFunnel = [
  { stage: 'New', count: 450, percentage: 100 },
  { stage: 'Contacted', count: 380, percentage: 84 },
  { stage: 'Qualified', count: 220, percentage: 49 },
  { stage: 'Proposal', count: 120, percentage: 27 },
  { stage: 'Won', count: 45, percentage: 10 },
]

const topAgents = [
  { name: 'Ali Öztürk', deals: 18, revenue: 5500000 },
  { name: 'Fatma Demir', deals: 15, revenue: 4100000 },
  { name: 'Ahmet Yılmaz', deals: 12, revenue: 3200000 },
]

export default function AnalyticsPage() {
  const maxRevenue = Math.max(...salesByMonth.map(m => m.revenue))

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
          <p className="text-gray-500 mt-1">Performance insights and reporting</p>
        </div>
        <Button variant="outline"><Download className="mr-2 h-4 w-4" />Export Report</Button>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        {kpis.map((kpi) => (
          <Card key={kpi.label}>
            <CardContent className="p-4">
              <p className="text-sm text-muted-foreground">{kpi.label}</p>
              <div className="flex items-center justify-between mt-1">
                <p className="text-2xl font-bold">{kpi.value}</p>
                <div className={`flex items-center text-sm ${kpi.trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
                  {kpi.trend === 'up' ? <TrendingUp className="h-4 w-4 mr-1" /> : <TrendingDown className="h-4 w-4 mr-1" />}
                  {kpi.change > 0 ? '+' : ''}{kpi.change}%
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Monthly Revenue</CardTitle><CardDescription>Revenue trend over the past 6 months</CardDescription></CardHeader>
          <CardContent>
            <div className="h-64 flex items-end justify-between gap-2 pt-4">
              {salesByMonth.map((item) => (
                <div key={item.month} className="flex-1 flex flex-col items-center gap-1">
                  <div className="w-full bg-blue-500 rounded-t hover:bg-blue-600 transition-colors" style={{ height: `${(item.revenue / maxRevenue) * 200}px` }} />
                  <span className="text-xs text-muted-foreground">{item.month}</span>
                  <span className="text-xs font-medium">₺{(item.revenue / 1000000).toFixed(1)}M</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Lead Conversion Funnel</CardTitle><CardDescription>Lead progression through stages</CardDescription></CardHeader>
          <CardContent>
            <div className="space-y-4">
              {leadFunnel.map((stage, index) => (
                <div key={stage.stage} className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>{stage.stage}</span>
                    <span className="font-medium">{stage.count} ({stage.percentage}%)</span>
                  </div>
                  <Progress value={stage.percentage} className="h-3" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Top Performing Agents</CardTitle></CardHeader>
        <CardContent>
          <div className="space-y-4">
            {topAgents.map((agent, index) => (
              <div key={agent.name} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-4">
                  <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold">{index + 1}</div>
                  <div><p className="font-medium">{agent.name}</p><p className="text-sm text-muted-foreground">{agent.deals} deals closed</p></div>
                </div>
                <p className="text-xl font-bold text-blue-600">₺{(agent.revenue / 1000000).toFixed(1)}M</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
