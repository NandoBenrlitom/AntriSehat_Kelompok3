from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String(100), nullable=False)
    poli = Column(String(50), nullable=False)

    # Relasi ke tabel schedules (One-to-Many)
    schedules = relationship("Schedule", back_populates="doctor")

class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    hari = Column(String(20), nullable=False) # Contoh: 'Senin', 'Selasa'
    jam_mulai = Column(Time, nullable=False)
    jam_selesai = Column(Time, nullable=False)
    kuota_maks = Column(Integer, default=30) # Wajib K05: Batas maksimal pasien

    # Relasi
    doctor = relationship("Doctor", back_populates="schedules")
    queues = relationship("Queue", back_populates="schedule")

class Queue(Base):
    __tablename__ = "queues"

    id = Column(Integer, primary_key=True, index=True)
    nama_pasien = Column(String(100), nullable=True, default="Pasien")
    poli = Column(String(50), nullable=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id"), nullable=True)
    tanggal = Column(Date, default=func.current_date(), nullable=False)
    nomor_urut = Column(Integer, nullable=False)
    status = Column(String(20), default="waiting") # waiting, called, expired (untuk scheduler)

    # Relasi
    schedule = relationship("Schedule", back_populates="queues")

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    poli = Column(String(50), nullable=False, index=True)
    tanggal = Column(Date, default=func.current_date(), nullable=False)


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    poli = Column(String(50), nullable=False, index=True)
    tanggal = Column(Date, default=func.current_date(), nullable=False)