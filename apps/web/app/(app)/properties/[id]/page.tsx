'use client'

import { useParams } from 'next/navigation'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Separator } from '@/components/ui/separator'
import { 
  ArrowLeft, Edit, MapPin, Bed, Bath, Square, Calendar, Share2,
  Heart, Phone, Mail, Building2, Car, Wifi, Trees, Shield, Droplet
} from 'lucide-react'

// Mock property data
const mockProperty = {
  id: 'prop-1',
  title: 'Modern 3+1 Apartment in Çankaya',
  address: 'Kızılırmak Caddesi No:45',
  city: 'Ankara',
  district: 'Çankaya',
  price: 2500000,
  currency: 'TRY',
  type: 'sale',
  propertyType: 'apartment',
  bedrooms: 3,
  bathrooms: 2,
  area: 145,
  yearBuilt: 2022,
  floor: 8,
  totalFloors: 12,
  latitude: 39.9208,
  longitude: 32.8541,
  features: ['Balcony', 'Parking', 'Security', 'Pool', 'Gym', 'Central Heating'],
  images: [
    'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=800',
    'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800',
    'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800',
    'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800',
  ],
  status: 'available',
  description: 'This stunning modern apartment offers luxurious living in the heart of Çankaya. With 3 spacious bedrooms and 2 full bathrooms, this unit provides ample space for families. The open-concept living area features floor-to-ceiling windows with breathtaking city views. The modern kitchen comes equipped with high-end appliances and custom cabinetry. Building amenities include 24/7 security, swimming pool, fitness center, and covered parking.',
  agent: { id: 'user-1', name: 'Ahmet Yılmaz', phone: '+90 532 111 2233', email: 'ahmet@dynamiccrm.com' },
  createdAt: '2024-01-10',
  updatedAt: '2024-01-15',
  views: 245,
  inquiries: 12,
}

const featureIcons: Record<string, any> = {
  'Parking': Car,
  'Balcony': Building2,
  'Security': Shield,
  'Pool': Droplet,
  'Gym': Building2,
  'Central Heating': Building2,
  'Garden': Trees,
  'WiFi': Wifi,
}

