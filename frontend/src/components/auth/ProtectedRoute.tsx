import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuthStore, type AuthProfile } from '@/stores/authStore';

interface ProtectedRouteProps {
  allowedRoles: AuthProfile[];
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ allowedRoles }) => {
  const { isAuthenticated, user } = useAuthStore();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (user && !allowedRoles.includes(user.perfil)) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
};
