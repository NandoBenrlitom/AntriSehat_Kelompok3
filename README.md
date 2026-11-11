# AntriSehat - Sistem Manajemen Antrean & Janji Temu Faskes

Tugas Besar Komputasi Awan (Cloud Computing) — Kelas IS-07-01  
**Kelompok 3 (K05)**

### 👥 Anggota Kelompok
* **Nanda Pratama Sugiarto** (10206240019)
* **Muhammad Haidar Mirza** (102062400151)
* **Veny Etika Dzakiyyah** (102062400108)
* **Kurnia Ragil Wulansari** (102062400047)

---

## 📌 Tentang Proyek

**AntriSehat** adalah sistem backend berbasis RESTful API dan Cloud Native Architecture yang dirancang untuk mengelola antrean pasien dan reservasi janji temu poli kesehatan (klinik/puskesmas) secara tertib, otomatis, dan berurutan.

Sistem ini dirancang dengan prinsip **Cloud Computing**, memisahkan service API, basis data, dan penjadwal tugas (*job scheduler*) ke dalam container terisolasi, didukung pipeline CI/CD otomatis (*Continuous Integration & Continuous Deployment*) menggunakan Jenkins.

### 🌟 Fitur Utama
1. **Health Check Monitoring (`/health`)**: Endpoint pemeriksaan ketersediaan server untuk pemantauan container (*liveness/readiness probe*) dan *smoke testing*.
2. **Reservasi Janji Temu (`/appointments`)**: Pendaftaran janji temu pasien dengan validasi pembatasan kuota maksimal 30 pasien per poli per hari.
3. **Penomoran Antrean Berurutan (`/queues`)**: Generator nomor antrean otomatis dan berurutan secara harian per poli.
4. **Daily Queue Scheduler (`scheduler.py`)**: Layanan pembersih harian otomatis untuk memperbarui status antrean kedaluwarsa (*expired*) dan mereset giliran antrean di hari berikutnya.
5. **Containerized Multi-Stage & CI/CD**: Pengujian otomatis dan *deployment* nirhenti menggunakan Docker multi-stage build dan Jenkins Pipeline.

---

## 🛠️ Tech Stack & Ekosistem

