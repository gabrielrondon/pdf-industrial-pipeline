# Netlify Environment Variables - Admin Frontend

This document contains the environment variables that need to be configured in Netlify for the admin frontend deployment.

## How to Set Environment Variables in Netlify

1. Go to your Netlify dashboard
2. Select your admin frontend site
3. Go to Site settings > Environment variables
4. Add each variable below with its corresponding value

## Required Environment Variables

### API Configuration
```
VITE_API_BASE_URL = https://pdf-industrial-pipeline-production.up.railway.app
VITE_API_VERSION = v2
VITE_API_TIMEOUT = 30000
```

### Supabase Configuration (REQUIRED)
```
VITE_SUPABASE_URL = https://rjbiyndpxqaallhjmbwm.supabase.co
VITE_SUPABASE_ANON_KEY = your-supabase-anon-key-here
```

### Stripe Configuration (REQUIRED)
```
VITE_STRIPE_PUBLISHABLE_KEY = pk_live_your-stripe-publishable-key-here
```

### App Configuration
```
NODE_ENV = production
VITE_APP_NAME = PDF Industrial Pipeline - Admin
VITE_APP_VERSION = 1.0.0
```

### Admin Features
```
VITE_ENABLE_USER_MANAGEMENT = true
VITE_ENABLE_SYSTEM_MONITORING = true
VITE_ENABLE_FINANCIAL_REPORTS = true
VITE_ENABLE_BULK_OPERATIONS = true
```

### Feature Flags
```
VITE_ENABLE_SEMANTIC_SEARCH = true
VITE_ENABLE_LARGE_DOCUMENT_PROCESSING = true
VITE_ENABLE_AI_ANALYSIS = true
VITE_ENABLE_JUDICIAL_ANALYSIS = true
VITE_ENABLE_REAL_TIME_UPDATES = true
```

### Upload Configuration (Higher limits for admin)
```
VITE_MAX_FILE_SIZE = 104857600
VITE_ALLOWED_FILE_TYPES = .pdf
VITE_MAX_FILES_PER_UPLOAD = 10
```

### UI Configuration
```
VITE_DEFAULT_THEME = light
VITE_ENABLE_DARK_MODE = true
VITE_DEFAULT_LANGUAGE = pt-BR
VITE_SUPPORTED_LANGUAGES = pt-BR,en-US
```

### Performance Configuration (Faster polling for admin)
```
VITE_STATUS_POLL_INTERVAL = 1000
VITE_RESULTS_POLL_INTERVAL = 2000
VITE_BACKGROUND_POLL_INTERVAL = 10000
VITE_CACHE_DOCUMENTS = true
VITE_CACHE_DURATION = 300000
```

### Admin Security
```
VITE_REQUIRE_ADMIN_2FA = true
VITE_ADMIN_SESSION_TIMEOUT = 3600000
VITE_CSP_ENABLED = true
```

### Build Configuration
```
VITE_BUILD_SOURCEMAP = false
VITE_BUILD_MINIFY = true
```

### Regional Settings
```
VITE_TIMEZONE = America/Sao_Paulo
VITE_LOCALE = pt-BR
VITE_CURRENCY_SYMBOL = R$
```

## Optional Environment Variables

### Analytics (Optional - set if you have accounts)
```
VITE_GA_TRACKING_ID = G-XXXXXXXXXX
VITE_SENTRY_DSN = https://your-sentry-dsn@sentry.io/project-id
VITE_SENTRY_ENVIRONMENT = production
```

### Company Information (Optional)
```
VITE_COMPANY_NAME = Your Company Name
VITE_COMPANY_EMAIL = contact@your-domain.com
VITE_SUPPORT_EMAIL = support@your-domain.com
```

### Legal Pages (Optional)
```
VITE_PRIVACY_POLICY_URL = https://your-domain.com/privacy
VITE_TERMS_OF_SERVICE_URL = https://your-domain.com/terms
```

### CORS Configuration (Optional)
```
VITE_ALLOWED_ORIGINS = https://admin.your-domain.com
```

## Deployment Notes

- All variables starting with `VITE_` are exposed to the client-side code
- The Railway API URL is: `https://pdf-industrial-pipeline-production.up.railway.app`
- Supabase and Stripe credentials are the actual production values
- Admin frontend has higher file upload limits and faster polling intervals
- After setting these variables, redeploy your site in Netlify for changes to take effect

## Admin-Specific Features

The admin frontend includes additional features:
- User management capabilities
- System monitoring and metrics
- Financial reporting
- Bulk operations support
- Enhanced security with 2FA requirements
- Higher file processing limits