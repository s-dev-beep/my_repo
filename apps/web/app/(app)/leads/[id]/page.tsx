'use client'

import { useParams } from 'next/navigation'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Separator } from '@/components/ui/separator'
import { 
  ArrowLeft, Edit, Phone, Mail, MapPin, Building2, Calendar,
  DollarSign, User, Clock, Target, CheckSquare, MessageSquare, FileText
} from 'lucide-react'

// Mock lead data
const mockLead = {
  id: 'lead-1',
  name: 'Mehmet Kaya',
  email: 'mehmet.kaya@email.com',
  phone: '+90 532 123 4567',
  status: 'qualified',
  source: 'Website',
  budget: 2000000,
  preferredLocation: 'Çankaya',
  propertyType: 'Apartment',
  bedrooms: '3+1',
  notes: 'Looking for a modern apartment near metro station. Prefers new construction with balcony and parking.',
  assignedTo: { id: 'user-1', name: 'Ahmet Yılmaz', avatar: '' },
  createdAt: '2024-01-15T10:30:00Z',
  updatedAt: '2024-01-15T14:20:00Z',
  lastContact: '2024-01-15T14:20:00Z',
}

const activities = [
  { id: 1, type: 'call', title: 'Phone call', description: 'Discussed property preferences', user: 'Ahmet Yılmaz', time: '2 hours ago' },
  { id: 2, type: 'email', title: 'Email sent', description: 'Sent property listings', user: 'Ahmet Yılmaz', time: '1 day ago' },
  { id: 3, type: 'status', title: 'Status changed', description: 'New → Contacted', user: 'System', time: '2 days ago' },
  { id: 4, type: 'note', title: 'Note added', description: 'Client prefers morning viewings', user: 'Ahmet Yılmaz', time: '3 days ago' },
]

const tasks = [
  { id: 'task-1', title: 'Schedule property viewing', dueDate: '2024-01-17', status: 'pending', priority: 'high' },
  { id: 'task-2', title: 'Send comparison report', dueDate: '2024-01-18', status: 'pending', priority: 'medium' },
  { id: 'task-3', title: 'Follow-up call', dueDate: '2024-01-20', status: 'pending', priority: 'low' },
]

const matchedProperties = [
  { id: 'prop-1', title: 'Modern 3+1 Apartment in Çankaya', price: 2500000, score: 95 },
  { id: 'prop-2', title: '2+1 Apartment Near Metro', price: 1800000, score: 82 },
  { id: 'prop-3', title: 'Penthouse with Terrace', price: 6500000, score: 65 },
]

const statusConfig: Record<string, { label: string; color: string }> = {
  new: { label: 'New', color: 'bg-blue-500' },
  contacted: { label: 'Contacted', color: 'bg-yellow-500' },
  qualified: { label: 'Qualified', color: 'bg-purple-500' },
  proposal: { label: 'Proposal', color: 'bg-orange-500' },
  negotiation: { label: 'Negotiation', color: 'bg-pink-500' },
  won: { label: 'Won', color: 'bg-green-500' },
  lost: { label: 'Lost', color: 'bg-red-500' },
}

const activityIcons: Record<string, any> = {
  call: Phone,
  email: Mail,
  status: CheckSquare,
  note: MessageSquare,
}