| Komponen | Teknologi | Deskripsi / Peran |
| :--- | :--- | :--- |
| **Backend Framework** | [FastAPI](https://fastapi.tiangolo.com/) | Framework API asinkron Python dengan performa tinggi & dokumentasi interaktif OpenAPI/Swagger |
| **ASGI Server** | [Uvicorn](https://www.uvicorn.org/) | Server HTTP asinkron untuk menjalankan aplikasi FastAPI |
| **Database** | [PostgreSQL 15 (Alpine)](https://www.postgresql.org/) | RDBMS utama untuk penyimpanan relasional data antrean dan janji temu |
| **ORM & Driver** | [SQLAlchemy](https://www.sqlalchemy.org/) & `psycopg2-binary` | Object Relational Mapping dan driver database PostgreSQL |
| **Testing** | [Pytest](https://docs.pytest.org/) & [HTTPX](https://www.python-httpx.org/) | Automated unit testing & HTTP client testing (`TestClient`) |
| **Containerization** | [Docker](https://www.docker.com/) | Multi-stage packaging container (`base`, `deps`, `test`, `production`) |
| **Orchestration** | [Docker Compose](https://docs.docker.com/compose/) | Manajemen multi-container (`app`, `scheduler`, `db`) dan isolasi network |
| **CI/CD Pipeline** | [Jenkins](https://www.jenkins.io/) | Automasi pengujian (*test*), perakitan (*build*), publikasi ke Docker Hub, dan *smoke test* |
| **Konfigurasi** | `python-dotenv` | Manajemen variabel lingkungan melalui berkas `.env` |

---

## 📂 Struktur File & Direktori

```text
AntriSehat_Kelompok3/
├── .env                  # Konfigurasi environment variables (database credentials, host, image user)
├── .gitattributes        # Konfigurasi penanganan EOL & atribut Git
├── compose.yaml          # Orkestrasi multi-container Docker Compose (app, scheduler, db, network)
├── Dockerfile            # Multi-stage Docker build: base -> deps -> test -> production
├── Jenkinsfile           # Skrip declarative pipeline CI/CD Jenkins
├── requirements.txt      # Daftar dependensi pustaka Python
├── main.py               # Entrypoint aplikasi FastAPI (definisi route API dan validasi kuota)
├── database.py           # Inisialisasi koneksi database PostgreSQL & sesi SQLAlchemy
├── scheduler.py          # Background worker/cron job untuk reset & pembaruan status antrean harian
├── test_main.py          # Skrip pengujian otomatis unit & integrasi API menggunakan Pytest
└── README.md             # Dokumentasi teknis proyek
```

### 🔍 Penjelasan Komponen File:
* **`main.py`**: Mendefinisikan endpoint REST API:
  * `GET /health`: Cek kesehatan aplikasi.
  * `POST /appointments`: Pembuatan janji temu baru dengan validasi batas kuota 30 pasien.
  * `POST /queues`: Pengambilan nomor antrean berurutan secara harian per poli.
* **`database.py`**: Menangani konfigurasi *connection string* ke PostgreSQL, pembuatan engine `SessionLocal`, serta dependency injection `get_db()`.
* **`scheduler.py`**: Script mandiri (*standalone worker*) yang bertugas menandai antrean dari hari sebelumnya yang masih menggantung (*status = 'waiting'*) menjadi *'expired'*.
* **`compose.yaml`**: Mendefinisikan 3 layanan:
  * `app`: Menjalankan REST API FastAPI pada port 8000 (terhubung ke network `frontend` dan `backend`).
  * `scheduler`: Menjalankan background worker `python scheduler.py` (terhubung ke network `backend`).
  * `db`: PostgreSQL 15 dengan persistensi volume `pg_data` dan healthcheck `pg_isready` (terisolasi pada network `backend` internal).
* **`Dockerfile`**: Menggunakan teknik *multi-stage build*:
  * Target `test`: Menjalankan `pytest -v` untuk verifikasi build pada pipeline CI/CD.
  * Target `production`: Menjalankan server aplikasi production dengan `uvicorn`.
* **`Jenkinsfile`**: Mengatur tahapan CI/CD: *Checkout* ➔ *Test* ➔ *Build Image* ➔ *Push Image ke Docker Hub* ➔ *Deploy via Compose* ➔ *Smoke Test* (`/health`).
* **`test_main.py`**: Berisi automated tests untuk memastikan endpoint `/health` merespons `200 OK` dan pembatasan kuota janji temu (maksimal 30) menolak request ke-31 dengan kode status `400 Bad Request`.

---

## ⚙️ Langkah Kerja & Alur Jalannya Program

### 1. Arsitektur Jaringan & Layanan
```
  [ Klien / Pasien / Frontend ]
               │
               ▼ (Port 8000)
    ┌───────────────────── Jaringan 'frontend' ─────────────────────┐
    │                                                               │
    │   ┌───────────────────────────────────────────────────────┐   │
    │   │                  Container 'app'                      │   │
    │   │            (FastAPI + Uvicorn Server)                 │   │
    │   └──────────────────────────┬────────────────────────────┘   │
    └──────────────────────────────┼────────────────────────────────┘
                                   │
    ┌────────────────────── Jaringan 'backend' (Internal) ──────────┐
    │                              │                                │
    │                              ▼                                │
    │   ┌───────────────────────────────────────────────────────┐   │
    │   │                  Container 'db'                       │   │
    │   │               (PostgreSQL 15 Engine)                  │   │
    │   │                  Volume: pg_data                      │   │
    │   └──────────────────────────▲────────────────────────────┘   │
    │                              │                                │
    │   ┌──────────────────────────┴────────────────────────────┐   │
    │   │               Container 'scheduler'                   │   │
    │   │               (Daily Reset Worker)                    │   │
    │   └───────────────────────────────────────────────────────┘   │
    └───────────────────────────────────────────────────────────────┘
```

### 2. Alur Eksekusi Program (End-to-End Lifecycle)

1. **Inisialisasi Container & Database**:
   * Saat `docker compose up` dijalankan, container `db` menyala terlebih dahulu.
   * Container `app` dan `scheduler` menunggu hingga pemeriksaan *healthcheck* PostgreSQL (`pg_isready`) berstatus *healthy*.
   * Pada saat `app` dimuat, SQLAlchemy mengeksekusi `Base.metadata.create_all(bind=engine)` untuk memastikan tabel data siap digunakan.

2. **Alur Pembuatan Janji Temu (`POST /appointments`)**:
   * Klien mengirim request parameter nama poli: `POST /appointments?poli=Gigi`.
   * Sistem menghitung jumlah janji temu yang tercatat untuk poli terkait pada hari ini (`tanggal = CURRENT_DATE`).
   * **Validasi Kuota**: Jika jumlah janji temu sudah $\ge 30$, sistem langsung melempar exception `HTTP 400: Kuota dokter penuh (Maksimal 30 pasien/sesi)`.
   * Jika kuota masih tersedia, sistem mengonfirmasi dan mengembalikan nomor urutan janji temu.

3. **Alur Pengambilan Nomor Antrean (`POST /queues`)**:
   * Klien meminta nomor antrean harian: `POST /queues?poli=Umum`.
   * Sistem memeriksa nomor antrean paling akhir pada hari ini: `SELECT COALESCE(MAX(nomor_urut), 0)`.
   * Sistem menambahkan nomor baru (`last_queue + 1`) sehingga antrean selalu berurutan mulai dari nomor 1 setiap harinya.

4. **Alur Penjadwalan Pembersihan (`scheduler.py`)**:
   * Scheduler berjalan di latar belakang untuk melakukan pembersihan berkala (*maintenance job*).
   * Menjalankan query pembaruan status:
     ```sql
     UPDATE queues SET status = 'expired' WHERE tanggal < CURRENT_DATE AND status = 'waiting'
     ```
   * Memastikan nomor antrean untuk tanggal baru direset kembali ke 1 dan data lama diarsipkan dengan status kedaluwarsa.

5. **Siklus Otomasi CI/CD (Jenkins)**:
   * **Trigger**: Pipeline terpicu oleh commit baru atau cron terjadwal (`cron('H 1 * * *')`).
   * **Stage Test**: Jenkins merakit target `test` dari Dockerfile dan menjalankan `pytest -v`. Bila pengujian gagal, pipeline langsung berhenti (*fail-fast*).
   * **Stage Build & Push**: Image versi production dirakit dan diberi tag `${BUILD_NUMBER}` serta `latest`, lalu diunggah ke Docker Hub.
   * **Stage Deploy**: Lingkungan produksi melakukan `docker compose pull` dan me-restart container dengan versi terbaru.
   * **Stage Smoke Test**: Menjalankan pengujian akhir dengan memanggil `curl -fsS http://localhost:8000/health` untuk memastikan server aktif tanpa gangguan.

---

## 🚀 Panduan Instalasi & Menjalankan Aplikasi

### Prasyarat Sistem
* [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/)
* [Python 3.11+](https://www.python.org/) *(opsional, jika ingin menjalankan secara lokal tanpa Docker)*
* [Git](https://git-scm.com/)

---

### Metode 1: Menggunakan Docker Compose (Direkomendasikan)

1. **Clone Repository & Masuk ke Direktori Proyek**:
   ```bash
   git clone https://github.com/NandoBenrlitom/AntriSehat_Kelompok3
   cd AntriSehat_Kelompok3
   ```

2. **Konfigurasi Environment Variables**:
   Pastikan file `.env` sudah ada dan terkonfigurasi dengan benar:
   ```env
   DB_HOST=db
   DB_USER=postgres
   DB_PASSWORD=rahasia_sehat_123
   DB_NAME=antrisehat_db
   DOCKERHUB_USER=haidarmirza
   ```

3. **Build dan Jalankan Container**:
   ```bash
   docker compose up --build -d
   ```

4. **Periksa Status Layanan**:
   ```bash
   docker compose ps
   ```

5. **Akses Layanan**:
   * **API Base URL**: `http://localhost:8000`
   * **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)
   * **Dokumentasi Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
   * **Dokumentasi ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

6. **Menghentikan Layanan**:
   ```bash
   docker compose down
   ```

---

### Metode 2: Menjalankan Secara Lokal (Local Development)

1. **Buat & Aktifkan Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Di Linux/macOS
   # venv\Scripts\activate   # Di Windows
   ```

2. **Instal Dependensi**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Pastikan PostgreSQL Lokal Berjalan**:
   Sesuaikan parameter `DB_HOST=localhost` di berkas `.env`.

4. **Jalankan Aplikasi Web**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Jalankan Scheduler Secara Manual**:
   ```bash
   python scheduler.py
   ```

---

## 🧪 Menjalankan Pengujian (Automated Testing)

### Pengujian Lokal
Untuk menjalankan skrip pengujian unit dan verifikasi batas kuota menggunakan Pytest:
```bash
pytest -v
```

### Pengujian Berbasis Docker (Identik dengan Pipeline CI)
Untuk menguji di lingkungan container persis seperti yang dijalankan Jenkins:
```bash
docker build --target test -t antrisehat:test .
```

---

## 📡 Dokumentasi Endpoint API

| Method | Endpoint | Query Param | Respons Berhasil (200) | Respons Gagal (400) |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/health` | - | `{"status": "OK"}` | - |
| `POST` | `/appointments` | `poli` (string) | `{"message": "Janji temu berhasil dibuat", "urutan": 1}` | `{"detail": "Kuota dokter penuh (Maksimal 30 pasien/sesi)."}` |
| `POST` | `/queues` | `poli` (string) | `{"poli": "Gigi", "nomor_antrean": 1}` | - |

---

## 🔄 Integrasi CI/CD (Jenkins & Ngrok Port 8080)

Pipeline otomatisasi didefinisikan pada file `Jenkinsfile` dengan alur:

```
[ Git Push / GitHub Webhook (via Ngrok :8080) ] 
        ▼
   Stage: Checkout     ──▶ Mengambil source code terbaru dari branch SCM
        ▼
   Stage: Test         ──▶ Menjalankan Dockerfile target 'test' (pytest)
        ▼
   Stage: Build Image  ──▶ Merakit Docker image versi production
        ▼
   Stage: Push Image   ──▶ Login & Push image ke Docker Hub repository
        ▼
   Stage: Deploy       ──▶ Menyiapkan file .env dan memperbarui Docker Compose
        ▼
   Stage: Smoke Test   ──▶ Memvalidasi endpoint /health aktif via curl
```

### 🌐 Menjalankan Jenkins & Tunnel Ngrok pada Port 8080

1. **Jalankan Jenkins di Port 8080**:
   ```bash
   # Opsi A: Jalankan container existing
   docker start jenkins-docker

   # Opsi B: Jalankan via profil Docker Compose
   docker compose --profile ci up -d jenkins
   ```

2. **Jalankan Tunnel Ngrok untuk Meneruskan Port 8080**:
   ```bash
   ngrok http 8080
   ```
   *(Atau jalankan skrip praktis: `./start_ci_tunnel.sh`)*

3. **Konfigurasi Webhook di GitHub Repository**:
   * Buka **Settings** ➔ **Webhooks** ➔ **Add webhook**
   * **Payload URL**: `https://<SUBDOMAIN_NGROK>.ngrok-free.app/github-webhook/`
   * **Content type**: `application/json`
   * **Which events would you like to trigger this webhook?**: Pilih `Just the push event.`
   * Klik **Add webhook**. Setiap `git push` akan otomatis memicu build pipeline di Jenkins!

