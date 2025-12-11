'use client'

import { useParams } from 'next/navigation'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Progress } from '@/components/ui/progress'
import { Checkbox } from '@/components/ui/checkbox'
import { 
  ArrowLeft, Target, Building2, MapPin, Bed, Bath, Square, 
  Send, Heart, DollarSign, Check, X
} from 'lucide-react'

// Mock lead data
const lead = {
  id: 'lead-1',
  name: 'Mehmet Kaya',
  email: 'mehmet.kaya@email.com',
  phone: '+90 532 123 4567',
  budget: 2000000,
  preferredLocation: 'Çankaya',
  propertyType: 'Apartment',
  bedrooms: '3+1',
  minArea: 120,
  maxArea: 180,
  features: ['Balcony', 'Parking', 'Security'],
}

// Mock matched properties
const matchedProperties = [
  { id: 'prop-1', title: 'Modern 3+1 Apartment in Çankaya', price: 2500000, area: 145, bedrooms: 3, bathrooms: 2, district: 'Çankaya', score: 95, matchReasons: ['Budget +25%', 'Location match', 'Property type', '3 bedrooms'], image: 'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=400' },
  { id: 'prop-7', title: 'Penthouse with Terrace', price: 6500000, area: 220, bedrooms: 4, bathrooms: 3, district: 'Çankaya', score: 78, matchReasons: ['Location match', 'Property type', 'Premium features'], image: 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=400' },
  { id: 'prop-4', title: '2+1 Apartment Near Metro', price: 1800000, area: 95, bedrooms: 2, bathrooms: 1, district: 'Kızılay', score: 72, matchReasons: ['Within budget', 'Central location', 'Good transport'], image: 'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=400' },
  { id: 'prop-8', title: 'Cozy 1+1 for Rent', price: 15000, area: 55, bedrooms: 1, bathrooms: 1, district: 'Bahçelievler', score: 45, matchReasons: ['Affordable option'], image: 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=400' },
]

export default function LeadMatchingPage() {
  const params = useParams()

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/matching">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-5 w-5" />
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold">Property Matches</h1>
            <p className="text-muted-foreground">Finding matches for {lead.name}</p>
          </div>
        </div>
        <Button>
          <Send className="mr-2 h-4 w-4" />
          Send Selected to Lead
        </Button>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Lead Requirements */}
        <div className="lg:col-span-1 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Avatar>
                  <AvatarFallback>{lead.name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
                </Avatar>
                <div>
                  <p>{lead.name}</p>
                  <p className="text-sm font-normal text-muted-foreground">{lead.email}</p>
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-green-100 rounded-lg">
                  <DollarSign className="h-4 w-4 text-green-600" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Budget</p>
                  <p className="font-medium">₺{lead.budget.toLocaleString()}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <MapPin className="h-4 w-4 text-blue-600" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Location</p>
                  <p className="font-medium">{lead.preferredLocation}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <Building2 className="h-4 w-4 text-purple-600" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Property Type</p>
                  <p className="font-medium">{lead.propertyType}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="p-2 bg-orange-100 rounded-lg">
                  <Bed className="h-4 w-4 text-orange-600" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Bedrooms</p>
                  <p className="font-medium">{lead.bedrooms}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="p-2 bg-cyan-100 rounded-lg">
                  <Square className="h-4 w-4 text-cyan-600" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Area Range</p>
                  <p className="font-medium">{lead.minArea} - {lead.maxArea} m²</p>
                </div>
              </div>
              
              <div className="pt-4 border-t">
                <p className="text-sm text-muted-foreground mb-2">Desired Features</p>
                <div className="flex flex-wrap gap-2">
                  {lead.features.map((feature) => (
                    <Badge key={feature} variant="secondary">{feature}</Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Link href={`/leads/${lead.id}`}>
                <Button variant="outline" className="w-full justify-start">View Lead Profile</Button>
              </Link>
              <Link href="/matching/settings">
                <Button variant="outline" className="w-full justify-start">Adjust Matching Settings</Button>
              </Link>
            </CardContent>
          </Card>
        </div>

        {/* Matched Properties */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Matched Properties ({matchedProperties.length})</CardTitle>
              <CardDescription>Sorted by match score</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {matchedProperties.map((property) => (
                  <div key={property.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex gap-4">
                      <div className="flex items-center">
                        <Checkbox id={property.id} />
                      </div>
                      <img
                        src={property.image}
                        alt={property.title}
                        className="w-32 h-24 object-cover rounded-lg"
                      />
                      <div className="flex-1">
                        <div className="flex items-start justify-between">
                          <div>
                            <Link href={`/properties/${property.id}`}>
                              <h3 className="font-semibold hover:text-blue-600">{property.title}</h3>
                            </Link>
                            <div className="flex items-center gap-1 text-sm text-muted-foreground mt-1">
                              <MapPin className="h-3 w-3" />
                              {property.district}
                            </div>
                          </div>
                          <div className="text-right">
                            <div className={`text-2xl font-bold ${
                              property.score >= 90 ? 'text-green-600' :
                              property.score >= 70 ? 'text-blue-600' :
                              property.score >= 50 ? 'text-yellow-600' : 'text-gray-400'
                            }`}>
                              {property.score}%
                            </div>
                            <p className="text-xs text-muted-foreground">Match Score</p>
                          </div>
                        </div>
                        
                        <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
                          <span className="flex items-center gap-1">
                            <Bed className="h-4 w-4" />
                            {property.bedrooms} bed
                          </span>
                          <span className="flex items-center gap-1">
                            <Bath className="h-4 w-4" />
                            {property.bathrooms} bath
                          </span>
                          <span className="flex items-center gap-1">
                            <Square className="h-4 w-4" />
                            {property.area} m²
                          </span>
                        </div>

                        <div className="flex items-center justify-between mt-3">
                          <p className="text-lg font-bold text-blue-600">
                            ₺{property.price.toLocaleString()}
                          </p>
                          <div className="flex gap-2">
                            <Button variant="ghost" size="icon">
                              <Heart className="h-4 w-4" />
                            </Button>
                            <Link href={`/properties/${property.id}`}>
                              <Button size="sm" variant="outline">View</Button>
                            </Link>
                          </div>
                        </div>

                        {/* Match Reasons */}
                        <div className="mt-3 pt-3 border-t">
                          <p className="text-xs text-muted-foreground mb-2">Match Reasons:</p>
                          <div className="flex flex-wrap gap-1">
                            {property.matchReasons.map((reason, idx) => (
                              <Badge key={idx} variant="outline" className="text-xs">
                                <Check className="h-3 w-3 mr-1 text-green-500" />
                                {reason}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
