import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import TopBar from './TopBar';
import './Layout.css';

const Layout = () => {
  return (
    <div className="layout">
      <Sidebar />
      <div className="content-wrapper">
        <TopBar />
        <main className="main-content">
          <Outlet />
        </main>
        <footer className="footer">
          &copy; 2025 DYNAMIC WEB PROGRAMMING FINAL PROJECT. All rights reserved.
        </footer>
      </div>
    </div>
  );
};

export default Layout;
