'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { ArrowLeft, Save, Calendar, Bell, Clock } from 'lucide-react'

export default function CalendarSettingsPage() {
  const [settings, setSettings] = useState({
    defaultView: 'month',
    weekStart: 'monday',
    timeFormat: '24h',
    emailReminders: true,
    pushReminders: true,
    reminderTime: '30',
    showWeekends: true,
  })

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/calendar">
            <Button variant="ghost" size="icon"><ArrowLeft className="h-5 w-5" /></Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold">Calendar Settings</h1>
            <p className="text-muted-foreground">Configure your calendar preferences</p>
          </div>
        </div>
        <Button><Save className="mr-2 h-4 w-4" />Save</Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2"><Calendar className="h-5 w-5" />Display</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label>Default View</Label>
              <Select value={settings.defaultView} onValueChange={(v) => setSettings(s => ({...s, defaultView: v}))}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="month">Month</SelectItem>
                  <SelectItem value="week">Week</SelectItem>
                  <SelectItem value="day">Day</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Week Starts On</Label>
              <Select value={settings.weekStart} onValueChange={(v) => setSettings(s => ({...s, weekStart: v}))}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="sunday">Sunday</SelectItem>
                  <SelectItem value="monday">Monday</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="flex items-center justify-between">
            <div><Label>Show Weekends</Label><p className="text-sm text-muted-foreground">Display Saturday and Sunday</p></div>
            <Switch checked={settings.showWeekends} onCheckedChange={(v) => setSettings(s => ({...s, showWeekends: v}))} />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2"><Bell className="h-5 w-5" />Reminders</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div><Label>Email Reminders</Label><p className="text-sm text-muted-foreground">Receive event reminders via email</p></div>
            <Switch checked={settings.emailReminders} onCheckedChange={(v) => setSettings(s => ({...s, emailReminders: v}))} />
          </div>
          <div className="flex items-center justify-between">
            <div><Label>Push Notifications</Label><p className="text-sm text-muted-foreground">Receive browser notifications</p></div>
            <Switch checked={settings.pushReminders} onCheckedChange={(v) => setSettings(s => ({...s, pushReminders: v}))} />
          </div>
          <div className="space-y-2">
            <Label>Default Reminder Time</Label>
            <Select value={settings.reminderTime} onValueChange={(v) => setSettings(s => ({...s, reminderTime: v}))}>
              <SelectTrigger className="w-48"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="15">15 minutes before</SelectItem>
                <SelectItem value="30">30 minutes before</SelectItem>
                <SelectItem value="60">1 hour before</SelectItem>
                <SelectItem value="1440">1 day before</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
