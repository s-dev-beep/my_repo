'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Store, Search, Star, Users, Briefcase, GraduationCap, Wrench } from 'lucide-react'

const categories = [
  { name: 'Leads', count: 25, icon: Users },
  { name: 'Services', count: 48, icon: Briefcase },
  { name: 'Training', count: 15, icon: GraduationCap },
  { name: 'Tools', count: 32, icon: Wrench },
]

const products = [
  { id: 'mp-1', title: 'Lead Package - 50 Qualified Leads', price: 5000, seller: 'LeadGen Pro', rating: 4.8, sales: 156, category: 'Leads', description: 'High-quality verified leads' },
  { id: 'mp-2', title: 'Property Photography Service', price: 1500, seller: 'ProPhoto', rating: 4.9, sales: 89, category: 'Services', description: 'Professional real estate photography' },
  { id: 'mp-3', title: 'Virtual Tour Package', price: 2500, seller: '360 Tours', rating: 4.7, sales: 45, category: 'Services', description: '360° virtual property tours' },
  { id: 'mp-4', title: 'CRM Training Course', price: 3000, seller: 'CRM Academy', rating: 4.6, sales: 234, category: 'Training', description: 'Complete CRM mastery course' },
  { id: 'mp-5', title: 'Lead Scoring Tool', price: 2000, seller: 'SalesTools', rating: 4.5, sales: 67, category: 'Tools', description: 'AI-powered lead scoring' },
  { id: 'mp-6', title: 'Email Templates Pack', price: 500, seller: 'TemplateHub', rating: 4.4, sales: 312, category: 'Tools', description: '50+ professional templates' },
]

export default function MarketplacePage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('all')

  const filteredProducts = products.filter(p => {
    const matchesSearch = p.title.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesCategory = categoryFilter === 'all' || p.category === categoryFilter
    return matchesSearch && matchesCategory
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Marketplace</h1>
          <p className="text-gray-500 mt-1">Find tools, services, and resources</p>
        </div>
        <Button><Store className="mr-2 h-4 w-4" />Sell Product</Button>
      </div>

      <div className="grid md:grid-cols-4 gap-4">
        {categories.map((cat) => (
          <Card key={cat.name} className="cursor-pointer hover:shadow-md" onClick={() => setCategoryFilter(cat.name)}>
            <CardContent className="p-4 flex items-center gap-4">
              <div className="p-3 bg-blue-100 rounded-lg"><cat.icon className="h-6 w-6 text-blue-600" /></div>
              <div><p className="font-medium">{cat.name}</p><p className="text-sm text-muted-foreground">{cat.count} items</p></div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardContent className="p-4">
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input placeholder="Search marketplace..." className="pl-10" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} />
            </div>
            <Select value={categoryFilter} onValueChange={setCategoryFilter}>
              <SelectTrigger className="w-40"><SelectValue placeholder="Category" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                {categories.map(cat => (<SelectItem key={cat.name} value={cat.name}>{cat.name}</SelectItem>))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredProducts.map((product) => (
          <Link key={product.id} href={`/marketplace/${product.id}`}>
            <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
              <CardContent className="pt-6">
                <div className="flex items-start justify-between mb-3">
                  <Badge variant="secondary">{product.category}</Badge>
                  <div className="flex items-center gap-1">
                    <Star className="h-4 w-4 text-yellow-500 fill-yellow-500" />
                    <span className="text-sm font-medium">{product.rating}</span>
                  </div>
                </div>
                <h3 className="font-bold text-lg mb-2">{product.title}</h3>
                <p className="text-sm text-muted-foreground mb-4">{product.description}</p>
                <p className="text-xs text-muted-foreground mb-3">by {product.seller} • {product.sales} sales</p>
                <div className="flex items-center justify-between">
                  <p className="text-xl font-bold text-blue-600">₺{product.price.toLocaleString()}</p>
                  <Button size="sm">View Details</Button>
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  )
}
