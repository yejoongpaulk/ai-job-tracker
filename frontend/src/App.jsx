import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';

// Import our custom pages
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';

// Import core stylesheet layouts
import './index.css';

/**
 * Main Application Shell Component
 * Initializes the global authentication engine and defines the secure routing architecture.
 */
function App() {
  return (
    // 1. BrowserRouter: Supplies standard web browser URL management mechanics to the app
    <BrowserRouter>
      {/* 2. AuthProvider: Injects the shared Valkey/Cookie state context across all view layers */}
      <AuthProvider>
        <Routes>
          
          {/* ==========================================
             A. PUBLIC LAYOUT ROUTES 
             ========================================== */}
          {/* Unauthenticated gateway views accessible by everyone */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* ==========================================
             B. SECURE / APPLICATION FIREWALL VIEWS
             ========================================== */}
          {/* ProtectedRoute intercepts requests to any path nested inside this route definition */}
          <Route element={<ProtectedRoute />}>
            {/* Renders inside ProtectedRoute's <Outlet /> loop on successful authentication */}
            <Route path="/dashboard" element={<Dashboard />} />
          </Route>

          {/* ==========================================
             C. CATCH-ALL ACCELERATOR ROUTING
             ========================================== */}
          {/* Fallback route: If an invalid or random path is targeted, bounce them automatically. */}
          {/* If the user is logged in, Dashboard opens; if not, ProtectedRoute will catch and bounce them to /login */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />

        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
