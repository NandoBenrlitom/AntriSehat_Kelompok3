from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import engine, Base, get_db

# Membuat tabel secara otomatis jika belum ada
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AntriSehat API K05")

# 1. Endpoint Wajib K05: Health Check
@app.get("/health")
def health_check():
    return {"status": "OK"}

# 2. Endpoint: Buat Janji Temu (Validasi Kuota Maksimal 30)
@app.post("/appointments")
def create_appointment(poli: str, db: Session = Depends(get_db)):
    # Simulasi penghitungan pasien pada hari ini untuk poli tersebut
    query = text("SELECT COUNT(*) FROM appointments WHERE poli = :poli AND tanggal = CURRENT_DATE")
    result = db.execute(query, {"poli": poli}).scalar()
    
    if result >= 30:
        raise HTTPException(status_code=400, detail="Kuota dokter penuh (Maksimal 30 pasien/sesi).")
    
    # Logika insert ke database diletakkan di sini
    return {"message": "Janji temu berhasil dibuat", "urutan": result + 1}

# 3. Endpoint: Ambil Nomor Antrean Berurutan
@app.post("/queues")
def get_queue_number(poli: str, db: Session = Depends(get_db)):
    # Simulasi pencarian nomor antrean terakhir hari ini
    query = text("SELECT COALESCE(MAX(nomor_urut), 0) FROM queues WHERE poli = :poli AND tanggal = CURRENT_DATE")
    last_queue = db.execute(query, {"poli": poli}).scalar()
    
    new_queue = last_queue + 1
    # Logika insert antrean baru diletakkan di sini
    return {"poli": poli, "nomor_antrean": new_queue}