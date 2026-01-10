# GitHub Copilot Instructions - CJEI Board Game Recommendation System (Frontend)

## Project Overview

**Project Name:** `cjei-recommendations-frontend`  
**Purpose:** Interfaz web React para el sistema de recomendación de juegos de mesa del CJEI. Permite a asesores pedagógicos crear consultas basadas en contexto de clase, visualizar recomendaciones rankeadas con explicaciones, y registrar feedback post-sesión.

**Key Technologies:**
- **Framework:** React 18+ con TypeScript 5+
- **Build Tool:** Vite 5+
- **Routing:** React Router v6
- **State Management:** Context API + custom hooks
- **UI Components:** Material-UI (MUI) v5
- **Forms:** React Hook Form + Zod validation
- **HTTP Client:** Axios
- **Styling:** MUI theming + CSS-in-JS (Emotion)

**Target Environment:** Modern browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)

**MVP Scope:** Implementar únicamente las interfaces necesarias para los 19 requerimientos funcionales MUST del backend.

---

## Architecture

### Project Structure
```
frontend/
├── public/
│   ├── favicon.ico
│   └── logo-cjei.png
├── src/
│   ├── main.tsx                     # Application entry point
│   ├── App.tsx                      # Root component with routing
│   ├── vite-env.d.ts               # Vite type definitions
│   ├── api/                         # API client and services
│   │   ├── client.ts                # Axios instance with interceptors
│   │   ├── auth.service.ts          # Authentication endpoints
│   │   ├── games.service.ts         # Games CRUD endpoints
│   │   ├── skills.service.ts        # Skills endpoints
│   │   ├── recommendations.service.ts # Recommendations endpoints
│   │   └── feedback.service.ts      # Feedback endpoints
│   ├── components/                  # Reusable UI components
│   │   ├── common/                  # Generic components
│   │   │   ├── LoadingSpinner.tsx
│   │   │   ├── ErrorAlert.tsx
│   │   │   ├── ConfirmDialog.tsx
│   │   │   └── PageHeader.tsx
│   │   ├── layout/                  # Layout components
│   │   │   ├── MainLayout.tsx       # Main app layout with nav
│   │   │   ├── Navbar.tsx           # Top navigation bar
│   │   │   └── Footer.tsx           # Footer (optional)
│   │   ├── games/                   # Game-related components
│   │   │   ├── GameCard.tsx         # Game summary card
│   │   │   ├── GameDetailModal.tsx  # Full game details dialog
│   │   │   ├── GameList.tsx         # Paginated game list
│   │   │   └── GameForm.tsx         # Create/edit game form (admin)
│   │   ├── skills/                  # Skill-related components
│   │   │   ├── SkillCard.tsx
│   │   │   ├── SkillForm.tsx        # Create/edit skill form (admin)
│   │   │   └── SkillAssignmentDialog.tsx
│   │   ├── recommendations/         # Recommendation components
│   │   │   ├── SessionProfileForm.tsx     # Main consultation form
│   │   │   ├── ValidationWarnings.tsx     # Warnings display
│   │   │   ├── RecommendationCard.tsx     # Single recommendation
│   │   │   ├── RecommendationList.tsx     # Results list
│   │   │   └── ExplanationPanel.tsx       # Detailed explanation
│   │   └── feedback/                # Feedback components
│   │       ├── FeedbackForm.tsx     # Submit feedback dialog
│   │       └── FeedbackSummary.tsx  # Aggregated feedback display
│   ├── pages/                       # Page-level components (routes)
│   │   ├── auth/
│   │   │   └── LoginPage.tsx        # Login screen
│   │   ├── recommendations/
│   │   │   ├── CreateConsultationPage.tsx   # Main workflow page
│   │   │   └── RecommendationsResultPage.tsx # Results display
│   │   ├── games/
│   │   │   ├── GamesListPage.tsx    # Browse/search games
│   │   │   └── GameDetailPage.tsx   # Single game view
│   │   ├── admin/
│   │   │   ├── AdminDashboard.tsx   # Admin home
│   │   │   ├── ManageGamesPage.tsx  # Games CRUD
│   │   │   ├── ManageSkillsPage.tsx # Skills CRUD
│   │   │   └── ConfigPage.tsx       # Recommendation config
│   │   └── NotFoundPage.tsx         # 404 page
│   ├── context/                     # React Context providers
│   │   └── AuthContext.tsx          # Authentication state + methods
│   ├── hooks/                       # Custom React hooks
│   │   ├── useAuth.ts               # Auth context consumer
│   │   ├── useApi.ts                # Generic API call wrapper
│   │   ├── useGames.ts              # Games data fetching
│   │   ├── useSkills.ts             # Skills data fetching
│   │   └── useToast.ts              # Toast notifications
│   ├── types/                       # TypeScript type definitions
│   │   ├── api.types.ts             # API request/response types
│   │   ├── models.types.ts          # Domain models (User, Game, Skill, etc.)
│   │   └── forms.types.ts           # Form-specific types
│   ├── utils/                       # Utility functions
│   │   ├── formatters.ts            # Date, number formatting
│   │   ├── validators.ts            # Custom Zod schemas
│   │   └── constants.ts             # App constants
│   ├── theme/                       # MUI theme configuration
│   │   └── theme.ts                 # Custom CJEI theme
│   └── routes/                      # Route definitions
│       ├── ProtectedRoute.tsx       # Auth-protected route wrapper
│       └── AdminRoute.tsx           # Admin-only route wrapper
├── index.html                       # HTML entry point
├── package.json
├── tsconfig.json
├── tsconfig.node.json
├── vite.config.ts
└── .env.example
```

