import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Video, ArrowRight, Zap, Shield, Sparkles } from 'lucide-react';

export default function Landing() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) setIsLoggedIn(true);
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans overflow-hidden">
      <nav className="flex justify-between items-center p-6 max-w-7xl mx-auto relative z-10">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-indigo-600 rounded-lg shadow-sm">
            <Video className="w-5 h-5 text-white" />
          </div>
          <span className="font-bold text-xl tracking-tight text-slate-800">AI Summarizer</span>
        </div>
        <div className="flex gap-4">
          {isLoggedIn ? (
            <Link to="/dashboard" className="text-sm font-semibold bg-indigo-600 hover:bg-indigo-700 text-white transition-colors px-4 py-2 rounded-lg shadow-sm">
              Dashboard
            </Link>
          ) : (
            <>
              <Link to="/login" className="text-sm font-semibold text-slate-600 hover:text-slate-900 transition-colors px-4 py-2">
                Login
              </Link>
              <Link to="/register" className="text-sm font-semibold bg-indigo-600 hover:bg-indigo-700 text-white transition-colors px-4 py-2 rounded-lg shadow-sm">
                Get Started
              </Link>
            </>
          )}
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 pt-20 pb-32 text-center relative">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-indigo-200/50 rounded-full blur-[120px] pointer-events-none" />
        
        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-slate-900 mb-8 relative">
          Analyze Lectures in Seconds
        </h1>
        <p className="text-xl text-slate-600 max-w-2xl mx-auto mb-12 relative">
          Transform hours of video content into concise summaries, keyframes, and interactive chats using advanced AI models.
        </p>

        <div className="flex gap-4 justify-center relative">
          <Link to={isLoggedIn ? "/dashboard" : "/register"} className="bg-indigo-600 hover:bg-indigo-700 text-white px-8 py-4 rounded-xl font-bold flex items-center gap-2 transition-all hover:-translate-y-1 shadow-lg shadow-indigo-600/20">
            {isLoggedIn ? "Go to Dashboard" : "Start Summarizing"} <ArrowRight className="w-5 h-5" />
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-32 relative">
          <div className="p-8 bg-white rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <div className="w-14 h-14 bg-indigo-50 rounded-xl flex items-center justify-center mx-auto mb-6">
               <Zap className="w-7 h-7 text-indigo-600" />
            </div>
            <h3 className="text-xl font-bold mb-3 text-slate-800">Lightning Fast</h3>
            <p className="text-slate-600 leading-relaxed">Process long videos in a fraction of the time it takes to watch them.</p>
          </div>
          <div className="p-8 bg-white rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <div className="w-14 h-14 bg-indigo-50 rounded-xl flex items-center justify-center mx-auto mb-6">
               <Sparkles className="w-7 h-7 text-indigo-600" />
            </div>
            <h3 className="text-xl font-bold mb-3 text-slate-800">AI-Powered Summaries</h3>
            <p className="text-slate-600 leading-relaxed">Get highly accurate summaries and key takeaways automatically.</p>
          </div>
          <div className="p-8 bg-white rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
            <div className="w-14 h-14 bg-indigo-50 rounded-xl flex items-center justify-center mx-auto mb-6">
               <Shield className="w-7 h-7 text-indigo-600" />
            </div>
            <h3 className="text-xl font-bold mb-3 text-slate-800">Secure & Private</h3>
            <p className="text-slate-600 leading-relaxed">Your data and videos are encrypted and safely stored.</p>
          </div>
        </div>
      </main>
    </div>
  );
}
