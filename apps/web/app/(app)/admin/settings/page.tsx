'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Save, Building2, Globe, Bell, Shield } from 'lucide-react'

export default function AdminSettingsPage() {
  const [settings, setSettings] = useState({
    companyName: 'Dynamic CRM',
    defaultCurrency: 'TRY',
    timezone: 'Europe/Istanbul',
    emailNotifications: true,
    smsNotifications: true,
    autoAssignment: true,
    leadRotation: 'round_robin',
  })

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">System Settings</h1>
          <p className="text-gray-500 mt-1">Configure system-wide settings</p>
        </div>
        <Button><Save className="mr-2 h-4 w-4" />Save Settings</Button>
      </div>

      <Card>
        <CardHeader><CardTitle className="flex items-center gap-2"><Building2 className="h-5 w-5" />Company Information</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Company Name</Label>
            <Input value={settings.companyName} onChange={(e) => setSettings(s => ({...s, companyName: e.target.value}))} />
          </div>
          <div className="grid md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Default Currency</Label>
              <Select value={settings.defaultCurrency} onValueChange={(v) => setSettings(s => ({...s, defaultCurrency: v}))}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="TRY">Turkish Lira (TRY)</SelectItem>
                  <SelectItem value="USD">US Dollar (USD)</SelectItem>
                  <SelectItem value="EUR">Euro (EUR)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Timezone</Label>
              <Select value={settings.timezone} onValueChange={(v) => setSettings(s => ({...s, timezone: v}))}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="Europe/Istanbul">Istanbul (GMT+3)</SelectItem>
                  <SelectItem value="Europe/London">London (GMT)</SelectItem>
                  <SelectItem value="America/New_York">New York (GMT-5)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="flex items-center gap-2"><Bell className="h-5 w-5" />Notifications</CardTitle></CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div><Label>Email Notifications</Label><p className="text-sm text-muted-foreground">Send email notifications</p></div>
            <Switch checked={settings.emailNotifications} onCheckedChange={(v) => setSettings(s => ({...s, emailNotifications: v}))} />
          </div>
          <div className="flex items-center justify-between">
            <div><Label>SMS Notifications</Label><p className="text-sm text-muted-foreground">Send SMS notifications</p></div>
            <Switch checked={settings.smsNotifications} onCheckedChange={(v) => setSettings(s => ({...s, smsNotifications: v}))} />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="flex items-center gap-2"><Shield className="h-5 w-5" />Lead Management</CardTitle></CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div><Label>Auto Assignment</Label><p className="text-sm text-muted-foreground">Automatically assign leads to agents</p></div>
            <Switch checked={settings.autoAssignment} onCheckedChange={(v) => setSettings(s => ({...s, autoAssignment: v}))} />
          </div>
          <div className="space-y-2">
            <Label>Lead Rotation</Label>
            <Select value={settings.leadRotation} onValueChange={(v) => setSettings(s => ({...s, leadRotation: v}))}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="round_robin">Round Robin</SelectItem>
                <SelectItem value="load_balanced">Load Balanced</SelectItem>
                <SelectItem value="manual">Manual Assignment</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
