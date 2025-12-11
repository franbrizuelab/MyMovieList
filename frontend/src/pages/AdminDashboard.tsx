import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import api from '../api';
import { Search, Plus, Save, X } from 'lucide-react';
import './AdminDashboard.css';

interface AdminMovie {
  movieId: number;
  title: string;
  tagline?: string;
  overview: string;
  releaseDate: string;
  runtime?: number;
  budget: number;
  language: string;
  coverUrl: string;
  voteAverage?: number;
  voteCount?: number;
}

const AdminDashboard = () => {
  const { user, isLoggedIn, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [movies, setMovies] = useState<AdminMovie[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [pageInput, setPageInput] = useState('1');
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editForm, setEditForm] = useState<Partial<AdminMovie>>({});
  
  // New movie form state
  const [newMovie, setNewMovie] = useState({
    title: '',
    tagline: '',
    overview: '',
    releaseDate: '',
    runtime: 0,
    budget: 0,
    language: '',
    coverUrl: '',
    voteAverage: 0,
    voteCount: 0
  });

  useEffect(() => {
    if (authLoading) return;
    if (!isLoggedIn || user?.role !== 'admin') {
      navigate('/');
      return;
    }
    fetchMovies();
  }, [page, searchQuery, isLoggedIn, user, authLoading]);

  useEffect(() => {
    setPageInput(page.toString());
  }, [page]);

  const fetchMovies = async () => {
    setLoading(true);
    try {
      const response = await api.get('/admin/movies', {
        params: { page, query: searchQuery }
      });
      setMovies(response.data.movies);
      setTotalPages(response.data.total_pages);
    } catch (error) {
      console.error('Error fetching movies:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchMovies();
  };

  const handleAddMovie = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/admin/movie', newMovie);
      setNewMovie({
        title: '',
        tagline: '',
        overview: '',
        releaseDate: '',
        runtime: 0,
        budget: 0,
        language: '',
        coverUrl: '',
        voteAverage: 0,
        voteCount: 0
      });
      fetchMovies();
      alert('Movie added successfully!');
    } catch (error) {
      console.error('Error adding movie:', error);
      alert('Failed to add movie');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this movie?')) return;
    try {
      await api.delete(`/admin/movie/${id}`);
      fetchMovies();
    } catch (error) {
      console.error('Error deleting movie:', error);
      alert('Failed to delete movie');
    }
  };

  const startEdit = (movie: AdminMovie) => {
    setEditingId(movie.movieId);
    setEditForm(movie);
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditForm({});
  };

  const saveEdit = async () => {
    if (!editingId) return;
    try {
      // Format date to YYYY-MM-DD if it exists
      const payload = {
        ...editForm,
        releaseDate: editForm.releaseDate ? new Date(editForm.releaseDate).toISOString().split('T')[0] : null
      };
      await api.put(`/admin/movie/${editingId}`, payload);
      setEditingId(null);
      fetchMovies();
    } catch (error) {
      console.error('Error updating movie:', error);
      alert('Failed to update movie');
    }
  };

  const handleClearSearch = () => {
    setSearchQuery('');
    setPage(1);
    // We need to trigger a fetch with empty query, but since fetchMovies depends on searchQuery, 
    // setting it to '' will trigger the effect if we add it to dependency array, 
    // but currently it is in dependency array.
    // However, the effect depends on [page, searchQuery, ...].
    // So setting searchQuery to '' will trigger the effect.
  };

  const handlePageInputSubmit = () => {
    const newPage = parseInt(pageInput);
    if (!isNaN(newPage) && newPage >= 1 && newPage <= totalPages) {
      setPage(newPage);
    } else {
      setPageInput(page.toString());
    }
  };

  return (
    <div className="admin-dashboard">
      <div className="admin-header">
        <h1>Admin Dashboard</h1>
        <div className="search-wrapper">
          <form onSubmit={handleSearch}>
            <Search className="search-icon" size={18} />
            <input
              type="text"
              placeholder="Search movies..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            {searchQuery && (
              <button type="button" className="clear-btn" onClick={handleClearSearch}>
                <X size={16} />
              </button>
            )}
          </form>
        </div>
      </div>

      <form className="add-movie-form" onSubmit={handleAddMovie}>
        <h3>Add New Movie</h3>
        <input
          placeholder="Title"
          value={newMovie.title}
          onChange={e => setNewMovie({...newMovie, title: e.target.value})}
          required
        />
        <input
          placeholder="Tagline"
          value={newMovie.tagline}
          onChange={e => setNewMovie({...newMovie, tagline: e.target.value})}
        />
        <input
          type="date"
          value={newMovie.releaseDate}
          onChange={e => setNewMovie({...newMovie, releaseDate: e.target.value})}
        />
        <input
          type="number"
          placeholder="Runtime (mins)"
          value={newMovie.runtime || ''}
          onChange={e => setNewMovie({...newMovie, runtime: Number(e.target.value)})}
        />
        <input
          type="number"
          placeholder="Budget"
          value={newMovie.budget || ''}
          onChange={e => setNewMovie({...newMovie, budget: Number(e.target.value)})}
        />
        <input
          placeholder="Language"
          value={newMovie.language}
          onChange={e => setNewMovie({...newMovie, language: e.target.value})}
        />
        <input
          type="number"
          step="0.1"
          placeholder="Vote Average"
          value={newMovie.voteAverage || ''}
          onChange={e => setNewMovie({...newMovie, voteAverage: Number(e.target.value)})}
        />
        <input
          type="number"
          placeholder="Vote Count"
          value={newMovie.voteCount || ''}
          onChange={e => setNewMovie({...newMovie, voteCount: Number(e.target.value)})}
        />
        <input
          placeholder="Cover URL"
          value={newMovie.coverUrl}
          onChange={e => setNewMovie({...newMovie, coverUrl: e.target.value})}
          style={{ gridColumn: '1 / -1' }}
        />
        <textarea
          placeholder="Overview"
          value={newMovie.overview}
          onChange={e => setNewMovie({...newMovie, overview: e.target.value})}
          rows={3}
        />
        <button type="submit" className="action-btn" style={{ background: 'var(--accent-orange)', color: 'white', gridColumn: '1/-1' }}>
          <Plus size={16} style={{ marginRight: '5px', verticalAlign: 'middle' }} /> Add Movie
        </button>
      </form>

      {loading ? (
        <div>Loading...</div>
      ) : (
        <>
          <table className="movies-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Title</th>
                <th>Date</th>
                <th>Vote Avg</th>
                <th>Vote Count</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {movies.map(movie => (
                <div key={movie.movieId} style={{ display: 'contents' }}>
                  <tr>
                    <td>{movie.movieId}</td>
                    <td><span title={movie.title}>{movie.title}</span></td>
                    <td>{movie.releaseDate ? new Date(movie.releaseDate).toLocaleDateString() : 'N/A'}</td>
                    <td>{movie.voteAverage || 'N/A'}</td>
                    <td>{movie.voteCount || 0}</td>
                    <td style={{ whiteSpace: 'nowrap' }}>
                      {editingId === movie.movieId ? (
                        <button onClick={cancelEdit} className="action-btn cancel-btn"><X size={14} /></button>
                      ) : (
                        <>
                          <button onClick={() => startEdit(movie)} className="action-btn edit-btn">Edit</button>
                          <button onClick={() => handleDelete(movie.movieId)} className="action-btn delete-btn">Delete</button>
                        </>
                      )}
                    </td>
                  </tr>
                  {editingId === movie.movieId && (
                    <tr className="edit-row">
                      <td colSpan={6} className="edit-cell">
                        <div className="edit-form-expanded">
                          <h4>Edit Movie Details</h4>
                          <div className="edit-grid">
                            <div className="form-group">
                              <label>Title</label>
                              <input 
                                value={editForm.title || ''} 
                                onChange={e => setEditForm({...editForm, title: e.target.value})}
                              />
                            </div>
                            <div className="form-group">
                              <label>Tagline</label>
                              <input 
                                value={editForm.tagline || ''} 
                                onChange={e => setEditForm({...editForm, tagline: e.target.value})}
                              />
                            </div>
                            <div className="form-group">
                              <label>Release Date</label>
                              <input 
                                type="date"
                                value={editForm.releaseDate ? new Date(editForm.releaseDate).toISOString().split('T')[0] : ''} 
                                onChange={e => setEditForm({...editForm, releaseDate: e.target.value})}
                              />
                            </div>
                            <div className="form-group">
                              <label>Language</label>
                              <input 
                                value={editForm.language || ''} 
                                onChange={e => setEditForm({...editForm, language: e.target.value})}
                              />
                            </div>
                            <div className="form-group">
                              <label>Runtime (mins)</label>
                              <input 
                                type="number"
                                value={editForm.runtime || ''} 
                                onChange={e => setEditForm({...editForm, runtime: Number(e.target.value)})}
                              />
                            </div>
                            <div className="form-group">
                              <label>Budget</label>
                              <input 
                                type="number"
                                value={editForm.budget || ''} 
                                onChange={e => setEditForm({...editForm, budget: Number(e.target.value)})}
                              />
                            </div>
                            <div className="form-group">
                              <label>Vote Average</label>
                              <input 
                                type="number"
                                step="0.1"
                                value={editForm.voteAverage || ''} 
                                onChange={e => setEditForm({...editForm, voteAverage: Number(e.target.value)})}
                              />
                            </div>
                            <div className="form-group">
                              <label>Vote Count</label>
                              <input 
                                type="number"
                                value={editForm.voteCount || ''} 
                                onChange={e => setEditForm({...editForm, voteCount: Number(e.target.value)})}
                              />
                            </div>
                            <div className="form-group full-width">
                              <label>Cover URL</label>
                              <input 
                                value={editForm.coverUrl || ''} 
                                onChange={e => setEditForm({...editForm, coverUrl: e.target.value})}
                              />
                            </div>
                            <div className="form-group full-width">
                              <label>Overview</label>
                              <textarea 
                                value={editForm.overview || ''} 
                                onChange={e => setEditForm({...editForm, overview: e.target.value})}
                                rows={4}
                              />
                            </div>
                          </div>
                          <div className="edit-actions">
                            <button onClick={saveEdit} className="action-btn save-btn">
                              <Save size={16} style={{ marginRight: '5px', verticalAlign: 'middle' }} /> Save Changes
                            </button>
                            <button onClick={cancelEdit} className="action-btn cancel-btn">
                              Cancel
                            </button>
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </div>
              ))}
            </tbody>
          </table>

          <div className="pagination">
            <button 
              disabled={page === 1} 
              onClick={() => setPage(p => p - 1)}
              className="page-btn"
            >
              Previous
            </button>
            <div className="page-input-container">
              <span>Page</span>
              <input
                type="number"
                min={1}
                max={totalPages}
                value={pageInput}
                onChange={(e) => setPageInput(e.target.value)}
                onBlur={handlePageInputSubmit}
                onKeyDown={(e) => e.key === 'Enter' && handlePageInputSubmit()}
                className="page-input"
              />
              <span>of {totalPages}</span>
            </div>
            <button 
              disabled={page === totalPages} 
              onClick={() => setPage(p => p + 1)}
              className="page-btn"
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default AdminDashboard;
