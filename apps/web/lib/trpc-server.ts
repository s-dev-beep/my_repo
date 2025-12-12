import { initTRPC } from '@trpc/server'
import { z } from 'zod'
import { mockData } from './mock-data'
import { createServerSupabaseClient, isSupabaseConfigured } from './supabase'

const t = initTRPC.create()

export const router = t.router
export const publicProcedure = t.procedure

// Get Supabase client (may be null if not configured)
const supabase = createServerSupabaseClient()

// Helper to convert snake_case to camelCase for frontend
function toCamelCase<T extends Record<string, any>>(obj: T): any {
  if (Array.isArray(obj)) {
    return obj.map(toCamelCase)
  }
  if (obj !== null && typeof obj === 'object') {
    return Object.keys(obj).reduce((acc, key) => {
      const camelKey = key.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase())
      acc[camelKey] = toCamelCase(obj[key])
      return acc
    }, {} as any)
  }
  return obj
}

// Helper to convert camelCase to snake_case for database
function toSnakeCase<T extends Record<string, any>>(obj: T): any {
  if (Array.isArray(obj)) {
    return obj.map(toSnakeCase)
  }
  if (obj !== null && typeof obj === 'object') {
    return Object.keys(obj).reduce((acc, key) => {
      const snakeKey = key.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`)
      acc[snakeKey] = toSnakeCase(obj[key])
      return acc
    }, {} as any)
  }
  return obj
}

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
    getStats: publicProcedure.query(async () => {
      if (supabase) {
        try {
          const [leadsResult, propertiesResult, tasksResult] = await Promise.all([
            supabase.from('leads').select('status', { count: 'exact' }),
            supabase.from('properties').select('status', { count: 'exact' }),
            supabase.from('tasks').select('status', { count: 'exact' }).eq('status', 'pending'),
          ])
          
          return {
            totalLeads: leadsResult.count || 0,
            totalProperties: propertiesResult.count || 0,
            pendingTasks: tasksResult.count || 0,
            conversionRate: 18.5,
            revenue: 72000000,
            activeAgents: 12,
          }
        } catch (error) {
          console.error('Supabase error:', error)
        }
      }
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
      .query(async ({ input }) => {
        if (supabase) {
          try {
            let query = supabase.from('leads').select('*', { count: 'exact' })
            
            if (input?.status) {
              query = query.eq('status', input.status)
            }
            if (input?.search) {
              query = query.or(`name.ilike.%${input.search}%,phone.ilike.%${input.search}%,email.ilike.%${input.search}%`)
            }
            
            query = query
              .order('created_at', { ascending: false })
              .range(input?.offset || 0, (input?.offset || 0) + (input?.limit || 50) - 1)
            
            const { data, count, error } = await query
            
            if (error) throw error
            
            return {
              items: toCamelCase(data || []),
              total: count || 0,
            }
          } catch (error) {
            console.error('Supabase leads.list error:', error)
          }
        }
        
        // Fallback to mock data
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
      .query(async ({ input }) => {
        if (supabase) {
          try {
            const { data, error } = await supabase
              .from('leads')
              .select('*')
              .eq('id', input.id)
              .single()
            
            if (error) throw error
            return toCamelCase(data)
          } catch (error) {
            console.error('Supabase leads.getById error:', error)
          }
        }
        return mockData.leads.find(l => l.id === input.id) || null
      }),
    create: publicProcedure
      .input(leadSchema.omit({ id: true, createdAt: true, updatedAt: true }))
      .mutation(async ({ input }) => {
        if (supabase) {
          try {
            const { data, error } = await supabase
              .from('leads')
              .insert(toSnakeCase(input) as any)
              .select()
              .single()
            
            if (error) throw error
            return toCamelCase(data)
          } catch (error) {
            console.error('Supabase leads.create error:', error)
          }
        }
        
        // Fallback to mock
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
      .mutation(async ({ input }) => {
        if (supabase) {
          try {
            const updateData = { ...toSnakeCase(input.data), updated_at: new Date().toISOString() }
            const { data, error } = await supabase
              .from('leads')
              .update(updateData as any)
              .eq('id', input.id)
              .select()
              .single()
            
            if (error) throw error
            return toCamelCase(data)
          } catch (error) {
            console.error('Supabase leads.update error:', error)
          }
        }
        
        // Fallback to mock
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
      .mutation(async ({ input }) => {
        if (supabase) {
          try {
            const { error } = await supabase
              .from('leads')
              .delete()
              .eq('id', input.id)
            
            if (error) throw error
            return { success: true }
          } catch (error) {
            console.error('Supabase leads.delete error:', error)
          }
        }
        
        // Fallback to mock
        const index = mockData.leads.findIndex(l => l.id === input.id)
        if (index !== -1) {
          mockData.leads.splice(index, 1)
          return { success: true }
        }
        throw new Error('Lead not found')
      }),
    getStatsByStatus: publicProcedure.query(async () => {
      if (supabase) {
        try {
          const { data, error } = await supabase
            .from('leads')
            .select('status')
          
          if (error) throw error
          
          const stats: Record<string, number> = {}
          data?.forEach(lead => {
            stats[lead.status] = (stats[lead.status] || 0) + 1
          })
          return stats
        } catch (error) {
          console.error('Supabase leads.getStatsByStatus error:', error)
        }
      }
      
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
      .query(async ({ input }) => {
        if (supabase) {
          try {
            let query = supabase.from('properties').select('*', { count: 'exact' })
            
            if (input?.type) query = query.eq('type', input.type)
            if (input?.propertyType) query = query.eq('property_type', input.propertyType)
            if (input?.minPrice) query = query.gte('price', input.minPrice)
            if (input?.maxPrice) query = query.lte('price', input.maxPrice)
            if (input?.city) query = query.eq('city', input.city)
            if (input?.status) query = query.eq('status', input.status)
            if (input?.search) {
              query = query.or(`title.ilike.%${input.search}%,address.ilike.%${input.search}%,district.ilike.%${input.search}%`)
            }
            
            query = query
              .order('created_at', { ascending: false })
              .range(input?.offset || 0, (input?.offset || 0) + (input?.limit || 50) - 1)
            
            const { data, count, error } = await query
            
            if (error) throw error
            
            return {
              items: toCamelCase(data || []),
              total: count || 0,
            }
          } catch (error) {
            console.error('Supabase properties.list error:', error)
          }
        }
        
        // Fallback to mock data
        let properties = [...mockData.properties]
        if (input?.type) properties = properties.filter(p => p.type === input.type)
        if (input?.propertyType) properties = properties.filter(p => p.propertyType === input.propertyType)
        if (input?.minPrice) properties = properties.filter(p => p.price >= input.minPrice!)
        if (input?.maxPrice) properties = properties.filter(p => p.price <= input.maxPrice!)
        if (input?.city) properties = properties.filter(p => p.city === input.city)
        if (input?.status) properties = properties.filter(p => p.status === input.status)
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
      .query(async ({ input }) => {
        if (supabase) {
          try {
            const { data, error } = await supabase
              .from('properties')
              .select('*')
              .eq('id', input.id)
              .single()
            
            if (error) throw error
            return toCamelCase(data)
          } catch (error) {
            console.error('Supabase properties.getById error:', error)
          }
        }
        return mockData.properties.find(p => p.id === input.id) || null
      }),
    create: publicProcedure
      .input(propertySchema.omit({ id: true, createdAt: true, updatedAt: true }))
      .mutation(async ({ input }) => {
        if (supabase) {
          try {
            const { data, error } = await supabase
              .from('properties')
              .insert(toSnakeCase(input) as any)
              .select()
              .single()
            
            if (error) throw error
            return toCamelCase(data)
          } catch (error) {
            console.error('Supabase properties.create error:', error)
          }
        }
        
        // Fallback to mock
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
      .mutation(async ({ input }) => {
        if (supabase) {
          try {
            const updateData = { ...toSnakeCase(input.data), updated_at: new Date().toISOString() }
            const { data, error } = await supabase
              .from('properties')
              .update(updateData as any)
              .eq('id', input.id)
              .select()
              .single()
            
            if (error) throw error
            return toCamelCase(data)
          } catch (error) {
            console.error('Supabase properties.update error:', error)
          }
        }
        
        // Fallback to mock
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
      .mutation(async ({ input }) => {
        if (supabase) {
          try {
            const { error } = await supabase
              .from('properties')
              .delete()
              .eq('id', input.id)
            
            if (error) throw error
            return { success: true }
          } catch (error) {
            console.error('Supabase properties.delete error:', error)
          }
        }
        
        // Fallback to mock
        const index = mockData.properties.findIndex(p => p.id === input.id)
        if (index !== -1) {
          mockData.properties.splice(index, 1)
          return { success: true }
        }
        throw new Error('Property not found')
      }),
    getMapData: publicProcedure.query(async () => {
      if (supabase) {
        try {
          const { data, error } = await supabase
            .from('properties')
            .select('id, title, price, currency, type, latitude, longitude, status')
            .not('latitude', 'is', null)
            .not('longitude', 'is', null)
          
          if (error) throw error
          return toCamelCase(data || [])
        } catch (error) {
          console.error('Supabase properties.getMapData error:', error)
        }
      }
      
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
      .query(async ({ input }) => {
        if (supabase) {
          try {
            let query = supabase.from('tasks').select('*', { count: 'exact' })
            
            if (input?.status) query = query.eq('status', input.status)
            if (input?.priority) query = query.eq('priority', input.priority)
            if (input?.assignedTo) query = query.eq('assigned_to', input.assignedTo)
            if (input?.type) query = query.eq('type', input.type)
            
            query = query
              .order('due_date', { ascending: true })
              .range(input?.offset || 0, (input?.offset || 0) + (input?.limit || 50) - 1)
            
            const { data, count, error } = await query
            
            if (error) throw error
            
            return {
              items: toCamelCase(data || []),
              total: count || 0,
            }
          } catch (error) {
            console.error('Supabase tasks.list error:', error)
          }
        }
        
        // Fallback to mock data
        let tasks = [...mockData.tasks]
        if (input?.status) tasks = tasks.filter(t => t.status === input.status)
        if (input?.priority) tasks = tasks.filter(t => t.priority === input.priority)
        if (input?.assignedTo) tasks = tasks.filter(t => t.assignedTo === input.assignedTo)
        if (input?.type) tasks = tasks.filter(t => t.type === input.type)
        return {
          items: tasks.slice(input?.offset || 0, (input?.offset || 0) + (input?.limit || 50)),
          total: tasks.length,
        }
      }),
    getById: publicProcedure
      .input(z.object({ id: z.string() }))
      .query(async ({ input }) => {
        if (supabase) {
          try {
            const { data, error } = await supabase
              .from('tasks')
              .select('*')
              .eq('id', input.id)
              .single()
            
            if (error) throw error
            return toCamelCase(data)
          } catch (error) {
            console.error('Supabase tasks.getById error:', error)
          }
        }
        return mockData.tasks.find(t => t.id === input.id) || null
      }),
    create: publicProcedure
      .input(taskSchema.omit({ id: true, createdAt: true, updatedAt: true }))
      .mutation(async ({ input }) => {
        if (supabase) {
          try {
            const { data, error } = await supabase
              .from('tasks')
              .insert(toSnakeCase(input) as any)
              .select()
              .single()
            
            if (error) throw error
            return toCamelCase(data)
          } catch (error) {
            console.error('Supabase tasks.create error:', error)
          }
        }
        
        // Fallback to mock
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
      .mutation(async ({ input }) => {
        if (supabase) {
          try {
            const updateData = { ...toSnakeCase(input.data), updated_at: new Date().toISOString() }
            const { data, error } = await supabase
              .from('tasks')
              .update(updateData as any)
              .eq('id', input.id)
              .select()
              .single()
            
            if (error) throw error
            return toCamelCase(data)
          } catch (error) {
            console.error('Supabase tasks.update error:', error)
          }
        }
        
        // Fallback to mock
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
      .mutation(async ({ input }) => {
        if (supabase) {
          try {
            const { error } = await supabase
              .from('tasks')
              .delete()
              .eq('id', input.id)
            
            if (error) throw error
            return { success: true }
          } catch (error) {
            console.error('Supabase tasks.delete error:', error)
          }
        }
        
        // Fallback to mock
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
      .query(async ({ input }) => {
        if (supabase) {
          try {
            const { data, error } = await supabase
              .from('tasks')
              .select('*')
              .gte('due_date', input.startDate)
              .lte('due_date', input.endDate)
            
            if (error) throw error
            return toCamelCase(data || [])
          } catch (error) {
            console.error('Supabase tasks.getCalendarEvents error:', error)
          }
        }
        
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
      .query(async ({ input }) => {
        // For now, use mock matching logic
        // This would be replaced with a real matching algorithm
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
    list: publicProcedure.query(async () => {
      if (supabase) {
        try {
          const { data, error } = await supabase
            .from('users')
            .select('*')
            .order('name')
          
          if (error) throw error
          return toCamelCase(data || [])
        } catch (error) {
          console.error('Supabase users.list error:', error)
        }
      }
      return mockData.users
    }),
    getById: publicProcedure
      .input(z.object({ id: z.string() }))
      .query(async ({ input }) => {
        if (supabase) {
          try {
            const { data, error } = await supabase
              .from('users')
              .select('*')
              .eq('id', input.id)
              .single()
            
            if (error) throw error
            return toCamelCase(data)
          } catch (error) {
            console.error('Supabase users.getById error:', error)
          }
        }
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
      .query(async ({ input }) => {
        if (supabase) {
          try {
            let query = supabase.from('calls').select('*', { count: 'exact' })
            
            if (input?.status) query = query.eq('status', input.status)
            if (input?.userId) query = query.eq('user_id', input.userId)
            
            query = query
              .order('created_at', { ascending: false })
              .range(input?.offset || 0, (input?.offset || 0) + (input?.limit || 50) - 1)
            
            const { data, count, error } = await query
            
            if (error) throw error
            
            return {
              items: toCamelCase(data || []),
              total: count || 0,
            }
          } catch (error) {
            console.error('Supabase calls.list error:', error)
          }
        }
        
        let calls = [...mockData.calls]
        if (input?.status) calls = calls.filter(c => c.status === input.status)
        if (input?.userId) calls = calls.filter(c => c.userId === input.userId)
        return {
          items: calls.slice(input?.offset || 0, (input?.offset || 0) + (input?.limit || 50)),
          total: calls.length,
        }
      }),
    getById: publicProcedure
      .input(z.object({ id: z.string() }))
      .query(async ({ input }) => {
        if (supabase) {
          try {
            const { data, error } = await supabase
              .from('calls')
              .select('*')
              .eq('id', input.id)
              .single()
            
            if (error) throw error
            return toCamelCase(data)
          } catch (error) {
            console.error('Supabase calls.getById error:', error)
          }
        }
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
