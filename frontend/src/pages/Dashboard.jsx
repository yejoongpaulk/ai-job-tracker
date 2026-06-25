import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import { 
  Briefcase, 
  Building2, 
  Plus, 
  Trash2, 
  LogOut, 
  FileText, 
  CheckCircle2, 
  Clock, 
  XCircle, 
  AlertCircle 
} from 'lucide-react';

const Dashboard = () => {
  // --- 1. STATE MANAGEMENT ---
  const { user, logout } = useAuth();
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Form states for creating a new job entry
  const [title, setTitle] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [status, setStatus] = useState('Wishlist'); // This matches your Enum entry string
  const [rawJobPosting, setRawJobPosting] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // --- 2. API INTERACTION HANDLERS ---

  // Fetch all tracking rows belonging strictly to the user (GET /jobs/)
  const fetchJobs = async () => {
    try {
      setLoading(true);
      const response = await api.get('/jobs/');
      setJobs(response.data);
    } catch (err) {
      setError('Failed to fetch job tracking rows.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  // Creates a new tracking entry (POST /jobs/)
  const handleCreateJob = async (e) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      const response = await api.post('/jobs/', {
        title,
        company_name: companyName, // Maps to snake_case schema property
        status,
        raw_job_posting: rawJobPosting || null
      });

      // Optimistically append the newly returned row object into state
      setJobs([response.data, ...jobs]);
      
      // Reset input fields upon success
      setTitle('');
      setCompanyName('');
      setStatus('Applied');
      setRawJobPosting('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to append tracking entry.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Quick edit directly inside grid cells (PATCH /jobs/{id}/status)
  const handleStatusUpdate = async (jobId, newStatus) => {
    try {
      const response = await api.patch(`/jobs/${jobId}/status`, {
        status: newStatus
      });

      // Map across rows to swap status context inline
      setJobs(jobs.map(job => job.id === jobId ? response.data : job));
    } catch (err) {
      alert('Failed to update status validation requirements.');
    }
  };

  // Removes a tracker row completely (DELETE /jobs/{id})
  const handleDeleteJob = async (jobId) => {
    if (!window.confirm('Are you sure you want to delete this job application track?')) return;

    try {
      await api.delete(`/jobs/${jobId}`);
      // Filter out deleted row object from reactive array state
      setJobs(jobs.filter(job => job.id !== jobId));
    } catch (err) {
      alert('Unauthorized removal attempt or missing server link.');
    }
  };

  // Helper utility to style background states dynamically based on status values
  const getStatusBadgeClass = (currentStatus) => {
  switch (currentStatus) {
    case 'Offer': return 'badge-success';         // Matches backend "Offer"
    case 'Interviewing': return 'badge-warning';
    case 'Rejected': return 'badge-danger';
    case 'Ghosted': return 'badge-danger';         // Styled like rejected
    case 'Wishlist': return 'badge-neutral';
    default: return 'badge-neutral';
  }
};


  // --- 3. UI LAYOUT RENDERING ---
  return (
    <div className="dashboard-layout">
      {/* Top Application Header Profile Bar */}
      <header className="dashboard-header">
        <div className="header-left">
          <Briefcase className="header-icon" size={24} />
          <h1>AI Job Tracker</h1>
        </div>
        <div className="header-right">
          <span className="user-greeting">Welcome, <strong>{user?.username || 'User'}</strong></span>
          <button onClick={logout} className="logout-button" title="Sign Out">
            <LogOut size={18} />
            <span>Logout</span>
          </button>
        </div>
      </header>

      {/* Main Workspace Frame split into Tracker List and Side Panel Form */}
      <main className="dashboard-content">
        
        {/* Left Side Window: Main Tracking Table / Grid Interface */}
        <section className="tracker-panel">
          <h2>Application Pipeline Grid</h2>
          {error && <div className="error-alert">{error}</div>}

          {loading ? (
            <div className="loading-spinner">Querying session records...</div>
          ) : jobs.length === 0 ? (
            <div className="empty-state">
              <AlertCircle size={40} />
              <p>No jobs added yet. Use the side window panel to log your first listing application.</p>
            </div>
          ) : (
            <div className="jobs-list-grid">
              {jobs.map((job) => (
                <div key={job.id} className="job-row-card">
                  <div className="card-main-info">
                    <div className="title-block">
                      <h3>{job.title}</h3>
                      <div className="company-meta">
                        <Building2 size={14} />
                        <span>{job.company_name}</span>
                      </div>
                    </div>

                    {/* Status Mutation Cell Picker Selector */}
                    <div className="status-mutation-cell">
                      <span className={`status-badge ${getStatusBadgeClass(job.status)}`}>
                        {job.status}
                      </span>
                      <select 
                        value={job.status}
                        onChange={(e) => handleStatusUpdate(job.id, e.target.value)}
                        className="status-dropdown-select"
                      >
                        <option value="Wishlist">Wishlist</option>
                        <option value="Applied">Applied</option>
                        <option value="Interviewing">Interviewing</option>
                        <option value="Offer">Offer</option>
                        <option value="Rejected">Rejected</option>
                        <option value="Ghosted">Ghosted</option>
                      </select>
                    </div>
                  </div>

                  {/* Footer Context Info Meta Tags */}
                  <div className="card-footer-actions">
                    <div className="ai-status-indicator">
                      {job.raw_job_posting ? (
                        <span className="ai-metadata-tag active" title="Raw source text stored for parsing analytics">
                          <FileText size={12} /> AI Text Loaded
                        </span>
                      ) : (
                        <span className="ai-metadata-tag empty">Manual Record</span>
                      )}
                    </div>
                    <button 
                      onClick={() => handleDeleteJob(job.id)} 
                      className="delete-row-action"
                      title="Purge row entry"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Right Side Window: Sticky Submission Utility Form Panel */}
        <aside className="creation-panel-drawer">
          <div className="sticky-form-container">
            <div className="form-title-header">
              <Plus size={20} />
              <h2>Log Application Listing</h2>
            </div>
            
            <form onSubmit={handleCreateJob} className="creation-form">
              <div className="form-group-field">
                <label htmlFor="job-title">Role / Position Title *</label>
                <input
                  id="job-title"
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g., Software Engineer"
                />
              </div>

              <div className="form-group-field">
                <label htmlFor="company-name">Company Name *</label>
                <input
                  id="company-name"
                  type="text"
                  required
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  placeholder="e.g., OpenAI"
                />
              </div>

              <div className="form-group-field">
                <label htmlFor="initial-status">Pipeline Status Phase</label>
                <select
                  id="initial-status"
                  value={status}
                  onChange={(e) => setStatus(e.target.value)}
                >
                  <option value="Applied">Applied</option>
                  <option value="Interviewing">Interviewing</option>
                  <option value="Offered">Offered</option>
                  <option value="Rejected">Rejected</option>
                </select>
              </div>

              <div className="form-group-field">
                <label htmlFor="raw-posting">Raw Description / Clipboard Drop</label>
                <textarea
                  id="raw-posting"
                  rows={6}
                  value={rawJobPosting}
                  onChange={(e) => setRawJobPosting(e.target.value)}
                  placeholder="Paste the raw markdown, LinkedIn description, or copy text string block here. AI parsers process this data segment."
                />
              </div>

              <button type="submit" disabled={isSubmitting} className="form-submit-cta">
                {isSubmitting ? 'Writing Entry...' : 'Commit Row Tracker'}
              </button>
            </form>
          </div>
        </aside>

      </main>
    </div>
  );
};

export default Dashboard;
