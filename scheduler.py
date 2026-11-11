import psycopg2
import os
import time
from dotenv import load_dotenv

load_dotenv()

def reset_daily_queues():
    print("Menjalankan Job Scheduler: Mereset antrean harian AntriSehat...")
    max_retries = 10
    for attempt in range(1, max_retries + 1):
        try:
            conn = psycopg2.connect(
                host=os.getenv("DB_HOST", "localhost"),
                database=os.getenv("DB_NAME", "antrisehat_db"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD", "rahasia")
            )
            cur = conn.cursor()
            
            # Logika reset: Hapus antrean yang lewat dari hari ini, atau ubah statusnya
            cur.execute("UPDATE queues SET status = 'expired' WHERE tanggal < CURRENT_DATE AND status = 'waiting'")
            conn.commit()
            
            cur.close()
            conn.close()
            print("Reset antrean selesai. Nomor urut esok hari akan kembali ke 1.")
            return
        except Exception as e:
            print(f"[Percobaan {attempt}/{max_retries}] Menunggu database/tabel siap: {e}")
            time.sleep(3)
    print("Gagal menjalankan scheduler setelah beberapa percobaan.")

if __name__ == "__main__":
    reset_daily_queues()
