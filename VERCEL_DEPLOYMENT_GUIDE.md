# Vercel Deployment Guide

## Overview
This guide explains how to deploy the PDF Industrial Pipeline client frontend to Vercel.

## Prerequisites
- Vercel account
- GitHub repository access
- Railway credentials (for backend connection)
- Supabase credentials (for authentication)

## Environment Variables Required

Set these in Vercel dashboard under Project Settings > Environment Variables:

### Production Environment
```bash
NODE_ENV=production
VITE_APP_ENV=production
VITE_API_BASE_URL=https://pdf-industrial-pipeline-production.up.railway.app
VITE_SUPABASE_URL=[Your Supabase project URL]
VITE_SUPABASE_ANON_KEY=[Your Supabase anonymous key]
VITE_ENABLE_DEBUG=false
VITE_ENABLE_ANALYTICS=true
```

### Development/Preview Environment  
```bash
NODE_ENV=development
VITE_APP_ENV=development
VITE_API_BASE_URL=https://pdf-industrial-pipeline-production.up.railway.app
VITE_SUPABASE_URL=[Your Supabase project URL]
VITE_SUPABASE_ANON_KEY=[Your Supabase anonymous key]
VITE_ENABLE_DEBUG=true
VITE_ENABLE_ANALYTICS=false
```

## Deployment Steps

1. **Connect Repository**
   - Go to Vercel dashboard
   - Import from GitHub
   - Select this repository

2. **Configure Build Settings**
   - Framework: Vite
   - Root Directory: `apps/client-frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`

3. **Set Environment Variables**
   - Add all variables listed above
   - Use the actual credentials from your services

4. **Deploy**
   - Click Deploy
   - Monitor build logs for any issues

## Build Configuration

The project includes:
- `vercel.json`: Vercel-specific configuration
- `package.json`: Build scripts and dependencies
- `.vercelignore`: Files to exclude from deployment

## Post-Deployment

1. Test all functionality on live site
2. Configure custom domain if needed
3. Monitor performance metrics
4. Set up analytics and monitoring

## Troubleshooting

### Common Issues
- **Build failures**: Check environment variables are set correctly
- **API connection errors**: Verify VITE_API_BASE_URL points to Railway
- **Authentication issues**: Confirm Supabase credentials are valid

### Performance Optimization
- Enable Vercel Analytics
- Configure caching headers
- Monitor Core Web Vitals

## Security Notes
- Never commit actual credentials to version control
- Use Vercel's environment variable system
- Regularly rotate API keys and secrets