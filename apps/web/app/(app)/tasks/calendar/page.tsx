'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  ArrowLeft, ChevronLeft, ChevronRight, Plus, Calendar, List,
  Phone, Eye, User, FileText, Clock
} from 'lucide-react'

// Generate calendar days
const generateCalendarDays = (year: number, month: number) => {
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)
  const startPadding = firstDay.getDay()
  
  const days = []
  // Previous month padding
  for (let i = 0; i < startPadding; i++) {
    days.push({ date: null, isCurrentMonth: false })
  }
  // Current month days
  for (let i = 1; i <= lastDay.getDate(); i++) {
    days.push({ date: new Date(year, month, i), isCurrentMonth: true })
  }
  return days
}

// Mock tasks with dates
const tasks = [
  { id: 'task-1', title: 'Call Mehmet Kaya', type: 'call', date: '2024-01-16', time: '10:00', priority: 'high' },
  { id: 'task-2', title: 'Property Viewing', type: 'viewing', date: '2024-01-16', time: '14:00', priority: 'high' },
  { id: 'task-3', title: 'Prepare Proposal', type: 'document', date: '2024-01-15', time: '18:00', priority: 'urgent' },
  { id: 'task-4', title: 'Team Meeting', type: 'meeting', date: '2024-01-17', time: '09:00', priority: 'medium' },
  { id: 'task-5', title: 'Follow up Ayşe', type: 'follow_up', date: '2024-01-18', time: '11:00', priority: 'medium' },
  { id: 'task-6', title: 'Contract Review', type: 'meeting', date: '2024-01-16', time: '11:00', priority: 'urgent' },
]

const priorityColors: Record<string, string> = {
  urgent: 'bg-red-500',
  high: 'bg-orange-500',
  medium: 'bg-yellow-500',
  low: 'bg-green-500',
}

const typeIcons: Record<string, any> = {
  call: Phone,
  viewing: Eye,
  meeting: User,
  document: FileText,
  follow_up: Clock,
}

const months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

export default function TasksCalendarPage() {
  const [currentDate, setCurrentDate] = useState(new Date(2024, 0, 15)) // January 2024
  const [selectedDate, setSelectedDate] = useState<Date | null>(null)

  const calendarDays = generateCalendarDays(currentDate.getFullYear(), currentDate.getMonth())

  const getTasksForDate = (date: Date | null) => {
    if (!date) return []
    const dateStr = date.toISOString().split('T')[0]
    return tasks.filter(t => t.date === dateStr)
  }

  const goToPreviousMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1))
  }

  const goToNextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1))
  }

  const selectedDateTasks = selectedDate ? getTasksForDate(selectedDate) : []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/tasks">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-5 w-5" />
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold">Task Calendar</h1>
            <p className="text-muted-foreground">View tasks by date</p>
          </div>
        </div>
        <div className="flex gap-3">
          <Link href="/tasks">
            <Button variant="outline">
              <List className="mr-2 h-4 w-4" />
              List View
            </Button>
          </Link>
          <Link href="/tasks/new">
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              New Task
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
              <Button variant="outline" size="icon" onClick={goToPreviousMonth}>
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="icon" onClick={goToNextMonth}>
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {/* Week days header */}
            <div className="grid grid-cols-7 mb-2">
              {weekDays.map((day) => (
                <div key={day} className="text-center text-sm font-medium text-muted-foreground py-2">
                  {day}
                </div>
              ))}
            </div>
            {/* Calendar grid */}
            <div className="grid grid-cols-7 gap-1">
              {calendarDays.map((day, index) => {
                const dayTasks = day.date ? getTasksForDate(day.date) : []
                const isToday = day.date?.toDateString() === new Date().toDateString()
                const isSelected = selectedDate?.toDateString() === day.date?.toDateString()
                
                return (
                  <div
                    key={index}
                    className={`min-h-24 p-2 border rounded-lg cursor-pointer transition-colors ${
                      !day.isCurrentMonth ? 'bg-gray-50 text-gray-300' :
                      isSelected ? 'bg-blue-50 border-blue-500' :
                      isToday ? 'bg-yellow-50 border-yellow-300' : 'hover:bg-gray-50'
                    }`}
                    onClick={() => day.date && setSelectedDate(day.date)}
                  >
                    {day.date && (
                      <>
                        <div className={`text-sm font-medium mb-1 ${isToday ? 'text-blue-600' : ''}`}>
                          {day.date.getDate()}
                        </div>
                        <div className="space-y-1">
                          {dayTasks.slice(0, 2).map((task) => (
                            <div
                              key={task.id}
                              className={`text-xs p-1 rounded truncate ${priorityColors[task.priority]} text-white`}
                            >
                              {task.title}
                            </div>
                          ))}
                          {dayTasks.length > 2 && (
                            <div className="text-xs text-muted-foreground">
                              +{dayTasks.length - 2} more
                            </div>
                          )}
                        </div>
                      </>
                    )}
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>

        {/* Selected Day Tasks */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              {selectedDate ? (
                <span>{selectedDate.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}</span>
              ) : (
                <span>Select a Date</span>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {selectedDate ? (
              selectedDateTasks.length > 0 ? (
                <div className="space-y-3">
                  {selectedDateTasks.map((task) => {
                    const Icon = typeIcons[task.type] || Calendar
                    return (
                      <Link key={task.id} href={`/tasks/${task.id}`}>
                        <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100">
                          <div className="p-2 bg-white rounded-lg">
                            <Icon className="h-4 w-4 text-gray-600" />
                          </div>
                          <div className="flex-1">
                            <p className="font-medium text-sm">{task.title}</p>
                            <div className="flex items-center gap-2 mt-1">
                              <Clock className="h-3 w-3 text-gray-400" />
                              <span className="text-xs text-muted-foreground">{task.time}</span>
                            </div>
                          </div>
                          <Badge className={priorityColors[task.priority]}>{task.priority}</Badge>
                        </div>
                      </Link>
                    )
                  })}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <Calendar className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                  <p>No tasks scheduled</p>
                  <Link href="/tasks/new">
                    <Button variant="outline" className="mt-4">
                      <Plus className="mr-2 h-4 w-4" />
                      Add Task
                    </Button>
                  </Link>
                </div>
              )
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <p>Click on a date to view tasks</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
