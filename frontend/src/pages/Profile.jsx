import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, LogOut, Mail, Award } from 'lucide-react';

export default function Profile() {
  const [profile, setProfile] = useState({ username: '', email: '' });
  const [stats, setStats] = useState({ totalVideos: 0 });
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');

    let savedUsername = localStorage.getItem('username');
    if (savedUsername === 'undefined') savedUsername = null;
    let savedEmail = localStorage.getItem('email');
    if (savedEmail === 'undefined') savedEmail = null;

    setProfile({
      username: savedUsername || 'User',
      email: savedEmail || ''
    });

    const fetchProfile = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/auth/me', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
          const data = await response.json();
          setProfile({ username: data.username, email: data.email });
          localStorage.setItem('username', data.username);
          localStorage.setItem('email', data.email);
        } else if (response.status === 401) {
          // Token invalid or expired, log out
          localStorage.clear();
          navigate('/login');
        } else {
          console.error("Failed to fetch profile");
        }
      } catch (err) {
        console.error("Network error fetching profile:", err);
      }
    };
    fetchProfile();

    const fetchStats = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/history/videos', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
          const data = await response.json();
          setStats({ totalVideos: data.length });
        }
      } catch (err) {
        console.error(err);
      }
    };
    fetchStats();
  }, [navigate]);

  const handleLogout = () => {
    localStorage.clear();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 p-8 flex items-center justify-center font-sans">
      <div className="w-full max-w-2xl bg-white border border-slate-200 rounded-3xl p-10 shadow-sm">
        <div className="flex items-center justify-between mb-10 pb-8 border-b border-slate-200">
          <div className="flex items-center gap-6">
            <div className="w-20 h-20 bg-gradient-to-tr from-indigo-500 to-purple-500 rounded-2xl flex items-center justify-center shadow-md">
              <User className="w-10 h-10 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-slate-800 mb-1">{profile.username}</h1>
              <div className="flex items-center gap-2 text-slate-500">
                <Mail className="w-4 h-4" />
                <span>{profile.email}</span>
              </div>
            </div>
          </div>
          <button onClick={handleLogout} className="flex items-center gap-2 text-red-600 hover:text-red-700 hover:bg-red-50 px-4 py-2 rounded-lg transition-colors font-semibold">
            <LogOut className="w-5 h-5" /> Logout
          </button>
        </div>

        <div>
          <h2 className="text-xl font-bold mb-6 text-slate-800">Account Stats</h2>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-slate-50 border border-slate-200 p-6 rounded-2xl flex items-center gap-4 shadow-sm">
              <div className="p-3 bg-indigo-100 text-indigo-700 rounded-xl">
                <Award className="w-8 h-8" />
              </div>
              <div>
                <p className="text-slate-500 text-sm font-semibold uppercase tracking-wider mb-1">Videos Processed</p>
                <p className="text-3xl font-bold text-slate-800">{stats.totalVideos}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
