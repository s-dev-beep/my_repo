'use client'

import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Gift, Star, Trophy, Award, TrendingUp } from 'lucide-react'

const userStats = { points: 28000, tier: 'Gold', nextTier: 'Platinum', pointsToNext: 22000, rank: 3 }

const tiers = [
  { name: 'Bronze', minPoints: 0, benefits: ['5% commission bonus'] },
  { name: 'Silver', minPoints: 10000, benefits: ['10% commission bonus', 'Priority leads'] },
  { name: 'Gold', minPoints: 25000, benefits: ['15% commission bonus', 'Priority leads', 'VIP support'] },
  { name: 'Platinum', minPoints: 50000, benefits: ['20% commission bonus', 'Priority leads', 'VIP support', 'Exclusive events'] },
]

const recentActivity = [
  { id: 1, action: 'Deal Closed', points: 5000, date: '2024-01-15' },
  { id: 2, action: 'Lead Qualified', points: 500, date: '2024-01-14' },
  { id: 3, action: 'Property Viewing', points: 100, date: '2024-01-13' },
  { id: 4, action: 'Deal Closed', points: 8000, date: '2024-01-10' },
]

export default function LoyaltyPage() {
  const progressToNext = ((userStats.points - 25000) / (50000 - 25000)) * 100

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Loyalty Program</h1>
          <p className="text-gray-500 mt-1">Earn points and unlock rewards</p>
        </div>
        <div className="flex gap-3">
          <Link href="/loyalty/leaderboard"><Button variant="outline"><Trophy className="mr-2 h-4 w-4" />Leaderboard</Button></Link>
          <Link href="/loyalty/rewards"><Button><Gift className="mr-2 h-4 w-4" />Rewards</Button></Link>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2"><Star className="h-5 w-5 text-yellow-500" />Your Status</CardTitle>
                <CardDescription>Current tier and progress</CardDescription>
              </div>
              <Badge className="bg-yellow-500 text-lg px-4 py-2">{userStats.tier}</Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="text-center py-4">
              <p className="text-5xl font-bold text-blue-600">{userStats.points.toLocaleString()}</p>
              <p className="text-muted-foreground">Total Points</p>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span>Progress to {userStats.nextTier}</span>
                <span>{userStats.pointsToNext.toLocaleString()} points needed</span>
              </div>
              <Progress value={progressToNext} className="h-3" />
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="font-medium mb-2">Current Benefits</p>
              <ul className="space-y-1">
                {tiers.find(t => t.name === userStats.tier)?.benefits.map((benefit, i) => (
                  <li key={i} className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Star className="h-4 w-4 text-yellow-500" />{benefit}
                  </li>
                ))}
              </ul>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Recent Activity</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivity.map((activity) => (
                <div key={activity.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-sm">{activity.action}</p>
                    <p className="text-xs text-muted-foreground">{activity.date}</p>
                  </div>
                  <Badge variant="secondary" className="text-green-600">+{activity.points}</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Tier Benefits</CardTitle></CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-4 gap-4">
            {tiers.map((tier) => (
              <div key={tier.name} className={`p-4 rounded-lg border-2 ${tier.name === userStats.tier ? 'border-yellow-500 bg-yellow-50' : 'border-gray-200'}`}>
                <div className="flex items-center gap-2 mb-3">
                  <Award className={`h-5 w-5 ${tier.name === 'Bronze' ? 'text-orange-600' : tier.name === 'Silver' ? 'text-gray-400' : tier.name === 'Gold' ? 'text-yellow-500' : 'text-purple-500'}`} />
                  <p className="font-bold">{tier.name}</p>
                </div>
                <p className="text-sm text-muted-foreground mb-2">{tier.minPoints.toLocaleString()}+ points</p>
                <ul className="space-y-1">
                  {tier.benefits.map((benefit, i) => (<li key={i} className="text-xs text-muted-foreground">• {benefit}</li>))}
                </ul>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
