import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { Star } from 'lucide-react';
import api from '../api';
import type { Movie } from '../types';
import './Search.css';

const Search = () => {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('query') || '';
  const [results, setResults] = useState<Movie[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (query) {
      setLoading(true);
      api
        .get<Movie[]>('/search', { params: { query } })
        .then((response) => {
          setResults(response.data);
        })
        .catch((error) => {
          console.error('Search error:', error);
          setResults([]);
        })
        .finally(() => {
          setLoading(false);
        });
    }
  }, [query]);

  if (!query) {
    return (
      <div className="search-page">
        <p className="no-query">Please enter a search term.</p>
      </div>
    );
  }

  return (
    <div className="search-page">
      <h2>Search Results for "{query}"</h2>

      {loading ? (
        <div className="loading">Searching...</div>
      ) : results.length === 0 ? (
        <p className="no-results">No results found for your search. Please try again.</p>
      ) : (
        <div className="search-list">
          {results.map((movie) => (
            <Link to={`/movie/${movie.movieId}`} key={movie.movieId} className="search-item-link">
              <div className="search-item">
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
                    {movie.releaseDate && (
                      <span className="year"> ({new Date(movie.releaseDate).getFullYear()})</span>
                    )}
                  </h3>
                  
                  <p className="description">
                    {movie.overview ? (movie.overview.length > 150 ? movie.overview.substring(0, 150) + '...' : movie.overview) : 'No description available.'}
                  </p>
                </div>
                
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
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};

export default Search;
