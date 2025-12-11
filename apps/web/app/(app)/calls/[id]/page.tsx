'use client'

import Link from 'next/link'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { ArrowLeft, Phone, Clock, User, Calendar, FileText, PhoneOutgoing } from 'lucide-react'

const call = {
  id: 'call-1',
  leadName: 'Mehmet Kaya',
  leadId: 'lead-1',
  phone: '+90 532 123 4567',
  agent: 'Ahmet Yılmaz',
  direction: 'outbound',
  duration: 320,
  status: 'completed',
  outcome: 'interested',
  date: '2024-01-15',
  time: '10:30 AM',
  notes: 'Discussed property preferences. Client is interested in 3+1 apartments in Çankaya. Budget around 2.5M TRY. Scheduled viewing for next week.',
  recordingUrl: null,
}

const outcomeColors: Record<string, string> = {
  interested: 'bg-green-500', callback: 'bg-yellow-500', qualified: 'bg-purple-500', no_answer: 'bg-gray-500'
}

export default function CallDetailPage() {
  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/calls"><Button variant="ghost" size="icon"><ArrowLeft className="h-5 w-5" /></Button></Link>
          <div>
            <h1 className="text-2xl font-bold">Call Details</h1>
            <div className="flex items-center gap-2 mt-1">
              <Badge className={outcomeColors[call.outcome]}>{call.outcome}</Badge>
              <Badge variant="secondary">{call.direction}</Badge>
            </div>
          </div>
        </div>
        <Button><Phone className="mr-2 h-4 w-4" />Call Back</Button>
      </div>

      <Card>
        <CardHeader><CardTitle>Contact</CardTitle></CardHeader>
        <CardContent>
          <Link href={`/leads/${call.leadId}`}>
            <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100">
              <Avatar className="h-12 w-12"><AvatarFallback>{call.leadName.split(' ').map(n => n[0]).join('')}</AvatarFallback></Avatar>
              <div>
                <p className="font-medium text-lg">{call.leadName}</p>
                <p className="text-muted-foreground">{call.phone}</p>
              </div>
            </div>
          </Link>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Call Information</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <div className="grid md:grid-cols-2 gap-4">
            <div className="flex items-center gap-3"><Calendar className="h-5 w-5 text-gray-400" /><div><p className="text-sm text-muted-foreground">Date</p><p className="font-medium">{call.date}</p></div></div>
            <div className="flex items-center gap-3"><Clock className="h-5 w-5 text-gray-400" /><div><p className="text-sm text-muted-foreground">Time</p><p className="font-medium">{call.time}</p></div></div>
            <div className="flex items-center gap-3"><Clock className="h-5 w-5 text-gray-400" /><div><p className="text-sm text-muted-foreground">Duration</p><p className="font-medium">{formatDuration(call.duration)}</p></div></div>
            <div className="flex items-center gap-3"><User className="h-5 w-5 text-gray-400" /><div><p className="text-sm text-muted-foreground">Agent</p><p className="font-medium">{call.agent}</p></div></div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Notes</CardTitle></CardHeader>
        <CardContent><p className="text-muted-foreground">{call.notes}</p></CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Quick Actions</CardTitle></CardHeader>
        <CardContent className="flex gap-3">
          <Button variant="outline"><Phone className="mr-2 h-4 w-4" />Call Again</Button>
          <Button variant="outline"><FileText className="mr-2 h-4 w-4" />Create Task</Button>
          <Link href={`/leads/${call.leadId}`}><Button variant="outline"><User className="mr-2 h-4 w-4" />View Lead</Button></Link>
        </CardContent>
      </Card>
    </div>
  )
}
