# Seed Data Directory
 
This directory contains development seed data.
**DELETE THIS ENTIRE DIRECTORY** when connecting to production database.
 
## Files
- `leads.json` - Sample lead records
- `properties.json` - Sample property listings  
- `users.json` - Sample user/agent accounts
- `offices.json` - Sample office locations
- `tasks.json` - Sample task records
- `calls.json` - Sample call records
 
## Usage
```typescript
import { leads, properties, users } from '@/data'
```

## When to Delete
Delete when:
- Supabase is fully connected
- All tRPC endpoints return real data
- Production deployment is ready