### Key Components

**1. Authentication Layer**
- **AuthContext**: Manages authentication state (user, token, role)
- **LoginPage**: JWT-based login form
- **ProtectedRoute**: Redirects to login if not authenticated
- **AdminRoute**: Restricts access to admin-only routes

**2. Recommendation Workflow**
- **SessionProfileForm**: Captures class context (RF-CTX-01)
  - Objectives, skills, time, group size, language, modality
  - Real-time validation with Zod
  - Displays validation warnings from backend (RF-CTX-02)
- **RecommendationList**: Displays Top-N results (RF-REC-01)
  - Ranked cards with scores
  - Quick view of key attributes
  - Click to expand details
- **ExplanationPanel**: Shows why game was recommended (RF-EXP-01)
  - Skill match, operational fit, mechanics, warnings

**3. Game Management (Admin)**
- **GamesListPage**: Paginated, searchable game catalog
- **GameForm**: Create/edit games with normalization (RF-ING-01, RF-ING-02)
- **SkillAssignmentDialog**: Assign primary/secondary skills (RF-TAX-02)

**4. Feedback System**
- **FeedbackForm**: Post-session feedback submission (RF-RETRO-01)
  - Utility rating (1-5 stars)
  - Qualitative comments
  - Skill actually worked
- **FeedbackSummary**: Aggregated feedback display (RF-RETRO-02)
  - Average utility, distribution chart
  - Recent comments
  - Skill discrepancies warning

### Data Flow Patterns

**Authentication Flow:**
```
LoginPage
    ↓
POST /api/auth/login (email, password)
    ↓
Receive JWT + user object
    ↓
Store in AuthContext + localStorage
    ↓
Set Authorization header in Axios client
    ↓
Redirect to main app
```

**Recommendation Flow:**
```
CreateConsultationPage
    ↓
User fills SessionProfileForm
    ↓
Zod validation (client-side)
    ↓
POST /api/recommendations/generate
    ↓
Backend returns warnings (if any)
    ↓
Display warnings, user confirms
    ↓
Backend returns recommendations or NoResultsResponse
    ↓
Navigate to RecommendationsResultPage
    ↓
Display ranked list with explanations
    ↓
User clicks "Give Feedback" → FeedbackForm
```

**State Management:**
```
Global State (Context):
  - AuthContext: user, token, login(), logout()

Local State (useState/useReducer):
  - Form state: React Hook Form
  - UI state: modals, loading, errors

Server State (custom hooks):
  - useGames(): fetch, cache, invalidate
  - useSkills(): fetch, cache
  - useApi(): generic fetch wrapper with loading/error states
```

---

## Development Workflow

### Setup
```bash
# Clone repository
git clone <repository-url>
cd cjei-recommendations/frontend

# Install dependencies
npm install
# or
yarn install
# or
pnpm install

# Configure environment
cp .env.example .env
# Edit .env with backend API URL

# Start development server
npm run dev
```

### Build & Run

**Development:**
```bash
# Start dev server with hot reload
npm run dev
# Access: http://localhost:5173

# Type checking in watch mode
npm run type-check -- --watch
```

**Production Build:**
```bash
# Build for production
npm run build

# Preview production build locally
npm run preview

# Serve static files (after build)
# Output in dist/ directory
```

**Linting & Formatting:**
```bash
# Run ESLint
npm run lint

# Fix auto-fixable issues
npm run lint:fix

# Format with Prettier
npm run format

# Type check
npm run type-check
```

### Testing
```bash
# Run unit tests (Vitest)
npm run test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run E2E tests (if implemented)
npm run test:e2e
```

---

## Conventions & Patterns

### Code Style

**TypeScript:**
- Strict mode enabled
- No implicit any
- Explicit return types for exported functions
- Interface for object shapes, Type for unions/intersections

**Naming:**
- **Components:** `PascalCase` (e.g., `SessionProfileForm.tsx`)
- **Hooks:** `camelCase` with `use` prefix (e.g., `useAuth.ts`)
- **Types/Interfaces:** `PascalCase` with descriptive suffix (e.g., `GameResponse`, `LoginFormData`)
- **Files:** Match export name (e.g., `GameCard.tsx` exports `GameCard`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `API_BASE_URL`)

