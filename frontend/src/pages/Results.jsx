import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { FileText, MessageSquare, Download, ArrowLeft, Image as ImageIcon, BookOpen, Clock, FileQuestion, Users, FileType, Sparkles } from 'lucide-react';

export default function Results() {
  const { videoId } = useParams();
  const [data, setData] = useState(null);
  const [chatInput, setChatInput] = useState('');
  const [chatHistory, setChatHistory] = useState([
    { role: 'assistant', content: 'Hi! Ask me anything about this video transcript. I can explain complex terms, write code, or give summaries!' }
  ]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('summaries');

  useEffect(() => {
    const token = localStorage.getItem('token');
    const fetchData = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/video/results/${videoId}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
          const result = await response.json();
          setData(result);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [videoId]);

  const sendChatMessage = async (msgText) => {
    if (!msgText.trim()) return;
    const token = localStorage.getItem('token');
    setChatHistory(prev => [...prev, { role: 'user', content: msgText }]);

    const chatContainer = document.getElementById('ai-chat-sidebar');
    if (chatContainer) chatContainer.scrollIntoView({ behavior: 'smooth' });

    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/video/chat/${videoId}`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}` 
        },
        body: JSON.stringify({ question: msgText })
      });
      if (response.ok) {
        const result = await response.json();
        setChatHistory(prev => [...prev, { role: 'assistant', content: result.answer }]);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleChat = async (e) => {
    e.preventDefault();
    const userMsg = chatInput;
    setChatInput('');
    await sendChatMessage(userMsg);
  };

  const handleDownloadReport = async () => {
    const token = localStorage.getItem('token');
    window.open(`${import.meta.env.VITE_API_BASE_URL}/api/video/report/${videoId}?token=${token}`, '_blank');
  };

  const formatDuration = (seconds) => {
    if (!seconds) return '0:00';
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  if (loading) return <div className="min-h-screen bg-slate-50 flex items-center justify-center text-slate-500 font-medium">Loading results...</div>;
  if (!data) return <div className="min-h-screen bg-slate-50 flex items-center justify-center text-slate-500 font-medium">Results not found.</div>;

  const isYouTube = data.filename && data.filename.startsWith('youtube://');
  const youtubeId = isYouTube ? data.filename.replace('youtube://', '') : '';
  const videoStreamUrl = !isYouTube && data.filename ? `${import.meta.env.VITE_API_BASE_URL}/uploads/${data.filename}` : '';

  const tabs = [
    { id: 'summaries', label: 'Summaries', icon: FileText },
    { id: 'notes', label: 'Study Notes', icon: BookOpen },
    { id: 'transcript', label: 'Transcript', icon: FileType },
    { id: 'quiz', label: 'Quiz Sheet', icon: FileQuestion },
    { id: 'interview', label: 'Interview Prep', icon: Users },
    { id: 'keyframes', label: 'Keyframes', icon: ImageIcon },
  ];

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 p-6 md:p-8 font-sans flex flex-col h-screen overflow-hidden">
      {/* Header */}
      <div className="flex justify-between items-center mb-6 pb-6 border-b border-slate-200 shrink-0">
        <div className="flex items-center gap-6">
          <Link to="/dashboard" className="text-slate-400 hover:text-indigo-600 transition-colors">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-slate-800 truncate max-w-xl">{data.title || 'Video Analysis'}</h1>
            <div className="flex items-center gap-2 text-slate-500 text-xs font-semibold mt-1.5 tracking-wider">
              <Clock className="w-3.5 h-3.5" /> 
              <span>DURATION: {formatDuration(data.duration)}</span>
            </div>
          </div>
        </div>
        <button onClick={handleDownloadReport} className="flex items-center gap-2 bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 shadow-sm px-5 py-2.5 rounded-xl transition-colors font-semibold text-sm">
          <Download className="w-4 h-4" /> Download PDF Report
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-[minmax(350px,30%)_1fr] gap-8 flex-1 min-h-0">
        {/* Sidebar */}
        <div id="ai-chat-sidebar" className="flex flex-col space-y-6 min-h-0">
          <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm p-2 shrink-0">
            {isYouTube ? (
              <iframe
                className="w-full rounded-xl aspect-video object-cover"
                src={`https://www.youtube.com/embed/${youtubeId}`}
                title="YouTube video player"
                frameBorder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              ></iframe>
            ) : videoStreamUrl ? (
              <video src={videoStreamUrl} controls className="w-full rounded-xl bg-slate-950 aspect-video object-cover" />
            ) : (
              <div className="w-full aspect-video bg-slate-100 flex items-center justify-center rounded-xl border border-slate-200">
                <span className="text-slate-400">Video not available</span>
              </div>
            )}
          </div>

          <div className="flex-1 flex flex-col min-h-0 pb-2 bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-2 mb-4 shrink-0">
              <Sparkles className="w-4 h-4 text-indigo-500" /> AI Lecture Companion
            </h3>
            
            <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-2 flex flex-col">
              {chatHistory.map((msg, i) => (
                <div key={i} className={`p-4 rounded-2xl shadow-sm ${msg.role === 'user' ? 'bg-indigo-600 text-white ml-auto max-w-[85%]' : 'bg-slate-50 border border-slate-100 text-slate-700 mr-auto max-w-[95%]'}`}>
                  {msg.role === 'assistant' && <div className="text-[10px] font-bold text-slate-400 mb-2 uppercase tracking-wider">AI Instructor</div>}
                  <div className={`text-sm leading-relaxed whitespace-pre-wrap prose prose-sm max-w-none prose-p:my-1 prose-ul:my-1 prose-li:my-0 ${msg.role === 'user' ? 'text-white' : 'text-slate-700'}`}>
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  </div>
                </div>
              ))}
              <div id="chat-bottom"></div>
            </div>

            <form onSubmit={handleChat} className="flex gap-2 relative shrink-0">
              <input 
                type="text" 
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                placeholder="Ask a question about this lecture..."
                className="w-full bg-slate-50 border border-slate-200 rounded-2xl pl-5 pr-14 py-4 outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 text-sm placeholder:text-slate-400 text-slate-800 transition-all"
              />
              <button type="submit" className="absolute right-2 top-2 bottom-2 bg-indigo-600 hover:bg-indigo-700 w-10 flex items-center justify-center rounded-xl transition-colors shadow-sm">
                <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M12 5l7 7-7 7" />
                </svg>
              </button>
            </form>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="flex flex-col min-h-0">
          {/* Tabs */}
          <div className="flex items-center gap-2 overflow-x-auto pb-4 mb-2 scrollbar-hide shrink-0">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold transition-all whitespace-nowrap border shadow-sm ${
                    isActive 
                      ? 'bg-white text-indigo-700 border-indigo-100 ring-2 ring-indigo-50' 
                      : 'bg-white text-slate-500 hover:bg-slate-50 hover:text-slate-700 border-slate-200'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-indigo-600' : 'text-slate-400'}`} />
                  {tab.label}
                </button>
              );
            })}
          </div>

          {/* Tab Content */}
          <div className="flex-1 overflow-y-auto pr-2 space-y-6 pb-10 mt-4">
            {activeTab === 'summaries' && (
              <>
                <ContentCard title="Short Summary" content={data.short_summary || data.summary} />
                <ContentCard title="Detailed Analysis" content={data.detailed_summary} />
                <ContentCard title="Topic-wise Summary" content={data.topic_summary} />
              </>
            )}
            
            {activeTab === 'notes' && (
              <>
                <ContentCard title="Important Takeaways" content={data.notes_important} />
                <ContentCard title="Revision Cheatsheet" content={data.notes_revision} />
                <ContentCard title="Detailed Study Notes" content={data.notes_study} />
              </>
            )}

            {activeTab === 'transcript' && (
              <ContentCard title="Full Transcript" content={data.transcript} />
            )}

            {activeTab === 'quiz' && (
              <QuizCard dataStr={data.quiz} onAskBot={sendChatMessage} />
            )}

            {activeTab === 'interview' && (
              <InterviewCard dataStr={data.interview_questions} onAskBot={sendChatMessage} />
            )}

            {activeTab === 'keyframes' && (
              <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
                {isYouTube ? (
                  <div className="text-center py-12 text-slate-500">
                    <ImageIcon className="w-16 h-16 mx-auto mb-4 text-slate-300" />
                    <h3 className="text-xl font-bold text-slate-700 mb-2">Visual Analysis Skipped</h3>
                    <p className="max-w-md mx-auto text-slate-500 leading-relaxed">
                      To conserve cloud bandwidth, visual keyframe extraction is bypassed for YouTube links. 
                      If you need visual frame analysis, please use the <strong>Upload Local File</strong> option.
                    </p>
                  </div>
                ) : (
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {data.keyframes?.map((kf, i) => {
                      const filename = kf.filename || kf;
                      const timestamp = kf.timestamp !== undefined ? formatDuration(kf.timestamp) : '';
                      return (
                        <div key={i} className="relative group rounded-xl overflow-hidden border border-slate-200 shadow-sm hover:border-indigo-300 transition-colors">
                          <img 
                            src={`${import.meta.env.VITE_API_BASE_URL}/frames/video_${data.video_id || videoId}/${filename}`} 
                            alt="Keyframe" 
                            className="w-full object-cover aspect-video"
                          />
                          {timestamp && (
                            <div className="absolute bottom-2 right-2 bg-slate-900/80 text-white text-xs font-bold px-2 py-1 rounded backdrop-blur-sm">
                              {timestamp}
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function ContentCard({ title, content }) {
  if (!content) return null;
  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-8 relative overflow-hidden group shadow-sm">
      <div className="absolute left-0 top-0 bottom-0 w-1.5 bg-indigo-500"></div>
      <h3 className="text-xl font-bold mb-6 text-slate-800 pl-2">{title}</h3>
      <div className="prose prose-slate max-w-none prose-p:leading-relaxed text-slate-600 text-base pl-2">
        <ReactMarkdown>{content}</ReactMarkdown>
      </div>
    </div>
  );
}

function QuizCard({ dataStr, onAskBot }) {
  const [userAnswers, setUserAnswers] = useState({});
  const [submitted, setSubmitted] = useState(false);
  const [score, setScore] = useState(0);

  if (!dataStr) return null;
  let quiz = null;
  try {
    quiz = JSON.parse(dataStr);
  } catch (e) {
    return <ContentCard title="Practice Quiz" content={dataStr} />;
  }
  
  if (quiz.error) return <ContentCard title="Practice Quiz" content={quiz.error} />;

  const handleOptionSelect = (qIdx, opt) => {
    if (submitted) return;
    setUserAnswers(prev => ({ ...prev, [qIdx]: opt }));
  };

  const handleSubmit = () => {
    let newScore = 0;
    quiz.mcqs?.forEach((mcq, idx) => {
      if (userAnswers[idx] === mcq.answer) {
        newScore += 1;
      }
    });
    setScore(newScore);
    setSubmitted(true);
  };

  return (
    <div className="space-y-6">
      {quiz.mcqs && quiz.mcqs.length > 0 && (
        <div className="bg-white border border-slate-200 rounded-2xl p-8 shadow-sm relative overflow-hidden">
          <div className="absolute left-0 top-0 bottom-0 w-1.5 bg-indigo-500"></div>
          <div className="flex justify-between items-center mb-8 pl-2">
            <h3 className="text-xl font-bold text-slate-800">Multiple Choice Questions</h3>
            {submitted && (
              <div className="bg-indigo-50 text-indigo-700 border border-indigo-200 px-4 py-2 rounded-lg font-bold text-sm shadow-sm">
                Score: {score} / {quiz.mcqs.length}
              </div>
            )}
          </div>
          <div className="space-y-8 pl-2">
            {quiz.mcqs.map((mcq, idx) => (
              <div key={idx} className="bg-slate-50 p-6 rounded-xl border border-slate-200 shadow-sm">
                <p className="font-semibold text-slate-800 mb-4">{idx + 1}. {mcq.question}</p>
                <div className="space-y-3 mb-2">
                  {mcq.options?.map((opt, oIdx) => {
                    const isSelected = userAnswers[idx] === opt;
                    const isActualAnswer = mcq.answer === opt;
                    
                    let optionClass = "text-sm pl-4 py-3 border-l-4 rounded-r-lg cursor-pointer transition-colors duration-200 shadow-sm bg-white ";
                    
                    if (submitted) {
                      if (isActualAnswer) {
                        optionClass += "border-green-500 text-green-700 bg-green-50 font-semibold";
                      } else if (isSelected && !isActualAnswer) {
                        optionClass += "border-red-500 text-red-700 bg-red-50";
                      } else {
                        optionClass += "border-slate-200 text-slate-400";
                      }
                    } else {
                      if (isSelected) {
                        optionClass += "border-indigo-500 text-indigo-700 bg-indigo-50 font-semibold ring-1 ring-indigo-100";
                      } else {
                        optionClass += "border-slate-200 text-slate-600 hover:bg-slate-50 hover:border-slate-300";
                      }
                    }

                    return (
                      <div 
                        key={oIdx} 
                        onClick={() => handleOptionSelect(idx, opt)}
                        className={optionClass}
                      >
                        {opt}
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
          {!submitted && (
            <div className="mt-8 pl-2">
              <button 
                onClick={handleSubmit}
                disabled={Object.keys(userAnswers).length !== quiz.mcqs.length}
                className="bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-200 disabled:text-slate-400 text-white font-semibold py-3 px-8 rounded-xl transition-all text-sm shadow-sm"
              >
                Submit Answers
              </button>
              {Object.keys(userAnswers).length !== quiz.mcqs.length && (
                <span className="text-xs text-slate-500 ml-4 font-medium">Please answer all questions to submit.</span>
              )}
            </div>
          )}
        </div>
      )}

      {quiz.short_questions && quiz.short_questions.length > 0 && (
        <div className="bg-white border border-slate-200 rounded-2xl p-8 shadow-sm relative overflow-hidden">
          <div className="absolute left-0 top-0 bottom-0 w-1.5 bg-blue-500"></div>
          <h3 className="text-xl font-bold mb-6 text-slate-800 pl-2">Short Answer Questions</h3>
          <ul className="space-y-4 pl-2 text-slate-600 text-base">
            {quiz.short_questions.map((q, idx) => (
              <li key={idx} className="bg-slate-50 p-5 rounded-xl border border-slate-200 shadow-sm leading-relaxed flex flex-col md:flex-row md:items-start justify-between gap-4 group">
                <div className="flex gap-3">
                  <span className="text-slate-400 font-bold">{idx + 1}.</span>
                  <span className="text-slate-700 font-medium">{q}</span>
                </div>
                <button 
                  onClick={() => onAskBot(`Can you answer this short question from the quiz: ${q}`)}
                  className="shrink-0 flex items-center gap-1.5 bg-white border border-slate-200 hover:border-indigo-300 hover:bg-indigo-50 hover:text-indigo-600 text-slate-500 px-3 py-1.5 rounded-lg font-medium transition-all shadow-sm opacity-0 group-hover:opacity-100"
                >
                  <MessageSquare className="w-3.5 h-3.5" /> Ask AI
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}

      {quiz.long_questions && quiz.long_questions.length > 0 && (
        <div className="bg-white border border-slate-200 rounded-2xl p-8 shadow-sm relative overflow-hidden">
          <div className="absolute left-0 top-0 bottom-0 w-1.5 bg-purple-500"></div>
          <h3 className="text-xl font-bold mb-6 text-slate-800 pl-2">Long / Essay Questions</h3>
          <ul className="space-y-4 pl-2 text-slate-600 text-base">
            {quiz.long_questions.map((q, idx) => (
              <li key={idx} className="bg-slate-50 p-5 rounded-xl border border-slate-200 shadow-sm leading-relaxed flex flex-col md:flex-row md:items-start justify-between gap-4 group">
                <div className="flex gap-3">
                  <span className="text-slate-400 font-bold">{idx + 1}.</span>
                  <span className="text-slate-700 font-medium">{q}</span>
                </div>
                <button 
                  onClick={() => onAskBot(`Can you answer this long/essay question from the quiz: ${q}`)}
                  className="shrink-0 flex items-center gap-1.5 bg-white border border-slate-200 hover:border-purple-300 hover:bg-purple-50 hover:text-purple-600 text-slate-500 px-3 py-1.5 rounded-lg font-medium transition-all shadow-sm opacity-0 group-hover:opacity-100"
                >
                  <MessageSquare className="w-3.5 h-3.5" /> Ask AI
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function InterviewCard({ dataStr, onAskBot }) {
  if (!dataStr) return null;
  let interview = null;
  try {
    interview = JSON.parse(dataStr);
  } catch (e) {
    return <ContentCard title="Interview Questions" content={dataStr} />;
  }

  if (interview.error) return <ContentCard title="Interview Questions" content={interview.error} />;

  const levels = [
    { key: 'beginner', title: 'Beginner Level', color: 'bg-green-500', buttonHover: 'hover:text-green-600 hover:bg-green-50 hover:border-green-300' },
    { key: 'intermediate', title: 'Intermediate Level', color: 'bg-yellow-500', buttonHover: 'hover:text-yellow-600 hover:bg-yellow-50 hover:border-yellow-300' },
    { key: 'advanced', title: 'Advanced Level', color: 'bg-red-500', buttonHover: 'hover:text-red-600 hover:bg-red-50 hover:border-red-300' },
  ];

  return (
    <div className="space-y-6">
      {levels.map(({ key, title, color, buttonHover }) => {
        const questions = interview[key];
        if (!questions || questions.length === 0) return null;
        
        return (
          <div key={key} className="bg-white border border-slate-200 rounded-2xl p-8 shadow-sm relative overflow-hidden">
            <div className={`absolute left-0 top-0 bottom-0 w-1.5 ${color}`}></div>
            <h3 className="text-xl font-bold mb-6 text-slate-800 pl-2">{title}</h3>
            <ul className="space-y-4 pl-2 text-slate-600 text-base">
              {questions.map((q, idx) => (
                <li key={idx} className="bg-slate-50 p-5 rounded-xl border border-slate-200 shadow-sm leading-relaxed flex flex-col md:flex-row md:items-start justify-between gap-4 group">
                  <div className="flex gap-3">
                    <span className="text-slate-400 font-bold mt-0.5">•</span>
                    <span className="text-slate-700 font-medium">{q}</span>
                  </div>
                  <button 
                    onClick={() => onAskBot(`Can you help me answer this ${key} level interview question: ${q}`)}
                    className={`shrink-0 flex items-center gap-1.5 bg-white border border-slate-200 text-slate-500 px-3 py-1.5 rounded-lg font-medium transition-all shadow-sm opacity-0 group-hover:opacity-100 ${buttonHover}`}
                  >
                    <MessageSquare className="w-3.5 h-3.5" /> Ask AI
                  </button>
                </li>
              ))}
            </ul>
          </div>
        );
      })}
    </div>
  );
}
