# CJEI Board Game Recommendation System - Frontend

Frontend web application for the CJEI Board Game Recommendation System, built with React, TypeScript, and Vite.

## 🚀 Tech Stack

- **Framework**: React 18+
- **Language**: TypeScript
- **Build Tool**: Vite
- **Routing**: React Router v6
- **State Management**: TanStack Query (React Query)
- **HTTP Client**: Axios
- **Styling**: Tailwind CSS v4
- **Forms**: React Hook Form + Zod validation
- **Icons**: Lucide React

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/      # Reusable UI components
│   ├── pages/          # Page components (routes)
│   ├── services/       # API service layer
│   ├── types/          # TypeScript types/interfaces
│   ├── hooks/          # Custom React hooks
│   ├── utils/          # Utility functions
│   ├── lib/            # Third-party library configs
│   ├── App.tsx         # Main app component
│   └── main.tsx        # Entry point
├── public/             # Static assets
├── .env.development    # Development environment variables
├── vite.config.ts      # Vite configuration
├── tailwind.config.js  # Tailwind configuration
├── tsconfig.json       # TypeScript configuration
└── package.json        # Dependencies
```

## 🛠️ Setup & Installation

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend API running on http://localhost:8000

### Install Dependencies

```bash
npm install
```

### Environment Variables

Create a `.env.development` file:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
```

## 📜 Available Scripts

### Development

```bash
npm run dev
```

Runs the app in development mode at [http://localhost:5173](http://localhost:5173)

### Build

```bash
npm run build
```

Builds the app for production to the `dist` folder

### Preview

```bash
npm run preview
```

Previews the production build locally

## 🗺️ Routes

- `/` - Home page
- `/sessions/new` - Create new session profile
- `/games` - Game catalog browser
- `/recommendations/:sessionId` - View recommendations for a session
- `/skills` - Skill taxonomy tree viewer
- `/feedback/:recommendationId` - Submit/edit feedback

## 📦 Status

**Current Version**: 0.1.0 (MVP Scaffold)

**Completed**:
- ✅ Project setup with Vite + React + TypeScript
- ✅ Tailwind CSS v4 configuration
- ✅ React Router setup
- ✅ API client with Axios
- ✅ TypeScript types/interfaces
- ✅ Service layer (games, sessions, skills, recommendations)
- ✅ Basic page structure

**Next Steps**:
- 🔨 UI components implementation
- 🔨 Form implementations with validation
- 🔨 Game catalog with filters
- 🔨 Recommendation display
- 🔨 Skills tree visualization

---

**Built with ❤️ for educational gaming - CJEI**