**File Organization:**
- One component per file
- Co-locate component-specific types in same file
- Export types from `types/` for shared interfaces
- Barrel exports (index.ts) for cleaner imports

**Import Order:**
1. React and external libraries
2. Internal absolute imports (@/...)
3. Relative imports (../, ./)
4. CSS/Style imports

Example:
```typescript
import React, { useState } from 'react';
import { Button, TextField } from '@mui/material';
import { useForm } from 'react-hook-form';

import { useAuth } from '@/hooks/useAuth';
import { LoginRequest } from '@/types/api.types';

import { validateEmail } from './utils';
```

### Common Patterns

**Component Structure:**
```typescript
// 1. Imports
import React from 'react';
import { Box, Typography } from '@mui/material';

// 2. Types/Interfaces
interface GameCardProps {
  game: Game;
  onSelect?: (game: Game) => void;
}

// 3. Component
export const GameCard: React.FC<GameCardProps> = ({ game, onSelect }) => {
  // 4. Hooks (in order: state, effects, custom hooks)
  const [expanded, setExpanded] = useState(false);
  
  // 5. Event handlers
  const handleClick = () => {
    onSelect?.(game);
  };
  
  // 6. Render
  return (
    <Box>
      <Typography>{game.name}</Typography>
    </Box>
  );
};
```

**API Service Pattern:**
```typescript
// api/games.service.ts
import { apiClient } from './client';
import { Game, GameCreate, GameList } from '@/types/models.types';

export const gamesService = {
  async getAll(params: { page?: number; search?: string }): Promise<GameList> {
    const { data } = await apiClient.get('/games', { params });
    return data;
  },
  
  async getById(id: string): Promise<Game> {
    const { data } = await apiClient.get(`/games/${id}`);
    return data;
  },
  
  async create(gameData: GameCreate): Promise<Game> {
    const { data } = await apiClient.post('/games', gameData);
    return data;
  },
  
  // ... more methods
};
```

**Custom Hook Pattern:**
```typescript
// hooks/useGames.ts
import { useState, useEffect } from 'react';
import { gamesService } from '@/api/games.service';
import { Game } from '@/types/models.types';

export const useGames = (page: number = 1, search?: string) => {
  const [games, setGames] = useState<Game[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);
  
  useEffect(() => {
    const fetchGames = async () => {
      setLoading(true);
      setError(null);
      try {
        const result = await gamesService.getAll({ page, search });
        setGames(result.items);
        setTotal(result.total);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error loading games');
      } finally {
        setLoading(false);
      }
    };
    
    fetchGames();
  }, [page, search]);
  
  return { games, loading, error, total };
};
```

**Form with React Hook Form + Zod:**
```typescript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

// Zod schema
const loginSchema = z.object({
  email: z.string().email('Invalid email format'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

type LoginFormData = z.infer<typeof loginSchema>;

export const LoginForm: React.FC = () => {
  const { register, handleSubmit, formState: { errors } } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });
  
  const onSubmit = async (data: LoginFormData) => {
    // Handle login
  };
  
  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <TextField
        {...register('email')}
        error={!!errors.email}
        helperText={errors.email?.message}
        label="Email"
      />
      {/* ... */}
    </form>
  );
};
```

**Error Handling:**
```typescript
// Axios interceptor for global error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login
      authContext.logout();
    }
    
    if (error.response?.status === 403) {
      // Show permission denied message
    }
    
    return Promise.reject(error);
  }
);

// Component-level error handling
try {
  await gamesService.create(gameData);
  showToast('Game created successfully', 'success');
} catch (error) {
  if (axios.isAxiosError(error)) {
    showToast(error.response?.data?.detail || 'Error creating game', 'error');
  }
}
```

**Authentication Pattern:**
```typescript
// context/AuthContext.tsx
interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  isAdmin: boolean;
}

// hooks/useAuth.ts
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

// routes/ProtectedRoute.tsx
export const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
};
```

**Loading States:**
```typescript
// Component with loading state
const GameDetailPage: React.FC = () => {
  const { id } = useParams();
  const [game, setGame] = useState<Game | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    // Fetch logic
  }, [id]);
  
  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorAlert message={error} />;
  if (!game) return <Typography>Game not found</Typography>;
  
  return <GameDetail game={game} />;
};
```

---

## Important Notes

### Critical Requirements

**1. MVP Scope - MUST Features Only:**

**Implement these pages/features:**
- ✅ Login page with JWT authentication
- ✅ Create consultation page (session profile form)
- ✅ Recommendations results page (ranked list + explanations)
- ✅ Games list page (browse/search, view details)
- ✅ Admin pages: manage games, manage skills, assign skills
- ✅ Feedback submission dialog
- ✅ Feedback summary display in game details

