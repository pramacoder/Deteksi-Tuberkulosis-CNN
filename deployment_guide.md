# Panduan Deployment: Opsi A (Split Deployment)

Panduan ini menjelaskan langkah demi langkah untuk men-deploy aplikasi **Deteksi Tuberkulosis (TB)** secara online menggunakan **Vercel (Frontend)** dan **Render / Hugging Face Spaces (Backend API)**.

---

## Struktur Folder Proyek saat ini
Backend dan Frontend Anda sudah kami siapkan agar bersifat mandiri (*self-contained*):
- **`tb_api/`**: API Backend Python (FastAPI). File model `best_BasicCNN_v2_fixed.keras` sudah disalin ke dalam [tb_api/model/](file:///C:/Users/Monk/Downloads/Deteksi%20Tuberkulosis%20(TB)/tb_api/model/) sehingga mandiri dan siap dideploy menggunakan `requirements.txt` dan `Dockerfile` yang telah dibuat.
- **`tb_frontend/`**: Website Frontend Next.js. Siap mendeteksi variabel `NEXT_PUBLIC_API_URL` ketika dideploy.

---

## LANGKAH 1: Push Kode ke GitHub

1. Buat repositori baru di GitHub (misalnya: `deteksi-tuberkulosis`).
2. Jalankan perintah berikut di terminal komputer lokal Anda (di folder utama `/Deteksi Tuberkulosis (TB)`):
   ```bash
   git init
   git add .
   git commit -m "Prepare codebase for deployment"
   git branch -M main
   git remote add origin https://github.com/USERNAME_ANDA/REPOS_ANDA.git
   git push -u origin main
   ```

---

## LANGKAH 2: Deploy Backend API (Python FastAPI)

Ada dua pilihan terbaik untuk backend AI: **Render** (mudah/praktis) atau **Hugging Face Spaces** (gratis dengan RAM besar 16GB, direkomendasikan untuk TensorFlow).

### Pilihan 2.1: Menggunakan Hugging Face Spaces (Direkomendasikan - GRATIS & RAM 16GB)
Karena TensorFlow cukup berat, Hugging Face menyediakan server gratis dengan RAM 16GB jika menggunakan Docker Space.

1. Buka [Hugging Face Spaces](https://huggingface.co/spaces) dan buat akun.
2. Klik **Create new Space**.
3. Isi detail Space:
   - **Space name**: `tb-detection-api`
   - **License**: `mit` (atau bebas)
   - **SDK**: Pilih **Docker** (jangan pilih Gradio/Streamlit).
   - **Docker template**: Pilih **Blank** (Kosong).
   - **Space visibility**: **Public** (agar frontend Next.js dapat mengaksesnya).
4. Klik **Create Space**.
5. Hugging Face akan memberikan repositori Git khusus untuk Space Anda. Anda tinggal meng-upload **seluruh isi folder `tb_api/`** (termasuk `Dockerfile`, `requirements.txt`, `main.py`, folder `model`, dll.) ke repositori Hugging Face tersebut:
   ```bash
   git clone https://huggingface.co/spaces/USERNAME_HF/tb-detection-api
   # Salin seluruh isi folder tb_api/ ke dalam folder clone tersebut
   # Lakukan commit dan push ke Hugging Face:
   git add .
   git commit -m "Deploy FastAPI TB API to Space"
   git push
   ```
6. Setelah proses build selesai (hijau/Running), URL API Anda akan menjadi:
   `https://USERNAME_HF-tb-detection-api.hf.space`

---

### Pilihan 2.2: Menggunakan Render (Praktis, Terintegrasi GitHub)
1. Masuk ke [Render.com](https://render.com/) menggunakan akun GitHub Anda.
2. Klik **New** > **Web Service**.
3. Sambungkan repositori GitHub proyek Anda (`deteksi-tuberkulosis`).
4. Isi konfigurasi berikut:
   - **Name**: `tb-detection-api`
   - **Region**: Pilih terdekat (misal: Singapore)
   - **Branch**: `main`
   - **Root Directory**: Isi dengan `tb_api`
   - **Runtime**: Pilih **Docker** (Render akan otomatis mendeteksi file `Dockerfile` yang telah kita siapkan).
   - **Instance Type**: Pilih **Starter** (RAM 2GB, ~$7/bulan) karena TensorFlow membutuhkan minimal 1GB+ RAM yang melebihi batas Free Tier Render (512MB RAM).
5. Klik **Create Web Service**. Setelah proses deploy selesai, Render akan memberikan URL seperti:
   `https://tb-detection-api.onrender.com`

---

## LANGKAH 3: Deploy Frontend (Next.js) ke Vercel

1. Buka [Vercel.com](https://vercel.com/) dan masuk menggunakan akun GitHub Anda.
2. Klik **Add New** > **Project**.
3. Import repositori GitHub proyek Anda (`deteksi-tuberkulosis`).
4. Pada halaman konfigurasi project:
   - **Framework Preset**: Pilih **Next.js**.
   - **Root Directory**: Klik **Edit** dan pilih folder `tb_frontend`.
   - **Environment Variables**:
     - Tambahkan key: `NEXT_PUBLIC_API_URL`
     - Value: Masukkan URL Backend API Anda dari langkah sebelumnya (misal: `https://USERNAME_HF-tb-detection-api.hf.space` atau `https://tb-detection-api.onrender.com`).
     - *Catatan:* Jangan tambahkan tanda garis miring `/` di bagian paling akhir URL.
5. Klik **Deploy**.
6. Selesai! Vercel akan memberikan domain gratis (misal: `https://deteksi-tuberkulosis.vercel.app`) yang siap diakses secara publik.

---

## Tips & Troubleshooting
* **Cold Start (Render Free Tier):** Jika menggunakan Render Free tier (jika lolos batas RAM), layanan akan masuk ke mode tidur (*sleep*) jika tidak ada trafik selama 15 menit. Request pertama setelah tidur akan membutuhkan waktu sekitar 50-60 detik untuk memuat ulang model AI.
* **CORS Error:** Backend kami konfigurasi secara universal (`allow_origins=["*"]`) untuk menghindari error CORS. Jika Anda ingin mengamankannya di masa depan, ubah baris tersebut di `tb_api/main.py` menjadi alamat web Vercel Anda.
