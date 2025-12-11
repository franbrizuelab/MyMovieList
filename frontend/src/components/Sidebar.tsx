import { Link, useLocation } from 'react-router-dom';
import { Shield, Star, Shuffle, TrendingUp, Trophy } from 'lucide-react';
import { useAuth } from '../AuthContext';
import './Sidebar.css';

const Sidebar = () => {
  const location = useLocation();
  const { user } = useAuth();

  const isActive = (path: string) => location.pathname === path;

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <Link to="/">
          <img src="/nycuflix.png" alt="MM" className="logo-img" />
        </Link>
      </div>

      <nav className="sidebar-nav">
        <ul>
          <li>
            <Link to="/" className={isActive('/') || isActive('/rating') ? 'active' : ''}>
              <Star size={20} />
              <span>Rating</span>
            </Link>
          </li>
          <li>
            <Link to="/random" className={isActive('/random') ? 'active' : ''}>
              <Shuffle size={20} />
              <span>Random</span>
            </Link>
          </li>
          <li>
            <Link to="/trending" className={isActive('/trending') ? 'active' : ''}>
              <TrendingUp size={20} />
              <span>Trending</span>
            </Link>
          </li>
          <li>
            <Link to="/popular" className={isActive('/popular') ? 'active' : ''}>
              <Trophy size={20} />
              <span>Popular</span>
            </Link>
          </li>
          
          {user?.role === 'admin' && (
            <li>
              <a href="/admin" className={isActive('/admin') ? 'active' : ''}>
                <Shield size={20} />
                <span>Admin</span>
              </a>
            </li>
          )}
        </ul>
      </nav>
    </aside>

  );
};

export default Sidebar;
