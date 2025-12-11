import Link from 'next/link'
import { Building2, Users, MapPin, Calendar, Phone, BarChart3 } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Dynamic CRM
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Complete Real Estate Management Solution
          </p>
          <Link
            href="/dashboard/agent"
            className="inline-flex items-center px-8 py-4 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
          >
            Enter Dashboard
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
          <FeatureCard
            icon={<Users className="w-8 h-8" />}
            title="Lead Management"
            description="Track and manage leads through the entire sales pipeline"
            href="/leads"
          />
          <FeatureCard
            icon={<Building2 className="w-8 h-8" />}
            title="Property Catalog"
            description="Comprehensive property listings with rich details"
            href="/properties"
          />
          <FeatureCard
            icon={<MapPin className="w-8 h-8" />}
            title="Map View"
            description="Interactive Google Maps integration for properties"
            href="/properties/map"
          />
          <FeatureCard
            icon={<Calendar className="w-8 h-8" />}
            title="Task Management"
            description="Organize tasks and schedule property viewings"
            href="/tasks"
          />
          <FeatureCard
            icon={<Phone className="w-8 h-8" />}
            title="Call Center"
            description="Integrated calling and communication tools"
            href="/calls"
          />
          <FeatureCard
            icon={<BarChart3 className="w-8 h-8" />}
            title="Analytics"
            description="Comprehensive reporting and analytics dashboard"
            href="/analytics"
          />
        </div>
      </div>
    </div>
  )
}

function FeatureCard({
  icon,
  title,
  description,
  href,
}: {
  icon: React.ReactNode
  title: string
  description: string
  href: string
}) {
  return (
    <Link href={href}>
      <div className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow cursor-pointer">
        <div className="text-blue-600 mb-4">{icon}</div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">{title}</h3>
        <p className="text-gray-600">{description}</p>
      </div>
    </Link>
  )
}
