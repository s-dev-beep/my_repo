'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { ScrollArea } from '@/components/ui/scroll-area'
import {
  LayoutDashboard,
  Users,
  Building2,
  CheckSquare,
  Calendar,
  Phone,
  BarChart3,
  Settings,
  Gift,
  Store,
  Target,
  Shield,
  MapPin,
  UserCog,
  ChevronDown,
} from 'lucide-react'

const navigation = [
  {
    title: 'Dashboards',
    items: [
      { name: 'Agent Dashboard', href: '/dashboard/agent', icon: LayoutDashboard },
      { name: 'Team Lead', href: '/dashboard/team-lead', icon: Users },
      { name: 'Owner', href: '/dashboard/owner', icon: Building2 },
      { name: 'Admin', href: '/dashboard/admin', icon: Shield },
      { name: 'Call Center', href: '/dashboard/call-center', icon: Phone },
      { name: 'Marketplace', href: '/dashboard/marketplace', icon: Store },
    ],
  },
  {
    title: 'CRM',
    items: [
      { name: 'Leads', href: '/leads', icon: Users },
      { name: 'Properties', href: '/properties', icon: Building2 },
      { name: 'Map View', href: '/properties/map', icon: MapPin },
      { name: 'Matching', href: '/matching', icon: Target },
    ],
  },
  {
    title: 'Operations',
    items: [
      { name: 'Tasks', href: '/tasks', icon: CheckSquare },
      { name: 'Calendar', href: '/calendar', icon: Calendar },
      { name: 'Calls', href: '/calls', icon: Phone },
    ],
  },
  {
    title: 'Analytics',
    items: [
      { name: 'Reports', href: '/analytics', icon: BarChart3 },
    ],
  },
  {
    title: 'Admin',
    items: [
      { name: 'Users', href: '/admin/users', icon: UserCog },
      { name: 'Roles', href: '/admin/roles', icon: Shield },
      { name: 'Settings', href: '/admin/settings', icon: Settings },
      { name: 'Audit Log', href: '/admin/audit', icon: CheckSquare },
      { name: 'System', href: '/admin/system', icon: Settings },
    ],
  },
  {
    title: 'Engagement',
    items: [
      { name: 'Loyalty', href: '/loyalty', icon: Gift },
      { name: 'Marketplace', href: '/marketplace', icon: Store },
    ],
  },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <div className="flex h-full w-64 flex-col border-r bg-white">
      <div className="flex h-16 items-center border-b px-6">
        <Link href="/" className="flex items-center gap-2 font-bold text-xl">
          <Building2 className="h-6 w-6 text-blue-600" />
          <span>Dynamic CRM</span>
        </Link>
      </div>
      <ScrollArea className="flex-1 px-3 py-4">
        <nav className="space-y-6">
          {navigation.map((section) => (
            <div key={section.title}>
              <h3 className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-gray-500">
                {section.title}
              </h3>
              <div className="space-y-1">
                {section.items.map((item) => {
                  const isActive = pathname === item.href || pathname.startsWith(item.href + '/')
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      className={cn(
                        'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                        isActive
                          ? 'bg-blue-50 text-blue-600'
                          : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
                      )}
                    >
                      <item.icon className="h-5 w-5" />
                      {item.name}
                    </Link>
                  )
                })}
              </div>
            </div>
          ))}
        </nav>
      </ScrollArea>
    </div>
  )
}
