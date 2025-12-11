'use client'

import { useParams } from 'next/navigation'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Separator } from '@/components/ui/separator'
import { 
  ArrowLeft, Edit, Calendar, Clock, User, Phone, Building2, 
  CheckSquare, MessageSquare, FileText, Trash2, Check
} from 'lucide-react'

// Mock task data
const mockTask = {
  id: 'task-1',
  title: 'Call Mehmet Kaya for follow-up',
  description: 'Discuss property preferences and schedule a viewing for the Çankaya apartment. Client showed interest in 3+1 apartments with balcony.',
  type: 'call',
  priority: 'high',
  status: 'pending',
  dueDate: '2024-01-16T10:00:00',
  assignedTo: { id: 'user-1', name: 'Ahmet Yılmaz' },
  lead: { id: 'lead-1', name: 'Mehmet Kaya', phone: '+90 532 123 4567' },
  property: { id: 'prop-1', title: 'Modern 3+1 Apartment in Çankaya' },
  createdAt: '2024-01-15T08:00:00',
  updatedAt: '2024-01-15T08:00:00',
  notes: [
    { id: 1, user: 'Ahmet Yılmaz', text: 'Client prefers morning calls', time: '2024-01-15T08:30:00' },
    { id: 2, user: 'System', text: 'Task created', time: '2024-01-15T08:00:00' },
  ],
}

const priorityColors: Record<string, string> = {
  urgent: 'bg-red-500',
  high: 'bg-orange-500',
  medium: 'bg-yellow-500',
  low: 'bg-green-500',
}

const statusColors: Record<string, string> = {
  pending: 'bg-gray-500',
  in_progress: 'bg-blue-500',
  completed: 'bg-green-500',
  cancelled: 'bg-red-500',
}

export default function TaskDetailPage() {
  const params = useParams()
  const task = mockTask

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/tasks">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-5 w-5" />
            </Button>
          </Link>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold">{task.title}</h1>
            </div>
            <div className="flex items-center gap-2 mt-1">
              <Badge className={priorityColors[task.priority]}>{task.priority}</Badge>
              <Badge className={statusColors[task.status]}>{task.status}</Badge>
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Edit className="mr-2 h-4 w-4" />
            Edit
          </Button>
          <Button>
            <Check className="mr-2 h-4 w-4" />
            Mark Complete
          </Button>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="md:col-span-2 space-y-6">
          {/* Description */}
          <Card>
            <CardHeader>
              <CardTitle>Description</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">{task.description}</p>
            </CardContent>
          </Card>

          {/* Related Items */}
          <Card>
            <CardHeader>
              <CardTitle>Related Items</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {task.lead && (
                <Link href={`/leads/${task.lead.id}`}>
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-blue-100 rounded-lg">
                        <User className="h-5 w-5 text-blue-600" />
                      </div>
                      <div>
                        <p className="font-medium">{task.lead.name}</p>
                        <p className="text-sm text-muted-foreground">{task.lead.phone}</p>
                      </div>
                    </div>
                    <Badge variant="outline">Lead</Badge>
                  </div>
                </Link>
              )}
              {task.property && (
                <Link href={`/properties/${task.property.id}`}>
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-green-100 rounded-lg">
                        <Building2 className="h-5 w-5 text-green-600" />
                      </div>
                      <div>
                        <p className="font-medium">{task.property.title}</p>
                      </div>
                    </div>
                    <Badge variant="outline">Property</Badge>
                  </div>
                </Link>
              )}
            </CardContent>
          </Card>

          {/* Notes/Activity */}
          <Card>
            <CardHeader>
              <CardTitle>Activity</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {task.notes.map((note) => (
                  <div key={note.id} className="flex gap-3">
                    <div className="p-2 bg-gray-100 rounded-lg h-fit">
                      <MessageSquare className="h-4 w-4 text-gray-600" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <p className="font-medium text-sm">{note.user}</p>
                        <span className="text-xs text-muted-foreground">
                          {new Date(note.time).toLocaleString()}
                        </span>
                      </div>
                      <p className="text-sm text-muted-foreground">{note.text}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Task Details */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="text-sm text-muted-foreground">Due Date</p>
                <div className="flex items-center gap-2 mt-1">
                  <Calendar className="h-4 w-4 text-gray-400" />
                  <p className="font-medium">{new Date(task.dueDate).toLocaleDateString()}</p>
                </div>
              </div>
              <Separator />
              <div>
                <p className="text-sm text-muted-foreground">Due Time</p>
                <div className="flex items-center gap-2 mt-1">
                  <Clock className="h-4 w-4 text-gray-400" />
                  <p className="font-medium">{new Date(task.dueDate).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>
                </div>
              </div>
              <Separator />
              <div>
                <p className="text-sm text-muted-foreground">Type</p>
                <div className="flex items-center gap-2 mt-1">
                  <Phone className="h-4 w-4 text-gray-400" />
                  <p className="font-medium capitalize">{task.type}</p>
                </div>
              </div>
              <Separator />
              <div>
                <p className="text-sm text-muted-foreground">Created</p>
                <p className="font-medium mt-1">{new Date(task.createdAt).toLocaleDateString()}</p>
              </div>
            </CardContent>
          </Card>

          {/* Assigned To */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Assigned To</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-3">
                <Avatar>
                  <AvatarFallback>{task.assignedTo.name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
                </Avatar>
                <div>
                  <p className="font-medium">{task.assignedTo.name}</p>
                  <p className="text-sm text-muted-foreground">Sales Agent</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button className="w-full" variant="default">
                <Check className="mr-2 h-4 w-4" />
                Complete Task
              </Button>
              <Button className="w-full" variant="outline">
                <Clock className="mr-2 h-4 w-4" />
                Reschedule
              </Button>
              <Button className="w-full text-red-600 hover:text-red-700" variant="outline">
                <Trash2 className="mr-2 h-4 w-4" />
                Delete Task
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
