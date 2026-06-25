import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { UserPlus, User, Mail, Lock } from 'lucide-react';

const Register = () => {
  // --- 1. STATE MANAGEMENT ---
  // Captures fields that map directly to your UserRegister Pydantic schema
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  
  // Local verification field (processed completely on the client side)
  const [confirmPassword, setConfirmPassword] = useState('');
  
  // Error state for handling both client mismatch and 400 Bad Request responses
  const [error, setError] = useState('');
  
  // Triggers a success banner and delays route transitions for better UX
  const [success, setSuccess] = useState(false);
  
  // UI flag to prevent rapid double-clicks on the submission pipeline
  const [isSubmitting, setIsSubmitting] = useState(false);

  // --- 2. HOOKS & UTILITIES ---
  // Calls the registration handler mapped inside AuthContext
  const { register } = useAuth();
  
  // Hook used to programmatically flip the user over to /login after signup
  const navigate = useNavigate();

  // --- 3. FORM SUBMISSION & ACCOUNT CREATION HANDLER ---
  const handleSubmit = async (e) => {
    e.preventDefault(); // Inhibits natural browser document refreshes
    setError('');       // Resets any errors surfaced during earlier attempts

    // Performance Optimization: Client-side validation prevents unnecessary server roundtrips
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setIsSubmitting(true); // Engages button locks & loading indicators

    try {
      // Dispatches structured registration fields to backend database pipeline
      await register(username, email, password);
      
      // Updates view to reflect user creation status
      setSuccess(true);
      
      // Holds view for 2 seconds so user can read message before redirecting
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (err) {
      // Isolates unique username/email collision exceptions thrown by FastAPI router
      const backendMessage = err.response?.data?.detail;
      setError(backendMessage || 'Registration failed. Please try again.');
      setIsSubmitting(false); // Only re-enables button if submission explicitly fails
    }
  };

  // --- 4. UI LAYOUT ---
  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Create Account</h2>
        <p className="auth-subtitle">Start organizing your career search</p>

        {/* Conditional Messaging Alerts */}
        {error && <div className="auth-error-banner">{error}</div>}
        {success && (
          <div className="auth-success-banner">
            Account created successfully! Redirecting...
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          
          {/* Username Field Block */}
          <div className="input-group">
            <label htmlFor="username">Username</label>
            <div className="input-with-icon">
              <User className="input-icon" size={18} />
              <input
                id="username"
                type="text"
                required
                disabled={success}
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="johndoe"
              />
            </div>
          </div>

          {/* Email Address Field Block */}
          <div className="input-group">
            <label htmlFor="email">Email Address</label>
            <div className="input-with-icon">
              <Mail className="input-icon" size={18} />
              <input
                id="email"
                type="email"
                required
                disabled={success}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
              />
            </div>
          </div>

          {/* Password Creation Box */}
          <div className="input-group">
            <label htmlFor="password">Password</label>
            <div className="input-with-icon">
              <Lock className="input-icon" size={18} />
              <input
                id="password"
                type="password"
                required
                disabled={success}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
              />
            </div>
          </div>

          {/* Local Password Confirmation Box */}
          <div className="input-group">
            <label htmlFor="confirmPassword">Confirm Password</label>
            <div className="input-with-icon">
              <Lock className="input-icon" size={18} />
              <input
                id="confirmPassword"
                type="password"
                required
                disabled={success}
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••"
              />
            </div>
          </div>

          {/* Submission Control (Locks state upon success or network activity) */}
          <button type="submit" disabled={isSubmitting || success} className="auth-button">
            {isSubmitting ? 'Creating account...' : (
              <>
                <UserPlus size={18} />
                <span>Sign Up</span>
              </>
            )}
          </button>
        </form>

        {/* Back Link routing to Login page layout */}
        <p className="auth-footer">
          Already have an account? <Link to="/login">Log in here</Link>
        </p>
      </div>
    </div>
  );
};

export default Register;
