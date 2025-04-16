# StopJudol - JSON-RPC Edition

![StopJudol Logo](assets/icons/app_icon.ico)

## Tentang Aplikasi

StopJudol adalah aplikasi yang dirancang untuk membantu kreator konten YouTube mengidentifikasi dan menghapus secara otomatis komentar spam, iklan judi online (judol), dan konten ilegal lainnya dari video mereka. Versi ini menggunakan arsitektur client-server dengan JSON-RPC untuk komunikasi, memungkinkan skalabilitas yang lebih baik dan pemisahan tanggung jawab.

## Arsitektur

Aplikasi ini dibagi menjadi tiga komponen utama:

1. **Client**: Aplikasi GUI berbasis PyQt6 yang menangani interaksi pengguna dan menampilkan hasil.
2. **Server**: Server JSON-RPC yang menangani interaksi dengan YouTube API dan analisis komentar.
3. **Shared**: Kode dan utilitas yang digunakan bersama oleh client dan server.

```
+----------------+        JSON-RPC        +----------------+         +----------------+
|                |<--------------------->|                |<------->|                |
|  Client (GUI)  |        HTTP/HTTPS     |  RPC Server    |   API   |  YouTube API   |
|                |<--------------------->|                |<------->|                |
+----------------+                       +----------------+         +----------------+
```

Untuk informasi arsitektur yang lebih detail, lihat [Dokumentasi Arsitektur](docs/architecture.md).

## Dokumentasi

Dokumentasi komprehensif tersedia untuk membantu Anda memahami sistem:

- [Arsitektur](docs/architecture.md) - Penjelasan detail tentang arsitektur sistem
- [Referensi API](docs/api_reference.md) - Dokumentasi lengkap API JSON-RPC
- [Struktur Proyek](docs/project_structure.md) - Panduan organisasi kode
- [Alur Kerja](docs/workflow.md) - Penjelasan detail alur kerja utama
- [Briefing Laporan](docs/briefing-buat-laporan.md) - Panduan untuk menyusun laporan proyek

## Fitur

- **Otentikasi Aman**: Login melalui Google/YouTube OAuth 2.0 dan JWT untuk komunikasi client-server
- **Pemindaian Komentar**: Analisis komentar dari video YouTube manapun menggunakan URL video
- **Deteksi Cerdas**: Identifikasi konten spam dan perjudian menggunakan pola regex dan pencocokan kata kunci
- **Sistem Peninjauan**: Tinjau komentar yang ditandai sebelum penghapusan
- **Penghapusan Massal**: Hapus beberapa komentar sekaligus dengan dukungan untuk berbagai metode penghapusan
- **Pengaturan yang Dapat Disesuaikan**: Konfigurasi kata kunci blacklist dan whitelist
- **Arsitektur Client-Server**: Pemisahan UI dari logika bisnis untuk skalabilitas yang lebih baik

## Persyaratan

### Persyaratan Server
- Python 3.8 atau lebih baru
- Google API Client Library untuk Python
- Akses ke YouTube Data API v3
- Library JSON-RPC Server (jsonrpcserver, aiohttp)
- Variabel lingkungan atau file .env untuk konfigurasi

### Persyaratan Client
- Python 3.8 atau lebih baru
- PyQt6
- Library JSON-RPC Client (jsonrpcclient)
- Library Google OAuth untuk autentikasi

## Instalasi dan Pengaturan

### Instalasi dari Source

1. Clone repository:
   ```
   git clone https://github.com/gerrymoeis/StopJudol-RPC.git
   cd StopJudol-RPC
   ```

2. Buat dan aktifkan virtual environment:
   ```
   python -m venv venv
   # Di Windows
   venv\Scripts\activate
   # Di Linux/Mac
   # source venv/bin/activate
   ```

3. Instal dependensi:
   ```
   # Dependensi Server
   pip install jsonrpcserver aiohttp python-dotenv marshmallow pyjwt
   
   # Dependensi Client
   pip install PyQt6 jsonrpcclient requests
   
   # Dependensi Umum
   pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
   
   # Untuk Build
   pip install pyinstaller
   ```

### Konfigurasi

1. Buat file `.env` di folder `stopjudol`:
   ```
   # API Authentication
   API_USERNAME=admin
   API_PASSWORD=password

   # JWT Authentication
   JWT_SECRET_KEY=StopJudol_Secret_Key_Change_This_In_Production
   JWT_ALGORITHM=HS256
   JWT_EXPIRE_HOURS=24

   # Server Configuration
   SERVER_HOST=0.0.0.0
   SERVER_PORT=5000

   # YouTube API
   YOUTUBE_API_KEY=your_api_key_here

   # Logging
   LOG_LEVEL=INFO
   ```

2. Dapatkan kredensial OAuth dari Google Cloud Console dan simpan sebagai `client_secret.json` di folder `server/config`.

## Menjalankan Aplikasi

### Menjalankan Server

```
cd stopjudol
python run_server.py
```

### Menjalankan Client

```
cd stopjudol
python run_client.py
```

## Build Executable

### Build Server

```
cd stopjudol
python build_server.py
```

### Build Client

```
cd stopjudol
python build_client.py
```

Executable akan dibuat di folder `dist`.

## Perbaikan Bug Terbaru

1. **Penanganan Komentar**:
   - Perbaikan pada penghapusan komentar dengan menggunakan ID komentar yang benar
   - Implementasi metode alternatif untuk menandai komentar sebagai spam jika penghapusan langsung tidak berhasil
   - Dukungan untuk moderasi komentar pada video yang dimiliki oleh pengguna yang terautentikasi

2. **Implementasi JSON-RPC**:
   - Perbaikan masalah import path di server dan client
   - Pembaruan kode untuk kompatibilitas dengan jsonrpcclient versi 4.0.3
   - Perbaikan struktur modul dengan file __init__.py yang tepat

3. **Build System**:
   - Perbaikan script build untuk menggunakan Python dari venv untuk menjalankan PyInstaller
   - Penanganan path ikon yang benar untuk build client dan server

## Kontribusi

Kontribusi selalu diterima! Silakan buat pull request atau buka issue untuk diskusi.

## Lisensi

Proyek ini dilisensikan di bawah [MIT License](../LICENSE).
