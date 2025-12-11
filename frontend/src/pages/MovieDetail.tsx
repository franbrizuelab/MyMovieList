import { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { Star, Calendar, Clock, DollarSign, Globe, Tag, Film } from 'lucide-react';
import api from '../api';
import { useAuth } from '../AuthContext';
import type { MovieDetail, Comment } from '../types';
import './MovieDetail.css';

const StarRatingInput = ({ rating, setRating }: { rating: number; setRating: (r: number) => void }) => {
  const [hovered, setHovered] = useState(0);

  return (
    <div className="star-rating-input" style={{ display: 'flex', gap: '5px', cursor: 'pointer' }}>
      {[1, 2, 3, 4, 5].map((star) => (
        <Star
          key={star}
          size={24}
          fill={star <= (hovered || rating) ? "var(--accent-orange)" : "none"}
          color={star <= (hovered || rating) ? "var(--accent-orange)" : "#666"}
          onMouseEnter={() => setHovered(star)}
          onMouseLeave={() => setHovered(0)}
          onClick={() => setRating(star)}
          style={{ transition: 'transform 0.1s' }}
        />
      ))}
    </div>
  );
};

const MovieDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const [data, setData] = useState<MovieDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [rating, setRating] = useState<number>(0);
  const [comment, setComment] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const { isLoggedIn, user } = useAuth();
  const navigate = useNavigate();

  const fetchMovie = async () => {
    try {
      const response = await api.get<MovieDetail>(`/movie/${id}`);
      setData(response.data);
    } catch (error) {
      console.error('Error fetching movie:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMovie();
  }, [id]);

  const handleRating = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isLoggedIn) {
      navigate(`/login?next=${id}`);
      return;
    }
    setSubmitting(true);
    try {
      await api.post(`/movie/${id}/rate`, { rating });
      fetchMovie();
    } catch (error) {
      console.error('Error rating movie:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const handleComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isLoggedIn) {
      navigate(`/login?next=${id}`);
      return;
    }
    if (!comment.trim()) return;
    setSubmitting(true);
    try {
      await api.post(`/movie/${id}/comment`, { comment: comment.trim() });
      setComment('');
      fetchMovie();
    } catch (error) {
      console.error('Error posting comment:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteComment = async (commentId: number) => {
    if (!confirm('Are you sure you want to delete this comment?')) return;
    try {
      await api.post(`/delete_comment/${commentId}`, { movie_id: id });
      fetchMovie();
    } catch (error) {
      console.error('Error deleting comment:', error);
    }
  };

  if (loading) return <div className="loading">Loading...</div>;
  if (!data) return <div className="error">Movie not found</div>;

  const { movie, user_rating_average, user_rating, comments } = data;

  return (
    <div className="movie-detail-page">
      <div className="movie-content">
        <div className="movie-layout">
          <div className="movie-info">
            <h1>{movie.title}</h1>
            {movie.tagline && <p className="tagline">{movie.tagline}</p>}
            
            <div className="overview-section">
              <h3>Overview</h3>
              <p>{movie.overview || 'No overview available.'}</p>
            </div>

            <div className="details-grid">
              <div className="detail-item">
                <Calendar size={16} className="detail-icon" />
                <span className="detail-label">Released:</span>
                <span className="detail-value">{movie.releaseDate ? new Date(movie.releaseDate).toISOString().split('T')[0] : 'N/A'}</span>
              </div>
              <div className="detail-item">
                <Globe size={16} className="detail-icon" />
                <span className="detail-label">Language:</span>
                <span className="detail-value">{movie.language || 'N/A'}</span>
              </div>
              <div className="detail-item">
                <Clock size={16} className="detail-icon" />
                <span className="detail-label">Runtime:</span>
                <span className="detail-value">{movie.runtime ? `${movie.runtime} mins` : 'N/A'}</span>
              </div>
              <div className="detail-item">
                <DollarSign size={16} className="detail-icon" />
                <span className="detail-label">Budget:</span>
                <span className="detail-value">{movie.budget ? `$${movie.budget.toLocaleString()}` : 'N/A'}</span>
              </div>
              <div className="detail-item">
                <Tag size={16} className="detail-icon" />
                <span className="detail-label">Critic Rating:</span>
                <span className="detail-value">{movie.voteAverage || 'N/A'}</span>
              </div>
              <div className="detail-item">
                <Star size={16} className="detail-icon" />
                <span className="detail-label">User Rating:</span>
                <span className="detail-value">{user_rating_average || 'N/A'}</span>
              </div>
            </div>

            {isLoggedIn && (
              <div className="rating-section">
                {user_rating !== null ? (
                  <>
                    <p>
                      <span>Your Rating:</span> {user_rating}
                    </p>
                    <form onSubmit={handleRating} className="rating-form">
                      <label>Update your rating:</label>
                      <StarRatingInput rating={rating} setRating={setRating} />
                      <button type="submit" disabled={submitting}>
                        Update Rating
                      </button>
                    </form>
                  </>
                ) : (
                  <>
                    <p>You haven't rated this movie yet.</p>
                    <form onSubmit={handleRating} className="rating-form">
                      <label>Rate this movie:</label>
                      <StarRatingInput rating={rating} setRating={setRating} />
                      <button type="submit" disabled={submitting}>
                        Submit Rating
                      </button>
                    </form>
                  </>
                )}
              </div>
            )}
            
            <Link to="/" className="back-link">
              Back to Main Page
            </Link>
          </div>

          <div className="movie-poster-container">
            {movie.coverUrl ? (
              <img src={movie.coverUrl} alt={movie.title} className="movie-poster" />
            ) : (
              <div className="no-poster">
                <Film size={48} />
                <span>No Poster</span>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="comments-section">
        <h2>Comments</h2>

        {comments.length > 0 ? (
          <ul className="comments-list">
            {comments.map((c: Comment) => (
              <li key={c.commentId} className="comment-item">
                <div className="comment-avatar">
                  {c.userName.charAt(0).toUpperCase()}
                </div>
                <div className="comment-content">
                  <div className="comment-header">
                    <strong>{c.userName}</strong>
                    <div className="comment-meta">
                      {isLoggedIn && (user?.username === c.userName || user?.role === 'admin') && (
                        <button className="delete-btn" onClick={() => handleDeleteComment(c.commentId)}>
                          Delete
                        </button>
                      )}
                      <span className="comment-date">{c.timeStamp}</span>
                    </div>
                  </div>
                  <p className="comment-text">{c.commentText}</p>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p className="no-comments">No comments yet. Be the first to comment!</p>
        )}

        {isLoggedIn ? (
          <form onSubmit={handleComment} className="comment-form">
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="Leave a comment..."
              rows={3}
              required
            />
            <button type="submit" disabled={submitting}>
              Post Comment
            </button>
          </form>
        ) : (
          <p className="login-prompt">
            <Link to={`/login?next=${id}`}>Log in</Link> to leave a comment.
          </p>
        )}
      </div>
    </div>
  );
};

export default MovieDetailPage;
