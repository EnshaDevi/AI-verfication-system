from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./verisense.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class ScanHistory(Base):
    __tablename__ = "scan_history"

    id = Column(Integer, primary_key=True, index=True)
    user = Column(String, default="System User")
    module = Column(String, index=True)
    input_data = Column(String)  # The text, url, or filename
    risk_score = Column(Integer)
    classification = Column(String)
    advice = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
