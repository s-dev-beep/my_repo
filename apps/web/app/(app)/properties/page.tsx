'use client'

import { useState } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
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
  Building2, Plus, Search, Filter, Download, Upload, MapPin, 
  Bed, Bath, Square, Grid, List, Map, MoreVertical, Eye, Edit, Trash2
} from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'

const properties = [
  { id: 'prop-1', title: 'Modern 3+1 Apartment in Çankaya', address: 'Kızılırmak Caddesi No:45', city: 'Ankara', district: 'Çankaya', price: 2500000, type: 'sale', propertyType: 'apartment', bedrooms: 3, bathrooms: 2, area: 145, status: 'available', image: 'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=400' },
  { id: 'prop-2', title: 'Luxury Villa with Garden', address: 'Oran Sitesi 15. Cadde', city: 'Ankara', district: 'Oran', price: 8500000, type: 'sale', propertyType: 'villa', bedrooms: 5, bathrooms: 4, area: 350, status: 'available', image: 'https://images.unsplash.com/photo-1613490493576-7fde63acd811?w=400' },
  { id: 'prop-3', title: 'Office Space in Business Center', address: 'Eskişehir Yolu 8. km', city: 'Ankara', district: 'Çankaya', price: 45000, type: 'rent', propertyType: 'office', bedrooms: 0, bathrooms: 2, area: 200, status: 'available', image: 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=400' },
  { id: 'prop-4', title: '2+1 Apartment Near Metro', address: 'Kızılay Meydanı Yakını', city: 'Ankara', district: 'Kızılay', price: 1800000, type: 'sale', propertyType: 'apartment', bedrooms: 2, bathrooms: 1, area: 95, status: 'pending', image: 'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=400' },
  { id: 'prop-5', title: 'Commercial Space for Retail', address: 'Tunalı Hilmi Caddesi', city: 'Ankara', district: 'Kavaklıdere', price: 75000, type: 'rent', propertyType: 'commercial', bedrooms: 0, bathrooms: 1, area: 120, status: 'available', image: 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400' },
  { id: 'prop-6', title: 'Investment Land in Çayyolu', address: 'Çayyolu 8. Cadde', city: 'Ankara', district: 'Çayyolu', price: 12000000, type: 'sale', propertyType: 'land', bedrooms: 0, bathrooms: 0, area: 5000, status: 'available', image: 'https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=400' },
]

const statusColors: Record<string, string> = {
  available: 'bg-green-500',
  pending: 'bg-yellow-500',
  sold: 'bg-blue-500',
  rented: 'bg-purple-500',
}

const stats = [
  { label: 'Total Properties', value: properties.length },
  { label: 'For Sale', value: properties.filter(p => p.type === 'sale').length },
  { label: 'For Rent', value: properties.filter(p => p.type === 'rent').length },
  { label: 'Available', value: properties.filter(p => p.status === 'available').length },
]

export default function PropertiesPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [typeFilter, setTypeFilter] = useState<string>('all')
  const [propertyTypeFilter, setPropertyTypeFilter] = useState<string>('all')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')

  const filteredProperties = properties.filter(property => {
    const matchesSearch = property.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         property.address.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         property.district.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesType = typeFilter === 'all' || property.type === typeFilter
    const matchesPropertyType = propertyTypeFilter === 'all' || property.propertyType === propertyTypeFilter
    return matchesSearch && matchesType && matchesPropertyType
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Properties</h1>
          <p className="text-gray-500 mt-1">Manage your property listings</p>
        </div>
        <div className="flex gap-3">
          <Link href="/properties/map">
            <Button variant="outline">
              <Map className="mr-2 h-4 w-4" />
              Map View
            </Button>
          </Link>
          <Link href="/properties/import">
            <Button variant="outline">
              <Upload className="mr-2 h-4 w-4" />
              Import
            </Button>
          </Link>
          <Link href="/properties/new">
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Add Property
            </Button>
          </Link>
        </div>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.label}>
            <CardContent className="p-4">
              <p className="text-sm text-muted-foreground">{stat.label}</p>
              <p className="text-2xl font-bold">{stat.value}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search properties by title, address, or district..."
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
            <div className="flex gap-1 border rounded-md p-1">
              <Button
                variant={viewMode === 'grid' ? 'default' : 'ghost'}
                size="icon"
                onClick={() => setViewMode('grid')}
              >
                <Grid className="h-4 w-4" />
              </Button>
              <Button
                variant={viewMode === 'list' ? 'default' : 'ghost'}
                size="icon"
                onClick={() => setViewMode('list')}
              >
                <List className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Property Grid */}
      {viewMode === 'grid' ? (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filteredProperties.map((property) => (
            <Card key={property.id} className="overflow-hidden hover:shadow-lg transition-shadow">
              <div className="relative h-48">
                <img
                  src={property.image}
                  alt={property.title}
                  className="w-full h-full object-cover"
                />
                <Badge className={`absolute top-3 left-3 ${statusColors[property.status]}`}>
                  {property.status}
                </Badge>
                <Badge className="absolute top-3 right-3" variant="secondary">
                  {property.type === 'sale' ? 'For Sale' : 'For Rent'}
                </Badge>
              </div>
              <CardContent className="p-4">
                <Link href={`/properties/${property.id}`}>
                  <h3 className="font-semibold text-lg hover:text-blue-600">{property.title}</h3>
                </Link>
                <div className="flex items-center gap-1 text-muted-foreground text-sm mt-1">
                  <MapPin className="h-3 w-3" />
                  {property.district}, {property.city}
                </div>
                <div className="flex items-center gap-4 mt-3 text-sm text-muted-foreground">
                  {property.bedrooms > 0 && (
                    <div className="flex items-center gap-1">
                      <Bed className="h-4 w-4" />
                      {property.bedrooms}
                    </div>
                  )}
                  {property.bathrooms > 0 && (
                    <div className="flex items-center gap-1">
                      <Bath className="h-4 w-4" />
                      {property.bathrooms}
                    </div>
                  )}
                  <div className="flex items-center gap-1">
                    <Square className="h-4 w-4" />
                    {property.area} m²
                  </div>
                </div>
                <div className="flex items-center justify-between mt-4">
                  <p className="text-xl font-bold text-blue-600">
                    ₺{property.price.toLocaleString()}
                    {property.type === 'rent' && <span className="text-sm font-normal">/mo</span>}
                  </p>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon">
                        <MoreVertical className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem asChild>
                        <Link href={`/properties/${property.id}`}>
                          <Eye className="mr-2 h-4 w-4" />
                          View Details
                        </Link>
                      </DropdownMenuItem>
                      <DropdownMenuItem asChild>
                        <Link href={`/properties/${property.id}/edit`}>
                          <Edit className="mr-2 h-4 w-4" />
                          Edit
                        </Link>
                      </DropdownMenuItem>
                      <DropdownMenuItem className="text-red-600">
                        <Trash2 className="mr-2 h-4 w-4" />
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="p-0">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 font-medium">Property</th>
                  <th className="text-left py-3 px-4 font-medium">Type</th>
                  <th className="text-left py-3 px-4 font-medium">Location</th>
                  <th className="text-left py-3 px-4 font-medium">Price</th>
                  <th className="text-left py-3 px-4 font-medium">Status</th>
                  <th className="text-left py-3 px-4 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredProperties.map((property) => (
                  <tr key={property.id} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-4">
                      <Link href={`/properties/${property.id}`} className="flex items-center gap-3">
                        <img src={property.image} alt="" className="w-16 h-12 object-cover rounded" />
                        <div>
                          <p className="font-medium hover:text-blue-600">{property.title}</p>
                          <p className="text-sm text-muted-foreground">{property.area} m²</p>
                        </div>
                      </Link>
                    </td>
                    <td className="py-3 px-4 capitalize">{property.propertyType}</td>
                    <td className="py-3 px-4">{property.district}, {property.city}</td>
                    <td className="py-3 px-4 font-medium">
                      ₺{property.price.toLocaleString()}
                      {property.type === 'rent' && '/mo'}
                    </td>
                    <td className="py-3 px-4">
                      <Badge className={statusColors[property.status]}>{property.status}</Badge>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex gap-2">
                        <Link href={`/properties/${property.id}`}>
                          <Button variant="ghost" size="icon">
                            <Eye className="h-4 w-4" />
                          </Button>
                        </Link>
                        <Link href={`/properties/${property.id}/edit`}>
                          <Button variant="ghost" size="icon">
                            <Edit className="h-4 w-4" />
                          </Button>
                        </Link>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
