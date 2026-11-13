# 🏥 AntriSehat — Sistem Manajemen Antrean & Janji Temu Faskes

> **Tugas Besar Komputasi Awan (Cloud Computing)** — Kelas IS-07-01 | **Kelompok 3 (K05)**

Sistem backend berbasis **REST API Cloud-Native** untuk mengelola antrean pasien dan reservasi janji temu di fasilitas kesehatan (klinik / puskesmas) secara tertib, otomatis, dan berurutan — dikemas penuh dalam container Docker dengan pipeline CI/CD otomatis via Jenkins dan Ngrok.

---

## 👥 Anggota Kelompok

| Nama | NIM |
| :--- | :--- |
| **Nanda Pratama Sugiarto** | 102062400019 |
| **Muhammad Haidar Mirza** | 102062400151 |
| **Veny Etika Dzakiyyah** | 102062400108 |
| **Kurnia Ragil Wulansari** | 102062400047 |

---

## 📌 Tentang Proyek

**AntriSehat** mengimplementasikan prinsip **Cloud-Native Architecture** dengan memisahkan service API, basis data, dan job scheduler ke dalam container terisolasi yang saling berkomunikasi melalui jaringan Docker internal. Sistem didukung pipeline CI/CD otomatis yang terpicu oleh setiap `git push` melalui **GitHub Webhook ↔ Ngrok ↔ Jenkins**.

### 🌟 Fitur Utama

| # | Fitur | Deskripsi |
| :--- | :--- | :--- |
| 1 | **Health Check** | Endpoint `/health` sebagai liveness probe untuk monitoring container |
| 2 | **Janji Temu** | Registrasi antrian dengan validasi batas kuota **30 pasien/poli/hari** |
| 3 | **Nomor Antrean** | Generator nomor antrean berurutan otomatis, reset setiap hari |
| 4 | **Daily Scheduler** | Background worker yang menandai antrean kadaluwarsa setiap hari |
| 5 | **CI/CD Otomatis** | Build → Test → Push → Deploy dipicu otomatis dari `git push` |

---

## 🛠️ Tech Stack

