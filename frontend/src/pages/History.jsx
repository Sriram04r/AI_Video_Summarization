import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { History as HistoryIcon, Clock, ArrowRight } from 'lucide-react';

export default function History() {
  const [videos, setVideos] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');


    const fetchHistory = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/history/videos`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
          const data = await response.json();
          setVideos(data);
        }
      } catch (err) {
        console.error(err);
      }
    };
    fetchHistory();
  }, [navigate]);

  const handleClearHistory = async () => {
    if (!window.confirm("Are you sure you want to clear all processing history? This action cannot be undone.")) return;
    
    const token = localStorage.getItem('token');
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/history/clear`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        setVideos([]);
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 p-4 md:p-8 font-sans">
      <div className="max-w-5xl mx-auto">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-10 pb-6 border-b border-slate-200">
          <div className="flex items-center gap-3">
            <HistoryIcon className="w-8 h-8 text-indigo-600" />
            <h1 className="text-3xl font-bold text-slate-800">Processing History</h1>
          </div>
          {videos.length > 0 && (
            <button
              onClick={handleClearHistory}
              className="px-4 py-2 bg-red-50 text-red-600 border border-red-200 rounded-lg hover:bg-red-100 transition-colors text-sm font-semibold shadow-sm"
            >
              Clear History
            </button>
          )}
        </div>

        {videos.length === 0 ? (
          <div className="text-center py-20 bg-white rounded-3xl border border-slate-200 shadow-sm">
            <p className="text-slate-500 text-lg">No videos found in your history.</p>
            <Link to="/upload" className="mt-6 inline-block bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-xl font-semibold transition-colors shadow-sm">
              Process a Video
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {videos.map((vid) => (
              <div key={vid.video_id || vid.id} className="bg-white border border-slate-200 shadow-sm p-6 rounded-2xl hover:border-indigo-300 transition-colors flex flex-col justify-between group">
                <div>
                  <h3 className="text-xl font-bold mb-2 truncate text-slate-800">{vid.title || vid.filename}</h3>
                  <div className="flex items-center gap-2 text-slate-500 text-sm mb-4">
                    <Clock className="w-4 h-4" /> 
                    <span>{new Date(vid.created_at || Date.now()).toLocaleDateString()}</span>
                  </div>
                  <div className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200">
                    {vid.status}
                  </div>
                </div>
                
                <div className="mt-6 pt-4 border-t border-slate-100">
                  <Link to={`/results/${vid.video_id || vid.id}`} className="flex items-center justify-between text-slate-500 group-hover:text-indigo-600 transition-colors">
                    <span className="font-semibold">View Results</span>
                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
