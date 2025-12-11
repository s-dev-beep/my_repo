'use client'

import Link from 'next/link'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ArrowLeft, Edit, Calendar, Clock, MapPin, User, Trash2 } from 'lucide-react'

const event = {
  id: 1,
  title: 'Property Viewing - Luxury Villa',
  type: 'viewing',
  date: '2024-01-16',
  time: '10:00',
  duration: '1 hour',
  location: 'Oran Sitesi 15. Cadde, Ankara',
  description: 'Scheduled property viewing with Hasan Demir for the luxury villa in Oran.',
  attendees: [{ name: 'Hasan Demir', role: 'Client' }, { name: 'Ahmet Yılmaz', role: 'Agent' }],
  property: { id: 'prop-2', title: 'Luxury Villa with Garden' },
}

export default function CalendarEventPage() {
  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/calendar">
            <Button variant="ghost" size="icon"><ArrowLeft className="h-5 w-5" /></Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold">{event.title}</h1>
            <Badge variant="secondary">{event.type}</Badge>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline"><Edit className="mr-2 h-4 w-4" />Edit</Button>
          <Button variant="destructive"><Trash2 className="mr-2 h-4 w-4" />Delete</Button>
        </div>
      </div>

      <Card>
        <CardHeader><CardTitle>Event Details</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-3">
            <Calendar className="h-5 w-5 text-gray-400" />
            <div>
              <p className="font-medium">{new Date(event.date).toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })}</p>
              <p className="text-sm text-muted-foreground">{event.time} ({event.duration})</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <MapPin className="h-5 w-5 text-gray-400" />
            <p>{event.location}</p>
          </div>
          <div className="pt-4 border-t">
            <p className="text-muted-foreground">{event.description}</p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Attendees</CardTitle></CardHeader>
        <CardContent>
          <div className="space-y-3">
            {event.attendees.map((attendee, i) => (
              <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <User className="h-5 w-5 text-gray-400" />
                  <p className="font-medium">{attendee.name}</p>
                </div>
                <Badge variant="outline">{attendee.role}</Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {event.property && (
        <Card>
          <CardHeader><CardTitle>Related Property</CardTitle></CardHeader>
          <CardContent>
            <Link href={`/properties/${event.property.id}`}>
              <div className="p-3 bg-gray-50 rounded-lg hover:bg-gray-100">
                <p className="font-medium">{event.property.title}</p>
              </div>
            </Link>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
