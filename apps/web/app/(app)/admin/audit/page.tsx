'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Search, User, Settings, Shield, FileText, LogIn } from 'lucide-react'

const auditLogs = [
  { id: 1, action: 'user.login', user: 'Ahmet Yılmaz', ip: '192.168.1.100', timestamp: '2024-01-15 10:30', details: 'Successful login', status: 'success' },
  { id: 2, action: 'lead.create', user: 'Fatma Demir', ip: '192.168.1.101', timestamp: '2024-01-15 10:25', details: 'Created lead: Elif Şen', status: 'success' },
  { id: 3, action: 'property.update', user: 'Ali Öztürk', ip: '192.168.1.102', timestamp: '2024-01-15 10:20', details: 'Updated property pricing', status: 'success' },
  { id: 4, action: 'settings.change', user: 'Zeynep Arslan', ip: '192.168.1.103', timestamp: '2024-01-15 10:15', details: 'Changed notification settings', status: 'warning' },
  { id: 5, action: 'user.login', user: 'Unknown', ip: '203.45.67.89', timestamp: '2024-01-15 10:10', details: 'Failed login attempt', status: 'error' },
  { id: 6, action: 'lead.delete', user: 'Ahmet Yılmaz', ip: '192.168.1.100', timestamp: '2024-01-15 10:05', details: 'Deleted duplicate lead', status: 'warning' },
]

const actionIcons: Record<string, any> = { 'user.login': LogIn, 'lead.create': User, 'lead.delete': User, 'property.update': FileText, 'settings.change': Settings }
const statusColors: Record<string, string> = { success: 'bg-green-500', warning: 'bg-yellow-500', error: 'bg-red-500' }

export default function AdminAuditPage() {
  const [searchQuery, setSearchQuery] = useState('')

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Audit Log</h1>
        <p className="text-gray-500 mt-1">Track all system activity and changes</p>
      </div>

      <Card>
        <CardContent className="p-4">
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input placeholder="Search logs..." className="pl-10" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} />
            </div>
            <Select defaultValue="all"><SelectTrigger className="w-40"><SelectValue placeholder="Action" /></SelectTrigger><SelectContent><SelectItem value="all">All Actions</SelectItem><SelectItem value="login">Login</SelectItem><SelectItem value="create">Create</SelectItem><SelectItem value="update">Update</SelectItem><SelectItem value="delete">Delete</SelectItem></SelectContent></Select>
            <Select defaultValue="all"><SelectTrigger className="w-40"><SelectValue placeholder="Status" /></SelectTrigger><SelectContent><SelectItem value="all">All Status</SelectItem><SelectItem value="success">Success</SelectItem><SelectItem value="warning">Warning</SelectItem><SelectItem value="error">Error</SelectItem></SelectContent></Select>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Activity Log</CardTitle></CardHeader>
        <CardContent>
          <div className="space-y-3">
            {auditLogs.map((log) => {
              const Icon = actionIcons[log.action] || Shield
              return (
                <div key={log.id} className="flex items-center gap-4 p-4 border rounded-lg">
                  <div className={`p-2 rounded-lg ${log.status === 'success' ? 'bg-green-100' : log.status === 'warning' ? 'bg-yellow-100' : 'bg-red-100'}`}>
                    <Icon className={`h-5 w-5 ${log.status === 'success' ? 'text-green-600' : log.status === 'warning' ? 'text-yellow-600' : 'text-red-600'}`} />
                  </div>
                  <div className="flex-1">
                    <p className="font-medium">{log.action}</p>
                    <p className="text-sm text-muted-foreground">{log.details}</p>
                    <p className="text-xs text-muted-foreground mt-1">{log.user} • {log.ip}</p>
                  </div>
                  <div className="text-right">
                    <Badge className={statusColors[log.status]}>{log.status}</Badge>
                    <p className="text-sm text-muted-foreground mt-1">{log.timestamp}</p>
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
