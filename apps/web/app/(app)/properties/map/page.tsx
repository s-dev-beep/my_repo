'use client'

import { useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { MapPin, List, Search, Home, Building2, Filter, X, ExternalLink, AlertCircle } from 'lucide-react'

// Check if Google Maps API key is available
const GOOGLE_MAPS_API_KEY = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY

// Mock properties with coordinates (for when Supabase isn't configured)
const mockProperties = [
  { id: 'prop-1', title: 'Luxury Apartment in Çankaya', price: 2500000, currency: '₺', type: 'sale', propertyType: 'apartment', latitude: 39.9012, longitude: 32.8597, status: 'available', address: 'Çankaya, Ankara', bedrooms: 3, area: 150 },
  { id: 'prop-2', title: 'Modern Villa in Eryaman', price: 4500000, currency: '₺', type: 'sale', propertyType: 'villa', latitude: 39.9834, longitude: 32.6597, status: 'available', address: 'Eryaman, Ankara', bedrooms: 5, area: 320 },
  { id: 'prop-3', title: 'Office Space in Kızılay', price: 15000, currency: '₺', type: 'rent', propertyType: 'office', latitude: 39.9208, longitude: 32.8541, status: 'available', address: 'Kızılay, Ankara', bedrooms: 0, area: 200 },
  { id: 'prop-4', title: 'Penthouse in GOP', price: 5500000, currency: '₺', type: 'sale', propertyType: 'apartment', latitude: 39.9112, longitude: 32.8641, status: 'pending', address: 'GOP, Ankara', bedrooms: 4, area: 220 },
  { id: 'prop-5', title: 'Studio in Bahçelievler', price: 8500, currency: '₺', type: 'rent', propertyType: 'apartment', latitude: 39.9278, longitude: 32.8297, status: 'available', address: 'Bahçelievler, Ankara', bedrooms: 1, area: 45 },
  { id: 'prop-6', title: 'Commercial Space', price: 3200000, currency: '₺', type: 'sale', propertyType: 'commercial', latitude: 39.9334, longitude: 32.8197, status: 'available', address: 'Ulus, Ankara', bedrooms: 0, area: 500 },
  { id: 'prop-7', title: 'Family Home in Çayyolu', price: 3800000, currency: '₺', type: 'sale', propertyType: 'villa', latitude: 39.8634, longitude: 32.7097, status: 'available', address: 'Çayyolu, Ankara', bedrooms: 4, area: 280 },
]

// Status colors
const statusColors: Record<string, string> = {
  available: 'bg-green-500',
  pending: 'bg-yellow-500',
  sold: 'bg-red-500',
  rented: 'bg-blue-500',
}

// Property type icons
const propertyTypeIcons: Record<string, string> = {
  apartment: '🏢',
  villa: '🏡',
  office: '🏛️',
  land: '🌍',
  commercial: '🏪',
}

// Google Maps Component (only renders if API key is available)
function GoogleMapsView({ properties, onSelectProperty, selectedProperty }: {
  properties: typeof mockProperties
  onSelectProperty: (property: typeof mockProperties[0] | null) => void
  selectedProperty: typeof mockProperties[0] | null
}) {
  const router = useRouter()
  
  // Dynamic import for Google Maps (only if API key exists)
  if (!GOOGLE_MAPS_API_KEY) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-100 rounded-lg">
        <Card className="max-w-md">
          <CardContent className="pt-6 text-center">
            <AlertCircle className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
            <h3 className="font-bold text-lg mb-2">Google Maps API Key Required</h3>
            <p className="text-muted-foreground mb-4">
              To enable the interactive map, add your Google Maps API key to the environment variables.
            </p>
            <code className="block bg-gray-100 p-2 rounded text-sm mb-4">
              NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your-key-here
            </code>
            <p className="text-sm text-muted-foreground">
              Get your API key from the{' '}
              <a href="https://console.cloud.google.com/google/maps-apis" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                Google Cloud Console
              </a>
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  // If we have an API key, render the map
  return (
    <GoogleMapsWithScript 
      properties={properties}
      onSelectProperty={onSelectProperty}
      selectedProperty={selectedProperty}
    />
  )
}

// Actual Google Maps component with script loading
function GoogleMapsWithScript({ properties, onSelectProperty, selectedProperty }: {
  properties: typeof mockProperties
  onSelectProperty: (property: typeof mockProperties[0] | null) => void
  selectedProperty: typeof mockProperties[0] | null
}) {
  const router = useRouter()
  const [mapLoaded, setMapLoaded] = useState(false)
  const [mapError, setMapError] = useState<string | null>(null)

  // This would use @react-google-maps/api in production
  // For now, show a placeholder with the properties listed
  return (
    <div className="relative h-full bg-gradient-to-br from-blue-50 to-green-50 rounded-lg overflow-hidden">
      {/* Map background pattern */}
      <div className="absolute inset-0" style={{
        backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%239C92AC' fill-opacity='0.1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
      }} />
      
      {/* Property markers as positioned dots */}
      <div className="absolute inset-0">
        {properties.map((property, index) => {
          // Calculate position based on lat/lng (simplified)
          const baseLeft = ((property.longitude - 32.5) / 0.6) * 100
          const baseTop = ((40.1 - property.latitude) / 0.4) * 100
          const left = Math.max(5, Math.min(90, baseLeft))
          const top = Math.max(5, Math.min(90, baseTop))
          
          const isSelected = selectedProperty?.id === property.id
          
          return (
            <button
              key={property.id}
              className={`absolute transform -translate-x-1/2 -translate-y-full transition-all duration-200 ${
                isSelected ? 'z-20 scale-125' : 'z-10 hover:scale-110'
              }`}
              style={{ left: `${left}%`, top: `${top}%` }}
              onClick={() => onSelectProperty(isSelected ? null : property)}
            >
              <div className={`relative ${isSelected ? 'animate-bounce' : ''}`}>
                <MapPin 
                  className={`h-8 w-8 drop-shadow-lg ${
                    property.status === 'available' ? 'text-green-500' :
                    property.status === 'pending' ? 'text-yellow-500' :
                    'text-red-500'
                  }`}
                  fill="currentColor"
                />
                <span className="absolute -top-1 -right-1 text-xs">
                  {propertyTypeIcons[property.propertyType]}
                </span>
              </div>
              
              {/* Price label */}
              <div className={`absolute top-full left-1/2 -translate-x-1/2 mt-1 px-2 py-0.5 bg-white rounded shadow text-xs font-medium whitespace-nowrap ${
                isSelected ? 'block' : 'hidden group-hover:block'
              }`}>
                {property.type === 'rent' ? `${property.currency}${property.price.toLocaleString()}/mo` : `${property.currency}${(property.price / 1000000).toFixed(1)}M`}
              </div>
            </button>
          )
        })}
      </div>

      {/* Info card for selected property */}
      {selectedProperty && (
        <div className="absolute bottom-4 left-4 right-4 md:left-auto md:right-4 md:w-80 z-30">
          <Card className="shadow-xl">
            <CardContent className="p-4">
              <div className="flex justify-between items-start mb-2">
                <Badge variant={selectedProperty.status === 'available' ? 'default' : 'secondary'}>
                  {selectedProperty.status}
                </Badge>
                <Button variant="ghost" size="sm" onClick={() => onSelectProperty(null)}>
                  <X className="h-4 w-4" />
                </Button>
              </div>
              <h3 className="font-bold mb-1">{selectedProperty.title}</h3>
              <p className="text-sm text-muted-foreground mb-2">{selectedProperty.address}</p>
              <div className="flex items-center gap-4 text-sm mb-3">
                <span>{selectedProperty.bedrooms} bed</span>
                <span>{selectedProperty.area} m²</span>
                <span className="font-bold text-blue-600">
                  {selectedProperty.type === 'rent' 
                    ? `${selectedProperty.currency}${selectedProperty.price.toLocaleString()}/mo`
                    : `${selectedProperty.currency}${selectedProperty.price.toLocaleString()}`
                  }
                </span>
              </div>
              <Link href={`/properties/${selectedProperty.id}`}>
                <Button className="w-full" size="sm">
                  <ExternalLink className="mr-2 h-4 w-4" />
                  View Details
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Map controls */}
      <div className="absolute top-4 right-4 flex flex-col gap-2">
        <Button variant="secondary" size="icon" className="shadow">
          <span className="text-lg">+</span>
        </Button>
        <Button variant="secondary" size="icon" className="shadow">
          <span className="text-lg">−</span>
        </Button>
      </div>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 bg-white/90 backdrop-blur rounded-lg p-3 shadow md:bottom-auto md:top-4 md:left-4">
        <p className="text-xs font-medium mb-2">Property Status</p>
        <div className="flex flex-col gap-1 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-green-500" />
            <span>Available</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-yellow-500" />
            <span>Pending</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-red-500" />
            <span>Sold/Rented</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function PropertiesMapPage() {
  const router = useRouter()
  const [properties] = useState(mockProperties)
  const [selectedProperty, setSelectedProperty] = useState<typeof mockProperties[0] | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [typeFilter, setTypeFilter] = useState('all')
  const [propertyTypeFilter, setPropertyTypeFilter] = useState('all')
  const [showFilters, setShowFilters] = useState(false)

  // Filter properties
  const filteredProperties = properties.filter(p => {
    const matchesSearch = p.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         p.address.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesType = typeFilter === 'all' || p.type === typeFilter
    const matchesPropertyType = propertyTypeFilter === 'all' || p.propertyType === propertyTypeFilter
    return matchesSearch && matchesType && matchesPropertyType
  })

  return (
    <div className="h-[calc(100vh-120px)] flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-2xl font-bold">Property Map</h1>
          <p className="text-muted-foreground">{filteredProperties.length} properties</p>
        </div>
        <div className="flex gap-2">
          <Link href="/properties">
            <Button variant="outline">
              <List className="mr-2 h-4 w-4" />
              List View
            </Button>
          </Link>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="flex gap-2 mb-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search properties..."
            className="pl-10"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <Button 
          variant={showFilters ? 'default' : 'outline'}
          onClick={() => setShowFilters(!showFilters)}
        >
          <Filter className="mr-2 h-4 w-4" />
          Filters
        </Button>
      </div>

      {/* Filter panel */}
      {showFilters && (
        <div className="flex gap-4 mb-4 p-4 bg-gray-50 rounded-lg">
          <Select value={typeFilter} onValueChange={setTypeFilter}>
            <SelectTrigger className="w-32">
              <SelectValue placeholder="Type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Types</SelectItem>
              <SelectItem value="sale">For Sale</SelectItem>
              <SelectItem value="rent">For Rent</SelectItem>
            </SelectContent>
          </Select>
          <Select value={propertyTypeFilter} onValueChange={setPropertyTypeFilter}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Property Type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Properties</SelectItem>
              <SelectItem value="apartment">Apartment</SelectItem>
              <SelectItem value="villa">Villa</SelectItem>
              <SelectItem value="office">Office</SelectItem>
              <SelectItem value="commercial">Commercial</SelectItem>
              <SelectItem value="land">Land</SelectItem>
            </SelectContent>
          </Select>
          {(typeFilter !== 'all' || propertyTypeFilter !== 'all' || searchQuery) && (
            <Button variant="ghost" onClick={() => {
              setTypeFilter('all')
              setPropertyTypeFilter('all')
              setSearchQuery('')
            }}>
              Clear Filters
            </Button>
          )}
        </div>
      )}

      {/* Map */}
      <div className="flex-1 rounded-lg overflow-hidden border">
        <GoogleMapsView
          properties={filteredProperties}
          onSelectProperty={setSelectedProperty}
          selectedProperty={selectedProperty}
        />
      </div>
    </div>
  )
}
