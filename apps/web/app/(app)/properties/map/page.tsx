'use client'

import { useState, useCallback } from 'react'
import Link from 'next/link'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { 
  ArrowLeft, Search, Filter, MapPin, Bed, Bath, Square, 
  Building2, X, ZoomIn, ZoomOut, Layers
} from 'lucide-react'

// Mock property data with coordinates (Ankara, Turkey)
const properties = [
  { id: 'prop-1', title: 'Modern 3+1 Apartment', district: 'Çankaya', price: 2500000, type: 'sale', propertyType: 'apartment', bedrooms: 3, bathrooms: 2, area: 145, status: 'available', lat: 39.9208, lng: 32.8541, image: 'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=400' },
  { id: 'prop-2', title: 'Luxury Villa', district: 'Oran', price: 8500000, type: 'sale', propertyType: 'villa', bedrooms: 5, bathrooms: 4, area: 350, status: 'available', lat: 39.8674, lng: 32.8012, image: 'https://images.unsplash.com/photo-1613490493576-7fde63acd811?w=400' },
  { id: 'prop-3', title: 'Office Space', district: 'Çankaya', price: 45000, type: 'rent', propertyType: 'office', bedrooms: 0, bathrooms: 2, area: 200, status: 'available', lat: 39.9072, lng: 32.7987, image: 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=400' },
  { id: 'prop-4', title: '2+1 Apartment', district: 'Kızılay', price: 1800000, type: 'sale', propertyType: 'apartment', bedrooms: 2, bathrooms: 1, area: 95, status: 'pending', lat: 39.9195, lng: 32.8597, image: 'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=400' },
  { id: 'prop-5', title: 'Commercial Space', district: 'Kavaklıdere', price: 75000, type: 'rent', propertyType: 'commercial', bedrooms: 0, bathrooms: 1, area: 120, status: 'available', lat: 39.9089, lng: 32.8656, image: 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400' },
  { id: 'prop-6', title: 'Investment Land', district: 'Çayyolu', price: 12000000, type: 'sale', propertyType: 'land', bedrooms: 0, bathrooms: 0, area: 5000, status: 'available', lat: 39.8456, lng: 32.7123, image: 'https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=400' },
  { id: 'prop-7', title: 'Penthouse', district: 'Çankaya', price: 6500000, type: 'sale', propertyType: 'apartment', bedrooms: 4, bathrooms: 3, area: 220, status: 'available', lat: 39.9156, lng: 32.8612, image: 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=400' },
  { id: 'prop-8', title: '1+1 for Rent', district: 'Bahçelievler', price: 15000, type: 'rent', propertyType: 'apartment', bedrooms: 1, bathrooms: 1, area: 55, status: 'available', lat: 39.9234, lng: 32.8234, image: 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=400' },
]

const statusColors: Record<string, string> = {
  available: 'bg-green-500',
  pending: 'bg-yellow-500',
  sold: 'bg-blue-500',
  rented: 'bg-purple-500',
}

export default function PropertiesMapPage() {
  const [selectedProperty, setSelectedProperty] = useState<typeof properties[0] | null>(null)
  const [typeFilter, setTypeFilter] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState('')

  const filteredProperties = properties.filter(property => {
    const matchesSearch = property.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         property.district.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesType = typeFilter === 'all' || property.type === typeFilter
    return matchesSearch && matchesType
  })

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/properties">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-5 w-5" />
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold">Property Map</h1>
            <p className="text-muted-foreground">View properties on the map</p>
          </div>
        </div>
        <div className="flex gap-3">
          <Link href="/properties">
            <Button variant="outline">
              <Building2 className="mr-2 h-4 w-4" />
              List View
            </Button>
          </Link>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search properties..."
                className="pl-10"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <Select value={typeFilter} onValueChange={setTypeFilter}>
              <SelectTrigger className="w-40">
                <SelectValue placeholder="Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="sale">For Sale</SelectItem>
                <SelectItem value="rent">For Rent</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Map Container */}
      <div className="grid lg:grid-cols-3 gap-4 h-[calc(100vh-300px)]">
        {/* Map */}
        <div className="lg:col-span-2 relative rounded-lg overflow-hidden border bg-gray-100">
          {/* Map Placeholder - Replace with Google Maps when API key is available */}
          <div className="absolute inset-0 bg-gradient-to-br from-green-100 to-blue-100">
            {/* Simple SVG Map of Ankara */}
            <svg viewBox="0 0 800 600" className="w-full h-full">
              {/* Background */}
              <rect fill="#e8f4e8" width="800" height="600" />
              
              {/* Roads */}
              <path d="M 0 300 L 800 300" stroke="#d4d4d4" strokeWidth="8" />
              <path d="M 400 0 L 400 600" stroke="#d4d4d4" strokeWidth="8" />
              <path d="M 100 100 L 700 500" stroke="#d4d4d4" strokeWidth="4" />
              <path d="M 100 500 L 700 100" stroke="#d4d4d4" strokeWidth="4" />
              
              {/* Property Markers */}
              {filteredProperties.map((property, index) => {
                // Convert lat/lng to x/y for our simple map
                const x = ((property.lng - 32.7) * 800 / 0.2)
                const y = ((39.95 - property.lat) * 600 / 0.15)
                const isSelected = selectedProperty?.id === property.id
                
                return (
                  <g 
                    key={property.id} 
                    onClick={() => setSelectedProperty(property)}
                    className="cursor-pointer"
                  >
                    <circle
                      cx={Math.max(30, Math.min(770, x))}
                      cy={Math.max(30, Math.min(570, y))}
                      r={isSelected ? 20 : 15}
                      fill={property.type === 'sale' ? '#3b82f6' : '#10b981'}
                      stroke="#fff"
                      strokeWidth="3"
                      className="transition-all hover:r-20"
                    />
                    <text
                      x={Math.max(30, Math.min(770, x))}
                      y={Math.max(30, Math.min(570, y)) + 4}
                      textAnchor="middle"
                      fill="white"
                      fontSize="10"
                      fontWeight="bold"
                    >
                      ₺{property.price >= 1000000 ? `${(property.price / 1000000).toFixed(1)}M` : `${(property.price / 1000).toFixed(0)}K`}
                    </text>
                  </g>
                )
              })}
            </svg>
            
            {/* Map Controls */}
            <div className="absolute top-4 right-4 flex flex-col gap-2">
              <Button variant="secondary" size="icon">
                <ZoomIn className="h-4 w-4" />
              </Button>
              <Button variant="secondary" size="icon">
                <ZoomOut className="h-4 w-4" />
              </Button>
              <Button variant="secondary" size="icon">
                <Layers className="h-4 w-4" />
              </Button>
            </div>

            {/* Legend */}
            <div className="absolute bottom-4 left-4 bg-white rounded-lg p-3 shadow-md">
              <p className="text-sm font-medium mb-2">Legend</p>
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded-full bg-blue-500" />
                  <span className="text-sm">For Sale</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded-full bg-green-500" />
                  <span className="text-sm">For Rent</span>
                </div>
              </div>
            </div>

            {/* Google Maps Integration Notice */}
            <div className="absolute top-4 left-4 bg-white/90 rounded-lg p-3 shadow-md max-w-xs">
              <p className="text-sm font-medium">Interactive Map</p>
              <p className="text-xs text-muted-foreground mt-1">
                Click on markers to view property details. Add Google Maps API key in .env.local for full functionality.
              </p>
            </div>
          </div>
        </div>

        {/* Property List */}
        <div className="overflow-auto">
          <Card className="h-full">
            <CardHeader className="py-3">
              <CardTitle className="text-lg">Properties ({filteredProperties.length})</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="divide-y">
                {filteredProperties.map((property) => (
                  <div
                    key={property.id}
                    className={`p-3 cursor-pointer hover:bg-gray-50 transition-colors ${
                      selectedProperty?.id === property.id ? 'bg-blue-50 border-l-4 border-blue-500' : ''
                    }`}
                    onClick={() => setSelectedProperty(property)}
                  >
                    <div className="flex gap-3">
                      <img
                        src={property.image}
                        alt={property.title}
                        className="w-20 h-16 object-cover rounded"
                      />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-2">
                          <h4 className="font-medium text-sm truncate">{property.title}</h4>
                          <Badge className={statusColors[property.status]} variant="secondary">
                            {property.status}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-1 text-xs text-muted-foreground mt-1">
                          <MapPin className="h-3 w-3" />
                          {property.district}
                        </div>
                        <div className="flex items-center gap-3 mt-1 text-xs text-muted-foreground">
                          {property.bedrooms > 0 && (
                            <span className="flex items-center gap-1">
                              <Bed className="h-3 w-3" />
                              {property.bedrooms}
                            </span>
                          )}
                          <span className="flex items-center gap-1">
                            <Square className="h-3 w-3" />
                            {property.area}m²
                          </span>
                        </div>
                        <p className="text-sm font-bold text-blue-600 mt-1">
                          ₺{property.price.toLocaleString()}
                          {property.type === 'rent' && '/mo'}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Selected Property Detail */}
      {selectedProperty && (
        <Card className="fixed bottom-4 left-1/2 -translate-x-1/2 w-96 shadow-xl z-50">
          <CardContent className="p-4">
            <Button
              variant="ghost"
              size="icon"
              className="absolute top-2 right-2"
              onClick={() => setSelectedProperty(null)}
            >
              <X className="h-4 w-4" />
            </Button>
            <div className="flex gap-4">
              <img
                src={selectedProperty.image}
                alt={selectedProperty.title}
                className="w-24 h-20 object-cover rounded"
              />
              <div className="flex-1">
                <h3 className="font-semibold">{selectedProperty.title}</h3>
                <p className="text-sm text-muted-foreground">{selectedProperty.district}</p>
                <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
                  {selectedProperty.bedrooms > 0 && (
                    <span className="flex items-center gap-1">
                      <Bed className="h-4 w-4" />
                      {selectedProperty.bedrooms} bed
                    </span>
                  )}
                  <span className="flex items-center gap-1">
                    <Square className="h-4 w-4" />
                    {selectedProperty.area}m²
                  </span>
                </div>
                <div className="flex items-center justify-between mt-3">
                  <p className="text-lg font-bold text-blue-600">
                    ₺{selectedProperty.price.toLocaleString()}
                    {selectedProperty.type === 'rent' && '/mo'}
                  </p>
                  <Link href={`/properties/${selectedProperty.id}`}>
                    <Button size="sm">View Details</Button>
                  </Link>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
