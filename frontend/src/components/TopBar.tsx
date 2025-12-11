import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import { Search, LogOut, User as UserIcon, X } from 'lucide-react';
import './TopBar.css';

const TopBar = () => {
  const { isLoggedIn, user, logout } = useAuth();
  const [query, setQuery] = useState('');
  const navigate = useNavigate();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      navigate(`/search?query=${encodeURIComponent(query.trim())}`);
    }
  };

  const handleClear = () => {
    setQuery('');
  };

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  return (
    <div className="top-bar">
      <div className="search-wrapper">
        <form onSubmit={handleSearch}>
          <Search className="search-icon" size={18} />
          <input
            type="text"
            placeholder="Search for movies..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          {query && (
            <button type="button" className="clear-btn" onClick={handleClear}>
              <X size={16} />
            </button>
          )}
        </form>
      </div>

      <div className="user-actions">
        {isLoggedIn ? (
          <div className="user-profile">
            <span className="username">{user?.username}</span>
            <div className="avatar">
              {user?.username.charAt(0).toUpperCase()}
            </div>
            {user?.role === 'admin' && (
              <Link to="/admin" className="admin-badge">Admin</Link>
            )}
            <button onClick={handleLogout} className="logout-btn" title="Logout">
              <LogOut size={18} />
            </button>
          </div>
        ) : (
          <Link to="/login" className="login-link">
            <UserIcon size={18} />
            <span>Login</span>
          </Link>
        )}
      </div>
    </div>
  );
};

export default TopBar;
