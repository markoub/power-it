# PowerIt Frontend

This is a [Next.js](https://nextjs.org) static frontend for the PowerIt Presentation Creator application, integrated with a FastAPI backend.

## Getting Started

First, make sure the backend is running (see main README.md for instructions), then start the frontend development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the application.

## Static Build

To create a static build of the frontend:

```bash
npm run build
```

This will create a static build in the `build` directory, which can be served using any static file server.

To test the static build locally:

```bash
npx serve build
```

## Features

- Modern UI built with Next.js, React, and Tailwind CSS
- Integration with the backend API for fetching and creating presentations
- AI-powered presentation creation workflow
- Interactive presentation editor with AI Wizard assistant
- Context-aware wizard for modifying research, slides, and presentations
- Responsive design for mobile and desktop
- Static build for easy deployment on any hosting platform

## Backend Integration

The frontend integrates with the backend API through:

1. API client in `lib/api.ts` which handles all API requests directly to the backend
2. CORS-enabled API calls to connect to the backend
3. Robust error handling and loading states
4. Environment variables for configuring the backend URL

## Project Structure

```
frontend/
├── app/             # Next.js app router pages
│   ├── create/      # Create presentation page
│   ├── edit/        # Edit presentation page
│   └── page.tsx     # Home page
├── components/      # Reusable React components
│   ├── ui/          # UI components (buttons, inputs, etc.)
│   ├── wizard/      # AI Wizard components
│   ├── steps/       # Step-specific components
│   ├── slides/      # Slide type renderers
│   └── ...          # Application-specific components
├── lib/             # Utilities and services
│   ├── api.ts       # API client for backend communication
│   ├── types.ts     # TypeScript type definitions
│   └── ...          # Other utilities
├── public/          # Static assets
└── build/           # Static build output (after running build)
```

## Development

You can start editing any page or component to see the changes reflected in real-time.

### Environment Variables

The frontend uses the following environment variables:

- `NEXT_PUBLIC_API_URL` - Backend API URL (defaults to http://localhost:8000)

To set environment variables for production, create a `.env.production` file with the appropriate settings.

For local development, create a `.env.local` file with:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Dependencies

Main dependencies include:

- Next.js - React framework
- Tailwind CSS - Utility-first CSS framework
- shadcn/ui - UI component library
- framer-motion - Animation library
- sonner - Toast notifications

## Learn More

To learn more about the technologies used in this project:

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://reactjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Framer Motion](https://www.framer.com/motion)

## Deployment

The application can be deployed as a static site on any hosting platform that supports static files, such as:

- Netlify
- Vercel
- GitHub Pages
- Amazon S3
- Cloudflare Pages

Example deployment with Netlify:

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Build the site
npm run build

# Deploy to Netlify
netlify deploy --dir=build
```
