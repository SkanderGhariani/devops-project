from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from datetime import date
from typing import List, Optional
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Gauge

# Database setup
DATABASE_URL = "sqlite:///./poker_sessions.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
# Custom metrics
user_count = Gauge('user_count', 'Total number of users')
session_count = Gauge('session_count', 'Total number of poker sessions')

# SQLAlchemy models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    sessions = relationship("PokerSession", back_populates="owner")

    @property
    def total_profit(self):
        return sum(session.profit for session in self.sessions)

class PokerSession(Base):
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    session_date = Column(Date)
    buy_in = Column(Float)
    winnings = Column(Float)

    owner = relationship("User", back_populates="sessions")

    @property
    def profit(self):
        return self.winnings - self.buy_in

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# Pydantic schemas
class UserCreate(BaseModel):
    username: str

class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True

class SessionCreate(BaseModel):
    user_id: int
    session_date: date
    buy_in: float
    winnings: float

class SessionResponse(BaseModel):
    id: int
    user_id: int
    session_date: date
    buy_in: float
    winnings: float
    profit: float

    class Config:
        orm_mode = True

# FastAPI app
app = FastAPI()
Instrumentator().instrument(app).expose(app)

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(username=user.username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    user_count.inc()  # Increment user count
    return db_user

@app.post("/sessions/", response_model=SessionResponse)
async def create_session(session: SessionCreate, db: Session = Depends(get_db)):
    db_session = PokerSession(**session.dict())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    session_count.inc()  # Increment session count
    return db_session

# Read all sessions for a user with optional date range filter
@app.get("/users/{user_id}/sessions/", response_model=List[SessionResponse])
async def read_user_sessions(user_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    query = db.query(PokerSession).filter(PokerSession.user_id == user_id)
    if start_date:
        query = query.filter(PokerSession.session_date >= start_date)
    if end_date:
        query = query.filter(PokerSession.session_date <= end_date)
    sessions = query.offset(skip).limit(limit).all()
    return sessions

# Read a specific session for a user
@app.get("/users/{user_id}/sessions/{session_id}", response_model=SessionResponse)
async def read_session(user_id: int, session_id: int, db: Session = Depends(get_db)):
    session = db.query(PokerSession).filter(PokerSession.id == session_id, PokerSession.user_id == user_id).first()
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found or does not belong to the user")
    return session

# Update a specific session for a user
@app.put("/users/{user_id}/sessions/{session_id}", response_model=SessionResponse)
async def update_session(user_id: int, session_id: int, session: SessionCreate, db: Session = Depends(get_db)):
    db_session = db.query(PokerSession).filter(PokerSession.id == session_id, PokerSession.user_id == user_id).first()
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found or does not belong to the user")
    
    for key, value in session.dict().items():
        setattr(db_session, key, value)
    
    db.commit()
    db.refresh(db_session)
    return db_session

# Delete a specific session for a user
@app.delete("/users/{user_id}/sessions/{session_id}")
async def delete_session(user_id: int, session_id: int, db: Session = Depends(get_db)):
    db_session = db.query(PokerSession).filter(PokerSession.id == session_id, PokerSession.user_id == user_id).first()
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found or does not belong to the user")
    
    db.delete(db_session)
    db.commit()
    return {"detail": "Session deleted"}
