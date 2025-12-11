import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import { Search, LogOut, User } from 'lucide-react';
import { useState } from 'react';
import './Header.css';

const Header = () => {
  const { isLoggedIn, user, logout } = useAuth();
  const [query, setQuery] = useState('');
  const navigate = useNavigate();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      navigate(`/search?query=${encodeURIComponent(query.trim())}`);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  return (
    <header className="header">
      <div className="logo">
        <Link to="/">
          <span className="logo-text">MyMovieList</span>
        </Link>
      </div>

      <div className="search-container">
        <form onSubmit={handleSearch}>
          <input
            type="text"
            placeholder="Search for movies..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            required
          />
          <button type="submit" className="search-button">
            <Search size={20} />
          </button>
        </form>
      </div>

      <div className="header-actions">
        {isLoggedIn ? (
          <>
            <span className="username">Hi, {user?.username}</span>
            {user?.role === 'admin' && (
              <Link to="/admin" className="admin-btn">
                Admin
              </Link>
            )}
            <button onClick={handleLogout} className="logout-button">
              <LogOut size={20} />
            </button>
          </>
        ) : (
          <Link to="/login" className="login-button">
            <User size={20} />
          </Link>
        )}
      </div>
    </header>
  );
};

export default Header;
