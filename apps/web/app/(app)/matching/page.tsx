'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Progress } from '@/components/ui/progress'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { 
  Target, Search, Settings, Users, Building2, ArrowRight, 
  TrendingUp, Sparkles, Filter
} from 'lucide-react'

const leads = [
  { id: 'lead-1', name: 'Mehmet Kaya', budget: 2000000, location: 'Çankaya', propertyType: 'Apartment', status: 'qualified', matchCount: 8 },
  { id: 'lead-2', name: 'Ayşe Yıldız', budget: 3500000, location: 'Kızılay', propertyType: 'Office', status: 'contacted', matchCount: 5 },
  { id: 'lead-3', name: 'Hasan Demir', budget: 5000000, location: 'Oran', propertyType: 'Villa', status: 'qualified', matchCount: 12 },
  { id: 'lead-4', name: 'Fatma Çelik', budget: 1500000, location: 'Batıkent', propertyType: 'Apartment', status: 'proposal', matchCount: 6 },
  { id: 'lead-5', name: 'Ali Koç', budget: 8000000, location: 'Bilkent', propertyType: 'Villa', status: 'negotiation', matchCount: 4 },
]

const topMatches = [
  { leadId: 'lead-3', leadName: 'Hasan Demir', propertyId: 'prop-2', propertyTitle: 'Luxury Villa with Garden', score: 95 },
  { leadId: 'lead-1', leadName: 'Mehmet Kaya', propertyId: 'prop-1', propertyTitle: 'Modern 3+1 Apartment', score: 92 },
  { leadId: 'lead-5', leadName: 'Ali Koç', propertyId: 'prop-9', propertyTitle: 'Family Villa in Bilkent', score: 88 },
]

const stats = {
  totalMatches: 156,
  highScoreMatches: 45,
  sentToday: 12,
  conversionRate: 23,
}

const statusColors: Record<string, string> = {
  qualified: 'bg-purple-500',
  contacted: 'bg-yellow-500',
  proposal: 'bg-orange-500',
  negotiation: 'bg-pink-500',
}

export default function MatchingPage() {
  const [searchQuery, setSearchQuery] = useState('')

  const filteredLeads = leads.filter(lead =>
    lead.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    lead.location.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Property Matching</h1>
          <p className="text-gray-500 mt-1">Find the perfect properties for your leads</p>
        </div>
        <div className="flex gap-3">
          <Link href="/matching/settings">
            <Button variant="outline">
              <Settings className="mr-2 h-4 w-4" />
              Settings
            </Button>
          </Link>
          <Button>
            <Sparkles className="mr-2 h-4 w-4" />
            Run Auto-Match
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Target className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.totalMatches}</p>
                <p className="text-sm text-muted-foreground">Total Matches</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <TrendingUp className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.highScoreMatches}</p>
                <p className="text-sm text-muted-foreground">High Score (90%+)</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Users className="h-5 w-5 text-purple-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.sentToday}</p>
                <p className="text-sm text-muted-foreground">Sent Today</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-orange-100 rounded-lg">
                <Building2 className="h-5 w-5 text-orange-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.conversionRate}%</p>
                <p className="text-sm text-muted-foreground">Conversion Rate</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Top Matches */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-yellow-500" />
            Top Matches Today
          </CardTitle>
          <CardDescription>Highest scoring lead-property matches</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {topMatches.map((match) => (
              <div key={`${match.leadId}-${match.propertyId}`} className="flex items-center justify-between p-4 bg-gradient-to-r from-blue-50 to-green-50 rounded-lg">
                <div className="flex items-center gap-4">
                  <Avatar>
                    <AvatarFallback>{match.leadName.split(' ').map(n => n[0]).join('')}</AvatarFallback>
                  </Avatar>
                  <div>
                    <p className="font-medium">{match.leadName}</p>
                    <p className="text-sm text-muted-foreground">Lead</p>
                  </div>
                </div>
                <div className="flex items-center gap-2 px-4">
                  <ArrowRight className="h-5 w-5 text-gray-400" />
                  <div className="w-16 h-16 rounded-lg bg-white flex items-center justify-center">
                    <span className="text-2xl font-bold text-green-600">{match.score}%</span>
                  </div>
                  <ArrowRight className="h-5 w-5 text-gray-400" />
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className="font-medium">{match.propertyTitle}</p>
                    <p className="text-sm text-muted-foreground">Property</p>
                  </div>
                  <Link href={`/matching/${match.leadId}`}>
                    <Button size="sm">View</Button>
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Search & Filter */}
      <Card>
        <CardContent className="p-4">
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search leads..."
                className="pl-10"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <Select defaultValue="all">
              <SelectTrigger className="w-40">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="qualified">Qualified</SelectItem>
                <SelectItem value="contacted">Contacted</SelectItem>
                <SelectItem value="proposal">Proposal</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Leads for Matching */}
      <Card>
        <CardHeader>
          <CardTitle>Leads Ready for Matching</CardTitle>
          <CardDescription>Select a lead to find matching properties</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {filteredLeads.map((lead) => (
              <Link key={lead.id} href={`/matching/${lead.id}`}>
                <div className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 cursor-pointer">
                  <div className="flex items-center gap-4">
                    <Avatar>
                      <AvatarFallback>{lead.name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
                    </Avatar>
                    <div>
                      <div className="flex items-center gap-2">
                        <p className="font-medium">{lead.name}</p>
                        <Badge className={statusColors[lead.status]}>{lead.status}</Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        Budget: ₺{lead.budget.toLocaleString()} • {lead.location} • {lead.propertyType}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <p className="text-2xl font-bold text-blue-600">{lead.matchCount}</p>
                      <p className="text-sm text-muted-foreground">Matches</p>
                    </div>
                    <Button variant="outline" size="sm">
                      <Target className="mr-2 h-4 w-4" />
                      Find Matches
                    </Button>
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
