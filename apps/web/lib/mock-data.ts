// Comprehensive mock data for the CRM application

export const mockData = {
  // Dashboard stats
  dashboardStats: {
    totalLeads: 1247,
    newLeadsToday: 23,
    activeProperties: 856,
    pendingTasks: 47,
    closedDealsMonth: 34,
    totalRevenue: 12500000,
    conversionRate: 18.5,
    avgResponseTime: 2.4,
  },

  // Recent activity
  recentActivity: [
    { id: '1', type: 'lead', action: 'New lead created', user: 'Ahmet Yılmaz', time: '5 minutes ago', details: 'Mehmet Kaya - Looking for 3+1 apartment' },
    { id: '2', type: 'property', action: 'Property updated', user: 'Fatma Demir', time: '15 minutes ago', details: 'Luxury Villa in Çankaya - Price reduced' },
    { id: '3', type: 'task', action: 'Task completed', user: 'Ali Öztürk', time: '30 minutes ago', details: 'Property viewing with client' },
    { id: '4', type: 'call', action: 'Call logged', user: 'Zeynep Arslan', time: '1 hour ago', details: 'Follow-up call with lead #1234' },
    { id: '5', type: 'deal', action: 'Deal closed', user: 'Mustafa Şahin', time: '2 hours ago', details: 'Apartment sale in Kızılay - ₺2,500,000' },
  ],

  // Leads data
  leads: [
    { id: 'lead-1', name: 'Mehmet Kaya', email: 'mehmet.kaya@email.com', phone: '+90 532 123 4567', status: 'new' as const, source: 'Website', budget: 2000000, preferredLocation: 'Çankaya', propertyType: 'Apartment', notes: 'Looking for 3+1 apartment near metro', assignedTo: 'user-1', createdAt: '2024-01-15T10:30:00Z', updatedAt: '2024-01-15T10:30:00Z' },
    { id: 'lead-2', name: 'Ayşe Yıldız', email: 'ayse.yildiz@email.com', phone: '+90 533 234 5678', status: 'contacted' as const, source: 'Referral', budget: 3500000, preferredLocation: 'Kızılay', propertyType: 'Office', notes: 'Business owner looking for office space', assignedTo: 'user-2', createdAt: '2024-01-14T14:20:00Z', updatedAt: '2024-01-15T09:00:00Z' },
    { id: 'lead-3', name: 'Hasan Demir', email: 'hasan.demir@email.com', phone: '+90 534 345 6789', status: 'qualified' as const, source: 'Social Media', budget: 5000000, preferredLocation: 'Oran', propertyType: 'Villa', notes: 'Family of 5, needs garden', assignedTo: 'user-1', createdAt: '2024-01-13T08:45:00Z', updatedAt: '2024-01-15T11:30:00Z' },
    { id: 'lead-4', name: 'Fatma Çelik', email: 'fatma.celik@email.com', phone: '+90 535 456 7890', status: 'proposal' as const, source: 'Walk-in', budget: 1500000, preferredLocation: 'Batıkent', propertyType: 'Apartment', notes: 'First-time buyer, needs financing help', assignedTo: 'user-3', createdAt: '2024-01-12T16:15:00Z', updatedAt: '2024-01-14T10:00:00Z' },
    { id: 'lead-5', name: 'Ali Koç', email: 'ali.koc@email.com', phone: '+90 536 567 8901', status: 'negotiation' as const, source: 'Website', budget: 8000000, preferredLocation: 'Bilkent', propertyType: 'Villa', notes: 'Wants smart home features', assignedTo: 'user-2', createdAt: '2024-01-11T11:00:00Z', updatedAt: '2024-01-15T14:30:00Z' },
    { id: 'lead-6', name: 'Zeynep Öz', email: 'zeynep.oz@email.com', phone: '+90 537 678 9012', status: 'won' as const, source: 'Referral', budget: 2200000, preferredLocation: 'Çankaya', propertyType: 'Apartment', notes: 'Closed deal on 3+1 apartment', assignedTo: 'user-1', createdAt: '2024-01-10T09:30:00Z', updatedAt: '2024-01-13T16:00:00Z' },
    { id: 'lead-7', name: 'Mustafa Aydın', email: 'mustafa.aydin@email.com', phone: '+90 538 789 0123', status: 'lost' as const, source: 'Website', budget: 4000000, preferredLocation: 'Ümitköy', propertyType: 'Villa', notes: 'Went with competitor', assignedTo: 'user-3', createdAt: '2024-01-09T13:45:00Z', updatedAt: '2024-01-12T11:00:00Z' },
    { id: 'lead-8', name: 'Elif Şen', email: 'elif.sen@email.com', phone: '+90 539 890 1234', status: 'new' as const, source: 'Social Media', budget: 1800000, preferredLocation: 'Yenimahalle', propertyType: 'Apartment', notes: 'Young professional, studio or 1+1', assignedTo: 'user-2', createdAt: '2024-01-15T08:00:00Z', updatedAt: '2024-01-15T08:00:00Z' },
    { id: 'lead-9', name: 'Osman Tan', email: 'osman.tan@email.com', phone: '+90 530 901 2345', status: 'contacted' as const, source: 'Walk-in', budget: 6000000, preferredLocation: 'Çayyolu', propertyType: 'Villa', notes: 'Relocating from Istanbul', assignedTo: 'user-1', createdAt: '2024-01-14T10:30:00Z', updatedAt: '2024-01-15T12:00:00Z' },
    { id: 'lead-10', name: 'Selin Ak', email: 'selin.ak@email.com', phone: '+90 531 012 3456', status: 'qualified' as const, source: 'Website', budget: 2500000, preferredLocation: 'Kavaklıdere', propertyType: 'Apartment', notes: 'Investment property', assignedTo: 'user-3', createdAt: '2024-01-13T15:20:00Z', updatedAt: '2024-01-14T16:00:00Z' },
  ],

  // Properties data
  properties: [
    { id: 'prop-1', title: 'Modern 3+1 Apartment in Çankaya', address: 'Kızılırmak Caddesi No:45', city: 'Ankara', district: 'Çankaya', price: 2500000, currency: 'TRY', type: 'sale' as const, propertyType: 'apartment' as const, bedrooms: 3, bathrooms: 2, area: 145, latitude: 39.9208, longitude: 32.8541, features: ['Balcony', 'Parking', 'Security', 'Pool'], images: ['https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=800'], status: 'available' as const, description: 'Luxurious apartment with stunning city views', createdAt: '2024-01-10T10:00:00Z', updatedAt: '2024-01-15T10:00:00Z' },
    { id: 'prop-2', title: 'Luxury Villa with Garden', address: 'Oran Sitesi 15. Cadde', city: 'Ankara', district: 'Oran', price: 8500000, currency: 'TRY', type: 'sale' as const, propertyType: 'villa' as const, bedrooms: 5, bathrooms: 4, area: 350, latitude: 39.8674, longitude: 32.8012, features: ['Garden', 'Pool', 'Smart Home', 'Garage', 'Security'], images: ['https://images.unsplash.com/photo-1613490493576-7fde63acd811?w=800'], status: 'available' as const, description: 'Magnificent villa with private pool and garden', createdAt: '2024-01-08T14:30:00Z', updatedAt: '2024-01-14T09:00:00Z' },
    { id: 'prop-3', title: 'Office Space in Business Center', address: 'Eskişehir Yolu 8. km', city: 'Ankara', district: 'Çankaya', price: 45000, currency: 'TRY', type: 'rent' as const, propertyType: 'office' as const, bedrooms: 0, bathrooms: 2, area: 200, latitude: 39.9072, longitude: 32.7987, features: ['Meeting Room', 'Reception', 'Parking', '24/7 Access'], images: ['https://images.unsplash.com/photo-1497366216548-37526070297c?w=800'], status: 'available' as const, description: 'Prime office location with all amenities', createdAt: '2024-01-12T11:00:00Z', updatedAt: '2024-01-15T08:30:00Z' },
    { id: 'prop-4', title: '2+1 Apartment Near Metro', address: 'Kızılay Meydanı Yakını', city: 'Ankara', district: 'Kızılay', price: 1800000, currency: 'TRY', type: 'sale' as const, propertyType: 'apartment' as const, bedrooms: 2, bathrooms: 1, area: 95, latitude: 39.9208, longitude: 32.8541, features: ['Metro Access', 'Balcony', 'Furnished'], images: ['https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800'], status: 'pending' as const, description: 'Central location, perfect for professionals', createdAt: '2024-01-05T09:15:00Z', updatedAt: '2024-01-13T14:20:00Z' },
    { id: 'prop-5', title: 'Commercial Space for Retail', address: 'Tunalı Hilmi Caddesi', city: 'Ankara', district: 'Kavaklıdere', price: 75000, currency: 'TRY', type: 'rent' as const, propertyType: 'commercial' as const, bedrooms: 0, bathrooms: 1, area: 120, latitude: 39.9089, longitude: 32.8656, features: ['Street Front', 'Storage', 'High Ceiling'], images: ['https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800'], status: 'available' as const, description: 'High foot traffic location for retail', createdAt: '2024-01-11T16:45:00Z', updatedAt: '2024-01-15T11:00:00Z' },
    { id: 'prop-6', title: 'Investment Land in Çayyolu', address: 'Çayyolu 8. Cadde', city: 'Ankara', district: 'Çayyolu', price: 12000000, currency: 'TRY', type: 'sale' as const, propertyType: 'land' as const, bedrooms: 0, bathrooms: 0, area: 5000, latitude: 39.8456, longitude: 32.7123, features: ['Zoned Residential', 'Road Access', 'Utilities Ready'], images: ['https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=800'], status: 'available' as const, description: 'Prime development opportunity', createdAt: '2024-01-07T10:30:00Z', updatedAt: '2024-01-12T15:00:00Z' },
    { id: 'prop-7', title: 'Penthouse with Terrace', address: 'Gaziosmanpaşa Mahallesi', city: 'Ankara', district: 'Çankaya', price: 6500000, currency: 'TRY', type: 'sale' as const, propertyType: 'apartment' as const, bedrooms: 4, bathrooms: 3, area: 220, latitude: 39.9156, longitude: 32.8612, features: ['Terrace', 'Panoramic View', 'Smart Home', 'Private Elevator'], images: ['https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800'], status: 'available' as const, description: 'Exclusive penthouse living', createdAt: '2024-01-09T13:00:00Z', updatedAt: '2024-01-14T10:30:00Z' },
    { id: 'prop-8', title: 'Cozy 1+1 for Rent', address: 'Bahçelievler 6. Cadde', city: 'Ankara', district: 'Bahçelievler', price: 15000, currency: 'TRY', type: 'rent' as const, propertyType: 'apartment' as const, bedrooms: 1, bathrooms: 1, area: 55, latitude: 39.9234, longitude: 32.8234, features: ['Furnished', 'Heating', 'Near University'], images: ['https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800'], status: 'rented' as const, description: 'Perfect for students or singles', createdAt: '2024-01-06T08:00:00Z', updatedAt: '2024-01-10T16:00:00Z' },
    { id: 'prop-9', title: 'Family Villa in Bilkent', address: 'Bilkent 3. Cadde', city: 'Ankara', district: 'Bilkent', price: 9500000, currency: 'TRY', type: 'sale' as const, propertyType: 'villa' as const, bedrooms: 6, bathrooms: 5, area: 420, latitude: 39.8712, longitude: 32.7456, features: ['Private Pool', 'Garden', 'Home Theater', 'Wine Cellar', 'Guest House'], images: ['https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800'], status: 'available' as const, description: 'Ultimate family residence', createdAt: '2024-01-04T11:30:00Z', updatedAt: '2024-01-13T09:00:00Z' },
    { id: 'prop-10', title: 'Studio Apartment Downtown', address: 'Sakarya Caddesi', city: 'Ankara', district: 'Kızılay', price: 12000, currency: 'TRY', type: 'rent' as const, propertyType: 'apartment' as const, bedrooms: 0, bathrooms: 1, area: 35, latitude: 39.9195, longitude: 32.8597, features: ['Furnished', 'Central', 'Internet Included'], images: ['https://images.unsplash.com/photo-1536376072261-38c75010e6c9?w=800'], status: 'available' as const, description: 'Compact city living', createdAt: '2024-01-13T14:00:00Z', updatedAt: '2024-01-15T09:30:00Z' },
  ],

  // Tasks data
  tasks: [
    { id: 'task-1', title: 'Call Mehmet Kaya for follow-up', description: 'Discuss property preferences and schedule viewing', type: 'call' as const, priority: 'high' as const, status: 'pending' as const, dueDate: '2024-01-16T10:00:00Z', assignedTo: 'user-1', leadId: 'lead-1', propertyId: undefined, createdAt: '2024-01-15T08:00:00Z', updatedAt: '2024-01-15T08:00:00Z' },
    { id: 'task-2', title: 'Property viewing - Luxury Villa', description: 'Meet Hasan Demir at Oran villa', type: 'viewing' as const, priority: 'high' as const, status: 'pending' as const, dueDate: '2024-01-16T14:00:00Z', assignedTo: 'user-1', leadId: 'lead-3', propertyId: 'prop-2', createdAt: '2024-01-14T16:00:00Z', updatedAt: '2024-01-14T16:00:00Z' },
    { id: 'task-3', title: 'Prepare proposal for Ali Koç', description: 'Include financing options and property comparisons', type: 'document' as const, priority: 'urgent' as const, status: 'in_progress' as const, dueDate: '2024-01-15T18:00:00Z', assignedTo: 'user-2', leadId: 'lead-5', propertyId: 'prop-9', createdAt: '2024-01-14T10:00:00Z', updatedAt: '2024-01-15T09:00:00Z' },
    { id: 'task-4', title: 'Team meeting - Weekly review', description: 'Review sales targets and pipeline', type: 'meeting' as const, priority: 'medium' as const, status: 'pending' as const, dueDate: '2024-01-17T09:00:00Z', assignedTo: 'user-1', leadId: undefined, propertyId: undefined, createdAt: '2024-01-13T11:00:00Z', updatedAt: '2024-01-13T11:00:00Z' },
    { id: 'task-5', title: 'Follow up with Ayşe Yıldız', description: 'Send office space options', type: 'follow_up' as const, priority: 'medium' as const, status: 'completed' as const, dueDate: '2024-01-15T11:00:00Z', assignedTo: 'user-2', leadId: 'lead-2', propertyId: 'prop-3', createdAt: '2024-01-14T08:00:00Z', updatedAt: '2024-01-15T10:30:00Z' },
    { id: 'task-6', title: 'Update property photos', description: 'Upload new photos for Penthouse listing', type: 'other' as const, priority: 'low' as const, status: 'pending' as const, dueDate: '2024-01-18T16:00:00Z', assignedTo: 'user-3', leadId: undefined, propertyId: 'prop-7', createdAt: '2024-01-12T14:00:00Z', updatedAt: '2024-01-12T14:00:00Z' },
    { id: 'task-7', title: 'Call Elif Şen - New lead', description: 'Initial contact for studio apartment inquiry', type: 'call' as const, priority: 'high' as const, status: 'pending' as const, dueDate: '2024-01-15T15:00:00Z', assignedTo: 'user-2', leadId: 'lead-8', propertyId: undefined, createdAt: '2024-01-15T08:30:00Z', updatedAt: '2024-01-15T08:30:00Z' },
    { id: 'task-8', title: 'Contract review meeting', description: 'Review final contract with legal team', type: 'meeting' as const, priority: 'urgent' as const, status: 'pending' as const, dueDate: '2024-01-16T11:00:00Z', assignedTo: 'user-1', leadId: 'lead-5', propertyId: 'prop-9', createdAt: '2024-01-15T07:00:00Z', updatedAt: '2024-01-15T07:00:00Z' },
  ],

  // Users/Team data
  users: [
    { id: 'user-1', name: 'Ahmet Yılmaz', email: 'ahmet@dynamiccrm.com', role: 'agent', avatar: 'https://ui-avatars.com/api/?name=Ahmet+Yilmaz&background=3b82f6&color=fff', phone: '+90 532 111 2233', performance: { leads: 45, closedDeals: 12, revenue: 3200000 } },
    { id: 'user-2', name: 'Fatma Demir', email: 'fatma@dynamiccrm.com', role: 'agent', avatar: 'https://ui-avatars.com/api/?name=Fatma+Demir&background=ec4899&color=fff', phone: '+90 533 222 3344', performance: { leads: 38, closedDeals: 15, revenue: 4100000 } },
    { id: 'user-3', name: 'Ali Öztürk', email: 'ali@dynamiccrm.com', role: 'team_lead', avatar: 'https://ui-avatars.com/api/?name=Ali+Ozturk&background=10b981&color=fff', phone: '+90 534 333 4455', performance: { leads: 52, closedDeals: 18, revenue: 5500000 } },
    { id: 'user-4', name: 'Zeynep Arslan', email: 'zeynep@dynamiccrm.com', role: 'admin', avatar: 'https://ui-avatars.com/api/?name=Zeynep+Arslan&background=f59e0b&color=fff', phone: '+90 535 444 5566', performance: { leads: 0, closedDeals: 0, revenue: 0 } },
  ],

  // Team stats
  teamStats: {
    totalAgents: 12,
    activeAgents: 10,
    avgDealsPerAgent: 8.5,
    topPerformer: 'Ali Öztürk',
    teamTarget: 15000000,
    teamAchieved: 12800000,
  },

  // Calls data
  calls: [
    { id: 'call-1', leadId: 'lead-1', leadName: 'Mehmet Kaya', userId: 'user-1', userName: 'Ahmet Yılmaz', direction: 'outbound', duration: 320, status: 'completed', outcome: 'interested', notes: 'Scheduled property viewing', createdAt: '2024-01-15T09:30:00Z' },
    { id: 'call-2', leadId: 'lead-8', leadName: 'Elif Şen', userId: 'user-2', userName: 'Fatma Demir', direction: 'inbound', duration: 180, status: 'completed', outcome: 'callback', notes: 'Will call back after 5pm', createdAt: '2024-01-15T10:15:00Z' },
    { id: 'call-3', leadId: 'lead-9', leadName: 'Osman Tan', userId: 'user-1', userName: 'Ahmet Yılmaz', direction: 'outbound', duration: 0, status: 'missed', outcome: 'no_answer', notes: '', createdAt: '2024-01-15T11:00:00Z' },
    { id: 'call-4', leadId: 'lead-3', leadName: 'Hasan Demir', userId: 'user-1', userName: 'Ahmet Yılmaz', direction: 'outbound', duration: 540, status: 'completed', outcome: 'qualified', notes: 'Very interested in Oran villa', createdAt: '2024-01-14T15:30:00Z' },
  ],

  // Call stats
  callStats: {
    totalCalls: 156,
    completedCalls: 142,
    missedCalls: 14,
    avgDuration: 285,
    callsToday: 23,
    conversionRate: 32,
  },

  // Property analytics
  propertyAnalytics: {
    totalListings: 856,
    newListingsMonth: 78,
    avgTimeOnMarket: 45,
    avgPricePerSqm: 35000,
    priceByDistrict: [
      { district: 'Çankaya', avgPrice: 42000 },
      { district: 'Oran', avgPrice: 55000 },
      { district: 'Kızılay', avgPrice: 38000 },
      { district: 'Bilkent', avgPrice: 48000 },
      { district: 'Çayyolu', avgPrice: 35000 },
    ],
    typeDistribution: [
      { type: 'Apartment', count: 520, percentage: 61 },
      { type: 'Villa', count: 156, percentage: 18 },
      { type: 'Office', count: 98, percentage: 11 },
      { type: 'Commercial', count: 52, percentage: 6 },
      { type: 'Land', count: 30, percentage: 4 },
    ],
  },

  // Sales analytics
  salesAnalytics: {
    monthlyData: [
      { month: 'Jan', sales: 8, revenue: 18500000 },
      { month: 'Feb', sales: 12, revenue: 25000000 },
      { month: 'Mar', sales: 15, revenue: 32000000 },
      { month: 'Apr', sales: 10, revenue: 22000000 },
      { month: 'May', sales: 18, revenue: 38000000 },
      { month: 'Jun', sales: 14, revenue: 29000000 },
      { month: 'Jul', sales: 20, revenue: 42000000 },
      { month: 'Aug', sales: 16, revenue: 35000000 },
      { month: 'Sep', sales: 22, revenue: 48000000 },
      { month: 'Oct', sales: 19, revenue: 41000000 },
      { month: 'Nov', sales: 25, revenue: 55000000 },
      { month: 'Dec', sales: 34, revenue: 72000000 },
    ],
    yearlyGrowth: 28,
    avgDealSize: 2800000,
  },

  // Lead conversion data
  leadConversion: {
    funnel: [
      { stage: 'New', count: 450, percentage: 100 },
      { stage: 'Contacted', count: 380, percentage: 84 },
      { stage: 'Qualified', count: 220, percentage: 49 },
      { stage: 'Proposal', count: 120, percentage: 27 },
      { stage: 'Negotiation', count: 75, percentage: 17 },
      { stage: 'Won', count: 45, percentage: 10 },
    ],
    avgConversionTime: 28,
    sourceEfficiency: [
      { source: 'Website', leads: 180, converted: 25, rate: 14 },
      { source: 'Referral', leads: 120, converted: 28, rate: 23 },
      { source: 'Social Media', leads: 95, converted: 12, rate: 13 },
      { source: 'Walk-in', leads: 55, converted: 15, rate: 27 },
    ],
  },

  // Property stats
  propertyStats: {
    viewsToday: 1245,
    inquiriesToday: 89,
    mostViewedProperty: 'prop-2',
    hotZones: ['Çankaya', 'Oran', 'Bilkent'],
  },

  // Matching settings
  matchingSettings: {
    budgetWeight: 30,
    locationWeight: 25,
    sizeWeight: 20,
    featuresWeight: 15,
    propertyTypeWeight: 10,
    autoMatch: true,
    notifyAgent: true,
    minScore: 70,
  },

  // System stats
  systemStats: {
    totalUsers: 45,
    activeUsers: 38,
    totalLeads: 1247,
    totalProperties: 856,
    totalTasks: 324,
    storageUsed: '45.2 GB',
    apiCalls: 125000,
    uptime: '99.9%',
  },

  // Audit logs
  auditLogs: [
    { id: 'log-1', action: 'user.login', user: 'Ahmet Yılmaz', ip: '192.168.1.100', timestamp: '2024-01-15T08:00:00Z', details: 'Successful login' },
    { id: 'log-2', action: 'lead.create', user: 'Fatma Demir', ip: '192.168.1.101', timestamp: '2024-01-15T08:30:00Z', details: 'Created lead: Elif Şen' },
    { id: 'log-3', action: 'property.update', user: 'Ali Öztürk', ip: '192.168.1.102', timestamp: '2024-01-15T09:15:00Z', details: 'Updated property: prop-2' },
    { id: 'log-4', action: 'settings.change', user: 'Zeynep Arslan', ip: '192.168.1.103', timestamp: '2024-01-15T10:00:00Z', details: 'Changed system settings' },
  ],

  // Roles
  roles: [
    { id: 'role-1', name: 'Admin', permissions: ['all'], userCount: 2 },
    { id: 'role-2', name: 'Team Lead', permissions: ['leads', 'properties', 'tasks', 'reports', 'team'], userCount: 4 },
    { id: 'role-3', name: 'Agent', permissions: ['leads', 'properties', 'tasks'], userCount: 25 },
    { id: 'role-4', name: 'Call Center', permissions: ['leads', 'calls'], userCount: 10 },
    { id: 'role-5', name: 'Viewer', permissions: ['view'], userCount: 4 },
  ],

  // Admin settings
  adminSettings: {
    companyName: 'Dynamic CRM',
    defaultCurrency: 'TRY',
    timezone: 'Europe/Istanbul',
    emailNotifications: true,
    smsNotifications: true,
    autoAssignment: true,
    leadRotation: 'round_robin',
  },

  // Loyalty program
  loyaltyProgram: {
    name: 'CRM Stars',
    totalMembers: 156,
    totalPointsIssued: 2450000,
    tiers: [
      { name: 'Bronze', minPoints: 0, benefits: ['5% commission bonus'] },
      { name: 'Silver', minPoints: 10000, benefits: ['10% commission bonus', 'Priority leads'] },
      { name: 'Gold', minPoints: 25000, benefits: ['15% commission bonus', 'Priority leads', 'VIP support'] },
      { name: 'Platinum', minPoints: 50000, benefits: ['20% commission bonus', 'Priority leads', 'VIP support', 'Exclusive events'] },
    ],
  },

  // Loyalty leaderboard
  loyaltyLeaderboard: [
    { rank: 1, userId: 'user-3', name: 'Ali Öztürk', points: 52000, tier: 'Platinum' },
    { rank: 2, userId: 'user-2', name: 'Fatma Demir', points: 38000, tier: 'Gold' },
    { rank: 3, userId: 'user-1', name: 'Ahmet Yılmaz', points: 28000, tier: 'Gold' },
    { rank: 4, userId: 'user-5', name: 'Mustafa Şahin', points: 15000, tier: 'Silver' },
    { rank: 5, userId: 'user-6', name: 'Ayşe Kara', points: 12000, tier: 'Silver' },
  ],

  // Loyalty rewards
  loyaltyRewards: [
    { id: 'reward-1', name: 'Weekend Getaway', points: 25000, category: 'Travel', available: 5 },
    { id: 'reward-2', name: 'Tech Gadget', points: 15000, category: 'Electronics', available: 10 },
    { id: 'reward-3', name: 'Restaurant Voucher', points: 5000, category: 'Dining', available: 20 },
    { id: 'reward-4', name: 'Spa Day', points: 10000, category: 'Wellness', available: 8 },
  ],

  // Marketplace listings
  marketplaceListings: [
    { id: 'mp-1', title: 'Lead Package - 50 Qualified Leads', price: 5000, currency: 'TRY', seller: 'LeadGen Pro', rating: 4.8, sales: 156, category: 'leads' },
    { id: 'mp-2', title: 'Property Photography Service', price: 1500, currency: 'TRY', seller: 'ProPhoto', rating: 4.9, sales: 89, category: 'services' },
    { id: 'mp-3', title: 'Virtual Tour Package', price: 2500, currency: 'TRY', seller: '360 Tours', rating: 4.7, sales: 45, category: 'services' },
    { id: 'mp-4', title: 'CRM Training Course', price: 3000, currency: 'TRY', seller: 'CRM Academy', rating: 4.6, sales: 234, category: 'training' },
  ],

  // Marketplace categories
  marketplaceCategories: [
    { id: 'cat-1', name: 'Leads', count: 25, icon: 'users' },
    { id: 'cat-2', name: 'Services', count: 48, icon: 'briefcase' },
    { id: 'cat-3', name: 'Training', count: 15, icon: 'graduation-cap' },
    { id: 'cat-4', name: 'Tools', count: 32, icon: 'wrench' },
  ],
}