**Do NOT implement (Should/Could):**
- ❌ Session templates (RF-CTX-03)
- ❌ Advanced search filters (RF-UI-05)
- ❌ User management UI (RF-ADM-03)
- ❌ Analytics dashboard (RF-RETRO-03)
- ❌ Report exports (RF-RETRO-04)

**2. Authentication Requirements:**

**JWT Token Management:**
- Store token in localStorage (key: `cjei_token`)
- Store user object in localStorage (key: `cjei_user`)
- Include token in all API requests via Authorization header
- Redirect to /login on 401 responses
- Clear storage on logout

**Protected Routes:**
```typescript
// Public routes
/login

// Authenticated routes (asesor + admin)
/
/recommendations/new
/recommendations/:id
/games
/games/:id

// Admin-only routes
/admin
/admin/games
/admin/skills
/admin/config
```

**3. Form Validation Rules:**

**Session Profile Form (SessionProfileCreate):**
- `class_objectives`: required, min 10 characters
- `primary_skill_id`: required, UUID from skills dropdown
- `secondary_skill_ids`: optional, array of UUIDs
- `available_time`: required, integer 15-240
- `group_size`: required, integer 1-100
- `language_restriction`: required, enum ["ninguna", "baja", "media", "alta"]
- `modality_preference`: optional, enum ["competitivo", "cooperativo", "sin_preferencia"]
- `additional_constraints`: optional, max 500 characters

**Display backend warnings** (ValidationWarning[]) after form submission:
- Show in Alert/Banner above results
- List all warnings with their suggestions
- Allow user to proceed anyway

**4. UI/UX Requirements:**

**Recommendation Cards Must Display:**
- Rank (#1, #2, ..., #10)
- Game name and image
- Score (0-100, display as progress bar or badge)
- Key attributes: players, duration, complexity
- Primary skill badge
- "View Details" button → expands ExplanationPanel
- "Give Feedback" button → opens FeedbackForm dialog

**Explanation Panel Must Show:**
- Skill match explanation (primary/secondary)
- Operational fit (players, time, language)
- Relevant mechanics (top 3)
- Warnings (if any) in alert/warning style
- Link to full game details

**Feedback Form Must Include:**
- Star rating (1-5) for utility *required*
- "Was this game used?" toggle *required*
- Skill actually worked (dropdown, optional)
- "What worked well" (textarea, max 500 chars)
- "What didn't work" (textarea, max 500 chars)
- "Additional notes" (textarea, max 500 chars)
- Edit window notice: "You can edit this feedback for 7 days"

**5. Accessibility Requirements:**

- All forms have proper labels
- Buttons have descriptive text (no icon-only buttons without aria-label)
- Color contrast meets WCAG AA standards
- Keyboard navigation works for all interactive elements
- Error messages are screen-reader friendly

**6. Responsive Design:**

**Breakpoints:**
- Mobile: <600px (sm)
- Tablet: 600-960px (md)
- Desktop: >960px (lg)

**Mobile Considerations:**
- Stack cards vertically
- Collapsible navigation drawer
- Touch-friendly tap targets (min 44x44px)
- Simplified tables on mobile

**7. Performance Targets:**

- Initial page load: <2 seconds
- Route transitions: <300ms
- API calls: show loading indicator if >500ms
- Pagination: 10-20 items per page (configurable)
- Debounce search input: 300ms

### Gotchas and Non-Obvious Behaviors

**1. MUI Theme Customization:**
```typescript
// theme/theme.ts
import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2', // CJEI brand color (update with actual)
    },
    secondary: {
      main: '#dc004e',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none', // Disable uppercase
        },
      },
    },
  },
});
```

**2. Axios Client Setup:**
```typescript
// api/client.ts
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to all requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('cjei_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 globally
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('cjei_token');
      localStorage.removeItem('cjei_user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

**3. React Router v6 Patterns:**
```typescript
// App.tsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        
        <Route element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
          <Route path="/" element={<Navigate to="/recommendations/new" replace />} />
          <Route path="/recommendations/new" element={<CreateConsultationPage />} />
          <Route path="/recommendations/:id" element={<RecommendationsResultPage />} />
          <Route path="/games" element={<GamesListPage />} />
          <Route path="/games/:id" element={<GameDetailPage />} />
        </Route>
        
        <Route element={<AdminRoute><MainLayout /></AdminRoute>}>
          <Route path="/admin" element={<AdminDashboard />} />
          <Route path="/admin/games" element={<ManageGamesPage />} />
          <Route path="/admin/skills" element={<ManageSkillsPage />} />
          <Route path="/admin/config" element={<ConfigPage />} />
        </Route>
        
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
}
```

**4. Type Safety with API Responses:**
```typescript
// types/models.types.ts
export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'asesor' | 'admin';
  is_active: boolean;
  created_at: string;
}

