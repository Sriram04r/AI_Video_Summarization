# 🧠 AI Video Summarization & Study Notes Generator

A full-stack AI application that transforms any educational video or lecture into comprehensive study materials. Built with React, FastAPI, and powered by Groq's lightning-fast AI inference.

## ✨ Features

- **Upload Local Videos**: Process educational MP4 videos directly from your device.
- **Smart Summarization**: Automatically generates structured summaries, bullet points, and key takeaways.
- **Study Notes & Quizzes**: Automatically creates detailed study notes, practice quizzes, and interview prep questions based on the video content.
- **Visual Keyframes**: Uses OpenCV to detect scene changes and extract important presentation slides or visual keyframes from the video.
- **PDF Export**: Download your AI-generated study materials as a clean, formatted PDF report.
- **Modern UI**: Built with React, TailwindCSS, and Lucide Icons for a beautiful, responsive, and glassmorphic user experience.

## 🚀 Technology Stack

**Frontend:**
- React (Vite)
- Tailwind CSS
- React Router
- Axios for API communication

**Backend:**
- Python (FastAPI)
- SQLite & SQLAlchemy (Database)
- Whisper (Local Speech-to-Text)
- OpenCV (Keyframe Extraction)

**AI & Cloud:**
- **Groq API**: For ultra-fast LLaMA 3 based text generation and summarization.
- **Render**: Backend deployment and hosting.
- **Vercel**: Frontend deployment and hosting.

## 💻 How to Run Locally

If you want to run this project on your own machine (which completely bypasses YouTube's bot detection for processing YouTube links!):

### 1. Clone the repository
```bash
git clone https://github.com/Sriram04r/AI_Video_Summarization.git
cd AI_Video_Summarization
```

### 2. Setup the Backend
```bash
# Create a virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create a .env file and add your Groq API Key
echo GROQ_API_KEY=your_api_key_here > .env

# Run the backend server
uvicorn main:app --reload --port 8000
```

### 3. Setup the Frontend
```bash
cd frontend

# Install dependencies
npm install

# Run the frontend development server
npm run dev
```

## 🔒 A Note on Cloud Deployments and YouTube Links
Because this demo is hosted on a free cloud provider (Render), YouTube's anti-bot system blocks the cloud server's IP address (Error 429: Too Many Requests). For the live cloud demo, please stick to **Local File Uploads**. 

To use the YouTube link feature flawlessly, simply run the application locally on your own computer!