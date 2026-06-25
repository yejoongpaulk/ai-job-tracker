import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogIn, Mail, Lock } from 'lucide-react';

const Login = () => {
  // --- 1. STATE MANAGEMENT ---
  // Tracks user input fields directly from the form
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  
  // Captures and handles backend errors (e.g., 401 Unauthorized)
  const [error, setError] = useState('');
  
  // UI lock to disable the login button and prevent double submissions
  const [isSubmitting, setIsSubmitting] = useState(false);

  // --- 2. HOOKS & UTILITIES ---
  // Pulls the global login action from our Valkey cookie-based AuthContext
  const { login } = useAuth();
  
  // React Router hook to programmatically route users post-login
  const navigate = useNavigate();

  // --- 3. FORM SUBMISSION HANDLER ---
  const handleSubmit = async (e) => {
    e.preventDefault(); // Prevents standard browser page reload
    setError('');       // Clears out any lingering previous errors
    setIsSubmitting(true); // Disables button & triggers loading state

    try {
      // Fires the Axios call. Cookie payload is dropped into browser automatically.
      await login(email, password);
      
      // Navigate to dashboard. 'replace: true' wipes /login from browser history.
      navigate('/dashboard', { replace: true });
    } catch (err) {
      // Pulls out custom validation messages returned by FastAPI's HTTPException
      const backendMessage = err.response?.data?.detail;
      setError(backendMessage || 'Invalid email or password. Please try again.');
    } finally {
      setIsSubmitting(false); // Re-enables the submission button
    }
  };

  // --- 4. UI LAYOUT ---
  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Welcome Back</h2>
        <p className="auth-subtitle">Sign in to track your applications</p>

        {/* Dynamic Alert Banner: Only renders if an API error state exists */}
        {error && <div className="auth-error-banner">{error}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          
          {/* Email Input Field Box */}
          <div className="input-group">
            <label htmlFor="email">Email Address</label>
            <div className="input-with-icon">
              <Mail className="input-icon" size={18} />
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
              />
            </div>
          </div>

          {/* Password Input Field Box */}
          <div className="input-group">
            <label htmlFor="password">Password</label>
            <div className="input-with-icon">
              <Lock className="input-icon" size={18} />
              <input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
              />
            </div>
          </div>

          {/* Form Submit Button (Changes text & locks when networking is active) */}
          <button type="submit" disabled={isSubmitting} className="auth-button">
            {isSubmitting ? 'Signing in...' : (
              <>
                <LogIn size={18} />
                <span>Sign In</span>
              </>
            )}
          </button>
        </form>

        {/* Link navigation to jump over to registration without page reloads */}
        <p className="auth-footer">
          Don't have an account? <Link to="/register">Sign up here</Link>
        </p>
      </div>
    </div>
  );
};

export default Login;
