// src/App.jsx
import React, { useState, useEffect, useCallback } from 'react';

const API_BASE_URL = 'http://localhost:8000/api';

const styles = {
  container: {
    minHeight: '100vh',
    width: '100vw',
    background: 'linear-gradient(to bottom right, #0f172a, #1e293b, #0f172a)',
    color: '#e2e8f0',
    fontFamily: 'system-ui, -apple-system, sans-serif',
    display: 'flex',
    flexDirection: 'column',
  },
  header: {
    position: 'sticky',
    top: 0,
    zIndex: 40,
    borderBottom: '1px solid #475569',
    background: 'rgba(15, 23, 42, 0.8)',
    backdropFilter: 'blur(12px)',
    padding: '1rem 2rem',
  },
  headerContent: {
    maxWidth: '80rem',
    margin: '0 auto',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  logo: {
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
  },
  logoIcon: {
    width: '40px',
    height: '40px',
    background: 'linear-gradient(to bottom right, #60a5fa, #3b82f6)',
    borderRadius: '0.5rem',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '24px',
  },
  logoText: {
    fontSize: '24px',
    fontWeight: 'bold',
    color: 'white',
  },
  tagline: {
    color: '#94a3b8',
    fontSize: '14px',
  },
  main: {
     maxWidth: '1100px',
    width: '100%',
    margin: '0 auto',
    padding: '2rem 1rem',
    flex: 1,
  },
  tabNav: {
    display: 'flex',
    gap: '0.5rem',
    marginBottom: '2rem',
    borderBottom: '1px solid #475569',
    paddingBottom: '0.5rem',
  },
  tab: {
    padding: '0.75rem 1.5rem',
    fontWeight: 500,
    border: 'none',
    background: 'none',
    color: '#94a3b8',
    cursor: 'pointer',
    transition: 'all 0.3s',
    borderBottom: '2px solid transparent',
    fontSize: '14px',
  },
  tabActive: {
    color: '#60a5fa',
    borderBottomColor: '#3b82f6',
  },
  errorAlert: {
    marginBottom: '1.5rem',
    padding: '1rem',
    background: 'rgba(127, 29, 29, 0.2)',
    border: '1px solid #b91c1c',
    borderRadius: '0.5rem',
    display: 'flex',
    gap: '0.75rem',
  },
  errorIcon: {
    fontSize: '20px',
    flexShrink: 0,
  },
  errorText: {
    flex: 1,
  },
  errorTitle: {
    color: '#f87171',
    fontWeight: 600,
  },
  errorDesc: {
    color: '#fca5a5',
    fontSize: '14px',
    marginTop: '0.25rem',
  },
  closeBtn: {
    background: 'none',
    border: 'none',
    color: '#f87171',
    cursor: 'pointer',
    fontSize: '18px',
  },
  grid2Col: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
    gap: '2rem',
    marginBottom: '3rem',
  },
  formSection: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1.5rem',
  },
  title: {
    fontSize: '32px',
    fontWeight: 'bold',
    color: 'white',
    marginBottom: '0.5rem',
  },
  subtitle: {
    color: '#94a3b8',
  },
  formGroup: {
    display: 'flex',
    flexDirection: 'column',
  },
  label: {
    fontSize: '14px',
    fontWeight: 600,
    color: '#cbd5e1',
    marginBottom: '0.5rem',
  },
  input: {
    width: '100%',
    padding: '0.75rem 1rem',
    background: '#1e293b',
    border: '1px solid #475569',
    borderRadius: '0.5rem',
    color: 'white',
    fontSize: '14px',
    transition: 'all 0.3s',
    boxSizing: 'border-box',
  },
  inputFocus: {
    borderColor: '#3b82f6',
    boxShadow: '0 0 0 1px #3b82f6',
  },
  helpText: {
    fontSize: '12px',
    color: '#64748b',
    marginTop: '0.5rem',
  },
  button: {
    padding: '0.75rem 1rem',
    background: 'linear-gradient(to right, #3b82f6, #2563eb)',
    color: 'white',
    border: 'none',
    borderRadius: '0.5rem',
    fontWeight: 600,
    cursor: 'pointer',
    transition: 'all 0.3s',
    fontSize: '14px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '0.5rem',
  },
  buttonHover: {
    background: 'linear-gradient(to right, #2563eb, #1d4ed8)',
  },
  buttonDisabled: {
    opacity: 0.5,
    cursor: 'not-allowed',
  },
  cardGrid: {
    display: 'grid',
    gap: '1rem',
  },
  card: {
    background: '#1e293b',
    border: '1px solid #334155',
    borderRadius: '0.5rem',
    padding: '1.5rem',
    display: 'flex',
    flexDirection: 'column',
    gap: '0.5rem',
  },
  cardHeader: {
    display: 'flex',
    gap: '0.75rem',
    alignItems: 'flex-start',
  },
  cardIcon: {
    width: '40px',
    height: '40px',
    borderRadius: '0.5rem',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '20px',
    flexShrink: 0,
  },
  cardContent: {
    flex: 1,
  },
  cardLabel: {
    color: '#94a3b8',
    fontSize: '12px',
  },
  cardTitle: {
    color: 'white',
    fontWeight: 600,
    fontSize: '14px',
  },
  cardDesc: {
    color: '#94a3b8',
    fontSize: '13px',
    marginTop: '0.5rem',
  },
  progressSection: {
    background: '#1e293b',
    border: '1px solid #334155',
    borderRadius: '0.5rem',
    padding: '2rem',
    maxWidth: '40rem',
    margin: '0 auto',
    display: 'flex',
    flexDirection: 'column',
    gap: '2rem',
  },
  progressHeader: {
    textAlign: 'center',
  },
  progressIcon: {
    width: '64px',
    height: '64px',
    background: 'rgba(59, 130, 246, 0.2)',
    borderRadius: '9999px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '32px',
    margin: '0 auto 1rem',
    animation: 'spin 1s linear infinite',
  },
  progressBar: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.5rem',
  },
  progressLabel: {
    display: 'flex',
    justifyContent: 'space-between',
  },
  progressLabelText: {
    color: 'white',
    fontWeight: 600,
  },
  progressPercent: {
    color: '#60a5fa',
    fontWeight: 600,
  },
  progressBarBg: {
    width: '100%',
    height: '12px',
    background: '#334155',
    borderRadius: '9999px',
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
    background: 'linear-gradient(to right, #3b82f6, #2563eb)',
    transition: 'width 0.5s ease-out',
  },
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: '1rem',
  },
  statCard: {
    background: 'rgba(51, 65, 85, 0.5)',
    borderRadius: '0.5rem',
    padding: '1rem',
    textAlign: 'center',
  },
  statLabel: {
    color: '#94a3b8',
    fontSize: '12px',
    marginBottom: '0.5rem',
  },
  statValue: {
    fontSize: '24px',
    fontWeight: 'bold',
    color: 'white',
  },
  successAlert: {
    background: 'rgba(16, 185, 129, 0.2)',
    border: '1px solid #059669',
    borderRadius: '0.5rem',
    padding: '1rem',
    display: 'flex',
    gap: '0.75rem',
  },
  gallerySection: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1.5rem',
  },
  galleryHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: '1rem',
  },
  imageGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))',
    gap: '1rem',
  },
  imageCard: {
    background: '#1e293b',
    border: '1px solid #334155',
    borderRadius: '0.5rem',
    overflow: 'hidden',
    transition: 'all 0.3s',
    cursor: 'pointer',
  },
  imageCardHover: {
    borderColor: '#3b82f6',
    boxShadow: '0 0 16px rgba(59, 130, 246, 0.2)',
  },
  imageContainer: {
    width: '100%',
    aspectRatio: '1',
    background: 'linear-gradient(to bottom right, #334155, #0f172a)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden',
  },
  image: {
    width: '100%',
    height: '100%',
    objectFit: 'cover',
    transition: 'transform 0.3s',
  },
  pagination: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    gap: '1rem',
    marginTop: '2rem',
  },
  paginationBtn: {
    padding: '0.5rem 1rem',
    background: '#1e293b',
    border: '1px solid #475569',
    color: 'white',
    borderRadius: '0.5rem',
    cursor: 'pointer',
    transition: 'all 0.3s',
    fontSize: '14px',
  },
  emptyState: {
    textAlign: 'center',
    padding: '4rem 2rem',
  },
  emptyIcon: {
    fontSize: '48px',
    marginBottom: '1rem',
    opacity: 0.5,
  },
  footer: {
    borderTop: '1px solid #475569',
    background: 'rgba(15, 23, 42, 0.5)',
    marginTop: '4rem',
    padding: '2rem',
    textAlign: 'center',
    color: '#94a3b8',
    fontSize: '14px',
  },
};