export default function LeadDetailPage() {
  const params = useParams()
  const lead = mockLead // In real app, fetch by params.id

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/leads">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-5 w-5" />
            </Button>
          </Link>
          <div className="flex items-center gap-4">
            <Avatar className="h-16 w-16">
              <AvatarFallback className="text-xl">{lead.name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
            </Avatar>
            <div>
              <div className="flex items-center gap-3">
                <h1 className="text-2xl font-bold">{lead.name}</h1>
                <Badge className={statusConfig[lead.status].color}>
                  {statusConfig[lead.status].label}
                </Badge>
              </div>
              <p className="text-muted-foreground">Lead from {lead.source}</p>
            </div>
          </div>
        </div>
        <div className="flex gap-3">
          <Link href={`/matching/${lead.id}`}>
            <Button variant="outline">
              <Target className="mr-2 h-4 w-4" />
              Find Matches
            </Button>
          </Link>
          <Link href={`/leads/${lead.id}/edit`}>
            <Button>
              <Edit className="mr-2 h-4 w-4" />
              Edit Lead
            </Button>
          </Link>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          <Tabs defaultValue="overview">
            <TabsList>
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="activity">Activity</TabsTrigger>
              <TabsTrigger value="tasks">Tasks</TabsTrigger>
              <TabsTrigger value="properties">Matched Properties</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-6 mt-6">
              {/* Contact Info */}
              <Card>
                <CardHeader>
                  <CardTitle>Contact Information</CardTitle>
                </CardHeader>
                <CardContent className="grid md:grid-cols-2 gap-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-blue-100 rounded-lg">
                      <Mail className="h-5 w-5 text-blue-600" />
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Email</p>
                      <p className="font-medium">{lead.email}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-green-100 rounded-lg">
                      <Phone className="h-5 w-5 text-green-600" />
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Phone</p>
                      <p className="font-medium">{lead.phone}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Requirements */}
              <Card>
                <CardHeader>
                  <CardTitle>Property Requirements</CardTitle>
                </CardHeader>
                <CardContent className="grid md:grid-cols-2 gap-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-purple-100 rounded-lg">
                      <DollarSign className="h-5 w-5 text-purple-600" />
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Budget</p>
                      <p className="font-medium">₺{lead.budget.toLocaleString()}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-orange-100 rounded-lg">
                      <MapPin className="h-5 w-5 text-orange-600" />
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Preferred Location</p>
                      <p className="font-medium">{lead.preferredLocation}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-cyan-100 rounded-lg">
                      <Building2 className="h-5 w-5 text-cyan-600" />
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Property Type</p>
                      <p className="font-medium">{lead.propertyType}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-pink-100 rounded-lg">
                      <Building2 className="h-5 w-5 text-pink-600" />
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Bedrooms</p>
                      <p className="font-medium">{lead.bedrooms}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Notes */}
              <Card>
                <CardHeader>
                  <CardTitle>Notes</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">{lead.notes}</p>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="activity" className="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle>Activity Timeline</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    {activities.map((activity) => {
                      const Icon = activityIcons[activity.type] || FileText
                      return (
                        <div key={activity.id} className="flex gap-4">
                          <div className="p-2 bg-gray-100 rounded-lg h-fit">
                            <Icon className="h-4 w-4 text-gray-600" />
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center justify-between">
                              <p className="font-medium">{activity.title}</p>
                              <span className="text-sm text-muted-foreground">{activity.time}</span>
                            </div>
                            <p className="text-sm text-muted-foreground">{activity.description}</p>
                            <p className="text-sm text-muted-foreground mt-1">by {activity.user}</p>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="tasks" className="mt-6">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                  <CardTitle>Related Tasks</CardTitle>
                  <Link href="/tasks/new">
                    <Button size="sm">Add Task</Button>
                  </Link>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {tasks.map((task) => (
                      <div key={task.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center gap-3">
                          <div className={`w-2 h-2 rounded-full ${
                            task.priority === 'high' ? 'bg-red-500' :
                            task.priority === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                          }`} />
                          <div>
                            <p className="font-medium">{task.title}</p>
                            <p className="text-sm text-muted-foreground">Due: {task.dueDate}</p>
                          </div>
                        </div>
                        <Badge variant="outline">{task.status}</Badge>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="properties" className="mt-6">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                  <CardTitle>Matched Properties</CardTitle>
                  <Link href={`/matching/${lead.id}`}>
                    <Button size="sm">View All Matches</Button>
                  </Link>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {matchedProperties.map((property) => (
                      <Link key={property.id} href={`/properties/${property.id}`}>
                        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer">
                          <div>
                            <p className="font-medium">{property.title}</p>
                            <p className="text-sm text-muted-foreground">₺{property.price.toLocaleString()}</p>
                          </div>
                          <Badge variant={property.score >= 90 ? 'default' : property.score >= 70 ? 'secondary' : 'outline'}>
                            {property.score}% match
                          </Badge>
                        </div>
                      </Link>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Assignment */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Assigned Agent</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-3">
                <Avatar>
                  <AvatarFallback>{lead.assignedTo.name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
                </Avatar>
                <div>
                  <p className="font-medium">{lead.assignedTo.name}</p>
                  <p className="text-sm text-muted-foreground">Sales Agent</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Timeline */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Timeline</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-3">
                <Calendar className="h-4 w-4 text-muted-foreground" />
                <div>
                  <p className="text-sm text-muted-foreground">Created</p>
                  <p className="font-medium">{new Date(lead.createdAt).toLocaleDateString()}</p>
                </div>
              </div>
              <Separator />
              <div className="flex items-center gap-3">
                <Clock className="h-4 w-4 text-muted-foreground" />
                <div>
                  <p className="text-sm text-muted-foreground">Last Contact</p>
                  <p className="font-medium">{new Date(lead.lastContact).toLocaleDateString()}</p>
                </div>
              </div>
              <Separator />
              <div className="flex items-center gap-3">
                <Edit className="h-4 w-4 text-muted-foreground" />
                <div>
                  <p className="text-sm text-muted-foreground">Last Updated</p>
                  <p className="font-medium">{new Date(lead.updatedAt).toLocaleDateString()}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button variant="outline" className="w-full justify-start">
                <Phone className="mr-2 h-4 w-4" />
                Log Call
              </Button>
              <Button variant="outline" className="w-full justify-start">
                <Mail className="mr-2 h-4 w-4" />
                Send Email
              </Button>
              <Button variant="outline" className="w-full justify-start">
                <CheckSquare className="mr-2 h-4 w-4" />
                Create Task
              </Button>
              <Button variant="outline" className="w-full justify-start">
                <Calendar className="mr-2 h-4 w-4" />
                Schedule Meeting
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
