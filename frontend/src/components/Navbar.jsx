import { Link, useNavigate } from 'react-router-dom';
import { FiShield, FiLogOut, FiHome, FiUpload, FiClock } from 'react-icons/fi';

export default function Navbar() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem('user') || 'null');

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  return (
    <nav className="bg-slate-900/80 border-b border-slate-700/50 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 flex items-center justify-between h-16">
        <Link to="/" className="flex items-center gap-2 text-xl font-bold no-underline">
          <FiShield className="text-blue-500" size={24} />
          <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            DeepGuard AI
          </span>
        </Link>

        <div className="flex items-center gap-6">
          {user ? (
            <>
              <Link to="/dashboard" className="flex items-center gap-1 text-slate-300 hover:text-white no-underline transition">
                <FiUpload size={16} /> Analyze
              </Link>
              <Link to="/history" className="flex items-center gap-1 text-slate-300 hover:text-white no-underline transition">
                <FiClock size={16} /> History
              </Link>
              <span className="text-slate-400 text-sm">Hi, {user.username}</span>
              <button onClick={logout} className="flex items-center gap-1 text-slate-400 hover:text-red-400 bg-transparent border-0 cursor-pointer transition text-sm">
                <FiLogOut size={16} /> Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/" className="text-slate-300 hover:text-white no-underline transition">
                <FiHome size={16} className="inline mr-1" /> Home
              </Link>
              <Link to="/login" className="text-slate-300 hover:text-white no-underline transition">Login</Link>
              <Link to="/signup" className="btn-primary text-sm no-underline py-2 px-4">Sign Up</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
