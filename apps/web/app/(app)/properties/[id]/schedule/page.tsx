'use client'

import { useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { ArrowLeft, Calendar, Clock, User, Building2, CheckCircle2 } from 'lucide-react'

// Mock property data
const property = {
  id: 'prop-1',
  title: 'Modern 3+1 Apartment in Çankaya',
  address: 'Kızılırmak Caddesi No:45, Çankaya, Ankara',
  image: 'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=400',
  price: 2500000,
}

// Mock available time slots
const timeSlots = [
  '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
  '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00'
]

// Mock available dates (next 7 days)
const getAvailableDates = () => {
  const dates = []
  for (let i = 1; i <= 7; i++) {
    const date = new Date()
    date.setDate(date.getDate() + i)
    dates.push(date.toISOString().split('T')[0])
  }
  return dates
}

export default function ScheduleViewingPage() {
  const router = useRouter()
  const params = useParams()
  const [step, setStep] = useState(1)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [formData, setFormData] = useState({
    date: '',
    time: '',
    visitorName: '',
    visitorPhone: '',
    visitorEmail: '',
    leadId: '',
    notes: '',
  })

  const availableDates = getAvailableDates()

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    await new Promise(resolve => setTimeout(resolve, 1000))
    setStep(3)
    setIsSubmitting(false)
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })
  }

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href={`/properties/${params.id}`}>
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-5 w-5" />
          </Button>
        </Link>
        <div>
          <h1 className="text-2xl font-bold">Schedule Viewing</h1>
          <p className="text-muted-foreground">Book a property viewing appointment</p>
        </div>
      </div>

      {/* Property Card */}
      <Card>
        <CardContent className="p-4">
          <div className="flex gap-4">
            <img
              src={property.image}
              alt={property.title}
              className="w-24 h-20 object-cover rounded"
            />
            <div>
              <h3 className="font-semibold">{property.title}</h3>
              <p className="text-sm text-muted-foreground">{property.address}</p>
              <p className="text-lg font-bold text-blue-600 mt-1">
                ₺{property.price.toLocaleString()}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Progress Steps */}
      <div className="flex items-center justify-center gap-4">
        <div className={`flex items-center gap-2 ${step >= 1 ? 'text-blue-600' : 'text-gray-400'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 1 ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>
            <Calendar className="h-4 w-4" />
          </div>
          <span className="font-medium">Date & Time</span>
        </div>
        <div className={`w-12 h-0.5 ${step >= 2 ? 'bg-blue-600' : 'bg-gray-200'}`} />
        <div className={`flex items-center gap-2 ${step >= 2 ? 'text-blue-600' : 'text-gray-400'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 2 ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>
            <User className="h-4 w-4" />
          </div>
          <span className="font-medium">Details</span>
        </div>
        <div className={`w-12 h-0.5 ${step >= 3 ? 'bg-blue-600' : 'bg-gray-200'}`} />
        <div className={`flex items-center gap-2 ${step >= 3 ? 'text-blue-600' : 'text-gray-400'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 3 ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>
            <CheckCircle2 className="h-4 w-4" />
          </div>
          <span className="font-medium">Confirm</span>
        </div>
      </div>

      {/* Step 1: Select Date & Time */}
      {step === 1 && (
        <Card>
          <CardHeader>
            <CardTitle>Select Date & Time</CardTitle>
            <CardDescription>Choose your preferred viewing slot</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <Label>Available Dates</Label>
              <div className="grid grid-cols-4 gap-2">
                {availableDates.map((date) => (
                  <Button
                    key={date}
                    type="button"
                    variant={formData.date === date ? 'default' : 'outline'}
                    className="flex flex-col h-auto py-3"
                    onClick={() => handleChange('date', date)}
                  >
                    <span className="text-xs">
                      {new Date(date).toLocaleDateString('en-US', { weekday: 'short' })}
                    </span>
                    <span className="text-lg font-bold">
                      {new Date(date).getDate()}
                    </span>
                    <span className="text-xs">
                      {new Date(date).toLocaleDateString('en-US', { month: 'short' })}
                    </span>
                  </Button>
                ))}
              </div>
            </div>

            {formData.date && (
              <div className="space-y-2">
                <Label>Available Times for {formatDate(formData.date)}</Label>
                <div className="grid grid-cols-5 gap-2">
                  {timeSlots.map((time) => (
                    <Button
                      key={time}
                      type="button"
                      variant={formData.time === time ? 'default' : 'outline'}
                      onClick={() => handleChange('time', time)}
                    >
                      {time}
                    </Button>
                  ))}
                </div>
              </div>
            )}

            <div className="flex justify-end">
              <Button
                onClick={() => setStep(2)}
                disabled={!formData.date || !formData.time}
              >
                Continue
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 2: Visitor Details */}
      {step === 2 && (
        <form onSubmit={handleSubmit}>
          <Card>
            <CardHeader>
              <CardTitle>Visitor Details</CardTitle>
              <CardDescription>Enter the visitor's information</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-blue-50 rounded-lg p-3 mb-4">
                <div className="flex items-center gap-2 text-blue-700">
                  <Calendar className="h-4 w-4" />
                  <span className="font-medium">{formatDate(formData.date)} at {formData.time}</span>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="visitorName">Visitor Name *</Label>
                <Input
                  id="visitorName"
                  placeholder="Enter full name"
                  value={formData.visitorName}
                  onChange={(e) => handleChange('visitorName', e.target.value)}
                  required
                />
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="visitorPhone">Phone *</Label>
                  <Input
                    id="visitorPhone"
                    placeholder="+90 5XX XXX XXXX"
                    value={formData.visitorPhone}
                    onChange={(e) => handleChange('visitorPhone', e.target.value)}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="visitorEmail">Email</Label>
                  <Input
                    id="visitorEmail"
                    type="email"
                    placeholder="email@example.com"
                    value={formData.visitorEmail}
                    onChange={(e) => handleChange('visitorEmail', e.target.value)}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="leadId">Link to Lead (optional)</Label>
                <Select value={formData.leadId} onValueChange={(v) => handleChange('leadId', v)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select existing lead" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="lead-1">Mehmet Kaya</SelectItem>
                    <SelectItem value="lead-2">Ayşe Yıldız</SelectItem>
                    <SelectItem value="lead-3">Hasan Demir</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="notes">Notes</Label>
                <Textarea
                  id="notes"
                  placeholder="Any special requests or notes..."
                  rows={3}
                  value={formData.notes}
                  onChange={(e) => handleChange('notes', e.target.value)}
                />
              </div>

              <div className="flex justify-between pt-4">
                <Button type="button" variant="outline" onClick={() => setStep(1)}>
                  Back
                </Button>
                <Button type="submit" disabled={isSubmitting}>
                  {isSubmitting ? 'Scheduling...' : 'Schedule Viewing'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </form>
      )}

      {/* Step 3: Confirmation */}
      {step === 3 && (
        <Card>
          <CardContent className="py-12 text-center">
            <CheckCircle2 className="h-16 w-16 text-green-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold mb-2">Viewing Scheduled!</h2>
            <p className="text-muted-foreground mb-6">
              Your property viewing has been successfully scheduled.
            </p>

            <div className="bg-gray-50 rounded-lg p-4 max-w-md mx-auto mb-6 text-left">
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <Building2 className="h-5 w-5 text-gray-400" />
                  <span>{property.title}</span>
                </div>
                <div className="flex items-center gap-3">
                  <Calendar className="h-5 w-5 text-gray-400" />
                  <span>{formatDate(formData.date)}</span>
                </div>
                <div className="flex items-center gap-3">
                  <Clock className="h-5 w-5 text-gray-400" />
                  <span>{formData.time}</span>
                </div>
                <div className="flex items-center gap-3">
                  <User className="h-5 w-5 text-gray-400" />
                  <span>{formData.visitorName}</span>
                </div>
              </div>
            </div>

            <div className="flex justify-center gap-3">
              <Link href="/tasks">
                <Button variant="outline">View in Tasks</Button>
              </Link>
              <Link href={`/properties/${params.id}`}>
                <Button>Back to Property</Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
