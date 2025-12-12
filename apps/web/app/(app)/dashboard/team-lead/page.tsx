'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { 
  Users, Building2, TrendingUp, Target, Award, BarChart3,
  ArrowUpRight, ArrowDownRight
} from 'lucide-react'
import Link from 'next/link'

const teamStats = {
  totalAgents: 8,
  activeAgents: 7,
  teamLeads: 145,
  teamDeals: 34,
  teamRevenue: 12800000,
  teamTarget: 15000000,
  avgConversion: 23.4,
}

const teamMembers = [
  { id: 'user-1', name: 'Ahmet Yılmaz', leads: 45, deals: 12, revenue: 3200000, performance: 95 },
  { id: 'user-2', name: 'Fatma Demir', leads: 38, deals: 15, revenue: 4100000, performance: 102 },
  { id: 'user-3', name: 'Ali Öztürk', leads: 52, deals: 18, revenue: 5500000, performance: 110 },
  { id: 'user-4', name: 'Zeynep Arslan', leads: 32, deals: 8, revenue: 2200000, performance: 85 },
]

const pipelineData = [
  { stage: 'New', count: 48, value: 125000000 },
  { stage: 'Contacted', count: 35, value: 95000000 },
  { stage: 'Qualified', count: 28, value: 78000000 },
  { stage: 'Proposal', count: 18, value: 52000000 },
  { stage: 'Negotiation', count: 12, value: 38000000 },
]

export default function TeamLeadDashboardPage() {
  const targetProgress = (teamStats.teamRevenue / teamStats.teamTarget) * 100

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Team Lead Dashboard</h1>
          <p className="text-gray-500 mt-1">Monitor your team's performance and pipeline</p>
        </div>
        <div className="flex gap-3">
          <Link href="/analytics">
            <Button variant="outline">
              <BarChart3 className="mr-2 h-4 w-4" />
              View Reports
            </Button>
          </Link>
          <Link href="/tasks/team">
            <Button>
              <Users className="mr-2 h-4 w-4" />
              Team Tasks
            </Button>
          </Link>
        </div>
      </div>

      {/* Team Stats */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Team Members</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{teamStats.activeAgents}/{teamStats.totalAgents}</div>
            <p className="text-xs text-muted-foreground">Active today</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Team Leads</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{teamStats.teamLeads}</div>
            <div className="flex items-center text-xs text-green-600">
              <ArrowUpRight className="h-3 w-3 mr-1" />
              +12 this week
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Closed Deals</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{teamStats.teamDeals}</div>
            <p className="text-xs text-muted-foreground">This month</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Conversion Rate</CardTitle>
            <Award className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{teamStats.avgConversion}%</div>
            <div className="flex items-center text-xs text-green-600">
              <ArrowUpRight className="h-3 w-3 mr-1" />
              +2.3% from last month
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Team Revenue Progress */}
      <Card>
        <CardHeader>
          <CardTitle>Team Revenue Target</CardTitle>
          <CardDescription>Progress towards monthly team goal</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex justify-between">
              <span className="text-2xl font-bold">₺{(teamStats.teamRevenue / 1000000).toFixed(1)}M</span>
              <span className="text-gray-500">Target: ₺{(teamStats.teamTarget / 1000000).toFixed(1)}M</span>
            </div>
            <Progress value={targetProgress} className="h-3" />
            <p className="text-sm text-muted-foreground">
              {targetProgress.toFixed(0)}% of monthly target achieved
            </p>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Team Performance */}
        <Card>
          <CardHeader>
            <CardTitle>Team Performance</CardTitle>
            <CardDescription>Individual agent metrics</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {teamMembers.map((member, index) => (
                <div key={member.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="flex items-center justify-center w-6 h-6 rounded-full bg-blue-100 text-blue-600 text-sm font-medium">
                      {index + 1}
                    </div>
                    <Avatar className="h-10 w-10">
                      <AvatarFallback>{member.name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
                    </Avatar>
                    <div>
                      <p className="font-medium">{member.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {member.leads} leads · {member.deals} deals
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">₺{(member.revenue / 1000000).toFixed(1)}M</p>
                    <Badge variant={member.performance >= 100 ? 'success' : 'secondary'}>
                      {member.performance}%
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Sales Pipeline */}
        <Card>
          <CardHeader>
            <CardTitle>Sales Pipeline</CardTitle>
            <CardDescription>Team pipeline by stage</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {pipelineData.map((stage, index) => (
                <div key={stage.stage} className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="font-medium">{stage.stage}</span>
                    <span className="text-muted-foreground">{stage.count} leads · ₺{(stage.value / 1000000).toFixed(0)}M</span>
                  </div>
                  <Progress value={(5 - index) * 20} className="h-2" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Team Management</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-3">
            <Link href="/leads">
              <Button variant="outline">
                <Target className="mr-2 h-4 w-4" />
                Assign Leads
              </Button>
            </Link>
            <Link href="/tasks/team">
              <Button variant="outline">
                <Users className="mr-2 h-4 w-4" />
                Team Tasks
              </Button>
            </Link>
            <Link href="/analytics">
              <Button variant="outline">
                <BarChart3 className="mr-2 h-4 w-4" />
                Performance Reports
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
