# Development Setup Guide

## 🎯 New Port Configuration (Conflict-Free)

To avoid conflicts with other projects, all applications now use unique ports:

- **Client Frontend**: [http://localhost:9080](http://localhost:9080)
- **Admin Frontend**: [http://localhost:9081](http://localhost:9081)  
- **Python API**: [http://localhost:9082](http://localhost:9082)

## 🚀 Quick Start Commands

### Start All Applications
```bash
# Start all three applications with colored output
npm run dev

# Alternative command (same as above)
npm run start:all
```

### Start Individual Applications
```bash
# Client frontend only (port 9080)
npm run dev:client

# Admin frontend only (port 9081)
npm run dev:admin

# Python API only (port 9082)
npm run dev:api
```

### Utility Commands
```bash
# Clean up hanging processes
npm run cleanup

# Test complete setup
npm run test:setup

# Full reset (cleanup + reinstall)
npm run reset
```

## 📁 Environment Files Structure

### API Environment Files
- `apps/api/.env` - Default (development settings)
- `apps/api/.env.development` - Development configuration
- `apps/api/.env.production` - Production configuration

### Frontend Environment Files
- `apps/client-frontend/.env` - Default (development settings)  
- `apps/client-frontend/.env.development` - Development configuration
- `apps/client-frontend/.env.production` - Production configuration
- `apps/admin-frontend/.env` - Default (development settings)
- `apps/admin-frontend/.env.development` - Development configuration
- `apps/admin-frontend/.env.production` - Production configuration

## 🔧 First Time Setup

1. **Install Dependencies**
   ```bash
   npm run setup
   ```

2. **Configure Environment Variables**
   - Copy `.env.example` files to `.env` in each frontend app
   - Update Supabase credentials in client frontend `.env`
   - Update database URLs if using different local database

3. **Start Development**
   ```bash
   npm run dev
   ```

## 🎨 Development Experience

- **Colored Logs**: Each application has its own color (client=cyan, admin=magenta, api=yellow)
- **Hot Reload**: All frontend applications support hot reload
- **API Auto-restart**: Python API restarts automatically on file changes (if using main_v2.py)

## 🔍 Accessing Applications

- **Client App**: [http://localhost:9080](http://localhost:9080) - Customer-facing PDF analysis interface
- **Admin App**: [http://localhost:9081](http://localhost:9081) - Administrative interface for system management
- **API Docs**: [http://localhost:9082/docs](http://localhost:9082/docs) - FastAPI interactive documentation

## ⚠️ Important Notes

- **Port 9080-9082**: These ports are now standardized to avoid conflicts
- **Environment Files**: Each app has its own environment configuration
- **Concurrent Development**: All apps can run simultaneously without conflicts
- **API Proxy**: Admin frontend proxies `/api` requests to the Python API
- **Database**: API runs in mock mode if no PostgreSQL database is available
- **Python Version**: Uses `python3` command (ensure Python 3.x is installed)

## 🐛 Troubleshooting

### Port Already in Use
If you get port conflicts, use the cleanup command:
```bash
npm run cleanup
```

Or manually check what's running on the ports:
```bash
lsof -i :9080  # Check client frontend port
lsof -i :9081  # Check admin frontend port  
lsof -i :9082  # Check API port
```

### Environment Variables Not Loading
- Ensure `.env` files exist in the correct directories
- Restart the development server after changing environment variables
- Check that variable names start with `VITE_` for frontend environment variables

### Database Issues
- API runs in mock mode if PostgreSQL is not available
- Mock mode returns sample data for testing
- For full functionality, install PostgreSQL and create `pdf_pipeline_dev` database

### Complete Setup Test
Run the automated test suite:
```bash
npm run test:setup
```
This will test all services and provide status feedback.