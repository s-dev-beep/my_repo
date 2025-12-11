'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { 
  Users, Plus, Search, Filter, Download, Upload, Phone, Mail,
  MoreVertical, Eye, Edit, Trash2, Target
} from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'

const leads = [
  { id: 'lead-1', name: 'Mehmet Kaya', email: 'mehmet.kaya@email.com', phone: '+90 532 123 4567', status: 'new', source: 'Website', budget: 2000000, location: 'Çankaya', assignedTo: 'Ahmet Yılmaz', createdAt: '2024-01-15' },
  { id: 'lead-2', name: 'Ayşe Yıldız', email: 'ayse.yildiz@email.com', phone: '+90 533 234 5678', status: 'contacted', source: 'Referral', budget: 3500000, location: 'Kızılay', assignedTo: 'Fatma Demir', createdAt: '2024-01-14' },
  { id: 'lead-3', name: 'Hasan Demir', email: 'hasan.demir@email.com', phone: '+90 534 345 6789', status: 'qualified', source: 'Social Media', budget: 5000000, location: 'Oran', assignedTo: 'Ahmet Yılmaz', createdAt: '2024-01-13' },
  { id: 'lead-4', name: 'Fatma Çelik', email: 'fatma.celik@email.com', phone: '+90 535 456 7890', status: 'proposal', source: 'Walk-in', budget: 1500000, location: 'Batıkent', assignedTo: 'Ali Öztürk', createdAt: '2024-01-12' },
  { id: 'lead-5', name: 'Ali Koç', email: 'ali.koc@email.com', phone: '+90 536 567 8901', status: 'negotiation', source: 'Website', budget: 8000000, location: 'Bilkent', assignedTo: 'Fatma Demir', createdAt: '2024-01-11' },
  { id: 'lead-6', name: 'Zeynep Öz', email: 'zeynep.oz@email.com', phone: '+90 537 678 9012', status: 'won', source: 'Referral', budget: 2200000, location: 'Çankaya', assignedTo: 'Ahmet Yılmaz', createdAt: '2024-01-10' },
  { id: 'lead-7', name: 'Mustafa Aydın', email: 'mustafa.aydin@email.com', phone: '+90 538 789 0123', status: 'lost', source: 'Website', budget: 4000000, location: 'Ümitköy', assignedTo: 'Ali Öztürk', createdAt: '2024-01-09' },
  { id: 'lead-8', name: 'Elif Şen', email: 'elif.sen@email.com', phone: '+90 539 890 1234', status: 'new', source: 'Social Media', budget: 1800000, location: 'Yenimahalle', assignedTo: 'Fatma Demir', createdAt: '2024-01-15' },
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

const stats = [
  { label: 'Total Leads', value: leads.length, change: '+12%' },
  { label: 'New Today', value: 2, change: '+5%' },
  { label: 'Qualified', value: 3, change: '+8%' },
  { label: 'Won', value: 1, change: '+15%' },
]

export default function LeadsPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')

  const filteredLeads = leads.filter(lead => {
    const matchesSearch = lead.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         lead.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         lead.phone.includes(searchQuery)
    const matchesStatus = statusFilter === 'all' || lead.status === statusFilter
    return matchesSearch && matchesStatus
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Leads</h1>
          <p className="text-gray-500 mt-1">Manage and track your leads pipeline</p>
        </div>
        <div className="flex gap-3">
          <Link href="/leads/import">
            <Button variant="outline">
              <Upload className="mr-2 h-4 w-4" />
              Import
            </Button>
          </Link>
          <Button variant="outline">
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
          <Link href="/leads/new">
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              New Lead
            </Button>
          </Link>
        </div>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.label}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">{stat.label}</p>
                  <p className="text-2xl font-bold">{stat.value}</p>
                </div>
                <span className="text-xs text-green-600 font-medium">{stat.change}</span>
              </div>
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
                placeholder="Search leads by name, email, or phone..."
                className="pl-10"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                {Object.entries(statusConfig).map(([key, { label }]) => (
                  <SelectItem key={key} value={key}>{label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button variant="outline">
              <Filter className="mr-2 h-4 w-4" />
              More Filters
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Leads Table */}
      <Card>
        <CardHeader>
          <CardTitle>All Leads ({filteredLeads.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 font-medium">Lead</th>
                  <th className="text-left py-3 px-4 font-medium">Contact</th>
                  <th className="text-left py-3 px-4 font-medium">Status</th>
                  <th className="text-left py-3 px-4 font-medium">Budget</th>
                  <th className="text-left py-3 px-4 font-medium">Location</th>
                  <th className="text-left py-3 px-4 font-medium">Assigned To</th>
                  <th className="text-left py-3 px-4 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredLeads.map((lead) => (
                  <tr key={lead.id} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-4">
                      <Link href={`/leads/${lead.id}`} className="flex items-center gap-3">
                        <Avatar className="h-10 w-10">
                          <AvatarFallback>{lead.name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
                        </Avatar>
                        <div>
                          <p className="font-medium hover:text-blue-600">{lead.name}</p>
                          <p className="text-sm text-muted-foreground">{lead.source}</p>
                        </div>
                      </Link>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex flex-col gap-1">
                        <div className="flex items-center gap-2 text-sm">
                          <Mail className="h-3 w-3" />
                          {lead.email}
                        </div>
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <Phone className="h-3 w-3" />
                          {lead.phone}
                        </div>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <Badge className={statusConfig[lead.status].color}>
                        {statusConfig[lead.status].label}
                      </Badge>
                    </td>
                    <td className="py-3 px-4 font-medium">
                      ₺{lead.budget.toLocaleString()}
                    </td>
                    <td className="py-3 px-4 text-muted-foreground">
                      {lead.location}
                    </td>
                    <td className="py-3 px-4 text-muted-foreground">
                      {lead.assignedTo}
                    </td>
                    <td className="py-3 px-4">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon">
                            <MoreVertical className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem asChild>
                            <Link href={`/leads/${lead.id}`}>
                              <Eye className="mr-2 h-4 w-4" />
                              View Details
                            </Link>
                          </DropdownMenuItem>
                          <DropdownMenuItem asChild>
                            <Link href={`/leads/${lead.id}/edit`}>
                              <Edit className="mr-2 h-4 w-4" />
                              Edit
                            </Link>
                          </DropdownMenuItem>
                          <DropdownMenuItem asChild>
                            <Link href={`/matching/${lead.id}`}>
                              <Target className="mr-2 h-4 w-4" />
                              Find Matches
                            </Link>
                          </DropdownMenuItem>
                          <DropdownMenuItem className="text-red-600">
                            <Trash2 className="mr-2 h-4 w-4" />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
