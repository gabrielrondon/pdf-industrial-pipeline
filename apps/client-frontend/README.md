# Arremate360 Lead Analyzer

Arremate360 Lead Analyzer is a React application used to analyze PDF documents and generate property auction leads. Supabase handles authentication, storage and the database while Stripe powers billing for the different plans.

## Setup

1. Install **Node.js** and **npm**.
2. Clone this repository and install dependencies:

```bash
npm install
```

3. Create a `.env` file in the project root and add the required environment variables:

```env
SUPABASE_URL=<your-supabase-url>
SUPABASE_ANON_KEY=<your-supabase-anon-key>
SUPABASE_SERVICE_ROLE_KEY=<your-supabase-service-role-key>
STRIPE_SECRET_KEY=<your-stripe-secret-key>
```

These values are needed by the application and Supabase Edge functions. You can obtain them from your Supabase project settings and Stripe dashboard.

## Running the development server

Start Vite in development mode:

```bash
npm run dev
```

The app will be available at [http://localhost:8080](http://localhost:8080).

## Deployment

The repository contains a `netlify.toml` file configured for Netlify. Build the project with:

```bash
npm run build
```

After building, deploy by connecting the repository to Netlify or using the Netlify CLI. Remember to configure the same environment variables in your Netlify project.

When running Supabase functions locally you can provide these variables with `supabase functions secrets set`.

## File limits

PDF files up to **50MB** and **1000 pages** are fully processed when using the native analysis. Larger documents will be truncated to the first 1000 pages.