export interface Game {
  id: string;
  name: string;
  bgg_id: number;
  duration_min: number;
  complexity: number;
  min_players: number;
  max_players: number;
  mechanics: string[];
  language_dependency: 'ninguna' | 'baja' | 'media' | 'alta';
  bgg_rank: number | null;
  available: boolean;
  image_url: string | null;
  description: string;
  primary_skill: SkillSummary | null;
  secondary_skill: SkillSummary | null;
  created_at: string;
}

// Always type API responses
const fetchGame = async (id: string): Promise<Game> => {
  const { data } = await apiClient.get<Game>(`/games/${id}`);
  return data;
};
```

**5. Environment Variables:**
```env
# .env.example
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_NAME=CJEI Recommendations
```

Access in code:
```typescript
const apiUrl = import.meta.env.VITE_API_BASE_URL;
```

**6. Handling NoResultsResponse:**
```typescript
// Backend can return either RecommendationResult[] or NoResultsResponse
interface NoResultsResponse {
  message: string;
  failed_constraints: string[];
  suggestions: string[];
}

// Type guard
function isNoResults(data: any): data is NoResultsResponse {
  return 'failed_constraints' in data;
}

// In component
const handleGenerate = async (profileData: SessionProfileCreate) => {
  const result = await recommendationsService.generate(profileData);
  
  if (isNoResults(result)) {
    // Show no results message with suggestions
    setNoResults(result);
  } else {
    // Show recommendations
    setRecommendations(result);
  }
};
```

**7. Date Formatting:**
```typescript
// utils/formatters.ts
export const formatDate = (isoString: string): string => {
  return new Date(isoString).toLocaleDateString('es-CO', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

export const formatDateTime = (isoString: string): string => {
  return new Date(isoString).toLocaleString('es-CO');
};
```

### Key Dependencies and Purposes

**Core:**
- **react**: UI library
- **react-dom**: React renderer for web
- **react-router-dom**: Client-side routing
- **typescript**: Type safety

**UI:**
- **@mui/material**: Component library
- **@mui/icons-material**: Icon set
- **@emotion/react**: CSS-in-JS (MUI dependency)
- **@emotion/styled**: Styled components (MUI dependency)

**Forms & Validation:**
- **react-hook-form**: Form state management
- **zod**: Schema validation
- **@hookform/resolvers**: Zod integration for RHF

**API:**
- **axios**: HTTP client
- **@tanstack/react-query** (optional): Server state management (if added post-MVP)

**Dev Tools:**
- **vite**: Build tool and dev server
- **@vitejs/plugin-react**: Vite React plugin
- **eslint**: Linting
- **prettier**: Code formatting
- **vitest**: Unit testing
- **@testing-library/react**: React component testing

---

## Quick Reference

### Common Commands Cheat Sheet

```bash
# Development
npm run dev              # Start dev server (http://localhost:5173)
npm run build            # Production build
npm run preview          # Preview production build locally

# Code Quality
npm run lint             # Run ESLint
npm run lint:fix         # Fix auto-fixable lint issues
npm run format           # Format with Prettier
npm run type-check       # TypeScript type checking

# Testing
npm run test             # Run tests
npm run test:watch       # Run tests in watch mode
npm run test:coverage    # Run tests with coverage report

# Dependencies
npm install <package>    # Add dependency
npm install -D <package> # Add dev dependency
npm update               # Update all dependencies
npm outdated             # Check for outdated packages
```

### MUI Components Quick Reference

**Layout:**
```typescript
import { Box, Container, Grid, Stack, Paper } from '@mui/material';

<Container maxWidth="lg">
  <Grid container spacing={2}>
    <Grid item xs={12} md={6}>
      <Paper elevation={2}>Content</Paper>
    </Grid>
  </Grid>
</Container>
```

**Typography:**
```typescript
import { Typography } from '@mui/material';

<Typography variant="h4" component="h1">Title</Typography>
<Typography variant="body1">Body text</Typography>
```

**Forms:**
```typescript
import { TextField, Select, MenuItem, Button, FormControl, FormLabel } from '@mui/material';

<TextField
  label="Name"
  value={name}
  onChange={(e) => setName(e.target.value)}
  error={!!error}
  helperText={error}
  fullWidth
/>
```

**Feedback:**
```typescript
import { Alert, Snackbar, CircularProgress } from '@mui/material';

<Alert severity="success">Success message</Alert>
<CircularProgress />
```

### Type Definitions Template

```typescript
// types/models.types.ts - Main domain models
export interface User { /* ... */ }
export interface Game { /* ... */ }
export interface Skill { /* ... */ }
export interface Recommendation { /* ... */ }

// types/api.types.ts - API request/response types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface SessionProfileCreate {
  class_objectives: string;
  primary_skill_id: string;
  secondary_skill_ids: string[];
  available_time: number;
  group_size: number;
  language_restriction: 'ninguna' | 'baja' | 'media' | 'alta';
  modality_preference: 'competitivo' | 'cooperativo' | 'sin_preferencia';
  additional_constraints?: string;
}

export interface ValidationWarning {
  type: string;
  message: string;
  suggestions: string[];
}

export interface RecommendationExplanation {
  skill_match: string;
  operational_fit: string[];
  relevant_mechanics: string[];
  warnings: string[];
  boost_applied: string | null;
}

export interface RecommendationResult {
  game: Game;
  rank: number;
  score: number;
  explanation: RecommendationExplanation;
}

export interface NoResultsResponse {
  message: string;
  failed_constraints: string[];
  suggestions: string[];
}

export interface FeedbackCreate {
  game_id: string;
  session_profile_id?: string;
  was_used: boolean;
  utility_rating: number;
  skill_actually_worked_id?: string;
  what_worked_well?: string;
  what_didnt_work?: string;
  additional_notes?: string;
}

export interface FeedbackSummary {
  game_id: string;
  game_name: string;
  total_uses: number;
  average_utility: number;
  rating_distribution: Record<number, number>;
  recent_comments: FeedbackComment[];
  skill_discrepancies: SkillDiscrepancy | null;
}

// types/forms.types.ts - Form-specific types
export type SessionProfileFormData = SessionProfileCreate;

export interface GameFormData {
  name: string;
  bgg_id: number;
  duration_min: number;
  complexity: number;
  min_players: number;
  max_players: number;
  mechanics: string[];
  language_dependency: string;
  available: boolean;
  description?: string;
  bgg_rank?: number;
  image_url?: string;
}
```

---

## Implementation Priorities

### Phase 1: Core Infrastructure
**Goal:** Authentication and basic navigation working

**Tasks:**
1. Setup Vite project with TypeScript + React
2. Install and configure dependencies (MUI, React Router, Axios, RHF, Zod)
3. Create MUI theme with CJEI branding
4. Implement API client with Axios interceptors
5. Implement AuthContext with login/logout
6. Create MainLayout with Navbar
7. Create LoginPage with form validation
8. Implement ProtectedRoute and AdminRoute wrappers
9. Setup basic routing structure

**Acceptance Criteria:**
- User can login with email/password
- JWT token stored and sent with all requests
- 401 responses redirect to login
- Navigation bar shows user info and logout button
- Protected routes redirect to login if not authenticated
- Admin routes show 403 if user is not admin

---

### Phase 2: Recommendation Workflow
**Goal:** Core user journey from consultation to results

**Tasks:**
1. Create types for SessionProfile and Recommendations
2. Implement SessionProfileForm component
   - All required fields with Zod validation
   - Skills dropdown (fetch from API)
   - Language and modality selects
   - Submit button
3. Implement ValidationWarnings component
4. Implement recommendationsService API calls
5. Create RecommendationsResultPage
6. Implement RecommendationCard component
7. Implement ExplanationPanel component (expandable)
8. Handle NoResultsResponse case

**Acceptance Criteria:**
- Form validates all fields correctly
- Backend warnings display clearly
- Recommendations show ranked 1-10
- Each card shows score, key attributes, skill badge
- Clicking card expands explanation panel
- Explanation shows all required fields (skill match, fit, mechanics, warnings)
- No results case shows message with suggestions

---

### Phase 3: Games Browsing
**Goal:** Users can browse and view game details

**Tasks:**
1. Create types for Game and GameList
2. Implement gamesService API calls
3. Create GamesListPage with pagination
4. Implement GameCard component (summary view)
5. Create GameDetailPage
6. Implement GameDetailModal (alternative: full page)
7. Display game attributes, skills, and mechanics
8. Show feedback summary in game detail

**Acceptance Criteria:**
- Games list loads with pagination
- Search by name works (debounced)
- Clicking game shows full details
- Game details show all normalized attributes
- Primary/secondary skills displayed
- Feedback summary shown (if available)

---

### Phase 4: Feedback System
**Goal:** Advisors can submit and view feedback

**Tasks:**
1. Create types for Feedback and FeedbackSummary
2. Implement feedbackService API calls
3. Create FeedbackForm dialog component
   - Star rating input (1-5)
   - "Was used" toggle
   - Skill dropdown (optional)
   - Three text areas for comments
   - 7-day edit window notice
4. Implement FeedbackSummary component
   - Average utility display
   - Rating distribution chart (bar chart or pie chart)
   - Recent comments list
   - Skill discrepancy warning
5. Add "Give Feedback" button to RecommendationCard
6. Display FeedbackSummary in GameDetailPage

**Acceptance Criteria:**
- Feedback form opens from recommendation card
- Form validates required fields (rating, was_used)
- Submission success shows toast message
- Feedback summary aggregates correctly
- Rating distribution visualized
- Skill discrepancies highlighted in warning banner

---

### Phase 5: Admin Features
**Goal:** Admins can manage games and skills

**Tasks:**
1. Create AdminDashboard page (simple welcome page)
2. Implement ManageGamesPage
   - Games list with edit/delete actions
   - "Add Game" button → GameForm dialog
   - Pagination
3. Implement GameForm component
   - All game fields
   - Mechanics multi-select
   - Client-side validation
   - Submit to POST /games or PUT /games/{id}
4. Implement ManageSkillsPage
   - Skills list grouped by category
   - "Add Skill" button → SkillForm dialog
   - Edit/delete actions
5. Implement SkillForm component
6. Implement SkillAssignmentDialog
   - Select primary skill (required)
   - Select secondary skill (optional)
   - Notes textarea
   - Submit to POST /skills/games/{id}/assign
7. Implement ConfigPage
   - Display current weights
   - Form to update weights
   - Validation: weights sum to 1.0
   - Submit to PUT /recommendations/config

**Acceptance Criteria:**
- Admin can create/edit/delete games
- Admin can create/edit/delete skills
- Admin can assign skills to games with audit trail
- Admin can update recommendation engine weights
- All forms validate properly
- Success/error messages display

---

### Phase 6: Polish and Testing
**Goal:** Production-ready application

**Tasks:**
1. Add loading spinners for all async operations
2. Implement error boundaries
3. Add toast notifications for all CRUD operations
4. Improve mobile responsiveness
5. Add accessibility attributes (aria-labels, roles)
6. Write unit tests for critical components
7. Write integration tests for main workflows
8. Performance optimization (code splitting, lazy loading)
9. Add 404 page
10. Final UI/UX review with CJEI team

**Acceptance Criteria:**
- All async operations show loading state
- Errors display user-friendly messages
- App works on mobile devices
- Keyboard navigation works
- 70%+ test coverage on critical paths
- No console errors in production build

---

## Testing Strategy

### Unit Tests (Vitest + React Testing Library)

**Test Components:**
```typescript
// components/recommendations/RecommendationCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { RecommendationCard } from './RecommendationCard';
import { mockGame } from '@/test-utils/mocks';

describe('RecommendationCard', () => {
  it('renders game name and rank', () => {
    render(<RecommendationCard game={mockGame} rank={1} score={85} />);
    expect(screen.getByText(mockGame.name)).toBeInTheDocument();
    expect(screen.getByText('#1')).toBeInTheDocument();
  });
  
  it('calls onSelect when clicked', () => {
    const onSelect = vi.fn();
    render(<RecommendationCard game={mockGame} rank={1} score={85} onSelect={onSelect} />);
    
    fireEvent.click(screen.getByRole('button', { name: /view details/i }));
    expect(onSelect).toHaveBeenCalledWith(mockGame);
  });
});
```

**Test Hooks:**
```typescript
// hooks/useAuth.test.ts
import { renderHook, act } from '@testing-library/react';
import { useAuth } from './useAuth';
import { AuthProvider } from '@/context/AuthContext';

describe('useAuth', () => {
  it('starts with no user', () => {
    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });
    
    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
  });
  
  it('sets user after login', async () => {
    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });
    
    await act(async () => {
      await result.current.login('test@example.com', 'password');
    });
    
    expect(result.current.user).toBeDefined();
    expect(result.current.isAuthenticated).toBe(true);
  });
});
```

**Test Utils:**
```typescript
// test-utils/mocks.ts
import { Game, User, Skill } from '@/types/models.types';

