
# Local LLM Chat Application

[Video Demo](https://youtu.be/ck39K0Dcbec)

## Project Description
Local LLM Chat Application adalah platform percakapan berbasis web yang memungkinkan pengguna berinteraksi dengan Large Language Model (LLM) secara **privat dan offline**. Proyek ini memanfaatkan **MLX** untuk mengoptimalkan performa model AI pada perangkat keras **Apple Silicon**.

Aplikasi ini juga menyediakan sistem manajemen pengguna lengkap, termasuk registrasi, autentikasi berbasis JWT, dan penyimpanan riwayat percakapan yang persisten menggunakan **MySQL**. Antarmuka pengguna menggunakan **Tailwind CSS** untuk pengalaman modern, responsif, dan mirip ChatGPT.

---

## Features
- **Local AI Inference**: Menggunakan model `Llama-3.2-3B-Instruct-4bit` dijalankan secara lokal melalui pustaka `mlx-lm`.
- **User Authentication**: Login dan registrasi aman dengan enkripsi password (`werkzeug.security`) dan manajemen sesi berbasis cookies JWT.
- **Persistent Chat History**: Setiap sesi percakapan disimpan di MySQL, memungkinkan pengguna melihat kembali riwayat chat.
- **Responsive UI**: Desain menggunakan Tailwind CSS dengan panel riwayat di sisi samping dan area chat utama.
- **Fully Offline Capability**: Setelah model diunduh, aplikasi dapat berjalan tanpa koneksi internet.

---

## File Structure
```
app.py            # Core Flask app: routing, autentikasi, database, chat processing
helpers.py        # Utility functions: model loading & text generation via MLX
download_model.py # Script untuk mengunduh bobot model dari Hugging Face
requirements.txt  # Daftar library Python yang dibutuhkan
schema_db.txt     # Skema SQL untuk membuat database & tabel
templates/        # Folder HTML templates
  ├─ layout.html  # Master template dengan Tailwind CSS & Alpine.js
  ├─ home.html    # Antarmuka chat utama
  ├─ login.html   # Halaman login
  └─ register.html# Halaman registrasi
```

---

## Design Choices
- **MLX over PyTorch**: Optimasi khusus untuk Unified Memory Architecture Apple Silicon, membuat model besar berjalan efisien di memori lokal.
- **JWT in Cookies**: Manajemen sesi aman dan stateless tanpa menyimpan data sesi di server.
- **MySQL Database**: Menyimpan data relasional pengguna dan percakapan secara terstruktur, lebih handal dibanding file teks.

---

## Prerequisites
- Perangkat **Apple Silicon** (M1, M2, M3, dst.)
- Python 3.9+
- MySQL Server aktif di sistem lokal

---

## Installation & Usage

### 1. Clone Repository
```bash
git clone <repository-url>
cd <project-folder>
```

### 2. Buat Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\\Scripts\\activate     # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Initialization
1. Buat database MySQL bernama `local_llm`.
2. Eksekusi SQL di `schema_db.txt` untuk membuat tabel `users`, `conversations`, dan `messages`.
3. Sesuaikan konfigurasi host, user, dan password di fungsi `get_db()` pada `app.py`.

### 5. Download Model
```bash
python download_model.py
```

### 6. Jalankan Aplikasi
```bash
python app.py
```

Akses aplikasi melalui browser di: `http://localhost:5000`

