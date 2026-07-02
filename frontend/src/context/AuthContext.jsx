import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

// Create the raw React Context object that will hold our global security state
const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  // --- 1. GLOBAL GLOBAL STATES ---
  // Tracks user details (e.g., id, username) returned by the backend
  const [user, setUser] = useState(null);
  
  // App-wide loading block to prevent unauthorized flicker during session verification
  const [loading, setLoading] = useState(true);

  // --- 2. AUTOMATIC BACKGROUND SESSION VERIFICATION ---
  useEffect(() => {
    const verifySessionOnBoot = async () => {
      try {
        // Ping a secure endpoint that relies on FastAPI's 'get_current_user' dependency
        // Replace '/auth/me' if your profile endpoint uses a different route string
        const response = await api.get('/auth/me');
        setUser(response.data); // Session cookie is valid, attach user profile to state
      } catch (error) {
        setUser(null); // No cookie or session expired, force unauthenticated state
      } finally {
        setLoading(false); // Drop loading block once networking resolution finishes
      }
    };

    verifySessionOnBoot();
  }, []);

  // --- 3. AUTHENTICATION ACTIONS LAYER ---
  // Triggers your FastAPI login router and lets the browser drop the HttpOnly cookie
  const login = async (email, password) => {
    // Explicitly passes a structured object to match your UserLogin schema
    const response = await api.post('/auth/login', { 
      email: email, 
      password: password 
    });
    
    setUser({ 
      username: response.data.username || 'User',
      email: email 
    });
    return response.data;
  };

  // Triggers account registration database commits
  const register = async (username, email, password) => {
    // Explicitly passes a structured object to match your UserRegister schema
    const response = await api.post('/auth/register', { 
      username: username, 
      email: email, 
      password: password 
    });
    return response.data;
  };


  // Clears out active Valkey caching values on the server and deletes client-side cookies
  const logout = async () => {
    try {
      await api.post('/auth/logout');
    } catch (err) {
      console.error('Session clearance network error:', err);
    } finally {
      // Always wipe local application memory regardless of network execution outcomes
      setUser(null);
    }
  };

  // --- 4. DATA HOOK PROVIDER EMISSION ---
  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {/* Structural Guard: Inhibit component rendering cycles until the server verifies cookies */}
      {!loading && children}
    </AuthContext.Provider>
  );
};

// --- 5. CUSTOM HOOK EXPORT ---
// Short-hand utility hook so sub-components don't have to import 'useContext(AuthContext)' manually
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth hook must be evaluated inside an AuthProvider wrapper element.');
  }
  return context;
};
