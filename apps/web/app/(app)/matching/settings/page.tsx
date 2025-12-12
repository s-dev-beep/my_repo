'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { ArrowLeft, Save, Target, Sliders, Bell, Zap } from 'lucide-react'

export default function MatchingSettingsPage() {
  const [settings, setSettings] = useState({
    budgetWeight: 30,
    locationWeight: 25,
    sizeWeight: 20,
    featuresWeight: 15,
    propertyTypeWeight: 10,
    minScore: 70,
    autoMatch: true,
    notifyAgent: true,
    notifyLead: false,
    budgetFlexibility: 20,
  })

  const handleWeightChange = (field: string, value: number) => {
    setSettings(prev => ({ ...prev, [field]: value }))
  }

  const handleToggle = (field: string, value: boolean) => {
    setSettings(prev => ({ ...prev, [field]: value }))
  }

  const totalWeight = settings.budgetWeight + settings.locationWeight + 
    settings.sizeWeight + settings.featuresWeight + settings.propertyTypeWeight

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/matching">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-5 w-5" />
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold">Matching Settings</h1>
            <p className="text-muted-foreground">Configure how properties are matched to leads</p>
          </div>
        </div>
        <Button>
          <Save className="mr-2 h-4 w-4" />
          Save Settings
        </Button>
      </div>

      {/* Weight Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sliders className="h-5 w-5" />
            Matching Weights
          </CardTitle>
          <CardDescription>
            Adjust the importance of each factor in the matching algorithm. Total should equal 100%.
            <span className={`ml-2 font-medium ${totalWeight === 100 ? 'text-green-600' : 'text-red-600'}`}>
              Current total: {totalWeight}%
            </span>
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between">
                <Label>Budget Match</Label>
                <span className="text-sm font-medium">{settings.budgetWeight}%</span>
              </div>
              <Input
                type="range"
                min="0"
                max="50"
                value={settings.budgetWeight}
                onChange={(e) => handleWeightChange('budgetWeight', parseInt(e.target.value))}
                className="w-full"
              />
              <p className="text-xs text-muted-foreground">How closely the property price matches the lead's budget</p>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between">
                <Label>Location Match</Label>
                <span className="text-sm font-medium">{settings.locationWeight}%</span>
              </div>
              <Input
                type="range"
                min="0"
                max="50"
                value={settings.locationWeight}
                onChange={(e) => handleWeightChange('locationWeight', parseInt(e.target.value))}
                className="w-full"
              />
              <p className="text-xs text-muted-foreground">How well the property location matches preferences</p>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between">
                <Label>Size Match</Label>
                <span className="text-sm font-medium">{settings.sizeWeight}%</span>
              </div>
              <Input
                type="range"
                min="0"
                max="50"
                value={settings.sizeWeight}
                onChange={(e) => handleWeightChange('sizeWeight', parseInt(e.target.value))}
                className="w-full"
              />
              <p className="text-xs text-muted-foreground">How well the property size matches requirements</p>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between">
                <Label>Features Match</Label>
                <span className="text-sm font-medium">{settings.featuresWeight}%</span>
              </div>
              <Input
                type="range"
                min="0"
                max="50"
                value={settings.featuresWeight}
                onChange={(e) => handleWeightChange('featuresWeight', parseInt(e.target.value))}
                className="w-full"
              />
              <p className="text-xs text-muted-foreground">How many desired features the property has</p>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between">
                <Label>Property Type Match</Label>
                <span className="text-sm font-medium">{settings.propertyTypeWeight}%</span>
              </div>
              <Input
                type="range"
                min="0"
                max="50"
                value={settings.propertyTypeWeight}
                onChange={(e) => handleWeightChange('propertyTypeWeight', parseInt(e.target.value))}
                className="w-full"
              />
              <p className="text-xs text-muted-foreground">Exact match of property type preference</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Threshold Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Threshold Settings
          </CardTitle>
          <CardDescription>Set minimum scores and flexibility ranges</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label htmlFor="minScore">Minimum Match Score (%)</Label>
              <Input
                id="minScore"
                type="number"
                min="0"
                max="100"
                value={settings.minScore}
                onChange={(e) => handleWeightChange('minScore', parseInt(e.target.value))}
              />
              <p className="text-xs text-muted-foreground">Properties below this score won't be shown</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="budgetFlexibility">Budget Flexibility (%)</Label>
              <Input
                id="budgetFlexibility"
                type="number"
                min="0"
                max="50"
                value={settings.budgetFlexibility}
                onChange={(e) => handleWeightChange('budgetFlexibility', parseInt(e.target.value))}
              />
              <p className="text-xs text-muted-foreground">Include properties within this range above budget</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Automation Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5" />
            Automation
          </CardTitle>
          <CardDescription>Configure automatic matching behavior</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <Label>Auto-Match New Properties</Label>
              <p className="text-sm text-muted-foreground">Automatically find matches when new properties are added</p>
            </div>
            <Switch
              checked={settings.autoMatch}
              onCheckedChange={(v) => handleToggle('autoMatch', v)}
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <Label>Notify Agent</Label>
              <p className="text-sm text-muted-foreground">Send notification when high-score matches are found</p>
            </div>
            <Switch
              checked={settings.notifyAgent}
              onCheckedChange={(v) => handleToggle('notifyAgent', v)}
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <Label>Auto-Send to Lead</Label>
              <p className="text-sm text-muted-foreground">Automatically email matches to leads (requires approval)</p>
            </div>
            <Switch
              checked={settings.notifyLead}
              onCheckedChange={(v) => handleToggle('notifyLead', v)}
            />
          </div>
        </CardContent>
      </Card>

      {/* Actions */}
      <div className="flex justify-end gap-3">
        <Button variant="outline">Reset to Defaults</Button>
        <Button>
          <Save className="mr-2 h-4 w-4" />
          Save Settings
        </Button>
      </div>
    </div>
  )
}