| Lapisan | Teknologi | Peran |
| :--- | :--- | :--- |
| **Backend API** | [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/) | Framework REST API asinkron, server ASGI |
| **Database** | [PostgreSQL 15 Alpine](https://www.postgresql.org/) | Penyimpanan data relasional persisten |
| **ORM / Driver** | [SQLAlchemy](https://www.sqlalchemy.org/) + `psycopg2-binary` | Object Relational Mapping & driver PostgreSQL |
| **Testing** | [Pytest](https://docs.pytest.org/) + [HTTPX](https://www.python-httpx.org/) | Unit test & HTTP integration test |
| **Container** | [Docker](https://www.docker.com/) (multi-stage build) | Packaging `base` → `deps` → `test` → `production` |
| **Orkestrasi** | [Docker Compose](https://docs.docker.com/compose/) | Manajemen service `app`, `scheduler`, `db`, `jenkins` |
| **CI/CD** | [Jenkins](https://www.jenkins.io/) LTS (port 8080) | Pipeline otomatis via Declarative Jenkinsfile |
| **Tunnel** | [Ngrok](https://ngrok.com/) (port 8080) | Webhook GitHub → Jenkins lokal via tunnel publik |
| **Konfigurasi** | `python-dotenv` + `.env` | Manajemen variabel lingkungan |

---

## 📂 Struktur File & Direktori

```text
AntriSehat_Kelompok3/
│
├── 📄 main.py               # Entrypoint FastAPI: definisi route API & validasi kuota
├── 📄 database.py           # Koneksi PostgreSQL, engine SQLAlchemy, & session get_db()
├── 📄 models.py             # Deklarasi model ORM: Doctor, Schedule, Queue, Appointment
├── 📄 scheduler.py          # Background worker: reset status antrean kadaluwarsa harian
├── 📄 test_main.py          # Automated testing (pytest + SQLite in-memory)
│
├── 🐳 Dockerfile            # Multi-stage build: base → deps → test → production
├── 🐳 compose.yaml          # Orkestrasi Docker: app, scheduler, db, jenkins (profile ci)
├── 📄 Jenkinsfile           # Declarative CI/CD Pipeline: Test→Build→Push→Deploy→SmokeTest
│
├── 📄 requirements.txt      # Daftar dependensi Python
├── 📄 .env                  # Konfigurasi lingkungan aktif (TIDAK di-commit ke Git)
├── 📄 .env.example          # Template variabel lingkungan untuk referensi
├── 📄 .gitignore            # Pola file yang dikecualikan dari Git
├── 📄 .gitattributes        # Konfigurasi EOL & atribut Git
│
├── 📄 start_ci_tunnel.sh    # Skrip otomatis: jalankan Jenkins + buka tunnel Ngrok :8080
└── 📄 README.md             # Dokumentasi proyek ini
```

### 🔍 Penjelasan Komponen Utama

**`main.py`** — Mendefinisikan tiga endpoint REST API:
- `GET  /health` — Liveness probe, selalu mengembalikan `{"status": "OK"}`.
- `POST /appointments?poli=<nama>` — Buat janji temu; menolak (HTTP 400) bila kuota ≥ 30.
- `POST /queues?poli=<nama>` — Ambil nomor antrean berurutan harian.

**`models.py`** — Skema database dengan empat tabel:
- `doctors` — Data dokter per poli.
- `schedules` — Jadwal praktik dokter & kuota maksimal.
- `queues` — Nomor antrean harian per poli (status: `waiting` / `expired`).
- `appointments` — Rekaman janji temu per poli per hari.

**`scheduler.py`** — Standalone worker yang menandai antrean dari hari sebelumnya menjadi `'expired'` dengan mekanisme retry otomatis (10x, interval 3 detik).

**`compose.yaml`** — Mendefinisikan empat service:
- `app` — FastAPI server di port `8000`, terhubung ke jaringan `frontend` dan `backend`.
- `scheduler` — Worker `python scheduler.py`, hanya di jaringan `backend`.
- `db` — PostgreSQL 15 dengan volume persisten `pg_data` dan healthcheck `pg_isready`.
- `jenkins` _(profile `ci`)_ — Jenkins LTS di port `8080` untuk CI/CD lokal.

---

## 🚀 Panduan Instalasi & Menjalankan Aplikasi

### ✅ Prasyarat

Pastikan software berikut sudah terpasang di sistem Anda:

| Software | Versi Minimum | Cek Versi |
| :--- | :--- | :--- |
| [Docker](https://docs.docker.com/get-docker/) | 24.x | `docker --version` |
| [Docker Compose](https://docs.docker.com/compose/install/) | v2.x | `docker compose version` |
| [Git](https://git-scm.com/) | — | `git --version` |
| Python 3.11+ *(opsional, untuk dev lokal)* | 3.11 | `python --version` |

---

### 🐳 Metode 1: Docker Compose dari Image Docker Hub *(Produksi — Direkomendasikan)*

Metode ini menarik image yang sudah dibangun dari Docker Hub — **tidak memerlukan source code lokal**.

#### Langkah-langkah:

**1. Clone repository dan masuk ke direktori proyek:**
```bash
git clone https://github.com/NandoBenrlitom/AntriSehat_Kelompok3.git
cd AntriSehat_Kelompok3
```

**2. Buat file `.env` dari template:**
```bash
cp .env.example .env
```

**3. Isi variabel di `.env`:**
```env
# Konfigurasi Database PostgreSQL
DB_HOST=db
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=ganti_dengan_password_aman
DB_NAME=antrisehat_db

# Username Docker Hub pemilik image
DOCKERHUB_USER=haidarmirza
```

> [!IMPORTANT]
> `DB_HOST=db` harus tetap `db` agar container `app` dapat menjangkau container database melalui jaringan Docker internal.

**4. Jalankan semua service:**
```bash
docker compose up -d
```

**5. Periksa status container:**
```bash
docker compose ps
```

Output yang diharapkan:
```
NAME                   STATUS          PORTS
antrisehat-app         Up (running)    0.0.0.0:8000->8000/tcp
antrisehat-db          Up (healthy)    5432/tcp
antrisehat-scheduler   Exited (0)      —
```

> [!NOTE]
> `antrisehat-scheduler` berstatus `Exited (0)` adalah **normal** — container ini menjalankan satu pekerjaan (reset antrean) lalu berhenti dengan sukses.

**6. Verifikasi aplikasi berjalan:**
```bash
curl http://localhost:8000/health
# Output: {"status":"OK"}
```

**7. Akses dokumentasi interaktif Swagger UI:**

Buka browser dan kunjungi: **[http://localhost:8000/docs](http://localhost:8000/docs)**

---

### 🔨 Metode 2: Build Lokal dari Source Code *(Development)*

Metode ini membangun image Docker langsung dari source code — cocok untuk pengembangan.

**1. Clone & masuk ke direktori:**
```bash
git clone https://github.com/NandoBenrlitom/AntriSehat_Kelompok3.git
cd AntriSehat_Kelompok3
```

**2. Siapkan file `.env`:**
```bash
cp .env.example .env
# Edit .env sesuai kebutuhan
```

**3. Build image dan jalankan:**
```bash
docker compose -f compose.yaml up --build -d
```

> [!NOTE]
> Perintah `--build` memaksa Docker membangun ulang image dari `Dockerfile` di direktori saat ini, mengabaikan image yang tersimpan di cache.

---

### 🐍 Metode 3: Development Lokal Tanpa Docker *(Tanpa Container)*

Gunakan metode ini untuk pengembangan cepat tanpa menjalankan container. Membutuhkan **PostgreSQL lokal** yang sudah berjalan.

**1. Clone & masuk ke direktori:**
```bash
git clone https://github.com/NandoBenrlitom/AntriSehat_Kelompok3.git
cd AntriSehat_Kelompok3
```

**2. Buat dan aktifkan virtual environment:**
```bash
# Linux / macOS
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

**3. Install dependensi:**
```bash
pip install -r requirements.txt
```

**4. Siapkan `.env` dengan konfigurasi database lokal:**
```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=password_lokal_anda
DB_NAME=antrisehat_db
DOCKERHUB_USER=haidarmirza
```

**5. Buat database PostgreSQL lokal (jika belum ada):**
```bash
psql -U postgres -c "CREATE DATABASE antrisehat_db;"
```

**6. Jalankan aplikasi:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**7. (Opsional) Jalankan scheduler secara manual:**
```bash
python scheduler.py
```

---

## 🔄 Menghentikan & Membersihkan Container

```bash
# Hentikan semua container (data tetap tersimpan)
docker compose down

# Hentikan dan hapus semua data volume (reset total)
docker compose down -v
```

---

## 🧪 Menjalankan Pengujian (Automated Testing)

Pengujian menggunakan **SQLite in-memory** sehingga **tidak memerlukan database aktif**.

### Pengujian di lingkungan lokal:
```bash
# Pastikan venv aktif
pytest -v
```

### Pengujian di dalam container Docker (identik dengan pipeline Jenkins):
```bash
# Build target 'test' dari Dockerfile
docker build --target test -t antrisehat:test .

# Jalankan pengujian dalam container
docker run --rm antrisehat:test
```

Output yang diharapkan:
```
test_main.py::test_health_check              PASSED  [ 33%]
test_main.py::test_appointment_quota_limit   PASSED  [ 66%]
test_main.py::test_get_queue_number          PASSED  [100%]

========================= 3 passed in X.XXs =========================
```

---

## 📡 Referensi Endpoint API

| Method | Endpoint | Query Param | Deskripsi |
| :---: | :--- | :--- | :--- |
| `GET` | `/health` | — | Health check liveness probe |
| `POST` | `/appointments` | `poli` *(string)* | Buat janji temu; maks 30/poli/hari |
| `POST` | `/queues` | `poli` *(string)* | Ambil nomor antrean berikutnya |

### Contoh Request & Response

**Health Check:**
```bash
curl http://localhost:8000/health
# → {"status":"OK"}
```

**Buat Janji Temu (berhasil):**
```bash
curl -X POST "http://localhost:8000/appointments?poli=Gigi"
# → {"message":"Janji temu berhasil dibuat","urutan":1}
```

**Buat Janji Temu (kuota penuh):**
```bash
# Setelah 30 request untuk poli yang sama:
curl -X POST "http://localhost:8000/appointments?poli=Gigi"
# → 400 {"detail":"Kuota dokter penuh (Maksimal 30 pasien/sesi)."}
```

**Ambil Nomor Antrean:**
```bash
curl -X POST "http://localhost:8000/queues?poli=Umum"
# → {"poli":"Umum","nomor_antrean":1}

curl -X POST "http://localhost:8000/queues?poli=Umum"
# → {"poli":"Umum","nomor_antrean":2}
```

---

## ⚙️ Alur Kerja Aplikasi

### Arsitektur Jaringan Container

```
  ┌──────────────────────────────────────────────────────────────────┐
  │                 Jaringan 'frontend' (publik)                     │
  │                                                                  │
  │   PORT 8000 ◄──┐    PORT 8080 ◄──┐                              │
  │                │                 │                              │
  │  ┌─────────────┴───┐  ┌──────────┴─────────┐                   │
  │  │  Container: app │  │ Container: jenkins  │  (profile: ci)    │
  │  │  FastAPI+Uvicorn│  │  Jenkins LTS        │                   │
  │  └────────┬────────┘  └────────────────────┘                   │
  └───────────┼──────────────────────────────────────────────────────┘
              │
  ┌───────────┼──────────────────────────────────────────────────────┐
  │           │       Jaringan 'backend' (internal)                  │
  │           │                                                      │
  │  ┌────────▼────────┐    ┌──────────────────────────────────┐    │
  │  │  Container: db  │    │   Container: scheduler           │    │
  │  │  PostgreSQL 15  │◄───│   python scheduler.py            │    │
  │  │  Volume: pg_data│    │   (reset antrean harian)         │    │
  │  └─────────────────┘    └──────────────────────────────────┘    │
  └──────────────────────────────────────────────────────────────────┘
```

### Alur Eksekusi Program

```
docker compose up
       │
       ▼
  [db] PostgreSQL 15 booting...
       │  healthcheck: pg_isready (interval 10s, retries 5)
       │
       ▼ (db: healthy)
  ┌────┴──────────────────────────┐
  │                               │
  ▼                               ▼
[app] FastAPI + Uvicorn      [scheduler] python scheduler.py
  │   port 8000                   │   retry 10x (interval 3s)
  │   create_all tabel            │   UPDATE queues status='expired'
  │   siap menerima request       │   lalu exit (0)
  │
  ▼
Klien ──► POST /appointments?poli=X
  │        SELECT COUNT(*) → n
  │        if n >= 30 → HTTP 400
  │        else INSERT → HTTP 200 urutan: n+1
  │
  └──► POST /queues?poli=X
         SELECT MAX(nomor_urut) → last
         INSERT nomor_urut = last + 1
         HTTP 200 nomor_antrean: last+1
```

---

## 🔄 Integrasi CI/CD (Jenkins + Ngrok)

### Alur Pipeline Otomatis

```
[ git push ke GitHub ]
         │
         ▼
[ GitHub Webhook ──► Ngrok Tunnel :8080 ──► Jenkins :8080 ]
         │
         ▼
   Stage: Checkout
         │  checkout scm (clone source code terbaru)
         ▼
   Stage: Test
         │  docker build --target test → pytest -v
         │  ✗ GAGAL → pipeline berhenti (fail-fast)
         ▼
   Stage: Build Image
         │  docker build -t haidarmirza/antrisehat:$BUILD_NUMBER
         ▼
   Stage: Push Image
         │  docker login → push ke Docker Hub
         ▼
   Stage: Deploy
         │  cp .env → docker compose pull → docker compose up -d
         ▼
   Stage: Smoke Test
         │  sleep 15 → curl /health → HTTP 200?
         ▼
   [SUCCESS] Pipeline selesai!
```

### Langkah Setup Jenkins + Ngrok

#### Prasyarat CI/CD:
- Container `jenkins-docker` sudah ada (image `jenkins/jenkins:lts`).
- Volume Docker `jenkins_home` sudah ada: `docker volume create jenkins_home`.
- Ngrok sudah terkonfigurasi dengan authtoken: `ngrok config add-authtoken <TOKEN>`.

#### 1. Jalankan Jenkins di Port 8080

```bash
# Jalankan otomatis dengan skrip bawaan:
./start_ci_tunnel.sh

# ATAU jalankan manual step-by-step:
docker start jenkins-docker          # nyalakan container Jenkins
docker compose --profile ci up -d    # atau via Docker Compose (profile ci)
```

Verifikasi Jenkins aktif: **[http://localhost:8080](http://localhost:8080)**

#### 2. Buka Tunnel Ngrok ke Port 8080

```bash
ngrok http 8080
```

Salin **Forwarding URL** HTTPS yang muncul, contoh:
```
Forwarding   https://abcd1234.ngrok-free.app → http://localhost:8080
```

#### 3. Daftarkan Webhook di GitHub

1. Buka repository GitHub → **Settings** → **Webhooks** → **Add webhook**
2. Isi form:
   - **Payload URL**: `https://abcd1234.ngrok-free.app/github-webhook/`
   - **Content type**: `application/json`
   - **Which events**: `Just the push event`
3. Klik **Add webhook** ✅

Sekarang setiap `git push` akan memicu build pipeline Jenkins secara otomatis!

#### 4. Konfigurasi Credentials di Jenkins

Masuk ke Jenkins → **Manage Jenkins** → **Credentials**, tambahkan:

| ID | Tipe | Isi |
| :--- | :--- | :--- |
| `dockerhub-credentials` | Username & Password | Akun Docker Hub |
| `antrisehat-env` | Secret File | File `.env` untuk deployment |

---

## 🗄️ Skema Database

```
doctors
├── id          INTEGER PK
├── nama        VARCHAR(100)
└── poli        VARCHAR(50)
         │
         │ One-to-Many
         ▼
schedules
├── id          INTEGER PK
├── doctor_id   INTEGER FK → doctors.id
├── hari        VARCHAR(20)   -- 'Senin', 'Selasa', dst.
├── jam_mulai   TIME
├── jam_selesai TIME
└── kuota_maks  INTEGER       -- default: 30
         │
         │ One-to-Many
         ▼
queues
├── id          INTEGER PK
├── poli        VARCHAR(50)
├── schedule_id INTEGER FK → schedules.id (nullable)
├── nama_pasien VARCHAR(100)
├── nomor_urut  INTEGER
├── tanggal     DATE          -- default: CURRENT_DATE
└── status      VARCHAR(20)   -- 'waiting' | 'expired'

appointments
├── id          INTEGER PK
├── poli        VARCHAR(50)
└── tanggal     DATE          -- default: CURRENT_DATE
```

---

## ❓ Pemecahan Masalah (Troubleshooting)

### Container `app` langsung berhenti (`Exited (1)`)

Periksa log untuk detail error:
```bash
docker compose logs app
```

Penyebab umum:
- **Database belum siap**: Tunggu hingga `antrisehat-db` berstatus `healthy`.
- **Konfigurasi `.env` salah**: Pastikan `DB_HOST=db` dan password sesuai.
- **Image belum ada**: Pastikan `DOCKERHUB_USER` di `.env` sudah benar.

### Port 8000 sudah dipakai proses lain

```bash
# Cek proses yang menggunakan port 8000
ss -tulpn | grep 8000

# Hentikan proses tersebut atau ganti port di compose.yaml:
# ports:
#   - "8001:8000"   ← host port diubah ke 8001
```

### Port 8080 (Jenkins) sudah dipakai

```bash
ss -tulpn | grep 8080
# Jika ada proses lain, hentikan atau ganti port Jenkins di compose.yaml
```

### Database tidak bisa diakses

```bash
# Cek log database
docker compose logs db

# Coba koneksi manual ke database
docker exec -it antrisehat-db psql -U postgres -d antrisehat_db -c "\dt"
```

---
