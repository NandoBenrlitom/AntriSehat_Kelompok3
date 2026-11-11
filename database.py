import os
from sqlalchemy import create_engine, Column, Integer, String, Date, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# Format URL PostgreSQL: postgresql+psycopg2://user:password@host:port/dbname
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql+psycopg2://{os.getenv('DB_USER', 'postgres')}:{os.getenv('DB_PASSWORD', 'rahasia')}@{os.getenv('DB_HOST', 'localhost')}:5432/{os.getenv('DB_NAME', 'antrisehat_db')}"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    poli = Column(String, index=True)
    tanggal = Column(Date, server_default=text("CURRENT_DATE"))

class Queue(Base):
    __tablename__ = "queues"

    id = Column(Integer, primary_key=True, index=True)
    poli = Column(String, index=True)
    nomor_urut = Column(Integer)
    tanggal = Column(Date, server_default=text("CURRENT_DATE"))
    status = Column(String, default="waiting")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
