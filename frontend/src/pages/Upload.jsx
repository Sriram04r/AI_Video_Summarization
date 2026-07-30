import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload as UploadIcon, Link as LinkIcon, Loader } from 'lucide-react';

export default function Upload() {
  const [file, setFile] = useState(null);
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState('file'); // 'file' or 'youtube'
  const navigate = useNavigate();

  const handleUpload = async (e) => {
    e.preventDefault();
    setLoading(true);
    const token = localStorage.getItem('token');

    try {
      if (mode === 'file' && file) {
        const xhr = new XMLHttpRequest();
        xhr.open('POST', `${import.meta.env.VITE_API_BASE_URL}/api/video/upload`);
        xhr.setRequestHeader('Authorization', `Bearer ${token}`);
        
        const formData = new FormData();
        formData.append('file', file);
        
        xhr.onload = () => {
          if (xhr.status >= 200 && xhr.status < 300) {
            const data = JSON.parse(xhr.responseText);
            navigate(`/processing/${data.video_id || data.id}`);
          } else {
            let errorMsg = 'Upload failed';
            try {
               const errData = JSON.parse(xhr.responseText);
               if (errData.detail) errorMsg = errData.detail;
            } catch(e) {}
            alert(`Upload failed: ${errorMsg}`);
            setLoading(false);
          }
        };
        xhr.send(formData);
      } else if (mode === 'youtube' && youtubeUrl) {
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/video/youtube`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ url: youtubeUrl })
        });
        if (response.ok) {
          const data = await response.json();
          navigate(`/processing/${data.video_id || data.id}`);
        } else {
          let errorMsg = response.statusText;
          try {
             const errorData = await response.json();
             if (errorData.detail) errorMsg = errorData.detail;
          } catch(e) {}
          alert(`Failed to process YouTube URL: ${errorMsg}`);
          setLoading(false);
        }
      }
    } catch (err) {
      console.error(err);
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex items-center justify-center p-4 md:p-6 font-sans">
      <div className="w-full max-w-xl bg-white border border-slate-200 p-6 md:p-8 rounded-3xl shadow-sm">
        <h2 className="text-3xl font-bold mb-6 text-center text-slate-800">Process Video</h2>
        
        <div className="flex gap-4 mb-8 p-1 bg-slate-100 rounded-xl">
          <button 
            className={`flex-1 py-2 rounded-lg text-sm font-semibold transition-all ${mode === 'file' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-500 hover:text-slate-900'}`}
            onClick={() => setMode('file')}
          >
            Local File
          </button>
          <button 
            className={`flex-1 py-2 rounded-lg text-sm font-semibold transition-all ${mode === 'youtube' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-500 hover:text-slate-900'}`}
            onClick={() => setMode('youtube')}
          >
            YouTube URL
          </button>
        </div>

        <form onSubmit={handleUpload}>
          {mode === 'file' ? (
            <div className="border-2 border-dashed border-slate-300 hover:border-indigo-500 hover:bg-slate-50 rounded-2xl p-6 md:p-12 text-center transition-colors">
              <UploadIcon className="w-12 h-12 text-slate-400 mx-auto mb-4" />
              <input 
                type="file" 
                accept="video/*" 
                onChange={(e) => setFile(e.target.files[0])}
                className="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 cursor-pointer"
              />
            </div>
          ) : (
            <div>
              <div className="relative">
                <LinkIcon className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input
                  type="url"
                  placeholder="https://youtube.com/watch?v=..."
                  value={youtubeUrl}
                  onChange={(e) => setYoutubeUrl(e.target.value)}
                  className="w-full bg-white border border-slate-300 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 rounded-xl py-4 pl-12 pr-4 outline-none transition-all text-slate-800 placeholder:text-slate-400"
                />
              </div>
            </div>
          )}

          <button 
            type="submit" 
            disabled={loading || (mode === 'file' && !file) || (mode === 'youtube' && !youtubeUrl)}
            className="w-full mt-8 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-200 disabled:text-slate-400 text-white py-4 rounded-xl font-bold flex items-center justify-center gap-2 transition-all shadow-sm"
          >
            {loading ? <Loader className="w-5 h-5 animate-spin" /> : 'Start Processing'}
          </button>
        </form>
      </div>
    </div>
  );
}
