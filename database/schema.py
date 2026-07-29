from datetime import datetime
from typing import List
from sqlalchemy import ForeignKey, String, Text, DateTime, Float, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Relationships
    videos: Mapped[List["Video"]] = relationship("Video", back_populates="user", cascade="all, delete-orphan")
    history: Mapped[List["History"]] = relationship("History", back_populates="user", cascade="all, delete-orphan")


class Video(Base):
    __tablename__ = "videos"
    
    video_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    duration: Mapped[float] = mapped_column(Float, nullable=True)
    upload_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="videos")
    summary: Mapped["Summary"] = relationship("Summary", back_populates="video", uselist=False, cascade="all, delete-orphan")
    frames: Mapped[List["Frame"]] = relationship("Frame", back_populates="video", cascade="all, delete-orphan")


class Summary(Base):
    __tablename__ = "summaries"
    
    summary_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    video_id: Mapped[int] = mapped_column(Integer, ForeignKey("videos.video_id", ondelete="CASCADE"), unique=True, nullable=False)
    short_summary: Mapped[str] = mapped_column(Text, nullable=True)
    detailed_summary: Mapped[str] = mapped_column(Text, nullable=True)
    topic_summary: Mapped[str] = mapped_column(Text, nullable=True)
    notes_important: Mapped[str] = mapped_column(Text, nullable=True)
    notes_revision: Mapped[str] = mapped_column(Text, nullable=True)
    notes_study: Mapped[str] = mapped_column(Text, nullable=True)
    keywords: Mapped[str] = mapped_column(Text, nullable=True)
    quiz: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string representing quiz questions
    interview_questions: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string representing interview questions
    transcript: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Relationships
    video: Mapped["Video"] = relationship("Video", back_populates="summary")


class Frame(Base):
    __tablename__ = "frames"
    
    frame_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    video_id: Mapped[int] = mapped_column(Integer, ForeignKey("videos.video_id", ondelete="CASCADE"), nullable=False)
    frame_path: Mapped[str] = mapped_column(String(500), nullable=False)
    timestamp: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Relationships
    video: Mapped["Video"] = relationship("Video", back_populates="frames")


class History(Base):
    __tablename__ = "history"
    
    history_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    activity: Mapped[str] = mapped_column(String(500), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="history")
