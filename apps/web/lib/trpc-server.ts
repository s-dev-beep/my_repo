import { initTRPC } from '@trpc/server'
import { z } from 'zod'
import { mockData } from './mock-data'

const t = initTRPC.create()

export const router = t.router
export const publicProcedure = t.procedure

// Lead schemas
const leadSchema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.string().email().optional(),
  phone: z.string(),
  status: z.enum(['new', 'contacted', 'qualified', 'proposal', 'negotiation', 'won', 'lost']),
  source: z.string(),
  budget: z.number().optional(),
  preferredLocation: z.string().optional(),
  propertyType: z.string().optional(),
  notes: z.string().optional(),
  assignedTo: z.string().optional(),
  createdAt: z.string(),
  updatedAt: z.string(),
})

// Property schemas
const propertySchema = z.object({
  id: z.string(),
  title: z.string(),
  address: z.string(),
  city: z.string(),
  district: z.string(),
  price: z.number(),
  currency: z.string(),
  type: z.enum(['sale', 'rent']),
  propertyType: z.enum(['apartment', 'villa', 'office', 'land', 'commercial']),
  bedrooms: z.number().optional(),
  bathrooms: z.number().optional(),
  area: z.number(),
  latitude: z.number(),
  longitude: z.number(),
  features: z.array(z.string()),
  images: z.array(z.string()),
  status: z.enum(['available', 'pending', 'sold', 'rented']),
  description: z.string().optional(),
  createdAt: z.string(),
  updatedAt: z.string(),
})

// Task schemas
const taskSchema = z.object({
  id: z.string(),
  title: z.string(),
  description: z.string().optional(),
  type: z.enum(['call', 'meeting', 'viewing', 'follow_up', 'document', 'other']),
  priority: z.enum(['low', 'medium', 'high', 'urgent']),
  status: z.enum(['pending', 'in_progress', 'completed', 'cancelled']),
  dueDate: z.string(),
  assignedTo: z.string(),
  leadId: z.string().optional(),
  propertyId: z.string().optional(),
  createdAt: z.string(),
  updatedAt: z.string(),
})

