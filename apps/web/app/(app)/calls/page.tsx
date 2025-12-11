'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Phone, PhoneCall, PhoneMissed, Search, Clock, TrendingUp, PhoneIncoming, PhoneOutgoing } from 'lucide-react'

const calls = [
  { id: 'call-1', leadName: 'Mehmet Kaya', phone: '+90 532 123 4567', agent: 'Ahmet Yılmaz', direction: 'outbound', duration: 320, status: 'completed', outcome: 'interested', time: '10:30 AM' },
  { id: 'call-2', leadName: 'Elif Şen', phone: '+90 533 234 5678', agent: 'Fatma Demir', direction: 'inbound', duration: 180, status: 'completed', outcome: 'callback', time: '11:15 AM' },
  { id: 'call-3', leadName: 'Osman Tan', phone: '+90 534 345 6789', agent: 'Ahmet Yılmaz', direction: 'outbound', duration: 0, status: 'missed', outcome: 'no_answer', time: '11:45 AM' },
  { id: 'call-4', leadName: 'Hasan Demir', phone: '+90 535 456 7890', agent: 'Ahmet Yılmaz', direction: 'outbound', duration: 540, status: 'completed', outcome: 'qualified', time: '2:30 PM' },
  { id: 'call-5', leadName: 'Ayşe Yıldız', phone: '+90 536 567 8901', agent: 'Fatma Demir', direction: 'inbound', duration: 420, status: 'completed', outcome: 'interested', time: '3:15 PM' },
]

const stats = { totalCalls: 156, completed: 142, missed: 14, avgDuration: 285, conversionRate: 32 }

const outcomeColors: Record<string, string> = {
  interested: 'bg-green-500', callback: 'bg-yellow-500', qualified: 'bg-purple-500', no_answer: 'bg-gray-500', not_interested: 'bg-red-500'
}

export default function CallsPage() {
  const [searchQuery, setSearchQuery] = useState('')

  const formatDuration = (seconds: number) => {
    if (seconds === 0) return '-'
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Calls</h1>
          <p className="text-gray-500 mt-1">Call history and logging</p>
        </div>
        <Button><Phone className="mr-2 h-4 w-4" />Log Call</Button>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card><CardContent className="p-4"><div className="flex items-center gap-3"><div className="p-2 bg-blue-100 rounded-lg"><PhoneCall className="h-5 w-5 text-blue-600" /></div><div><p className="text-2xl font-bold">{stats.totalCalls}</p><p className="text-sm text-muted-foreground">Total Calls</p></div></div></CardContent></Card>
        <Card><CardContent className="p-4"><div className="flex items-center gap-3"><div className="p-2 bg-green-100 rounded-lg"><PhoneCall className="h-5 w-5 text-green-600" /></div><div><p className="text-2xl font-bold">{stats.completed}</p><p className="text-sm text-muted-foreground">Completed</p></div></div></CardContent></Card>
        <Card><CardContent className="p-4"><div className="flex items-center gap-3"><div className="p-2 bg-red-100 rounded-lg"><PhoneMissed className="h-5 w-5 text-red-600" /></div><div><p className="text-2xl font-bold">{stats.missed}</p><p className="text-sm text-muted-foreground">Missed</p></div></div></CardContent></Card>
        <Card><CardContent className="p-4"><div className="flex items-center gap-3"><div className="p-2 bg-purple-100 rounded-lg"><TrendingUp className="h-5 w-5 text-purple-600" /></div><div><p className="text-2xl font-bold">{stats.conversionRate}%</p><p className="text-sm text-muted-foreground">Conversion</p></div></div></CardContent></Card>
      </div>

      <Card>
        <CardContent className="p-4">
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input placeholder="Search calls..." className="pl-10" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} />
            </div>
            <Select defaultValue="all"><SelectTrigger className="w-40"><SelectValue placeholder="Status" /></SelectTrigger><SelectContent><SelectItem value="all">All Status</SelectItem><SelectItem value="completed">Completed</SelectItem><SelectItem value="missed">Missed</SelectItem></SelectContent></Select>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Recent Calls</CardTitle></CardHeader>
        <CardContent>
          <div className="space-y-3">
            {calls.map((call) => (
              <Link key={call.id} href={`/calls/${call.id}`}>
                <div className="flex items-center gap-4 p-4 border rounded-lg hover:bg-gray-50">
                  <div className="p-2 bg-gray-100 rounded-lg">
                    {call.direction === 'inbound' ? <PhoneIncoming className="h-5 w-5 text-green-600" /> : <PhoneOutgoing className="h-5 w-5 text-blue-600" />}
                  </div>
                  <Avatar><AvatarFallback>{call.leadName.split(' ').map(n => n[0]).join('')}</AvatarFallback></Avatar>
                  <div className="flex-1">
                    <p className="font-medium">{call.leadName}</p>
                    <p className="text-sm text-muted-foreground">{call.phone} • {call.agent}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="text-right">
                      <p className="text-sm font-medium">{formatDuration(call.duration)}</p>
                      <p className="text-xs text-muted-foreground">{call.time}</p>
                    </div>
                    <Badge className={outcomeColors[call.outcome]}>{call.outcome.replace('_', ' ')}</Badge>
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
