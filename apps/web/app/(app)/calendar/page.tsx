'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  ChevronLeft, ChevronRight, Plus, Calendar as CalendarIcon, List,
  Phone, Eye, User, FileText, Clock, Building2
} from 'lucide-react'

const months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
const weekDays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

const events = [
  { id: 1, title: 'Property Viewing - Luxury Villa', type: 'viewing', date: '2024-01-16', time: '10:00', duration: '1h', color: 'bg-blue-500' },
  { id: 2, title: 'Call with Mehmet Kaya', type: 'call', date: '2024-01-16', time: '14:00', duration: '30m', color: 'bg-green-500' },
  { id: 3, title: 'Team Meeting', type: 'meeting', date: '2024-01-17', time: '09:00', duration: '1h', color: 'bg-purple-500' },
  { id: 4, title: 'Contract Signing', type: 'meeting', date: '2024-01-18', time: '11:00', duration: '2h', color: 'bg-orange-500' },
  { id: 5, title: 'Follow-up Call', type: 'call', date: '2024-01-15', time: '15:00', duration: '30m', color: 'bg-green-500' },
]

const generateCalendarDays = (year: number, month: number) => {
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)
  const startPadding = firstDay.getDay()
  const days = []
  for (let i = 0; i < startPadding; i++) {
    days.push({ date: null, isCurrentMonth: false })
  }
  for (let i = 1; i <= lastDay.getDate(); i++) {
    days.push({ date: new Date(year, month, i), isCurrentMonth: true })
  }
  return days
}

export default function CalendarPage() {
  const [currentDate, setCurrentDate] = useState(new Date(2024, 0, 15))
  const [selectedDate, setSelectedDate] = useState<Date | null>(new Date(2024, 0, 16))
  const [view, setView] = useState<'month' | 'week'>('month')

  const calendarDays = generateCalendarDays(currentDate.getFullYear(), currentDate.getMonth())

  const getEventsForDate = (date: Date | null) => {
    if (!date) return []
    const dateStr = date.toISOString().split('T')[0]
    return events.filter(e => e.date === dateStr)
  }

  const selectedDateEvents = selectedDate ? getEventsForDate(selectedDate) : []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Calendar</h1>
          <p className="text-gray-500 mt-1">Manage appointments and events</p>
        </div>
        <div className="flex gap-3">
          <Link href="/calendar/settings">
            <Button variant="outline">Settings</Button>
          </Link>
          <Link href="/calendar/new">
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              New Event
            </Button>
          </Link>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Calendar */}
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>{months[currentDate.getMonth()]} {currentDate.getFullYear()}</CardTitle>
            <div className="flex gap-2">
              <Button variant="outline" size="icon" onClick={() => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1))}>
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button variant="outline" onClick={() => setCurrentDate(new Date())}>Today</Button>
              <Button variant="outline" size="icon" onClick={() => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1))}>
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-7 mb-2">
              {weekDays.map((day) => (
                <div key={day} className="text-center text-sm font-medium text-muted-foreground py-2">
                  {day.slice(0, 3)}
                </div>
              ))}
            </div>
            <div className="grid grid-cols-7 gap-1">
              {calendarDays.map((day, index) => {
                const dayEvents = day.date ? getEventsForDate(day.date) : []
                const isSelected = selectedDate?.toDateString() === day.date?.toDateString()
                return (
                  <div
                    key={index}
                    className={`min-h-24 p-2 border rounded-lg cursor-pointer transition-colors ${
                      !day.isCurrentMonth ? 'bg-gray-50 text-gray-300' :
                      isSelected ? 'bg-blue-50 border-blue-500' : 'hover:bg-gray-50'
                    }`}
                    onClick={() => day.date && setSelectedDate(day.date)}
                  >
                    {day.date && (
                      <>
                        <div className="text-sm font-medium mb-1">{day.date.getDate()}</div>
                        <div className="space-y-1">
                          {dayEvents.slice(0, 2).map((event) => (
                            <div key={event.id} className={`text-xs p-1 rounded truncate ${event.color} text-white`}>
                              {event.time} {event.title}
                            </div>
                          ))}
                          {dayEvents.length > 2 && <div className="text-xs text-muted-foreground">+{dayEvents.length - 2} more</div>}
                        </div>
                      </>
                    )}
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>

        {/* Day Detail */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CalendarIcon className="h-5 w-5" />
              {selectedDate?.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {selectedDateEvents.length > 0 ? (
              <div className="space-y-3">
                {selectedDateEvents.map((event) => (
                  <Link key={event.id} href={`/calendar/${event.id}`}>
                    <div className="p-3 bg-gray-50 rounded-lg hover:bg-gray-100">
                      <div className="flex items-center gap-2 mb-2">
                        <div className={`w-3 h-3 rounded-full ${event.color}`} />
                        <span className="font-medium">{event.title}</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Clock className="h-4 w-4" />
                        {event.time} ({event.duration})
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <CalendarIcon className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                <p>No events scheduled</p>
                <Link href="/calendar/new">
                  <Button variant="outline" className="mt-4">
                    <Plus className="mr-2 h-4 w-4" />
                    Add Event
                  </Button>
                </Link>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
