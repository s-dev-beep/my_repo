'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { 
  Shield, Users, Database, Activity, Settings, Server,
  ArrowUpRight, HardDrive, Cpu, Globe
} from 'lucide-react'
import Link from 'next/link'

const systemStats = {
  totalUsers: 45,
  activeUsers: 38,
  totalLeads: 1247,
  totalProperties: 856,
  storageUsed: 45.2,
  storageTotal: 100,
  apiCalls: 125000,
  uptime: 99.9,
}

const recentActivity = [
  { id: 1, action: 'User Login', user: 'Ahmet Yılmaz', ip: '192.168.1.100', time: '2 min ago', status: 'success' },
  { id: 2, action: 'Lead Created', user: 'Fatma Demir', ip: '192.168.1.101', time: '5 min ago', status: 'success' },
  { id: 3, action: 'Property Updated', user: 'Ali Öztürk', ip: '192.168.1.102', time: '10 min ago', status: 'success' },
  { id: 4, action: 'Settings Changed', user: 'Admin', ip: '192.168.1.1', time: '15 min ago', status: 'warning' },
  { id: 5, action: 'Failed Login', user: 'Unknown', ip: '203.45.67.89', time: '20 min ago', status: 'error' },
]

const usersByRole = [
  { role: 'Admin', count: 2, color: 'bg-red-500' },
  { role: 'Team Lead', count: 4, color: 'bg-purple-500' },
  { role: 'Agent', count: 25, color: 'bg-blue-500' },
  { role: 'Call Center', count: 10, color: 'bg-green-500' },
  { role: 'Viewer', count: 4, color: 'bg-gray-500' },
]

export default function AdminDashboardPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
          <p className="text-gray-500 mt-1">System overview and administration</p>
        </div>
        <div className="flex gap-3">
          <Link href="/admin/audit">
            <Button variant="outline">
              <Activity className="mr-2 h-4 w-4" />
              Audit Log
            </Button>
          </Link>
          <Link href="/admin/settings">
            <Button>
              <Settings className="mr-2 h-4 w-4" />
              Settings
            </Button>
          </Link>
        </div>
      </div>

      {/* System Stats */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Users</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{systemStats.totalUsers}</div>
            <p className="text-xs text-muted-foreground">{systemStats.activeUsers} active now</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Database Records</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{(systemStats.totalLeads + systemStats.totalProperties).toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">Leads + Properties</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">API Calls (24h)</CardTitle>
            <Globe className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{(systemStats.apiCalls / 1000).toFixed(0)}K</div>
            <div className="flex items-center text-xs text-green-600">
              <ArrowUpRight className="h-3 w-3 mr-1" />
              Normal load
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">System Uptime</CardTitle>
            <Server className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{systemStats.uptime}%</div>
            <p className="text-xs text-green-600">All systems operational</p>
          </CardContent>
        </Card>
      </div>

      {/* Storage and System Health */}
      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>System Resources</CardTitle>
            <CardDescription>Server and storage metrics</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <div className="flex justify-between text-sm mb-2">
                <div className="flex items-center gap-2">
                  <HardDrive className="h-4 w-4" />
                  <span>Storage</span>
                </div>
                <span className="font-medium">{systemStats.storageUsed} GB / {systemStats.storageTotal} GB</span>
              </div>
              <Progress value={(systemStats.storageUsed / systemStats.storageTotal) * 100} className="h-2" />
            </div>
            <div>
              <div className="flex justify-between text-sm mb-2">
                <div className="flex items-center gap-2">
                  <Cpu className="h-4 w-4" />
                  <span>CPU Usage</span>
                </div>
                <span className="font-medium">23%</span>
              </div>
              <Progress value={23} className="h-2" />
            </div>
            <div>
              <div className="flex justify-between text-sm mb-2">
                <div className="flex items-center gap-2">
                  <Database className="h-4 w-4" />
                  <span>Memory</span>
                </div>
                <span className="font-medium">4.2 GB / 8 GB</span>
              </div>
              <Progress value={52.5} className="h-2" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Users by Role</CardTitle>
            <CardDescription>Distribution of user roles</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {usersByRole.map((role) => (
                <div key={role.role} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-full ${role.color}`} />
                    <span className="font-medium">{role.role}</span>
                  </div>
                  <Badge variant="secondary">{role.count} users</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>Latest system events and user actions</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recentActivity.map((activity) => (
              <div key={activity.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-4">
                  <div className={`w-2 h-2 rounded-full ${
                    activity.status === 'success' ? 'bg-green-500' :
                    activity.status === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
                  }`} />
                  <div>
                    <p className="font-medium">{activity.action}</p>
                    <p className="text-sm text-muted-foreground">
                      {activity.user} • {activity.ip}
                    </p>
                  </div>
                </div>
                <span className="text-sm text-muted-foreground">{activity.time}</span>
              </div>
            ))}
          </div>
          <Link href="/admin/audit">
            <Button variant="link" className="w-full mt-4">View all activity</Button>
          </Link>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Administration</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-3">
            <Link href="/admin/users">
              <Button variant="outline">
                <Users className="mr-2 h-4 w-4" />
                Manage Users
              </Button>
            </Link>
            <Link href="/admin/roles">
              <Button variant="outline">
                <Shield className="mr-2 h-4 w-4" />
                Roles & Permissions
              </Button>
            </Link>
            <Link href="/admin/settings">
              <Button variant="outline">
                <Settings className="mr-2 h-4 w-4" />
                System Settings
              </Button>
            </Link>
            <Link href="/admin/system">
              <Button variant="outline">
                <Server className="mr-2 h-4 w-4" />
                System Health
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
