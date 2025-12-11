'use client'

import { useEffect, useRef, useState } from 'react'

interface Property {
  id: string
  title: string
  price: number
  currency: string
  type: string
  latitude: number
  longitude: number
  status: string
  address?: string
}

interface GoogleMapProps {
  properties: Property[]
  onSelectProperty?: (property: Property | null) => void
  selectedProperty?: Property | null
  center?: { lat: number; lng: number }
  zoom?: number
  className?: string
}

// Declare google as global
declare global {
  interface Window {
    google: typeof google
    initMap: () => void
  }
}

export function GoogleMapComponent({
  properties,
  onSelectProperty,
  selectedProperty,
  center = { lat: 39.9334, lng: 32.8597 }, // Ankara default
  zoom = 12,
  className = 'w-full h-full',
}: GoogleMapProps) {
  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstanceRef = useRef<google.maps.Map | null>(null)
  const markersRef = useRef<google.maps.Marker[]>([])
  const infoWindowRef = useRef<google.maps.InfoWindow | null>(null)
  const [isLoaded, setIsLoaded] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Load Google Maps script
  useEffect(() => {
    const apiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY

    if (!apiKey) {
      setError('Google Maps API key not configured')
      return
    }

    // Check if already loaded
    if (window.google?.maps) {
      setIsLoaded(true)
      return
    }

    // Create script element
    const script = document.createElement('script')
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&callback=initMap`
    script.async = true
    script.defer = true

    // Set up callback
    window.initMap = () => {
      setIsLoaded(true)
    }

    script.onerror = () => {
      setError('Failed to load Google Maps')
    }

    document.head.appendChild(script)

    return () => {
      // Cleanup
      const existingScript = document.querySelector(`script[src*="maps.googleapis.com"]`)
      if (existingScript) {
        existingScript.remove()
      }
    }
  }, [])

  // Initialize map
  useEffect(() => {
    if (!isLoaded || !mapRef.current || mapInstanceRef.current) return
    if (!window.google?.maps) return

    const newMap = new window.google.maps.Map(mapRef.current, {
      center,
      zoom,
      styles: [
        {
          featureType: 'poi',
          elementType: 'labels',
          stylers: [{ visibility: 'off' }],
        },
      ],
      mapTypeControl: true,
      streetViewControl: true,
      fullscreenControl: true,
    })

    const newInfoWindow = new window.google.maps.InfoWindow()

    mapInstanceRef.current = newMap
    infoWindowRef.current = newInfoWindow
  }, [isLoaded, center, zoom])

  // Add markers
  useEffect(() => {
    const map = mapInstanceRef.current
    const infoWindow = infoWindowRef.current
    if (!map || !infoWindow || !window.google?.maps) return

    // Clear existing markers
    markersRef.current.forEach((marker) => marker.setMap(null))
    markersRef.current = []

    // Create new markers
    properties.forEach((property) => {
      const markerColor = 
        property.status === 'available' ? '#22c55e' :
        property.status === 'pending' ? '#eab308' :
        '#ef4444'

      const marker = new window.google.maps.Marker({
        position: { lat: property.latitude, lng: property.longitude },
        map,
        title: property.title,
        icon: {
          path: window.google.maps.SymbolPath.CIRCLE,
          fillColor: markerColor,
          fillOpacity: 1,
          strokeColor: '#ffffff',
          strokeWeight: 2,
          scale: 10,
        },
      })

      // Click handler
      marker.addListener('click', () => {
        const content = `
          <div style="max-width: 250px; padding: 8px;">
            <h3 style="font-weight: bold; margin-bottom: 4px;">${property.title}</h3>
            <p style="color: #666; font-size: 14px; margin-bottom: 8px;">${property.address || 'No address'}</p>
            <p style="font-weight: bold; color: #2563eb; font-size: 16px; margin-bottom: 8px;">
              ${property.type === 'rent' 
                ? `${property.currency}${property.price.toLocaleString()}/mo`
                : `${property.currency}${property.price.toLocaleString()}`
              }
            </p>
            <a href="/properties/${property.id}" 
               style="display: inline-block; background: #2563eb; color: white; padding: 8px 16px; 
                      border-radius: 4px; text-decoration: none; font-size: 14px;">
              View Details
            </a>
          </div>
        `
        infoWindow.setContent(content)
        infoWindow.open(map, marker)
        onSelectProperty?.(property)
      })

      markersRef.current.push(marker)
    })
  }, [isLoaded, properties, onSelectProperty])

  // Center on selected property
  useEffect(() => {
    const map = mapInstanceRef.current
    if (!map || !selectedProperty) return

    map.panTo({ lat: selectedProperty.latitude, lng: selectedProperty.longitude })
    map.setZoom(15)
  }, [selectedProperty])

  if (error) {
    return (
      <div className={`${className} flex items-center justify-center bg-gray-100`}>
        <div className="text-center p-4">
          <p className="text-red-500 font-medium">{error}</p>
          <p className="text-sm text-gray-500 mt-2">
            Please configure NEXT_PUBLIC_GOOGLE_MAPS_API_KEY in your .env.local file
          </p>
        </div>
      </div>
    )
  }

  if (!isLoaded) {
    return (
      <div className={`${className} flex items-center justify-center bg-gray-100`}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
          <p className="text-gray-500">Loading map...</p>
        </div>
      </div>
    )
  }

  return <div ref={mapRef} className={className} />
}

export default GoogleMapComponent
