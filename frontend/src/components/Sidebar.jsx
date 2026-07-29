import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { Video, LayoutDashboard, UploadCloud, History, User, LogOut } from 'lucide-react';

export default function Sidebar() {
  const navigate = useNavigate();
  let username = localStorage.getItem('username');
  if (!username || username === 'undefined') username = 'User';

  const handleLogout = () => {
    localStorage.clear();
    navigate('/');
  };

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Upload Video', path: '/upload', icon: UploadCloud },
    { name: 'History', path: '/history', icon: History },
    { name: 'Profile', path: '/profile', icon: User },
  ];

  return (
    <aside className="w-64 bg-[#0a0e17] border-r border-slate-900 flex flex-col shrink-0">
      {/* Branding */}
      <div className="p-6 border-b border-slate-900 flex items-center gap-2.5">
        <div className="p-1.5 bg-indigo-600 rounded-lg shadow-md shadow-indigo-600/20">
          <Video className="w-5 h-5 text-white" />
        </div>
        <span className="font-bold text-slate-200 text-sm tracking-wide">Nexus Video AI</span>
      </div>

      {/* Nav List */}
      <nav className="flex-1 px-4 py-6 space-y-1.5">
        {navItems.map((item) => (
          <NavLink
            key={item.name}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3.5 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${
                isActive
                  ? 'bg-indigo-600/10 text-indigo-400 border-l-2 border-indigo-500 pl-3.5'
                  : 'text-slate-400 hover:bg-slate-900/60 hover:text-slate-200'
              }`
            }
          >
            <item.icon className="w-5 h-5" />
            {item.name}
          </NavLink>
        ))}
      </nav>

      {/* Profile & Logout */}
      <div className="p-4 border-t border-slate-900 space-y-4">
        <div className="flex items-center gap-3 px-2">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-600 to-teal-500 flex items-center justify-center font-bold text-xs text-white">
            {username.charAt(0).toUpperCase()}
          </div>
          <div className="truncate">
            <h4 className="text-xs font-semibold text-slate-300 truncate">{username}</h4>
            <span className="text-[10px] text-slate-500 truncate">Logged in</span>
          </div>
        </div>
        
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-4 py-3 text-slate-400 hover:text-red-400 hover:bg-red-500/5 rounded-xl text-sm font-medium transition-all duration-200"
        >
          <LogOut className="w-5 h-5 text-slate-500 group-hover:text-red-400" />
          Sign Out
        </button>
      </div>
    </aside>
  );
}
