import React from 'react';
import { Calendar, User } from 'lucide-react';

export default function Header({ title }) {
  const username = localStorage.getItem('username') || 'User';
  const currentDate = new Date().toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
  });

  return (
    <header className="h-20 bg-[#070b14] border-b border-slate-900 px-8 flex justify-between items-center shrink-0">
      <div>
        <h1 className="text-xl font-bold text-white tracking-wide">{title}</h1>
      </div>
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2 text-slate-500 text-xs font-semibold">
          <Calendar className="w-4 h-4" />
          <span>{currentDate}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-slate-300">{username}</span>
        </div>
      </div>
    </header>
  );
}
