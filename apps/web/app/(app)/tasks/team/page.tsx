'use client'

import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Progress } from '@/components/ui/progress'
import { 
  ArrowLeft, Users, CheckSquare, Clock, AlertCircle, Plus,
  Phone, Eye, User, FileText
} from 'lucide-react'

const teamMembers = [
  { 
    id: 'user-1', 
    name: 'Ahmet Yılmaz', 
    role: 'Sales Agent',
    tasks: { total: 12, completed: 8, pending: 3, overdue: 1 },
    avatar: null
  },
  { 
    id: 'user-2', 
    name: 'Fatma Demir', 
    role: 'Sales Agent',
    tasks: { total: 10, completed: 7, pending: 3, overdue: 0 },
    avatar: null
  },
  { 
    id: 'user-3', 
    name: 'Ali Öztürk', 
    role: 'Team Lead',
    tasks: { total: 8, completed: 6, pending: 2, overdue: 0 },
    avatar: null
  },
  { 
    id: 'user-4', 
    name: 'Zeynep Arslan', 
    role: 'Admin',
    tasks: { total: 5, completed: 5, pending: 0, overdue: 0 },
    avatar: null
  },
]

const recentTeamTasks = [
  { id: 'task-1', title: 'Call Mehmet Kaya', assignee: 'Ahmet Yılmaz', type: 'call', priority: 'high', status: 'pending', dueDate: '2024-01-16' },
  { id: 'task-2', title: 'Property Viewing', assignee: 'Ahmet Yılmaz', type: 'viewing', priority: 'high', status: 'pending', dueDate: '2024-01-16' },
  { id: 'task-3', title: 'Prepare Proposal', assignee: 'Fatma Demir', type: 'document', priority: 'urgent', status: 'in_progress', dueDate: '2024-01-15' },
  { id: 'task-4', title: 'Team Meeting', assignee: 'Ali Öztürk', type: 'meeting', priority: 'medium', status: 'pending', dueDate: '2024-01-17' },
  { id: 'task-5', title: 'Follow up Ayşe', assignee: 'Fatma Demir', type: 'follow_up', priority: 'medium', status: 'completed', dueDate: '2024-01-15' },
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
}

const typeIcons: Record<string, any> = {
  call: Phone,
  viewing: Eye,
  meeting: User,
  document: FileText,
  follow_up: Clock,
}

const stats = {
  totalTasks: 35,
  completed: 26,
  pending: 8,
  overdue: 1,
}

export default function TeamTasksPage() {
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
            <h1 className="text-2xl font-bold">Team Tasks</h1>
            <p className="text-muted-foreground">Monitor team workload and assignments</p>
          </div>
        </div>
        <Link href="/tasks/new">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Assign Task
          </Button>
        </Link>
      </div>

      {/* Team Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <CheckSquare className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.totalTasks}</p>
                <p className="text-sm text-muted-foreground">Total Tasks</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <CheckSquare className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.completed}</p>
                <p className="text-sm text-muted-foreground">Completed</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <Clock className="h-5 w-5 text-yellow-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.pending}</p>
                <p className="text-sm text-muted-foreground">Pending</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-red-100 rounded-lg">
                <AlertCircle className="h-5 w-5 text-red-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.overdue}</p>
                <p className="text-sm text-muted-foreground">Overdue</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Team Members */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Team Workload
          </CardTitle>
          <CardDescription>Task distribution by team member</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {teamMembers.map((member) => {
              const completionRate = (member.tasks.completed / member.tasks.total) * 100
              return (
                <div key={member.id} className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Avatar>
                        <AvatarFallback>{member.name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
                      </Avatar>
                      <div>
                        <p className="font-medium">{member.name}</p>
                        <p className="text-sm text-muted-foreground">{member.role}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <span className="text-lg font-bold">{member.tasks.completed}</span>
                        <span className="text-muted-foreground">/{member.tasks.total}</span>
                      </div>
                      <div className="flex gap-1">
                        {member.tasks.overdue > 0 && (
                          <Badge variant="destructive">{member.tasks.overdue} overdue</Badge>
                        )}
                        <Badge variant="secondary">{member.tasks.pending} pending</Badge>
                      </div>
                    </div>
                  </div>
                  <Progress value={completionRate} className="h-2" />
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Recent Team Tasks */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Team Tasks</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {recentTeamTasks.map((task) => {
              const Icon = typeIcons[task.type] || CheckSquare
              return (
                <Link key={task.id} href={`/tasks/${task.id}`}>
                  <div className="flex items-center gap-4 p-4 border rounded-lg hover:bg-gray-50">
                    <div className="p-2 bg-gray-100 rounded-lg">
                      <Icon className="h-5 w-5 text-gray-600" />
                    </div>
                    <div className="flex-1">
                      <p className="font-medium">{task.title}</p>
                      <p className="text-sm text-muted-foreground">Assigned to: {task.assignee}</p>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-sm text-muted-foreground">{task.dueDate}</span>
                      <Badge className={priorityColors[task.priority]}>{task.priority}</Badge>
                      <Badge className={statusColors[task.status]}>{task.status.replace('_', ' ')}</Badge>
                    </div>
                  </div>
                </Link>
              )
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
