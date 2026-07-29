import React, { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Loader2 } from 'lucide-react';

export default function Processing() {
  const { videoId } = useParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('processing');
  const [error, setError] = useState(null);

  const processingRef = useRef(false);

  useEffect(() => {
    const token = localStorage.getItem('token');


    let interval;

    const startProcessing = async () => {
      try {
        // Initiate the processing pipeline on the backend
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/video/process/${videoId}?language=English&difficulty=Intermediate`, {
          method: 'POST',
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        if (!response.ok) {
           const errData = await response.json().catch(() => ({}));
           setStatus('failed');
           setError(errData.detail || 'Failed to initiate video processing.');
        }
      } catch (err) {
        console.error("Start process error:", err);
        setStatus('failed');
        setError('Network error while starting processing.');
      }
    };

    const checkStatus = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/video/status/${videoId}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (response.ok) {
          const data = await response.json();
          if (data.status === 'completed') {
            if (interval) clearInterval(interval);
            navigate(`/results/${videoId}`);
          } else if (data.status === 'failed') {
            if (interval) clearInterval(interval);
            setStatus('failed');
            setError('Processing failed. Please try again.');
          }
        }
      } catch (err) {
        console.error("Status check error:", err);
      }
    };

    if (!processingRef.current) {
      processingRef.current = true;
      startProcessing().then(() => {
        interval = setInterval(checkStatus, 5000);
        checkStatus();
      });
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [videoId, navigate]);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex items-center justify-center p-6 font-sans">
      <div className="text-center">
        {status === 'failed' ? (
          <div className="bg-red-50 border border-red-200 p-8 rounded-2xl shadow-sm">
            <h2 className="text-xl font-bold text-red-600 mb-2">Error</h2>
            <p className="text-slate-700 font-medium">{error}</p>
            <button onClick={() => navigate('/dashboard')} className="mt-6 bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 px-6 py-2.5 rounded-xl font-semibold shadow-sm transition-colors">Back to Dashboard</button>
          </div>
        ) : (
          <div className="flex flex-col items-center">
            <Loader2 className="w-16 h-16 text-indigo-600 animate-spin mb-6" />
            <h2 className="text-2xl font-bold mb-2 text-slate-800">Processing Video...</h2>
            <p className="text-slate-500 max-w-md mx-auto">
              Our AI is extracting frames, analyzing audio, and generating a comprehensive summary. This may take a few minutes depending on the video length.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
