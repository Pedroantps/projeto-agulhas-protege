import React, { lazy, Suspense, useEffect } from 'react';
import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
  useInRouterContext,
} from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';

import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { ErrorBoundary, PageSkeleton } from '@/components/common';
import { useThemeStore } from '@/stores/themeStore';

// Lazy loading para code-splitting por rota
const HomePublica = lazy(() => import('@/pages/HomePublica'));
const Login = lazy(() => import('@/pages/Login'));
const DashboardDefesaCivil = lazy(() => import('@/pages/DashboardDefesaCivil'));
const AdminConfiguracoes = lazy(() => import('@/pages/AdminConfiguracoes'));

const defaultQueryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      gcTime: 5 * 60_000,
      retry: 1,
      refetchOnWindowFocus: true,
    },
  },
});

export const AppRoutes: React.FC = () => {
  return (
    <ErrorBoundary>
      <Suspense fallback={<PageSkeleton />}>
        <Routes>
          {/* Rotas Públicas */}
          <Route path="/" element={<HomePublica />} />
          <Route path="/login" element={<Login />} />

          {/* Rotas Protegidas — Operador + Admin */}
          <Route
            element={
              <ProtectedRoute
                allowedRoles={['OPERADOR_DEFESA_CIVIL', 'ADMINISTRADOR']}
              />
            }
          >
            <Route path="/dashboard" element={<DashboardDefesaCivil />} />
          </Route>

          {/* Rotas Protegidas — Apenas Admin */}
          <Route element={<ProtectedRoute allowedRoles={['ADMINISTRADOR']} />}>
            <Route path="/admin" element={<AdminConfiguracoes />} />
          </Route>

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Suspense>
    </ErrorBoundary>
  );
};

export interface AppProps {
  withRouter?: boolean;
  queryClient?: QueryClient;
}

export const App: React.FC<AppProps> = ({
  withRouter = true,
  queryClient = defaultQueryClient,
}) => {
  const isInRouter = useInRouterContext();
  const { theme } = useThemeStore();

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
  }, [theme]);

  const content = (
    <>
      <AppRoutes />
      <Toaster
        position="top-right"
        toastOptions={{
          className: 'dark:bg-slate-800 dark:text-slate-100',
          duration: 4000,
        }}
      />
    </>
  );

  return (
    <QueryClientProvider client={queryClient}>
      {withRouter && !isInRouter ? (
        <BrowserRouter>{content}</BrowserRouter>
      ) : (
        content
      )}
    </QueryClientProvider>
  );
};

export default App;