export const appRouter = router({
  // Dashboard stats
  dashboard: router({
    getStats: publicProcedure.query(() => {
      return mockData.dashboardStats
    }),
    getRecentActivity: publicProcedure.query(() => {
      return mockData.recentActivity
    }),
  }),

  // Leads
  leads: router({
    list: publicProcedure
      .input(z.object({
        status: z.string().optional(),
        search: z.string().optional(),
        limit: z.number().optional(),
        offset: z.number().optional(),
      }).optional())
      .query(({ input }) => {
        let leads = [...mockData.leads]
        if (input?.status) {
          leads = leads.filter(l => l.status === input.status)
        }
        if (input?.search) {
          const search = input.search.toLowerCase()
          leads = leads.filter(l => 
            l.name.toLowerCase().includes(search) ||
            l.phone.includes(search) ||
            l.email?.toLowerCase().includes(search)
          )
        }
        return {
          items: leads.slice(input?.offset || 0, (input?.offset || 0) + (input?.limit || 50)),
          total: leads.length,
        }
      }),
    getById: publicProcedure
      .input(z.object({ id: z.string() }))
      .query(({ input }) => {
        return mockData.leads.find(l => l.id === input.id) || null
      }),
    create: publicProcedure
      .input(leadSchema.omit({ id: true, createdAt: true, updatedAt: true }))
      .mutation(({ input }) => {
        const newLead = {
          ...input,
          email: input.email || '',
          budget: input.budget || 0,
          preferredLocation: input.preferredLocation || '',
          propertyType: input.propertyType || '',
          notes: input.notes || '',
          assignedTo: input.assignedTo || '',
          id: `lead-${Date.now()}`,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        }
        mockData.leads.unshift(newLead as typeof mockData.leads[0])
        return newLead
      }),
    update: publicProcedure
      .input(z.object({
        id: z.string(),
        data: leadSchema.partial().omit({ id: true, createdAt: true }),
      }))
      .mutation(({ input }) => {
        const index = mockData.leads.findIndex(l => l.id === input.id)
        if (index !== -1) {
          mockData.leads[index] = {
            ...mockData.leads[index],
            ...input.data,
            updatedAt: new Date().toISOString(),
          } as typeof mockData.leads[0]
          return mockData.leads[index]
        }
        throw new Error('Lead not found')
      }),
    delete: publicProcedure
      .input(z.object({ id: z.string() }))
      .mutation(({ input }) => {
        const index = mockData.leads.findIndex(l => l.id === input.id)
        if (index !== -1) {
          mockData.leads.splice(index, 1)
          return { success: true }
        }
        throw new Error('Lead not found')
      }),
    getStatsByStatus: publicProcedure.query(() => {
      const stats: Record<string, number> = {}
      mockData.leads.forEach(lead => {
        stats[lead.status] = (stats[lead.status] || 0) + 1
      })
      return stats
    }),
  }),

  // Properties
  properties: router({
    list: publicProcedure
      .input(z.object({
        type: z.string().optional(),
        propertyType: z.string().optional(),
        minPrice: z.number().optional(),
        maxPrice: z.number().optional(),
        city: z.string().optional(),
        status: z.string().optional(),
        search: z.string().optional(),
        limit: z.number().optional(),
        offset: z.number().optional(),
      }).optional())
      .query(({ input }) => {
        let properties = [...mockData.properties]
        if (input?.type) {
          properties = properties.filter(p => p.type === input.type)
        }
        if (input?.propertyType) {
          properties = properties.filter(p => p.propertyType === input.propertyType)
        }
        if (input?.minPrice) {
          properties = properties.filter(p => p.price >= input.minPrice!)
        }
        if (input?.maxPrice) {
          properties = properties.filter(p => p.price <= input.maxPrice!)
        }
        if (input?.city) {
          properties = properties.filter(p => p.city === input.city)
        }
        if (input?.status) {
          properties = properties.filter(p => p.status === input.status)
        }
        if (input?.search) {
          const search = input.search.toLowerCase()
          properties = properties.filter(p =>
            p.title.toLowerCase().includes(search) ||
            p.address.toLowerCase().includes(search) ||
            p.district.toLowerCase().includes(search)
          )
        }
        return {
          items: properties.slice(input?.offset || 0, (input?.offset || 0) + (input?.limit || 50)),
          total: properties.length,
        }
      }),
    getById: publicProcedure
      .input(z.object({ id: z.string() }))
      .query(({ input }) => {
        return mockData.properties.find(p => p.id === input.id) || null
      }),
    create: publicProcedure
      .input(propertySchema.omit({ id: true, createdAt: true, updatedAt: true }))
      .mutation(({ input }) => {
        const newProperty = {
          ...input,
          bedrooms: input.bedrooms || 0,
          bathrooms: input.bathrooms || 0,
          description: input.description || '',
          id: `prop-${Date.now()}`,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        }
        mockData.properties.unshift(newProperty as typeof mockData.properties[0])
        return newProperty
      }),
    update: publicProcedure
      .input(z.object({
        id: z.string(),
        data: propertySchema.partial().omit({ id: true, createdAt: true }),
      }))
      .mutation(({ input }) => {
        const index = mockData.properties.findIndex(p => p.id === input.id)
        if (index !== -1) {
          mockData.properties[index] = {
            ...mockData.properties[index],
            ...input.data,
            updatedAt: new Date().toISOString(),
          } as typeof mockData.properties[0]
          return mockData.properties[index]
        }
        throw new Error('Property not found')
      }),
    delete: publicProcedure
      .input(z.object({ id: z.string() }))
      .mutation(({ input }) => {
        const index = mockData.properties.findIndex(p => p.id === input.id)
        if (index !== -1) {
          mockData.properties.splice(index, 1)
          return { success: true }
        }
        throw new Error('Property not found')
      }),
    getMapData: publicProcedure.query(() => {
      return mockData.properties.map(p => ({
        id: p.id,
        title: p.title,
        price: p.price,
        currency: p.currency,
        type: p.type,
        latitude: p.latitude,
        longitude: p.longitude,
        status: p.status,
      }))
    }),
    getAnalytics: publicProcedure.query(() => {
      return mockData.propertyAnalytics
    }),
  }),

  // Tasks
  tasks: router({
    list: publicProcedure
      .input(z.object({
        status: z.string().optional(),
        priority: z.string().optional(),
        assignedTo: z.string().optional(),
        type: z.string().optional(),
        startDate: z.string().optional(),
        endDate: z.string().optional(),
        limit: z.number().optional(),
        offset: z.number().optional(),
      }).optional())
      .query(({ input }) => {
        let tasks = [...mockData.tasks]
        if (input?.status) {
          tasks = tasks.filter(t => t.status === input.status)
        }
        if (input?.priority) {
          tasks = tasks.filter(t => t.priority === input.priority)
        }
        if (input?.assignedTo) {
          tasks = tasks.filter(t => t.assignedTo === input.assignedTo)
        }
        if (input?.type) {
          tasks = tasks.filter(t => t.type === input.type)
        }
        return {
          items: tasks.slice(input?.offset || 0, (input?.offset || 0) + (input?.limit || 50)),
          total: tasks.length,
        }
      }),
    getById: publicProcedure
      .input(z.object({ id: z.string() }))
      .query(({ input }) => {
        return mockData.tasks.find(t => t.id === input.id) || null
      }),
    create: publicProcedure
      .input(taskSchema.omit({ id: true, createdAt: true, updatedAt: true }))
      .mutation(({ input }) => {
        const newTask = {
          ...input,
          description: input.description || '',
          leadId: input.leadId || '',
          propertyId: input.propertyId || '',
          id: `task-${Date.now()}`,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        }
        mockData.tasks.unshift(newTask as typeof mockData.tasks[0])
        return newTask
      }),
    update: publicProcedure
      .input(z.object({
        id: z.string(),
        data: taskSchema.partial().omit({ id: true, createdAt: true }),
      }))
      .mutation(({ input }) => {
        const index = mockData.tasks.findIndex(t => t.id === input.id)
        if (index !== -1) {
          mockData.tasks[index] = {
            ...mockData.tasks[index],
            ...input.data,
            updatedAt: new Date().toISOString(),
          } as typeof mockData.tasks[0]
          return mockData.tasks[index]
        }
        throw new Error('Task not found')
      }),
    delete: publicProcedure
      .input(z.object({ id: z.string() }))
      .mutation(({ input }) => {
        const index = mockData.tasks.findIndex(t => t.id === input.id)
        if (index !== -1) {
          mockData.tasks.splice(index, 1)
          return { success: true }
        }
        throw new Error('Task not found')
      }),
    getCalendarEvents: publicProcedure
      .input(z.object({
        startDate: z.string(),
        endDate: z.string(),
      }))
      .query(({ input }) => {
        return mockData.tasks.filter(t => {
          const dueDate = new Date(t.dueDate)
          return dueDate >= new Date(input.startDate) && dueDate <= new Date(input.endDate)
        })
      }),
  }),

  // Matching
  matching: router({
    getMatches: publicProcedure
      .input(z.object({ leadId: z.string() }))
      .query(({ input }) => {
        const lead = mockData.leads.find(l => l.id === input.leadId)
        if (!lead) return []
        
        return mockData.properties
          .filter(p => p.status === 'available')
          .map(p => ({
            property: p,
            score: Math.floor(Math.random() * 30) + 70,
            matchReasons: ['Budget match', 'Location preference', 'Property type'],
          }))
          .sort((a, b) => b.score - a.score)
          .slice(0, 10)
      }),
    getSettings: publicProcedure.query(() => {
      return mockData.matchingSettings
    }),
    updateSettings: publicProcedure
      .input(z.object({
        budgetWeight: z.number().optional(),
        locationWeight: z.number().optional(),
        sizeWeight: z.number().optional(),
        featuresWeight: z.number().optional(),
      }))
      .mutation(({ input }) => {
        Object.assign(mockData.matchingSettings, input)
        return mockData.matchingSettings
      }),
  }),

  // Users/Team
  users: router({
    list: publicProcedure.query(() => {
      return mockData.users
    }),
    getById: publicProcedure
      .input(z.object({ id: z.string() }))
      .query(({ input }) => {
        return mockData.users.find(u => u.id === input.id) || null
      }),
    getTeamStats: publicProcedure.query(() => {
      return mockData.teamStats
    }),
  }),

  // Calls
  calls: router({
    list: publicProcedure
      .input(z.object({
        status: z.string().optional(),
        userId: z.string().optional(),
        limit: z.number().optional(),
        offset: z.number().optional(),
      }).optional())
      .query(({ input }) => {
        let calls = [...mockData.calls]
        if (input?.status) {
          calls = calls.filter(c => c.status === input.status)
        }
        if (input?.userId) {
          calls = calls.filter(c => c.userId === input.userId)
        }
        return {
          items: calls.slice(input?.offset || 0, (input?.offset || 0) + (input?.limit || 50)),
          total: calls.length,
        }
      }),
    getById: publicProcedure
      .input(z.object({ id: z.string() }))
      .query(({ input }) => {
        return mockData.calls.find(c => c.id === input.id) || null
      }),
    getStats: publicProcedure.query(() => {
      return mockData.callStats
    }),
  }),

  // Analytics
  analytics: router({
    getSalesData: publicProcedure.query(() => {
      return mockData.salesAnalytics
    }),
    getLeadConversion: publicProcedure.query(() => {
      return mockData.leadConversion
    }),
    getPropertyStats: publicProcedure.query(() => {
      return mockData.propertyStats
    }),
  }),

  // Admin
  admin: router({
    getSystemStats: publicProcedure.query(() => {
      return mockData.systemStats
    }),
    getAuditLogs: publicProcedure.query(() => {
      return mockData.auditLogs
    }),
    getRoles: publicProcedure.query(() => {
      return mockData.roles
    }),
    getSettings: publicProcedure.query(() => {
      return mockData.adminSettings
    }),
  }),

  // Loyalty
  loyalty: router({
    getProgram: publicProcedure.query(() => {
      return mockData.loyaltyProgram
    }),
    getLeaderboard: publicProcedure.query(() => {
      return mockData.loyaltyLeaderboard
    }),
    getRewards: publicProcedure.query(() => {
      return mockData.loyaltyRewards
    }),
  }),

  // Marketplace
  marketplace: router({
    getListings: publicProcedure.query(() => {
      return mockData.marketplaceListings
    }),
    getCategories: publicProcedure.query(() => {
      return mockData.marketplaceCategories
    }),
  }),
})

export type AppRouter = typeof appRouter
