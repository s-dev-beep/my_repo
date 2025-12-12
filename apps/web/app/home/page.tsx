'use client'

import Link from 'next/link'
import { useState } from 'react'
import { 
  Building2, Users, MapPin, Calendar, Phone, BarChart3, 
  ArrowRight, Check, Star, Trophy, Zap, Shield, Globe,
  TrendingUp, MessageSquare, Clock, Target
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'

export default function MarketingHomePage() {
  const [email, setEmail] = useState('')
  const [contactForm, setContactForm] = useState({
    name: '',
    email: '',
    message: ''
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle')

  const handleNewsletterSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    setIsSubmitting(false)
    setSubmitStatus('success')
    setEmail('')
    setTimeout(() => setSubmitStatus('idle'), 3000)
  }

  const handleContactSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500))
    setIsSubmitting(false)
    setSubmitStatus('success')
    setContactForm({ name: '', email: '', message: '' })
    setTimeout(() => setSubmitStatus('idle'), 3000)
  }

  return (
    <div className="flex flex-col">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-blue-50 via-white to-indigo-50 py-20 md:py-32">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center px-4 py-2 bg-blue-100 text-blue-700 rounded-full text-sm font-medium mb-6">
              <Zap className="w-4 h-4 mr-2" />
              #1 Real Estate CRM Platform
            </div>
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
              Transform Your Real Estate Business with{' '}
              <span className="text-blue-600">Dynamic CRM</span>
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
              The complete solution for managing leads, properties, and sales. 
              Streamline your workflow and close more deals with our intelligent platform.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/sign-in">
                <Button size="lg" className="bg-blue-600 hover:bg-blue-700 text-lg px-8">
                  Get Started Free
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
              <Link href="/dashboard/agent">
                <Button size="lg" variant="outline" className="text-lg px-8">
                  View Demo Dashboard
                </Button>
              </Link>
            </div>
            <div className="mt-12 flex items-center justify-center gap-8 text-sm text-gray-600">
              <div className="flex items-center">
                <Check className="w-5 h-5 text-green-500 mr-2" />
                No credit card required
              </div>
              <div className="flex items-center">
                <Check className="w-5 h-5 text-green-500 mr-2" />
                14-day free trial
              </div>
              <div className="flex items-center">
                <Check className="w-5 h-5 text-green-500 mr-2" />
                Cancel anytime
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-white border-y">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto">
            <div className="text-center">
              <div className="text-4xl font-bold text-blue-600 mb-2">10K+</div>
              <div className="text-gray-600">Active Users</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-blue-600 mb-2">50K+</div>
              <div className="text-gray-600">Properties Listed</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-blue-600 mb-2">98%</div>
              <div className="text-gray-600">Customer Satisfaction</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-blue-600 mb-2">24/7</div>
              <div className="text-gray-600">Support Available</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold text-gray-900 mb-4">
              Everything You Need to Succeed
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Powerful features designed to help real estate professionals work smarter and close deals faster.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
            <FeatureCard
              icon={<Users className="w-8 h-8" />}
              title="Lead Management"
              description="Track and nurture leads through the entire sales pipeline with automated workflows and smart notifications."
              link="/leads"
            />
            <FeatureCard
              icon={<Building2 className="w-8 h-8" />}
              title="Property Catalog"
              description="Manage your entire property portfolio with rich details, photos, and comprehensive search capabilities."
              link="/properties"
            />
            <FeatureCard
              icon={<MapPin className="w-8 h-8" />}
              title="Interactive Maps"
              description="Visualize properties on Google Maps with advanced filtering, clustering, and location-based insights."
              link="/properties/map"
            />
            <FeatureCard
              icon={<Calendar className="w-8 h-8" />}
              title="Task & Calendar"
              description="Schedule viewings, set reminders, and manage your entire workflow with our integrated calendar system."
              link="/tasks"
            />
            <FeatureCard
              icon={<Phone className="w-8 h-8" />}
              title="Call Center Integration"
              description="Make and track calls directly from the platform. Keep detailed records of all client communications."
              link="/calls"
            />
            <FeatureCard
              icon={<BarChart3 className="w-8 h-8" />}
              title="Advanced Analytics"
              description="Get actionable insights with comprehensive reports, conversion tracking, and performance metrics."
              link="/analytics"
            />
            <FeatureCard
              icon={<Target className="w-8 h-8" />}
              title="Smart Matching"
              description="Automatically match leads with the perfect properties using our intelligent recommendation engine."
              link="/matching"
            />
            <FeatureCard
              icon={<Trophy className="w-8 h-8" />}
              title="Loyalty Program"
              description="Reward your best agents with gamification, leaderboards, and achievement tracking."
              link="/loyalty"
            />
            <FeatureCard
              icon={<Globe className="w-8 h-8" />}
              title="Marketplace"
              description="Access a network of properties and leads shared across agencies for better opportunities."
              link="/marketplace"
            />
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold text-gray-900 mb-4">
              Trusted by Industry Leaders
            </h2>
            <p className="text-xl text-gray-600">
              See what our customers have to say about Dynamic CRM
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            <TestimonialCard
              quote="Dynamic CRM has transformed how we manage our properties. Our team's productivity increased by 40% in just 3 months."
              author="Sarah Johnson"
              role="Agency Owner"
              rating={5}
            />
            <TestimonialCard
              quote="The lead management features are incredible. We're closing deals 2x faster than before switching to Dynamic CRM."
              author="Michael Chen"
              role="Sales Manager"
              rating={5}
            />
            <TestimonialCard
              quote="Best CRM investment we've made. The map integration and property matching save us hours every day."
              author="Emma Williams"
              role="Senior Agent"
              rating={5}
            />
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold text-gray-900 mb-4">
              Simple, Transparent Pricing
            </h2>
            <p className="text-xl text-gray-600">
              Choose the plan that's right for your business
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <PricingCard
              name="Starter"
              price="₺299"
              period="per month"
              description="Perfect for individual agents"
              features={[
                'Up to 100 leads',
                '50 properties',
                'Basic analytics',
                'Email support',
                'Mobile app access'
              ]}
              cta="Start Free Trial"
              href="/sign-in"
            />
            <PricingCard
              name="Professional"
              price="₺799"
              period="per month"
              description="For growing teams"
              features={[
                'Unlimited leads',
                'Unlimited properties',
                'Advanced analytics',
                'Priority support',
                'Team collaboration',
                'API access',
                'Custom integrations'
              ]}
              cta="Start Free Trial"
              href="/sign-in"
              highlighted={true}
            />
            <PricingCard
              name="Enterprise"
              price="Custom"
              period="contact us"
              description="For large organizations"
              features={[
                'Everything in Professional',
                'Dedicated account manager',
                'Custom development',
                'SLA guarantees',
                'Advanced security',
                'Training & onboarding'
              ]}
              cta="Contact Sales"
              href="/#contact"
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-indigo-600 text-white">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-3xl md:text-5xl font-bold mb-6">
              Ready to Transform Your Business?
            </h2>
            <p className="text-xl mb-8 opacity-90">
              Join thousands of real estate professionals already using Dynamic CRM
            </p>
            <form onSubmit={handleNewsletterSubmit} className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
              <Input
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="flex-1 bg-white text-gray-900"
              />
              <Button 
                type="submit" 
                size="lg" 
                variant="secondary"
                disabled={isSubmitting}
                className="bg-white text-blue-600 hover:bg-gray-100"
              >
                {isSubmitting ? 'Sending...' : 'Get Started'}
              </Button>
            </form>
            {submitStatus === 'success' && (
              <p className="mt-4 text-green-200">✓ Thank you! We'll be in touch soon.</p>
            )}
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section id="contact" className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="text-3xl md:text-5xl font-bold text-gray-900 mb-4">
                Get in Touch
              </h2>
              <p className="text-xl text-gray-600">
                Have questions? We'd love to hear from you.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {/* Contact Form */}
              <Card>
                <CardHeader>
                  <CardTitle>Send us a message</CardTitle>
                  <CardDescription>
                    We'll get back to you within 24 hours
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleContactSubmit} className="space-y-4">
                    <div>
                      <Input
                        placeholder="Your name"
                        value={contactForm.name}
                        onChange={(e) => setContactForm({...contactForm, name: e.target.value})}
                        required
                      />
                    </div>
                    <div>
                      <Input
                        type="email"
                        placeholder="Your email"
                        value={contactForm.email}
                        onChange={(e) => setContactForm({...contactForm, email: e.target.value})}
                        required
                      />
                    </div>
                    <div>
                      <Textarea
                        placeholder="Your message"
                        rows={5}
                        value={contactForm.message}
                        onChange={(e) => setContactForm({...contactForm, message: e.target.value})}
                        required
                      />
                    </div>
                    <Button 
                      type="submit" 
                      className="w-full bg-blue-600 hover:bg-blue-700"
                      disabled={isSubmitting}
                    >
                      {isSubmitting ? 'Sending...' : 'Send Message'}
                    </Button>
                    {submitStatus === 'success' && (
                      <p className="text-green-600 text-sm">✓ Message sent successfully!</p>
                    )}
                  </form>
                </CardContent>
              </Card>

              {/* Contact Info */}
              <div className="space-y-6">
                <Card>
                  <CardContent className="pt-6">
                    <div className="flex items-start space-x-4">
                      <MessageSquare className="w-6 h-6 text-blue-600 mt-1" />
                      <div>
                        <h3 className="font-semibold mb-1">Live Chat</h3>
                        <p className="text-gray-600 text-sm">
                          Available Monday-Friday, 9am-6pm GMT+3
                        </p>
                        <Button variant="link" className="px-0 mt-2">
                          Start Chat →
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="pt-6">
                    <div className="flex items-start space-x-4">
                      <Phone className="w-6 h-6 text-blue-600 mt-1" />
                      <div>
                        <h3 className="font-semibold mb-1">Phone</h3>
                        <p className="text-gray-600 text-sm mb-1">
                          +90 555 123 45 67
                        </p>
                        <p className="text-gray-500 text-xs">
                          Monday-Friday, 9am-6pm GMT+3
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="pt-6">
                    <div className="flex items-start space-x-4">
                      <Clock className="w-6 h-6 text-blue-600 mt-1" />
                      <div>
                        <h3 className="font-semibold mb-1">Email</h3>
                        <p className="text-gray-600 text-sm mb-1">
                          info@dynamiccrm.com
                        </p>
                        <p className="text-gray-500 text-xs">
                          Response within 24 hours
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