// Create CSS animation for spinning
const styleSheet = document.createElement('style');
styleSheet.textContent = `
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
  input:focus { outline: none; }
  button:hover:not(:disabled) { opacity: 0.9; }
`;
document.head.appendChild(styleSheet);

export default function ImageImportApp() {
  const [activeTab, setActiveTab] = useState('import');
  const [importUrl, setImportUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [jobId, setJobId] = useState(null);
  const [jobStatus, setJobStatus] = useState(null);
  const [error, setError] = useState(null);
  const [images, setImages] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [imageCount, setImageCount] = useState(0);
  const [polling, setPolling] = useState(false);
  const IMAGES_PER_PAGE = 20;

  const isValidGoogleDriveUrl = (url) => {
    return /drive\.google\.com\/drive\/folders\/[a-zA-Z0-9-_]+/.test(url) || 
           /drive\.google\.com\/drive\/u\/\d+\/folders\/[a-zA-Z0-9-_]+/.test(url);
  };

  const handleImport = useCallback(async (e) => {
    e.preventDefault();
    setError(null);

    if (!importUrl.trim()) {
      setError('Please enter a Google Drive folder URL');
      return;
    }

    if (!isValidGoogleDriveUrl(importUrl)) {
      setError('Invalid Google Drive URL. Please enter a valid public folder link.');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/import/google-drive`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ folder_url: importUrl }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setJobId(data.job_id);
      setImportUrl('');
      setActiveTab('progress');
      setPolling(true);
    } catch (err) {
      setError(err.message || 'Failed to start import. Please check the URL and try again.');
    } finally {
      setLoading(false);
    }
  }, [importUrl]);

  useEffect(() => {
    if (!jobId || !polling) return;

    const pollStatus = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/import-status/${jobId}`);
        if (!response.ok) throw new Error('Failed to fetch status');
        
        const status = await response.json();
        setJobStatus(status);

        if (status.status === 'COMPLETED' || status.status === 'FAILED') {
          setPolling(false);
          if (status.status === 'COMPLETED') {
            setTimeout(() => setActiveTab('gallery'), 1000);
          }
        }
      } catch (err) {
        console.error('Polling error:', err);
      }
    };

    const interval = setInterval(pollStatus, 2000);
    return () => clearInterval(interval);
  }, [jobId, polling]);

  const fetchImages = useCallback(async (page = 1) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/images?page=${page}&size=${IMAGES_PER_PAGE}`
      );
      if (!response.ok) throw new Error('Failed to fetch images');
      
      const data = await response.json();
      setImages(data.items || []);
      setCurrentPage(data.page || 1);
      setTotalPages(data.total_pages || 1);
      setImageCount(data.total_count || 0);
    } catch (err) {
      setError('Failed to load images: ' + err.message);
    }
  }, []);

  useEffect(() => {
    if (activeTab === 'gallery') {
      fetchImages(1);
    }
  }, [activeTab, fetchImages]);

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setCurrentPage(newPage);
      fetchImages(newPage);
    }
  };

  const ProgressBar = ({ current, total }) => {
    const completed = processed + failed;
    const percentage = total > 0 ? (current / total) * 100 : 0;
    return (
      <div style={styles.progressBar}>
        <div style={styles.progressLabel}>
          <span style={styles.progressLabelText}>Progress</span>
          <span style={styles.progressPercent}>{Math.round(percentage)}%</span>
        </div>
        <div style={styles.progressBarBg}>
          <div style={{...styles.progressBarFill, width: `${percentage}%`}} />
        </div>
      </div>
    );
  };

  return (
    <div style={styles.container}>
      {/* Header */}
      <header style={styles.header}>
        <div style={styles.headerContent}>
          <div style={styles.logo}>
            <div style={styles.logoIcon}>📤</div>
            <h1 style={styles.logoText}>ImageSync</h1>
          </div>
          <p style={styles.tagline}>Import images from Google Drive & Dropbox</p>
        </div>
      </header>

      <main style={styles.main}>
        {/* Tabs */}
        <div style={styles.tabNav}>
          <button
            onClick={() => setActiveTab('import')}
            style={{...styles.tab, ...(activeTab === 'import' ? styles.tabActive : {})}}
          >
            📥 Import
          </button>
          {jobId && (
            <button
              onClick={() => setActiveTab('progress')}
              style={{...styles.tab, ...(activeTab === 'progress' ? styles.tabActive : {})}}
            >
              ⏳ Progress
            </button>
          )}
          <button
            onClick={() => setActiveTab('gallery')}
            style={{...styles.tab, ...(activeTab === 'gallery' ? styles.tabActive : {})}}
          >
            🖼️ Gallery ({imageCount})
          </button>
        </div>

        {/* Error Alert */}
        {error && (
          <div style={styles.errorAlert}>
            <div style={styles.errorIcon}>⚠️</div>
            <div style={styles.errorText}>
              <div style={styles.errorTitle}>Error</div>
              <div style={styles.errorDesc}>{error}</div>
            </div>
            <button style={styles.closeBtn} onClick={() => setError(null)}>✕</button>
          </div>
        )}

        {/* Import Tab */}
        {activeTab === 'import' && (
          <div style={styles.grid2Col}>
            <div style={styles.formSection}>
              <div>
                <h2 style={styles.title}>Import Images</h2>
                <p style={styles.subtitle}>Add a public Google Drive or Dropbox folder to get started</p>
              </div>

              <div style={styles.formGroup}>
                <label style={styles.label}>Google Drive Folder URL</label>
                <input
                  type="text"
                  placeholder="https://drive.google.com/drive/folders/1A2B3C4D5E6F7G8H9I0J..."
                  value={importUrl}
                  onChange={(e) => setImportUrl(e.target.value)}
                  disabled={loading}
                  style={styles.input}
                />
                <p style={styles.helpText}>Must be a public folder with images. Copy the sharing link from Google Drive.</p>
              </div>

              <button
                onClick={handleImport}
                disabled={loading || polling || !importUrl.trim()}
                style={{
                  ...styles.button,
                  ...(loading || polling ? styles.buttonDisabled : {})
                }}
              >
                {loading || polling ? '⏳ Importing...' : '📤 Start Import'}
              </button>

              <div style={styles.card}>
                <h3 style={{...styles.cardTitle, marginBottom: '0.5rem'}}>How to Get Your Link:</h3>
                <ol style={{paddingLeft: '1.5rem', color: '#cbd5e1', fontSize: '13px'}}>
                  <li>Open Google Drive folder in browser</li>
                  <li>Right-click folder → Share</li>
                  <li>Set to "Viewer" → Copy link</li>
                  <li>Paste link above and click Import</li>
                </ol>
              </div>
            </div>

            {/* Info Cards */}
            <div style={styles.cardGrid}>
              <div style={{...styles.card, background: 'rgba(59, 130, 246, 0.1)', border: '1px solid rgba(59, 130, 246, 0.3)'}}>
                <div style={styles.cardHeader}>
                  <div style={{...styles.cardIcon, background: 'rgba(59, 130, 246, 0.2)'}}>⚙️</div>
                  <div style={styles.cardContent}>
                    <div style={styles.cardLabel}>Processing</div>
                    <div style={styles.cardTitle}>Async Job Queue</div>
                  </div>
                </div>
                <p style={styles.cardDesc}>Imports happen in the background. You can close this window.</p>
              </div>

              <div style={{...styles.card, background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)'}}>
                <div style={styles.cardHeader}>
                  <div style={{...styles.cardIcon, background: 'rgba(16, 185, 129, 0.2)'}}>✅</div>
                  <div style={styles.cardContent}>
                    <div style={styles.cardLabel}>Storage</div>
                    <div style={styles.cardTitle}>Cloud Storage (S3)</div>
                  </div>
                </div>
                <p style={styles.cardDesc}>Images stored securely in AWS S3 with CDN acceleration.</p>
              </div>

              <div style={{...styles.card, background: 'rgba(168, 85, 247, 0.1)', border: '1px solid rgba(168, 85, 247, 0.3)'}}>
                <div style={styles.cardHeader}>
                  <div style={{...styles.cardIcon, background: 'rgba(168, 85, 247, 0.2)'}}>📊</div>
                  <div style={styles.cardContent}>
                    <div style={styles.cardLabel}>Scalability</div>
                    <div style={styles.cardTitle}>Handles 10,000+ images</div>
                  </div>
                </div>
                <p style={styles.cardDesc}>Parallel workers process multiple images simultaneously.</p>
              </div>

              <div style={{...styles.card, background: 'rgba(249, 115, 22, 0.1)', border: '1px solid rgba(249, 115, 22, 0.3)'}}>
                <div style={styles.cardHeader}>
                  <div style={{...styles.cardIcon, background: 'rgba(249, 115, 22, 0.2)'}}>🔄</div>
                  <div style={styles.cardContent}>
                    <div style={styles.cardLabel}>Reliability</div>
                    <div style={styles.cardTitle}>Automatic Retries</div>
                  </div>
                </div>
                <p style={styles.cardDesc}>Failed imports automatically retry with exponential backoff.</p>
              </div>
            </div>
          </div>
        )}

        {/* Progress Tab */}
        {activeTab === 'progress' && jobStatus && (
          <div style={styles.progressSection}>
            <div style={styles.progressHeader}>
              <div style={styles.progressIcon}>⏳</div>
              <h2 style={styles.title}>Import in Progress</h2>
              <p style={styles.subtitle}>Your images are being processed</p>
            </div>

            <ProgressBar
              processed={jobStatus.processed_images || 0}
              failed={jobStatus.failed_images || 0}
              total={jobStatus.total_images || 1}
            />


            <div style={styles.statsGrid}>
              <div style={styles.statCard}>
                <div style={styles.statLabel}>Total</div>
                <div style={styles.statValue}>{jobStatus.total_images || 0}</div>
              </div>
              <div style={styles.statCard}>
                <div style={styles.statLabel}>Processed</div>
                <div style={{...styles.statValue, color: '#10b981'}}>{jobStatus.processed_images || 0}</div>
              </div>
              <div style={styles.statCard}>
                <div style={styles.statLabel}>Failed</div>
                <div style={{...styles.statValue, color: '#ef4444'}}>{jobStatus.failed_images || 0}</div>
              </div>
            </div>

            {jobStatus.status === 'COMPLETED' && (
              <div style={styles.successAlert}>
                <div style={{fontSize: '20px'}}>✅</div>
                <div>
                  <div style={{color: '#10b981', fontWeight: 600}}>Import Complete!</div>
                  <div style={{color: '#86efac', fontSize: '13px', marginTop: '0.25rem'}}>All images have been successfully imported.</div>
                </div>
              </div>
            )}

            {jobStatus.status === 'FAILED' && (
              <div style={styles.errorAlert}>
                <div style={styles.errorIcon}>❌</div>
                <div>
                  <div style={styles.errorTitle}>Import Failed</div>
                  <div style={styles.errorDesc}>{jobStatus.error_message || 'Unknown error'}</div>
                </div>
              </div>
            )}

            <button
              onClick={() => {
                fetchImages(1);
                setActiveTab('gallery');
              }}
              style={styles.button}
            >
              🖼️ View Gallery
            </button>
          </div>
        )}

        {/* Gallery Tab */}
        {activeTab === 'gallery' && (
          <div style={styles.gallerySection}>
            <div style={styles.galleryHeader}>
              <div>
                <h2 style={styles.title}>Image Gallery</h2>
                <p style={styles.subtitle}>{imageCount} images total</p>
              </div>
            </div>

            {images.length > 0 ? (
              <>
                <div style={styles.imageGrid}>
                  {images.map((image) => (
                    <div
                      key={image.id}
                      style={styles.imageCard}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.borderColor = '#3b82f6';
                        e.currentTarget.style.boxShadow = '0 0 16px rgba(59, 130, 246, 0.2)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.borderColor = '#334155';
                        e.currentTarget.style.boxShadow = 'none';
                      }}
                    >
                      <div style={styles.imageContainer}>
                        <img
                          src={image.storage_path}
                          alt={image.name}
                          style={styles.image}
                          onError={(e) => {
                            e.target.style.display = 'none';
                            e.target.parentElement.textContent = 'No Image';
                          }}
                        />
                      </div>
                    </div>
                  ))}
                </div>

                <div style={styles.pagination}>
                  <button
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                    style={{...styles.paginationBtn, opacity: currentPage === 1 ? 0.5 : 1}}
                  >
                    ← Previous
                  </button>
                  <span style={{color: '#94a3b8'}}>Page {currentPage} of {totalPages}</span>
                  <button
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={currentPage === totalPages}
                    style={{...styles.paginationBtn, opacity: currentPage === totalPages ? 0.5 : 1}}
                  >
                    Next →
                  </button>
                </div>
              </>
            ) : (
              <div style={styles.emptyState}>
                <div style={styles.emptyIcon}>🖼️</div>
                <p style={{color: '#94a3b8'}}>No images imported yet. Start by importing from Google Drive!</p>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer style={styles.footer}>
        Built with React, FastAPI & PostgreSQL. Scalable image import system.
      </footer>
    </div>
  );
}