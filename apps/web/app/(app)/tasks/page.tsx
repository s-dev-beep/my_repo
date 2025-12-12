'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Checkbox } from '@/components/ui/checkbox'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { 
  CheckSquare, Plus, Search, Filter, Calendar, Clock, 
  User, Phone, Eye, Building2, FileText, MoreVertical
} from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'

const tasks = [
  { id: 'task-1', title: 'Call Mehmet Kaya for follow-up', type: 'call', priority: 'high', status: 'pending', dueDate: '2024-01-16', assignedTo: 'Ahmet Yılmaz', lead: 'Mehmet Kaya' },
  { id: 'task-2', title: 'Property viewing - Luxury Villa', type: 'viewing', priority: 'high', status: 'pending', dueDate: '2024-01-16', assignedTo: 'Ahmet Yılmaz', lead: 'Hasan Demir', property: 'Luxury Villa' },
  { id: 'task-3', title: 'Prepare proposal for Ali Koç', type: 'document', priority: 'urgent', status: 'in_progress', dueDate: '2024-01-15', assignedTo: 'Fatma Demir', lead: 'Ali Koç' },
  { id: 'task-4', title: 'Team meeting - Weekly review', type: 'meeting', priority: 'medium', status: 'pending', dueDate: '2024-01-17', assignedTo: 'Ahmet Yılmaz' },
  { id: 'task-5', title: 'Follow up with Ayşe Yıldız', type: 'follow_up', priority: 'medium', status: 'completed', dueDate: '2024-01-15', assignedTo: 'Fatma Demir', lead: 'Ayşe Yıldız' },
  { id: 'task-6', title: 'Update property photos', type: 'other', priority: 'low', status: 'pending', dueDate: '2024-01-18', assignedTo: 'Ali Öztürk', property: 'Penthouse' },
  { id: 'task-7', title: 'Call Elif Şen - New lead', type: 'call', priority: 'high', status: 'pending', dueDate: '2024-01-15', assignedTo: 'Fatma Demir', lead: 'Elif Şen' },
  { id: 'task-8', title: 'Contract review meeting', type: 'meeting', priority: 'urgent', status: 'pending', dueDate: '2024-01-16', assignedTo: 'Ahmet Yılmaz', lead: 'Ali Koç' },
]

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

const typeIcons: Record<string, any> = {
  call: Phone,
  viewing: Eye,
  meeting: User,
  document: FileText,
  follow_up: Clock,
  other: CheckSquare,
}

const stats = [
  { label: 'Total Tasks', value: tasks.length },
  { label: 'Pending', value: tasks.filter(t => t.status === 'pending').length },
  { label: 'In Progress', value: tasks.filter(t => t.status === 'in_progress').length },
  { label: 'Completed', value: tasks.filter(t => t.status === 'completed').length },
]

export default function TasksPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [priorityFilter, setPriorityFilter] = useState<string>('all')

  const filteredTasks = tasks.filter(task => {
    const matchesSearch = task.title.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesStatus = statusFilter === 'all' || task.status === statusFilter
    const matchesPriority = priorityFilter === 'all' || task.priority === priorityFilter
    return matchesSearch && matchesStatus && matchesPriority
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Tasks</h1>
          <p className="text-gray-500 mt-1">Manage and track your tasks</p>
        </div>
        <div className="flex gap-3">
          <Link href="/tasks/calendar">
            <Button variant="outline">
              <Calendar className="mr-2 h-4 w-4" />
              Calendar View
            </Button>
          </Link>
          <Link href="/tasks/team">
            <Button variant="outline">
              <User className="mr-2 h-4 w-4" />
              Team Tasks
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

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.label}>
            <CardContent className="p-4">
              <p className="text-sm text-muted-foreground">{stat.label}</p>
              <p className="text-2xl font-bold">{stat.value}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search tasks..."
                className="pl-10"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-40">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="in_progress">In Progress</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
              </SelectContent>
            </Select>
            <Select value={priorityFilter} onValueChange={setPriorityFilter}>
              <SelectTrigger className="w-40">
                <SelectValue placeholder="Priority" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Priority</SelectItem>
                <SelectItem value="urgent">Urgent</SelectItem>
                <SelectItem value="high">High</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="low">Low</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Tasks List */}
      <Card>
        <CardHeader>
          <CardTitle>All Tasks ({filteredTasks.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {filteredTasks.map((task) => {
              const TypeIcon = typeIcons[task.type] || CheckSquare
              return (
                <div key={task.id} className="flex items-center gap-4 p-4 border rounded-lg hover:bg-gray-50">
                  <Checkbox />
                  <div className={`p-2 rounded-lg bg-gray-100`}>
                    <TypeIcon className="h-5 w-5 text-gray-600" />
                  </div>
                  <div className="flex-1">
                    <Link href={`/tasks/${task.id}`}>
                      <p className="font-medium hover:text-blue-600">{task.title}</p>
                    </Link>
                    <div className="flex items-center gap-4 mt-1 text-sm text-muted-foreground">
                      {task.lead && <span>Lead: {task.lead}</span>}
                      {task.property && <span>Property: {task.property}</span>}
                      <span>Assigned: {task.assignedTo}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="flex items-center gap-2">
                      <Clock className="h-4 w-4 text-gray-400" />
                      <span className="text-sm">{task.dueDate}</span>
                    </div>
                    <Badge className={priorityColors[task.priority]}>{task.priority}</Badge>
                    <Badge className={statusColors[task.status]}>{task.status.replace('_', ' ')}</Badge>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon">
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem>Mark Complete</DropdownMenuItem>
                        <DropdownMenuItem>Edit Task</DropdownMenuItem>
                        <DropdownMenuItem>Reschedule</DropdownMenuItem>
                        <DropdownMenuItem className="text-red-600">Delete</DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
