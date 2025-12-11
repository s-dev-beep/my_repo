'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Server, Database, HardDrive, Cpu, Activity, RefreshCw, CheckCircle2 } from 'lucide-react'

const systemStats = {
  uptime: '99.9%',
  lastRestart: '15 days ago',
  version: '2.1.0',
  storage: { used: 45.2, total: 100 },
  memory: { used: 4.2, total: 8 },
  cpu: 23,
  apiCalls: 125000,
  activeConnections: 38,
}

const services = [
  { name: 'Web Server', status: 'healthy', uptime: '99.9%' },
  { name: 'Database', status: 'healthy', uptime: '99.8%' },
  { name: 'Cache Server', status: 'healthy', uptime: '99.9%' },
  { name: 'Email Service', status: 'healthy', uptime: '99.5%' },
  { name: 'Background Jobs', status: 'healthy', uptime: '99.7%' },
]

export default function AdminSystemPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">System Health</h1>
          <p className="text-gray-500 mt-1">Monitor system performance and status</p>
        </div>
        <Button variant="outline"><RefreshCw className="mr-2 h-4 w-4" />Refresh</Button>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card><CardContent className="p-4"><div className="flex items-center gap-3"><div className="p-2 bg-green-100 rounded-lg"><Server className="h-5 w-5 text-green-600" /></div><div><p className="text-2xl font-bold">{systemStats.uptime}</p><p className="text-sm text-muted-foreground">Uptime</p></div></div></CardContent></Card>
        <Card><CardContent className="p-4"><div className="flex items-center gap-3"><div className="p-2 bg-blue-100 rounded-lg"><Activity className="h-5 w-5 text-blue-600" /></div><div><p className="text-2xl font-bold">{systemStats.activeConnections}</p><p className="text-sm text-muted-foreground">Active Users</p></div></div></CardContent></Card>
        <Card><CardContent className="p-4"><div className="flex items-center gap-3"><div className="p-2 bg-purple-100 rounded-lg"><Database className="h-5 w-5 text-purple-600" /></div><div><p className="text-2xl font-bold">{(systemStats.apiCalls / 1000).toFixed(0)}K</p><p className="text-sm text-muted-foreground">API Calls (24h)</p></div></div></CardContent></Card>
        <Card><CardContent className="p-4"><div className="flex items-center gap-3"><div className="p-2 bg-orange-100 rounded-lg"><Server className="h-5 w-5 text-orange-600" /></div><div><p className="text-2xl font-bold">v{systemStats.version}</p><p className="text-sm text-muted-foreground">Version</p></div></div></CardContent></Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Resource Usage</CardTitle></CardHeader>
          <CardContent className="space-y-6">
            <div>
              <div className="flex justify-between text-sm mb-2"><div className="flex items-center gap-2"><HardDrive className="h-4 w-4" />Storage</div><span>{systemStats.storage.used} GB / {systemStats.storage.total} GB</span></div>
              <Progress value={(systemStats.storage.used / systemStats.storage.total) * 100} className="h-2" />
            </div>
            <div>
              <div className="flex justify-between text-sm mb-2"><div className="flex items-center gap-2"><Database className="h-4 w-4" />Memory</div><span>{systemStats.memory.used} GB / {systemStats.memory.total} GB</span></div>
              <Progress value={(systemStats.memory.used / systemStats.memory.total) * 100} className="h-2" />
            </div>
            <div>
              <div className="flex justify-between text-sm mb-2"><div className="flex items-center gap-2"><Cpu className="h-4 w-4" />CPU</div><span>{systemStats.cpu}%</span></div>
              <Progress value={systemStats.cpu} className="h-2" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Services Status</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-4">
              {services.map((service) => (
                <div key={service.name} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <CheckCircle2 className="h-5 w-5 text-green-500" />
                    <div>
                      <p className="font-medium">{service.name}</p>
                      <p className="text-sm text-muted-foreground">Uptime: {service.uptime}</p>
                    </div>
                  </div>
                  <Badge className="bg-green-500">{service.status}</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