export const mockUser: User = {
  id: '123',
  email: 'test@cjei.edu.co',
  full_name: 'Test User',
  role: 'asesor',
  is_active: true,
  created_at: '2024-01-01T00:00:00Z',
};

export const mockSkill: Skill = {
  id: '456',
  name: 'Pensamiento Crítico',
  definition: 'Capacidad de analizar...',
  category: 'cognitiva',
  examples: ['Análisis', 'Evaluación'],
  contexts: 'Debates éticos',
  games_count: 5,
  created_at: '2024-01-01T00:00:00Z',
};

export const mockGame: Game = {
  id: '789',
  name: 'Catan',
  bgg_id: 13,
  duration_min: 90,
  complexity: 2.3,
  min_players: 3,
  max_players: 4,
  mechanics: ['Trading', 'Resource Management'],
  language_dependency: 'baja',
  bgg_rank: 250,
  available: true,
  image_url: 'https://example.com/catan.jpg',
  description: 'A game about...',
  primary_skill: mockSkill,
  secondary_skill: null,
  created_at: '2024-01-01T00:00:00Z',
};
```

### Integration Tests

**Test Complete Workflows:**
```typescript
// tests/integration/recommendation-flow.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import App from '@/App';
import { server } from '@/test-utils/msw-server';

describe('Recommendation Flow', () => {
  beforeAll(() => server.listen());
  afterEach(() => server.resetHandlers());
  afterAll(() => server.close());
  
  it('completes full recommendation workflow', async () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
    
    // Login
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@cjei.edu.co' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'password123' },
    });
    fireEvent.click(screen.getByRole('button', { name: /login/i }));
    
    await waitFor(() => {
      expect(screen.getByText(/create consultation/i)).toBeInTheDocument();
    });
    
    // Fill form
    fireEvent.change(screen.getByLabelText(/objectives/i), {
      target: { value: 'Foster critical thinking' },
    });
    // ... fill other fields
    
    fireEvent.click(screen.getByRole('button', { name: /generate/i }));
    
    // Wait for results
    await waitFor(() => {
      expect(screen.getByText('#1')).toBeInTheDocument();
      expect(screen.getByText(/catan/i)).toBeInTheDocument();
    });
  });
});
```

### Mock Service Worker (MSW) Setup

```typescript
// test-utils/msw-handlers.ts
import { rest } from 'msw';

