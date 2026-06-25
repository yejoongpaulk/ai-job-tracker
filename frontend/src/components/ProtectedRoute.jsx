import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

/**
 * ProtectedRoute Component
 * Serves as a security firewall for your private application views.
 * Intercepts routing changes to verify the global user state before rendering children.
 */
const ProtectedRoute = () => {
  // Pulls the real-time active user session state from our global AuthContext
  const { user } = useAuth();

  // Condition check: If no user session data exists, lock entry out completely
  if (!user) {
    // Bounce the client directly back to the sign-in screen.
    // 'replace' wipes the current private page from history to prevent infinite back-button loops.
    return <Navigate to="/login" replace />;
  }

  // Success state: Render the active route's components (nested sub-routes) 
  // by projecting them out through the React Router Outlet pipeline.
  return <Outlet />;
};

export default ProtectedRoute;
