'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Users, Plus, Search, Edit, Trash2, MoreVertical, Shield } from 'lucide-react'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'

const users = [
  { id: 'user-1', name: 'Ahmet Yılmaz', email: 'ahmet@crm.com', role: 'agent', status: 'active', lastActive: '2 min ago' },
  { id: 'user-2', name: 'Fatma Demir', email: 'fatma@crm.com', role: 'agent', status: 'active', lastActive: '5 min ago' },
  { id: 'user-3', name: 'Ali Öztürk', email: 'ali@crm.com', role: 'team_lead', status: 'active', lastActive: '1 hour ago' },
  { id: 'user-4', name: 'Zeynep Arslan', email: 'zeynep@crm.com', role: 'admin', status: 'active', lastActive: '30 min ago' },
  { id: 'user-5', name: 'Mustafa Şahin', email: 'mustafa@crm.com', role: 'agent', status: 'inactive', lastActive: '2 days ago' },
]

const roleColors: Record<string, string> = { admin: 'bg-red-500', team_lead: 'bg-purple-500', agent: 'bg-blue-500', call_center: 'bg-green-500' }

export default function AdminUsersPage() {
  const [searchQuery, setSearchQuery] = useState('')

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">User Management</h1>
          <p className="text-gray-500 mt-1">Manage system users and permissions</p>
        </div>
        <Button><Plus className="mr-2 h-4 w-4" />Add User</Button>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card><CardContent className="p-4"><p className="text-sm text-muted-foreground">Total Users</p><p className="text-2xl font-bold">{users.length}</p></CardContent></Card>
        <Card><CardContent className="p-4"><p className="text-sm text-muted-foreground">Active</p><p className="text-2xl font-bold text-green-600">{users.filter(u => u.status === 'active').length}</p></CardContent></Card>
        <Card><CardContent className="p-4"><p className="text-sm text-muted-foreground">Admins</p><p className="text-2xl font-bold">{users.filter(u => u.role === 'admin').length}</p></CardContent></Card>
        <Card><CardContent className="p-4"><p className="text-sm text-muted-foreground">Agents</p><p className="text-2xl font-bold">{users.filter(u => u.role === 'agent').length}</p></CardContent></Card>
      </div>

      <Card>
        <CardContent className="p-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input placeholder="Search users..." className="pl-10" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>All Users</CardTitle></CardHeader>
        <CardContent>
          <div className="space-y-3">
            {users.map((user) => (
              <div key={user.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50">
                <div className="flex items-center gap-4">
                  <Avatar><AvatarFallback>{user.name.split(' ').map(n => n[0]).join('')}</AvatarFallback></Avatar>
                  <div>
                    <p className="font-medium">{user.name}</p>
                    <p className="text-sm text-muted-foreground">{user.email}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <Badge className={roleColors[user.role]}>{user.role.replace('_', ' ')}</Badge>
                  <Badge variant={user.status === 'active' ? 'default' : 'secondary'}>{user.status}</Badge>
                  <span className="text-sm text-muted-foreground">{user.lastActive}</span>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild><Button variant="ghost" size="icon"><MoreVertical className="h-4 w-4" /></Button></DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem><Edit className="mr-2 h-4 w-4" />Edit</DropdownMenuItem>
                      <DropdownMenuItem><Shield className="mr-2 h-4 w-4" />Change Role</DropdownMenuItem>
                      <DropdownMenuItem className="text-red-600"><Trash2 className="mr-2 h-4 w-4" />Delete</DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