const API_BASE_URL = 'http://localhost:8000/api';

export const handlers = [
  rest.post(`${API_BASE_URL}/auth/login`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        access_token: 'mock-token',
        token_type: 'bearer',
        user: mockUser,
      })
    );
  }),
  
  rest.get(`${API_BASE_URL}/games`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        items: [mockGame],
        total: 1,
        page: 1,
        page_size: 50,
        pages: 1,
      })
    );
  }),
  
  rest.post(`${API_BASE_URL}/recommendations/generate`, (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json([
        {
          game: mockGame,
          rank: 1,
          score: 85,
          explanation: {
            skill_match: 'Primary skill matches',
            operational_fit: ['3-4 players', '90 minutes'],
            relevant_mechanics: ['Trading'],
            warnings: [],
            boost_applied: null,
          },
        },
      ])
    );
  }),
];

// test-utils/msw-server.ts
import { setupServer } from 'msw/node';
import { handlers } from './msw-handlers';

export const server = setupServer(...handlers);
```

---

## Deployment

### Build for Production

```bash
# Build optimized bundle
npm run build

# Output directory: dist/
# Contains: index.html, assets/ (JS, CSS, images)
```

### Environment Configuration

```env
# .env.production
VITE_API_BASE_URL=https://api.cjei.example.com/api
VITE_APP_NAME=CJEI Recommendations
```

### Static File Hosting Options

**Option 1: Vercel**
```bash
npm install -g vercel
vercel --prod
```

**Option 2: Netlify**
```bash
npm install -g netlify-cli
netlify deploy --prod --dir=dist
```

**Option 3: Nginx**
```nginx
server {
    listen 80;
    server_name cjei-recommendations.example.com;
    
    root /var/www/cjei-frontend/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Option 4: Docker**
```dockerfile
# Dockerfile
FROM node:18-alpine AS build

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Docker Compose Integration

```yaml
# docker-compose.yml (add to backend compose file)
services:
  # ... backend and db services
  
  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    environment:
      - VITE_API_BASE_URL=http://localhost:8000/api
    depends_on:
      - backend
```

---

## Troubleshooting

### Common Issues

**Issue: CORS errors when calling API**
```
Solution:
1. Check backend CORS_ORIGINS includes frontend URL
2. Verify API_BASE_URL in .env is correct
3. Ensure backend is running
4. Check browser console for actual error
```

**Issue: 401 Unauthorized on all requests**
```
Solution:
1. Check token is stored in localStorage
2. Verify Axios interceptor is adding Authorization header
3. Check token hasn't expired (120 min default)
4. Try logging out and logging back in
```

**Issue: Build fails with TypeScript errors**
```
Solution:
1. Run `npm run type-check` to see all errors
2. Fix type mismatches
3. Ensure all imports have correct types
4. Check tsconfig.json is correct
```

**Issue: Form validation not working**
```
Solution:
1. Verify Zod schema matches form fields
2. Check resolver is correctly configured in useForm
3. Ensure error messages are displayed in UI
4. Log formState.errors to debug
```

**Issue: Recommendations not displaying**
```
Solution:
1. Check API response structure matches types
2. Verify isNoResults type guard is working
3. Check for errors in browser console
4. Test with network tab to see actual response
```

---

## Future Enhancements (Post-MVP)

### Should Priority Features
- Session templates (RF-CTX-03)
- Advanced search/filters (RF-UI-05)
- Historical query view (RF-EXP-03)
- Game detail enhancements (RF-UI-04)

### Could Priority Features
- Analytics dashboard (RF-RETRO-03)
- Report exports (RF-RETRO-04)
- User management UI (RF-ADM-03)
- Recommendation by seed game (RF-REC-05)
- Personal favorites/exclusions (RF-REC-06)

### Technical Improvements
- Migrate to TanStack Query for server state
- Add PWA support (offline capability)
- Implement code splitting and lazy loading
- Add E2E tests with Playwright
- Implement real-time updates with WebSockets
- Add internationalization (i18n)

---

**Last Updated:** January 2026  
**Project Version:** MVP 1.0  
**React Version:** 18+  
**Node Version:** 18+  
**Package Manager:** npm/yarn/pnpm