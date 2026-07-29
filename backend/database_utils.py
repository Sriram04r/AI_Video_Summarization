import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from database.schema import Base

# Determine Database URL. Default to local SQLite database in database/ folder.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database/db.sqlite")

# SQLite specific argument (only needed for SQLite)
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, connect_args=connect_args)

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize the database and create tables if they don't exist."""
    # Ensure the parent directory for SQLite database exists
    if DATABASE_URL.startswith("sqlite"):
        db_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database")
        os.makedirs(db_dir, exist_ok=True)
    
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency for getting a database session in FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