function FeatureCard({ 
  icon, 
  title, 
  description, 
  link 
}: { 
  icon: React.ReactNode
  title: string
  description: string
  link: string
}) {
  return (
    <Link href={link}>
      <Card className="h-full hover:shadow-lg transition-all cursor-pointer group border-2 hover:border-blue-500">
        <CardContent className="pt-6">
          <div className="text-blue-600 mb-4 group-hover:scale-110 transition-transform">
            {icon}
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors">
            {title}
          </h3>
          <p className="text-gray-600">
            {description}
          </p>
        </CardContent>
      </Card>
    </Link>
  )
}

function TestimonialCard({
  quote,
  author,
  role,
  rating
}: {
  quote: string
  author: string
  role: string
  rating: number
}) {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex mb-4">
          {[...Array(rating)].map((_, i) => (
            <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
          ))}
        </div>
        <p className="text-gray-700 mb-4 italic">"{quote}"</p>
        <div>
          <div className="font-semibold text-gray-900">{author}</div>
          <div className="text-sm text-gray-600">{role}</div>
        </div>
      </CardContent>
    </Card>
  )
}

function PricingCard({
  name,
  price,
  period,
  description,
  features,
  cta,
  href,
  highlighted = false
}: {
  name: string
  price: string
  period: string
  description: string
  features: string[]
  cta: string
  href: string
  highlighted?: boolean
}) {
  return (
    <Card className={`${highlighted ? 'border-2 border-blue-600 shadow-xl scale-105' : ''}`}>
      <CardHeader>
        {highlighted && (
          <div className="text-center mb-2">
            <span className="bg-blue-600 text-white text-xs font-semibold px-3 py-1 rounded-full">
              MOST POPULAR
            </span>
          </div>
        )}
        <CardTitle className="text-2xl">{name}</CardTitle>
        <CardDescription>{description}</CardDescription>
        <div className="mt-4">
          <span className="text-4xl font-bold text-gray-900">{price}</span>
          <span className="text-gray-600 ml-2">/ {period}</span>
        </div>
      </CardHeader>
      <CardContent>
        <ul className="space-y-3 mb-6">
          {features.map((feature, i) => (
            <li key={i} className="flex items-start">
              <Check className="w-5 h-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
              <span className="text-gray-700">{feature}</span>
            </li>
          ))}
        </ul>
        <Link href={href}>
          <Button 
            className={`w-full ${highlighted ? 'bg-blue-600 hover:bg-blue-700' : ''}`}
            variant={highlighted ? 'default' : 'outline'}
          >
            {cta}
          </Button>
        </Link>
      </CardContent>
    </Card>
  )
}
