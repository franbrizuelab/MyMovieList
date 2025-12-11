import { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Star, MessageSquare } from 'lucide-react';
import api from '../api';
import type { HomeData, Movie } from '../types';
import './Home.css';

type TabKey = 'rating' | 'random' | 'trending' | 'popular';

const Home = () => {
  const [data, setData] = useState<HomeData | null>(null);
  const [loading, setLoading] = useState(true);
  const location = useLocation();
  
  // Determine active tab from URL path
  const getActiveTab = (): TabKey => {
    const path = location.pathname.substring(1); // remove leading slash
    if (path === '' || path === 'rating') return 'rating';
    if (path === 'random') return 'random';
    if (path === 'trending') return 'trending';
    if (path === 'popular') return 'popular';
    return 'rating';
  };

  const activeTab = getActiveTab();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await api.get<HomeData>('/home');
        setData(response.data);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <div className="loading">Loading...</div>;
  if (!data) return <div className="error">Failed to load data</div>;

  let movies: Movie[] = [];
  let pageTitle = "Top Rated Movies";

  if (activeTab === 'rating') {
    movies = data.top_rated;
    pageTitle = "Top Rated Movies";
  } else if (activeTab === 'random') {
    movies = data.random;
    pageTitle = "Random Selection";
  } else if (activeTab === 'trending') {
    movies = data.trending;
    pageTitle = "Trending Now";
  } else {
    movies = data.popular;
    pageTitle = "Most Popular";
  }

  // Render Random Tab (Grid View)
  if (activeTab === 'random') {
    return (
      <div className="home-page">
        <header className="page-header">
          <div className="header-title">
            <h2>{pageTitle}</h2>
          </div>
        </header>

        <div className="movie-grid">
          {movies.map((movie) => (
            <Link to={`/movie/${movie.movieId}`} key={movie.movieId} className="movie-card-link">
              <div className="movie-card">
                <div className="card-poster">
                  {movie.coverUrl ? (
                    <img src={movie.coverUrl} alt={movie.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                  ) : (
                    <div className="poster-placeholder">
                      {movie.title.substring(0, 2).toUpperCase()}
                    </div>
                  )}
                </div>
                <div className="card-info">
                  <h3>{movie.title}</h3>
                  <p className="card-description">
                    {movie.overview ? (movie.overview.length > 80 ? movie.overview.substring(0, 80) + '...' : movie.overview) : 'No description available.'}
                  </p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    );
  }

  // Render List View (Rating, Trending, Popular)
  return (
    <div className="home-page">
      <header className="page-header">
        <div className="header-title">
          <h2>{pageTitle}</h2>
        </div>
      </header>

      <div className="movie-list">
        {movies.map((movie, index) => (
          <Link to={`/movie/${movie.movieId}`} key={movie.movieId} className="movie-item-link">
            <div className="movie-item">
              {/* Rank - Only for Rating and Popular */}
              {activeTab !== 'trending' && (
                <div className="rank">{index + 1}</div>
              )}
              
              <div className="poster">
                {movie.coverUrl ? (
                  <img src={movie.coverUrl} alt={movie.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                ) : (
                  <div className="poster-placeholder">
                    {movie.title.substring(0, 2).toUpperCase()}
                  </div>
                )}
              </div>
              
              <div className="info">
                <h3>
                  {movie.title} 
                  {/* Show Year for Rating and Popular */}
                  {activeTab !== 'trending' && movie.releaseDate && (
                    <span className="year"> ({new Date(movie.releaseDate).getFullYear()})</span>
                  )}
                </h3>
                
                <p className="description">
                  {movie.overview ? (movie.overview.length > 120 ? movie.overview.substring(0, 120) + '...' : movie.overview) : 'No description available.'}
                </p>
              </div>
              
              {/* Right Side Stats */}
              <div className="stats-box">
                {activeTab === 'popular' ? (
                  <div className="comment-stat">
                    <MessageSquare size={20} className="icon" />
                    <span className="count">{movie.totalComments || 0}</span>
                    <span className="label">Comments</span>
                  </div>
                ) : activeTab === 'trending' ? (
                  <div className="year-stat">
                    <span className="year-large">{movie.releaseYear || 'N/A'}</span>
                    <span className="label">Release Year</span>
                  </div>
                ) : (
                  <div className="rating-box">
                    <span className="score">{movie.voteAverage ? movie.voteAverage.toFixed(1) : 'N/A'}/10</span>
                    <div className="stars">
                      {[...Array(5)].map((_, i) => (
                        <Star 
                          key={i} 
                          size={12} 
                          fill={i < Math.round((movie.voteAverage || 0) / 2) ? "#ff6b00" : "#333"} 
                          stroke="none"
                        />
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
};

export default Home;
