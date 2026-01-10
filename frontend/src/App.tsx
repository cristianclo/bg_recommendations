import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Layout
import { MainLayout } from './components/layout/MainLayout';

// Pages
import HomePage from './pages/HomePage';
import SessionCreatePage from './pages/SessionCreatePage';
import GameCatalogPage from './pages/GameCatalogPage';
import RecommendationsPage from './pages/RecommendationsPage';
import SkillsPage from './pages/SkillsPage';
import FeedbackPage from './pages/FeedbackPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          <Route element={<MainLayout />}>
            <Route path="/" element={<HomePage />} />
            <Route path="/sessions/new" element={<SessionCreatePage />} />
            <Route path="/games" element={<GameCatalogPage />} />
            <Route path="/recommendations/:sessionId" element={<RecommendationsPage />} />
            <Route path="/skills" element={<SkillsPage />} />
            <Route path="/feedback/:recommendationId" element={<FeedbackPage />} />
          </Route>
        </Routes>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
