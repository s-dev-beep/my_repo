'use client'

import Link from 'next/link'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ArrowLeft, Star, ShoppingCart, CheckCircle2, User } from 'lucide-react'

const product = {
  id: 'mp-1',
  title: 'Lead Package - 50 Qualified Leads',
  price: 5000,
  seller: { name: 'LeadGen Pro', rating: 4.8, sales: 1250 },
  rating: 4.8,
  reviews: 156,
  sales: 156,
  category: 'Leads',
  description: 'Get 50 high-quality, verified leads for your real estate business. All leads are pre-qualified and include contact information, budget, and property preferences.',
  features: ['Verified contact information', 'Pre-qualified buyers', 'Budget confirmed', 'Property preferences included', 'Delivered within 48 hours'],
}

const reviews = [
  { id: 1, user: 'Ahmet Y.', rating: 5, comment: 'Excellent lead quality! Closed 3 deals from this package.', date: '2024-01-10' },
  { id: 2, user: 'Fatma D.', rating: 4, comment: 'Good leads, fast delivery. Will buy again.', date: '2024-01-08' },
  { id: 3, user: 'Ali Ö.', rating: 5, comment: 'Best lead provider in the marketplace.', date: '2024-01-05' },
]

export default function MarketplaceProductPage() {
  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="flex items-center gap-4">
        <Link href="/marketplace"><Button variant="ghost" size="icon"><ArrowLeft className="h-5 w-5" /></Button></Link>
        <div className="flex-1">
          <Badge variant="secondary">{product.category}</Badge>
          <h1 className="text-2xl font-bold mt-1">{product.title}</h1>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader><CardTitle>Description</CardTitle></CardHeader>
            <CardContent>
              <p className="text-muted-foreground">{product.description}</p>
              <div className="mt-6">
                <p className="font-medium mb-3">What's Included:</p>
                <ul className="space-y-2">
                  {product.features.map((feature, i) => (
                    <li key={i} className="flex items-center gap-2"><CheckCircle2 className="h-5 w-5 text-green-500" />{feature}</li>
                  ))}
                </ul>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Reviews ({product.reviews})</CardTitle></CardHeader>
            <CardContent>
              <div className="space-y-4">
                {reviews.map((review) => (
                  <div key={review.id} className="p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <User className="h-5 w-5 text-gray-400" />
                        <span className="font-medium">{review.user}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        {[...Array(5)].map((_, i) => (
                          <Star key={i} className={`h-4 w-4 ${i < review.rating ? 'text-yellow-500 fill-yellow-500' : 'text-gray-300'}`} />
                        ))}
                      </div>
                    </div>
                    <p className="text-muted-foreground">{review.comment}</p>
                    <p className="text-xs text-muted-foreground mt-2">{review.date}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardContent className="pt-6">
              <p className="text-3xl font-bold text-blue-600 mb-4">₺{product.price.toLocaleString()}</p>
              <div className="flex items-center gap-2 mb-4">
                <Star className="h-5 w-5 text-yellow-500 fill-yellow-500" />
                <span className="font-medium">{product.rating}</span>
                <span className="text-muted-foreground">({product.reviews} reviews)</span>
              </div>
              <p className="text-sm text-muted-foreground mb-6">{product.sales} purchases</p>
              <Button className="w-full" size="lg"><ShoppingCart className="mr-2 h-5 w-5" />Purchase Now</Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Seller</CardTitle></CardHeader>
            <CardContent>
              <p className="font-medium">{product.seller.name}</p>
              <div className="flex items-center gap-2 mt-1">
                <Star className="h-4 w-4 text-yellow-500 fill-yellow-500" />
                <span>{product.seller.rating}</span>
                <span className="text-muted-foreground">• {product.seller.sales} sales</span>
              </div>
              <Button variant="outline" className="w-full mt-4">Contact Seller</Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
