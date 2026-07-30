import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Video, Upload, History, User } from 'lucide-react';

export default function Dashboard() {
  const [videos, setVideos] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');


    const fetchDashboardData = async () => {
      try {
        const videosRes = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/history/videos`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (videosRes.ok) {
          const data = await videosRes.json();
          setVideos(data.slice(0, 5));
        }

        await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/history`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
      } catch (err) {
        console.error(err);
      }
    };
    fetchDashboardData();
  }, [navigate]);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 p-4 md:p-8 font-sans">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-8 text-slate-800">Dashboard</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <Link to="/upload" className="bg-white border border-indigo-100 hover:border-indigo-300 hover:bg-indigo-50 shadow-sm p-6 rounded-2xl transition-all group">
            <Upload className="w-8 h-8 text-indigo-600 mb-4 group-hover:scale-110 transition-transform" />
            <h2 className="text-xl font-semibold mb-2 text-slate-800">Upload Video</h2>
            <p className="text-sm text-slate-500">Process a new lecture or YouTube video</p>
          </Link>
          <Link to="/history" className="bg-white border border-slate-200 hover:border-slate-300 hover:bg-slate-50 shadow-sm p-6 rounded-2xl transition-all group">
            <History className="w-8 h-8 text-indigo-500 mb-4 group-hover:scale-110 transition-transform" />
            <h2 className="text-xl font-semibold mb-2 text-slate-800">View History</h2>
            <p className="text-sm text-slate-500">Access your previously processed videos</p>
          </Link>
          <Link to="/profile" className="bg-white border border-slate-200 hover:border-slate-300 hover:bg-slate-50 shadow-sm p-6 rounded-2xl transition-all group">
            <User className="w-8 h-8 text-indigo-500 mb-4 group-hover:scale-110 transition-transform" />
            <h2 className="text-xl font-semibold mb-2 text-slate-800">My Profile</h2>
            <p className="text-sm text-slate-500">Manage your account settings</p>
          </Link>
        </div>

        <div>
          <h2 className="text-2xl font-bold mb-6 text-slate-800">Recent Videos</h2>
          {videos.length === 0 ? (
            <div className="p-8 bg-white border border-slate-200 shadow-sm rounded-2xl text-center">
              <Video className="w-12 h-12 text-slate-300 mx-auto mb-4" />
              <p className="text-slate-500">No videos processed yet. Start by uploading one!</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {videos.map(video => (
                <Link key={video.video_id} to={`/results/${video.video_id}`} className="bg-white border border-slate-200 shadow-sm p-5 rounded-xl hover:border-indigo-300 transition-colors">
                  <h3 className="font-semibold text-lg text-slate-800 truncate">{video.title || video.filename}</h3>
                  <p className="text-sm text-slate-500 mt-2 font-medium">Status: {video.status}</p>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
