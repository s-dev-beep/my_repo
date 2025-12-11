'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { 
  Users, Building2, CheckSquare, Phone, TrendingUp, Calendar,
  ArrowUpRight, ArrowDownRight, Clock, Target
} from 'lucide-react'
import Link from 'next/link'

// Mock data for the dashboard
const stats = {
  totalLeads: 45,
  newLeadsToday: 8,
  activeProperties: 23,
  pendingTasks: 12,
  closedDealsMonth: 5,
  targetDeals: 8,
  revenue: 3200000,
  targetRevenue: 5000000,
}

const recentLeads = [
  { id: 'lead-1', name: 'Mehmet Kaya', status: 'new', time: '5 min ago' },
  { id: 'lead-2', name: 'Ayşe Yıldız', status: 'contacted', time: '15 min ago' },
  { id: 'lead-3', name: 'Hasan Demir', status: 'qualified', time: '1 hour ago' },
  { id: 'lead-4', name: 'Fatma Çelik', status: 'proposal', time: '2 hours ago' },
]

const upcomingTasks = [
  { id: 'task-1', title: 'Call Mehmet Kaya', type: 'call', time: '10:00 AM', priority: 'high' },
  { id: 'task-2', title: 'Property viewing at Oran', type: 'viewing', time: '2:00 PM', priority: 'high' },
  { id: 'task-3', title: 'Prepare proposal', type: 'document', time: '4:00 PM', priority: 'medium' },
]

const statusColors: Record<string, string> = {
  new: 'bg-blue-500',
  contacted: 'bg-yellow-500',
  qualified: 'bg-purple-500',
  proposal: 'bg-orange-500',
  negotiation: 'bg-pink-500',
  won: 'bg-green-500',
  lost: 'bg-red-500',
}

export default function AgentDashboardPage() {
  const progressPercentage = (stats.closedDealsMonth / stats.targetDeals) * 100
  const revenuePercentage = (stats.revenue / stats.targetRevenue) * 100

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Agent Dashboard</h1>
          <p className="text-gray-500 mt-1">Welcome back, Ahmet! Here's your performance overview.</p>
        </div>
        <div className="flex gap-3">
          <Link href="/leads/new">
            <Button>
              <Users className="mr-2 h-4 w-4" />
              New Lead
            </Button>
          </Link>
          <Link href="/tasks/new">
            <Button variant="outline">
              <CheckSquare className="mr-2 h-4 w-4" />
              New Task
            </Button>
          </Link>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Leads</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalLeads}</div>
            <div className="flex items-center text-xs text-green-600">
              <ArrowUpRight className="h-3 w-3 mr-1" />
              +{stats.newLeadsToday} today
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Properties</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.activeProperties}</div>
            <p className="text-xs text-muted-foreground">Assigned to you</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Tasks</CardTitle>
            <CheckSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.pendingTasks}</div>
            <p className="text-xs text-muted-foreground">Due this week</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Closed Deals</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.closedDealsMonth}</div>
            <p className="text-xs text-muted-foreground">This month</p>
          </CardContent>
        </Card>
      </div>

      {/* Progress and Activity */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* Monthly Target */}
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5" />
              Monthly Targets
            </CardTitle>
            <CardDescription>Your progress towards monthly goals</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span>Deals Closed</span>
                <span className="font-medium">{stats.closedDealsMonth}/{stats.targetDeals}</span>
              </div>
              <Progress value={progressPercentage} className="h-2" />
            </div>
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span>Revenue</span>
                <span className="font-medium">₺{(stats.revenue / 1000000).toFixed(1)}M / ₺{(stats.targetRevenue / 1000000).toFixed(1)}M</span>
              </div>
              <Progress value={revenuePercentage} className="h-2" />
            </div>
          </CardContent>
        </Card>

        {/* Recent Leads */}
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              Recent Leads
            </CardTitle>
            <CardDescription>Latest leads assigned to you</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentLeads.map((lead) => (
                <Link key={lead.id} href={`/leads/${lead.id}`}>
                  <div className="flex items-center justify-between hover:bg-gray-50 p-2 rounded-lg -mx-2 cursor-pointer">
                    <div className="flex items-center gap-3">
                      <Avatar className="h-8 w-8">
                        <AvatarFallback>{lead.name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
                      </Avatar>
                      <div>
                        <p className="text-sm font-medium">{lead.name}</p>
                        <p className="text-xs text-muted-foreground">{lead.time}</p>
                      </div>
                    </div>
                    <Badge className={statusColors[lead.status]}>{lead.status}</Badge>
                  </div>
                </Link>
              ))}
            </div>
            <Link href="/leads">
              <Button variant="link" className="w-full mt-4">View all leads</Button>
            </Link>
          </CardContent>
        </Card>

        {/* Upcoming Tasks */}
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Today's Tasks
            </CardTitle>
            <CardDescription>Your schedule for today</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {upcomingTasks.map((task) => (
                <Link key={task.id} href={`/tasks/${task.id}`}>
                  <div className="flex items-center justify-between hover:bg-gray-50 p-2 rounded-lg -mx-2 cursor-pointer">
                    <div className="flex items-center gap-3">
                      <div className={`w-2 h-2 rounded-full ${task.priority === 'high' ? 'bg-red-500' : 'bg-yellow-500'}`} />
                      <div>
                        <p className="text-sm font-medium">{task.title}</p>
                        <div className="flex items-center gap-1 text-xs text-muted-foreground">
                          <Clock className="h-3 w-3" />
                          {task.time}
                        </div>
                      </div>
                    </div>
                    <Badge variant="outline">{task.type}</Badge>
                  </div>
                </Link>
              ))}
            </div>
            <Link href="/tasks">
              <Button variant="link" className="w-full mt-4">View all tasks</Button>
            </Link>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-3">
            <Link href="/leads/new">
              <Button variant="outline">
                <Users className="mr-2 h-4 w-4" />
                Add Lead
              </Button>
            </Link>
            <Link href="/properties/new">
              <Button variant="outline">
                <Building2 className="mr-2 h-4 w-4" />
                Add Property
              </Button>
            </Link>
            <Link href="/tasks/new">
              <Button variant="outline">
                <CheckSquare className="mr-2 h-4 w-4" />
                Create Task
              </Button>
            </Link>
            <Link href="/calls">
              <Button variant="outline">
                <Phone className="mr-2 h-4 w-4" />
                Log Call
              </Button>
            </Link>
            <Link href="/matching">
              <Button variant="outline">
                <Target className="mr-2 h-4 w-4" />
                Match Properties
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
