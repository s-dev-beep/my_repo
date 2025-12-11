'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { 
  Phone, PhoneCall, PhoneMissed, PhoneOff, Clock, Users,
  TrendingUp, Target, Headphones
} from 'lucide-react'
import Link from 'next/link'

const callStats = {
  totalCalls: 156,
  completedCalls: 142,
  missedCalls: 14,
  avgDuration: 285,
  callsToday: 23,
  conversionRate: 32,
  queueSize: 5,
  avgWaitTime: 45,
}

const agentStatus = [
  { id: 1, name: 'Ayşe Kara', status: 'on_call', calls: 12, duration: '3:45', lead: 'Mehmet Kaya' },
  { id: 2, name: 'Emre Yıldız', status: 'available', calls: 8, duration: '0:00', lead: null },
  { id: 3, name: 'Selin Demir', status: 'on_call', calls: 15, duration: '1:23', lead: 'Ali Şahin' },
  { id: 4, name: 'Can Öztürk', status: 'break', calls: 10, duration: '0:00', lead: null },
  { id: 5, name: 'Deniz Arslan', status: 'available', calls: 6, duration: '0:00', lead: null },
]

const recentCalls = [
  { id: 1, lead: 'Mehmet Kaya', phone: '+90 532 123 4567', duration: '5:20', outcome: 'interested', agent: 'Ayşe Kara', time: '10 min ago' },
  { id: 2, lead: 'Elif Şen', phone: '+90 533 234 5678', duration: '3:00', outcome: 'callback', agent: 'Selin Demir', time: '25 min ago' },
  { id: 3, lead: 'Osman Tan', phone: '+90 534 345 6789', duration: '0:00', outcome: 'no_answer', agent: 'Emre Yıldız', time: '35 min ago' },
  { id: 4, lead: 'Hasan Demir', phone: '+90 535 456 7890', duration: '9:00', outcome: 'qualified', agent: 'Ayşe Kara', time: '1 hour ago' },
]

const statusColors: Record<string, { bg: string; text: string }> = {
  on_call: { bg: 'bg-green-100', text: 'text-green-700' },
  available: { bg: 'bg-blue-100', text: 'text-blue-700' },
  break: { bg: 'bg-yellow-100', text: 'text-yellow-700' },
  offline: { bg: 'bg-gray-100', text: 'text-gray-700' },
}

const outcomeColors: Record<string, string> = {
  interested: 'bg-green-500',
  callback: 'bg-yellow-500',
  no_answer: 'bg-gray-500',
  qualified: 'bg-purple-500',
  not_interested: 'bg-red-500',
}

export default function CallCenterDashboardPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Call Center Dashboard</h1>
          <p className="text-gray-500 mt-1">Monitor call activity and agent performance</p>
        </div>
        <div className="flex gap-3">
          <Link href="/calls">
            <Button variant="outline">
              <Phone className="mr-2 h-4 w-4" />
              Call History
            </Button>
          </Link>
          <Button>
            <Headphones className="mr-2 h-4 w-4" />
            Start Calling
          </Button>
        </div>
      </div>

      {/* Call Stats */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Calls Today</CardTitle>
            <PhoneCall className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{callStats.callsToday}</div>
            <p className="text-xs text-muted-foreground">{callStats.completedCalls} completed</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Queue Size</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{callStats.queueSize}</div>
            <p className="text-xs text-muted-foreground">Avg wait: {callStats.avgWaitTime}s</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Duration</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{Math.floor(callStats.avgDuration / 60)}:{(callStats.avgDuration % 60).toString().padStart(2, '0')}</div>
            <p className="text-xs text-muted-foreground">Per call</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Conversion Rate</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{callStats.conversionRate}%</div>
            <div className="flex items-center text-xs text-green-600">
              <TrendingUp className="h-3 w-3 mr-1" />
              +3% from yesterday
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Agent Status */}
        <Card>
          <CardHeader>
            <CardTitle>Agent Status</CardTitle>
            <CardDescription>Real-time agent activity</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {agentStatus.map((agent) => (
                <div key={agent.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="relative">
                      <Avatar className="h-10 w-10">
                        <AvatarFallback>{agent.name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
                      </Avatar>
                      <div className={`absolute -bottom-1 -right-1 w-4 h-4 rounded-full border-2 border-white ${
                        agent.status === 'on_call' ? 'bg-green-500' :
                        agent.status === 'available' ? 'bg-blue-500' :
                        agent.status === 'break' ? 'bg-yellow-500' : 'bg-gray-500'
                      }`} />
                    </div>
                    <div>
                      <p className="font-medium">{agent.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {agent.status === 'on_call' && agent.lead ? `On call with ${agent.lead}` :
                         agent.status === 'available' ? 'Available' :
                         agent.status === 'break' ? 'On break' : 'Offline'}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <Badge className={`${statusColors[agent.status].bg} ${statusColors[agent.status].text}`}>
                      {agent.status === 'on_call' ? agent.duration : agent.calls + ' calls'}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Recent Calls */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Calls</CardTitle>
            <CardDescription>Latest call activity</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentCalls.map((call) => (
                <div key={call.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full ${outcomeColors[call.outcome]}`} />
                    <div>
                      <p className="font-medium">{call.lead}</p>
                      <p className="text-sm text-muted-foreground">{call.phone}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium">{call.duration !== '0:00' ? call.duration : 'Missed'}</p>
                    <p className="text-xs text-muted-foreground">{call.time}</p>
                  </div>
                </div>
              ))}
            </div>
            <Link href="/calls">
              <Button variant="link" className="w-full mt-4">View all calls</Button>
            </Link>
          </CardContent>
        </Card>
      </div>

      {/* Call Performance */}
      <Card>
        <CardHeader>
          <CardTitle>Today's Performance</CardTitle>
          <CardDescription>Call outcomes breakdown</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-5 gap-4">
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <PhoneCall className="h-8 w-8 text-green-600 mx-auto mb-2" />
              <p className="text-2xl font-bold text-green-600">{callStats.completedCalls}</p>
              <p className="text-sm text-muted-foreground">Completed</p>
            </div>
            <div className="text-center p-4 bg-red-50 rounded-lg">
              <PhoneMissed className="h-8 w-8 text-red-600 mx-auto mb-2" />
              <p className="text-2xl font-bold text-red-600">{callStats.missedCalls}</p>
              <p className="text-sm text-muted-foreground">Missed</p>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <Target className="h-8 w-8 text-purple-600 mx-auto mb-2" />
              <p className="text-2xl font-bold text-purple-600">28</p>
              <p className="text-sm text-muted-foreground">Qualified</p>
            </div>
            <div className="text-center p-4 bg-yellow-50 rounded-lg">
              <Clock className="h-8 w-8 text-yellow-600 mx-auto mb-2" />
              <p className="text-2xl font-bold text-yellow-600">15</p>
              <p className="text-sm text-muted-foreground">Callbacks</p>
            </div>
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <TrendingUp className="h-8 w-8 text-blue-600 mx-auto mb-2" />
              <p className="text-2xl font-bold text-blue-600">{callStats.conversionRate}%</p>
              <p className="text-sm text-muted-foreground">Conversion</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
