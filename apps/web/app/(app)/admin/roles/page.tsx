'use client'

import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Shield, Plus, Edit, Users, CheckCircle2 } from 'lucide-react'

const roles = [
  { id: 'role-1', name: 'Admin', description: 'Full system access', userCount: 2, permissions: ['all'] },
  { id: 'role-2', name: 'Team Lead', description: 'Manage team and view reports', userCount: 4, permissions: ['leads', 'properties', 'tasks', 'reports', 'team'] },
  { id: 'role-3', name: 'Agent', description: 'Sales agent access', userCount: 25, permissions: ['leads', 'properties', 'tasks'] },
  { id: 'role-4', name: 'Call Center', description: 'Lead management and calls', userCount: 10, permissions: ['leads', 'calls'] },
  { id: 'role-5', name: 'Viewer', description: 'Read-only access', userCount: 4, permissions: ['view'] },
]

const allPermissions = ['leads', 'properties', 'tasks', 'calls', 'reports', 'team', 'admin', 'settings']

export default function AdminRolesPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Roles & Permissions</h1>
          <p className="text-gray-500 mt-1">Manage user roles and access levels</p>
        </div>
        <Button><Plus className="mr-2 h-4 w-4" />Create Role</Button>
      </div>

      <div className="grid gap-6">
        {roles.map((role) => (
          <Card key={role.id}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-100 rounded-lg"><Shield className="h-5 w-5 text-blue-600" /></div>
                  <div>
                    <CardTitle>{role.name}</CardTitle>
                    <CardDescription>{role.description}</CardDescription>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-2"><Users className="h-4 w-4 text-gray-400" /><span className="text-sm">{role.userCount} users</span></div>
                  <Button variant="outline" size="sm"><Edit className="mr-2 h-4 w-4" />Edit</Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-2">Permissions</p>
              <div className="flex flex-wrap gap-2">
                {role.permissions.includes('all') ? (
                  <Badge className="bg-green-500">Full Access</Badge>
                ) : (
                  role.permissions.map((perm) => (
                    <Badge key={perm} variant="secondary" className="capitalize">{perm}</Badge>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
