# StopJudol - Moderator Komentar YouTube (JSON-RPC Edition)

![StopJudol Logo](stopjudol/assets/icons/app_icon.ico)

## Tentang Aplikasi

StopJudol adalah aplikasi yang dirancang untuk membantu kreator konten YouTube mengidentifikasi dan menghapus secara otomatis komentar spam, iklan judi online (judol), dan konten ilegal lainnya dari video mereka. Versi terbaru ini menggunakan arsitektur client-server berbasis JSON-RPC untuk meningkatkan skalabilitas, pemeliharaan, dan modularitas.

## Unduh Aplikasi

Anda dapat mengunduh versi terbaru StopJudol dari halaman [Releases](https://github.com/gerrymoeis/StopJudol-RPC/releases/latest).

## Arsitektur Baru

Aplikasi ini telah dikonversi dari arsitektur monolitik menjadi arsitektur client-server yang terdiri dari tiga komponen utama:

1. **Client**: Aplikasi GUI berbasis PyQt6 yang menangani interaksi pengguna dan menampilkan hasil.
2. **Server**: Server JSON-RPC yang menangani interaksi dengan YouTube API dan analisis komentar.
3. **Shared**: Kode dan utilitas yang digunakan bersama oleh client dan server.

```markdown
+----------------+        JSON-RPC        +----------------+         +----------------+
|                |<--------------------->|                |<------->|                |
|  Client (GUI)  |        HTTP/HTTPS     |  RPC Server    |   API   |  YouTube API   |
|                |<--------------------->|                |<------->|                |
+----------------+                       +----------------+         +----------------+
```

## Fitur Utama

- **Otentikasi Aman**: Login melalui Google/YouTube OAuth 2.0 dan JWT untuk komunikasi client-server
- **Pemindaian Komentar**: Analisis komentar dari video YouTube manapun menggunakan URL video
- **Deteksi Cerdas**: Identifikasi konten spam dan perjudian menggunakan pola regex dan pencocokan kata kunci
- **Sistem Peninjauan**: Tinjau komentar yang ditandai sebelum penghapusan
- **Penghapusan Massal**: Hapus beberapa komentar sekaligus
- **Pengaturan yang Dapat Disesuaikan**: Konfigurasi kata kunci blacklist dan whitelist
- **Arsitektur Client-Server**: Pemisahan UI dari logika bisnis untuk skalabilitas yang lebih baik

## Persyaratan Sistem

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

## Panduan Penggunaan

Lihat [Panduan Pengguna](stopjudol/README.md) untuk instruksi lengkap tentang cara menggunakan aplikasi.

## Untuk Developer

### Setup Lingkungan Pengembangan

1. Clone repository ini:
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
   ```

### Menjalankan Aplikasi

1. Jalankan server:
   ```
   cd stopjudol
   venv\Scripts\python.exe run_server.py
   ```

2. Jalankan client (di terminal terpisah):
   ```
   cd stopjudol
   venv\Scripts\python.exe run_client.py
   ```

### Build Executable

1. Instal PyInstaller:
   ```
   pip install pyinstaller
   ```

2. Build server:
   ```
   cd stopjudol
   python build_server.py
   ```

3. Build client:
   ```
   cd stopjudol
   python build_client.py
   ```

## Dokumentasi

Dokumentasi komprehensif tersedia untuk membantu Anda memahami sistem:

- [Arsitektur](stopjudol/docs/architecture.md) - Penjelasan detail tentang arsitektur sistem
- [Referensi API](stopjudol/docs/api_reference.md) - Dokumentasi lengkap API JSON-RPC
- [Struktur Proyek](stopjudol/docs/project_structure.md) - Panduan organisasi kode
- [Alur Kerja](stopjudol/docs/workflow.md) - Penjelasan detail alur kerja utama

## Kontribusi

Kontribusi selalu diterima! Silakan buat pull request atau buka issue untuk diskusi.

## Lisensi

Proyek ini dilisensikan di bawah [MIT License](LICENSE).