const similarProperties = [
  { id: 'prop-7', title: 'Penthouse with Terrace', price: 6500000, area: 220, bedrooms: 4, district: 'Çankaya', image: 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=400' },
  { id: 'prop-4', title: '2+1 Apartment Near Metro', price: 1800000, area: 95, bedrooms: 2, district: 'Kızılay', image: 'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=400' },
  { id: 'prop-8', title: 'Cozy 1+1 for Rent', price: 15000, area: 55, bedrooms: 1, district: 'Bahçelievler', image: 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=400' },
]

const statusColors: Record<string, string> = {
  available: 'bg-green-500',
  pending: 'bg-yellow-500',
  sold: 'bg-blue-500',
  rented: 'bg-purple-500',
}

export default function PropertyDetailPage() {
  const params = useParams()
  const property = mockProperty // In real app, fetch by params.id

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/properties">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-5 w-5" />
            </Button>
          </Link>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold">{property.title}</h1>
              <Badge className={statusColors[property.status]}>{property.status}</Badge>
            </div>
            <div className="flex items-center gap-1 text-muted-foreground mt-1">
              <MapPin className="h-4 w-4" />
              {property.address}, {property.district}, {property.city}
            </div>
          </div>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" size="icon">
            <Heart className="h-5 w-5" />
          </Button>
          <Button variant="outline" size="icon">
            <Share2 className="h-5 w-5" />
          </Button>
          <Link href={`/properties/${property.id}/schedule`}>
            <Button variant="outline">
              <Calendar className="mr-2 h-4 w-4" />
              Schedule Viewing
            </Button>
          </Link>
          <Link href={`/properties/${property.id}/edit`}>
            <Button>
              <Edit className="mr-2 h-4 w-4" />
              Edit Property
            </Button>
          </Link>
        </div>
      </div>

      {/* Image Gallery */}
      <div className="grid grid-cols-4 gap-4">
        <div className="col-span-2 row-span-2">
          <img
            src={property.images[0]}
            alt={property.title}
            className="w-full h-full object-cover rounded-lg"
          />
        </div>
        {property.images.slice(1, 5).map((image, index) => (
          <div key={index}>
            <img
              src={image}
              alt={`${property.title} ${index + 2}`}
              className="w-full h-48 object-cover rounded-lg"
            />
          </div>
        ))}
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Price and Key Details */}
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <p className="text-3xl font-bold text-blue-600">
                    ₺{property.price.toLocaleString()}
                    {property.type === 'rent' && <span className="text-lg font-normal">/month</span>}
                  </p>
                  <p className="text-muted-foreground">
                    ₺{Math.round(property.price / property.area).toLocaleString()}/m²
                  </p>
                </div>
                <Badge variant="secondary" className="text-lg px-4 py-2">
                  {property.type === 'sale' ? 'For Sale' : 'For Rent'}
                </Badge>
              </div>
              <div className="grid grid-cols-4 gap-4 text-center">
                <div className="p-4 bg-gray-50 rounded-lg">
                  <Bed className="h-6 w-6 mx-auto mb-2 text-gray-600" />
                  <p className="text-2xl font-bold">{property.bedrooms}</p>
                  <p className="text-sm text-muted-foreground">Bedrooms</p>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <Bath className="h-6 w-6 mx-auto mb-2 text-gray-600" />
                  <p className="text-2xl font-bold">{property.bathrooms}</p>
                  <p className="text-sm text-muted-foreground">Bathrooms</p>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <Square className="h-6 w-6 mx-auto mb-2 text-gray-600" />
                  <p className="text-2xl font-bold">{property.area}</p>
                  <p className="text-sm text-muted-foreground">m² Area</p>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <Building2 className="h-6 w-6 mx-auto mb-2 text-gray-600" />
                  <p className="text-2xl font-bold">{property.floor}/{property.totalFloors}</p>
                  <p className="text-sm text-muted-foreground">Floor</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Tabs defaultValue="details">
            <TabsList>
              <TabsTrigger value="details">Details</TabsTrigger>
              <TabsTrigger value="features">Features</TabsTrigger>
              <TabsTrigger value="location">Location</TabsTrigger>
            </TabsList>

            <TabsContent value="details" className="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle>Description</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground whitespace-pre-line">{property.description}</p>
                  
                  <Separator className="my-6" />
                  
                  <h4 className="font-semibold mb-4">Property Details</h4>
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="flex justify-between py-2 border-b">
                      <span className="text-muted-foreground">Property Type</span>
                      <span className="font-medium capitalize">{property.propertyType}</span>
                    </div>
                    <div className="flex justify-between py-2 border-b">
                      <span className="text-muted-foreground">Year Built</span>
                      <span className="font-medium">{property.yearBuilt}</span>
                    </div>
                    <div className="flex justify-between py-2 border-b">
                      <span className="text-muted-foreground">Floor</span>
                      <span className="font-medium">{property.floor} of {property.totalFloors}</span>
                    </div>
                    <div className="flex justify-between py-2 border-b">
                      <span className="text-muted-foreground">Area</span>
                      <span className="font-medium">{property.area} m²</span>
                    </div>
                    <div className="flex justify-between py-2 border-b">
                      <span className="text-muted-foreground">Bedrooms</span>
                      <span className="font-medium">{property.bedrooms}</span>
                    </div>
                    <div className="flex justify-between py-2 border-b">
                      <span className="text-muted-foreground">Bathrooms</span>
                      <span className="font-medium">{property.bathrooms}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="features" className="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle>Features & Amenities</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid md:grid-cols-3 gap-4">
                    {property.features.map((feature) => {
                      const Icon = featureIcons[feature] || Building2
                      return (
                        <div key={feature} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                          <Icon className="h-5 w-5 text-blue-600" />
                          <span>{feature}</span>
                        </div>
                      )
                    })}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="location" className="mt-6">
              <Card>
                <CardHeader>
                  <CardTitle>Location</CardTitle>
                  <CardDescription>{property.address}, {property.district}, {property.city}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
                    <div className="text-center">
                      <MapPin className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                      <p className="text-muted-foreground">Map view</p>
                      <p className="text-sm text-muted-foreground">
                        Coordinates: {property.latitude}, {property.longitude}
                      </p>
                      <Link href="/properties/map">
                        <Button variant="outline" className="mt-4">
                          View on Map
                        </Button>
                      </Link>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          {/* Similar Properties */}
          <Card>
            <CardHeader>
              <CardTitle>Similar Properties</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-3 gap-4">
                {similarProperties.map((prop) => (
                  <Link key={prop.id} href={`/properties/${prop.id}`}>
                    <div className="border rounded-lg overflow-hidden hover:shadow-md transition-shadow">
                      <img src={prop.image} alt={prop.title} className="w-full h-32 object-cover" />
                      <div className="p-3">
                        <h4 className="font-medium text-sm truncate">{prop.title}</h4>
                        <p className="text-xs text-muted-foreground">{prop.district}</p>
                        <p className="text-sm font-bold text-blue-600 mt-1">
                          ₺{prop.price.toLocaleString()}
                        </p>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Agent Card */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Contact Agent</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-semibold">
                  {property.agent.name.split(' ').map(n => n[0]).join('')}
                </div>
                <div>
                  <p className="font-medium">{property.agent.name}</p>
                  <p className="text-sm text-muted-foreground">Sales Agent</p>
                </div>
              </div>
              <div className="space-y-3">
                <Button className="w-full" variant="default">
                  <Phone className="mr-2 h-4 w-4" />
                  {property.agent.phone}
                </Button>
                <Button className="w-full" variant="outline">
                  <Mail className="mr-2 h-4 w-4" />
                  Send Email
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Schedule Viewing */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Schedule a Viewing</CardTitle>
            </CardHeader>
            <CardContent>
              <Link href={`/properties/${property.id}/schedule`}>
                <Button className="w-full">
                  <Calendar className="mr-2 h-4 w-4" />
                  Book Appointment
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* Property Stats */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Statistics</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Views</span>
                <span className="font-medium">{property.views}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Inquiries</span>
                <span className="font-medium">{property.inquiries}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Listed</span>
                <span className="font-medium">{property.createdAt}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Updated</span>
                <span className="font-medium">{property.updatedAt}</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
