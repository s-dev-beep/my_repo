'use client'

import Link from 'next/link'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ArrowLeft, Gift, Star, Plane, Laptop, Utensils, Sparkles } from 'lucide-react'

const userPoints = 28000

const rewards = [
  { id: 1, name: 'Weekend Getaway', points: 25000, category: 'Travel', icon: Plane, available: 5, description: '2-night stay at luxury hotel' },
  { id: 2, name: 'Tech Gadget', points: 15000, category: 'Electronics', icon: Laptop, available: 10, description: 'Choose from latest gadgets' },
  { id: 3, name: 'Restaurant Voucher', points: 5000, category: 'Dining', icon: Utensils, available: 20, description: '₺500 dining voucher' },
  { id: 4, name: 'Spa Day', points: 10000, category: 'Wellness', icon: Sparkles, available: 8, description: 'Full day spa treatment' },
  { id: 5, name: 'Premium Subscription', points: 8000, category: 'Services', icon: Star, available: 15, description: '1 year premium access' },
  { id: 6, name: 'Gift Card', points: 3000, category: 'Shopping', icon: Gift, available: 50, description: '₺300 shopping voucher' },
]

export default function RewardsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/loyalty"><Button variant="ghost" size="icon"><ArrowLeft className="h-5 w-5" /></Button></Link>
          <div>
            <h1 className="text-2xl font-bold">Rewards Catalog</h1>
            <p className="text-muted-foreground">Redeem your points for rewards</p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-sm text-muted-foreground">Your Balance</p>
          <p className="text-2xl font-bold text-blue-600">{userPoints.toLocaleString()} points</p>
        </div>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {rewards.map((reward) => {
          const canAfford = userPoints >= reward.points
          return (
            <Card key={reward.id} className={!canAfford ? 'opacity-60' : ''}>
              <CardContent className="pt-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="p-3 bg-blue-100 rounded-lg">
                    <reward.icon className="h-6 w-6 text-blue-600" />
                  </div>
                  <Badge variant="secondary">{reward.category}</Badge>
                </div>
                <h3 className="font-bold text-lg">{reward.name}</h3>
                <p className="text-sm text-muted-foreground mb-4">{reward.description}</p>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xl font-bold text-blue-600">{reward.points.toLocaleString()}</p>
                    <p className="text-xs text-muted-foreground">points</p>
                  </div>
                  <Button disabled={!canAfford}>{canAfford ? 'Redeem' : 'Not enough points'}</Button>
                </div>
                <p className="text-xs text-muted-foreground mt-3">{reward.available} available</p>
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
