'use client'

import Link from 'next/link'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { ArrowLeft, Trophy, Medal, Award, Star } from 'lucide-react'

const leaderboard = [
  { rank: 1, name: 'Ali Öztürk', points: 52000, tier: 'Platinum', deals: 18 },
  { rank: 2, name: 'Fatma Demir', points: 38000, tier: 'Gold', deals: 15 },
  { rank: 3, name: 'Ahmet Yılmaz', points: 28000, tier: 'Gold', deals: 12 },
  { rank: 4, name: 'Mustafa Şahin', points: 15000, tier: 'Silver', deals: 8 },
  { rank: 5, name: 'Ayşe Kara', points: 12000, tier: 'Silver', deals: 6 },
  { rank: 6, name: 'Emre Yıldız', points: 9500, tier: 'Bronze', deals: 5 },
  { rank: 7, name: 'Selin Demir', points: 8200, tier: 'Bronze', deals: 4 },
  { rank: 8, name: 'Can Öztürk', points: 7100, tier: 'Bronze', deals: 4 },
]

const tierColors: Record<string, string> = { Platinum: 'bg-purple-500', Gold: 'bg-yellow-500', Silver: 'bg-gray-400', Bronze: 'bg-orange-600' }

export default function LeaderboardPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/loyalty"><Button variant="ghost" size="icon"><ArrowLeft className="h-5 w-5" /></Button></Link>
        <div>
          <h1 className="text-2xl font-bold">Leaderboard</h1>
          <p className="text-muted-foreground">Top performing agents this month</p>
        </div>
      </div>

      {/* Top 3 Podium */}
      <div className="grid md:grid-cols-3 gap-4">
        {leaderboard.slice(0, 3).map((user, index) => (
          <Card key={user.rank} className={index === 0 ? 'md:order-2 border-yellow-500 border-2' : index === 1 ? 'md:order-1' : 'md:order-3'}>
            <CardContent className="pt-6 text-center">
              <div className="relative inline-block">
                <Avatar className="h-20 w-20 mx-auto">
                  <AvatarFallback className="text-2xl">{user.name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
                </Avatar>
                <div className={`absolute -top-2 -right-2 w-8 h-8 rounded-full flex items-center justify-center ${index === 0 ? 'bg-yellow-500' : index === 1 ? 'bg-gray-400' : 'bg-orange-600'} text-white font-bold`}>
                  {user.rank}
                </div>
              </div>
              <h3 className="font-bold text-lg mt-4">{user.name}</h3>
              <Badge className={`${tierColors[user.tier]} mt-2`}>{user.tier}</Badge>
              <div className="mt-4">
                <p className="text-3xl font-bold text-blue-600">{user.points.toLocaleString()}</p>
                <p className="text-sm text-muted-foreground">points</p>
              </div>
              <p className="text-sm text-muted-foreground mt-2">{user.deals} deals closed</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Rest of leaderboard */}
      <Card>
        <CardHeader><CardTitle>Rankings</CardTitle></CardHeader>
        <CardContent>
          <div className="space-y-3">
            {leaderboard.slice(3).map((user) => (
              <div key={user.rank} className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg">
                <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center font-bold">{user.rank}</div>
                <Avatar><AvatarFallback>{user.name.split(' ').map(n => n[0]).join('')}</AvatarFallback></Avatar>
                <div className="flex-1">
                  <p className="font-medium">{user.name}</p>
                  <p className="text-sm text-muted-foreground">{user.deals} deals</p>
                </div>
                <Badge className={tierColors[user.tier]}>{user.tier}</Badge>
                <p className="font-bold">{user.points.toLocaleString()} pts</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
