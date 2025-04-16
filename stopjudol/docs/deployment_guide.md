# StopJudol JSON-RPC Deployment Guide

## Persiapan Deployment

Sebelum men-deploy aplikasi StopJudol yang telah dikonversi ke arsitektur JSON-RPC, pastikan Anda telah menyelesaikan langkah-langkah berikut:

1. Menginstal semua dependensi yang diperlukan
2. Menguji aplikasi secara lokal
3. Mengkonfigurasi file `.env` dengan pengaturan produksi

## Struktur Deployment

Aplikasi StopJudol terdiri dari dua komponen utama yang perlu di-deploy:

1. **Server**: Komponen backend yang menangani komunikasi dengan YouTube API dan analisis komentar
2. **Client**: Aplikasi desktop PyQt6 yang digunakan oleh pengguna akhir

## Deployment Server

### Opsi 1: Deployment Lokal

Untuk deployment server di lingkungan lokal:

```bash
# Aktifkan virtual environment
venv\Scripts\activate

# Jalankan server
python run_server.py
```

### Opsi 2: Deployment ke VPS/Cloud

Untuk deployment server ke VPS atau cloud:

1. Siapkan server dengan Python 3.8+ dan dependensi yang diperlukan
2. Salin direktori `stopjudol` ke server
3. Konfigurasi file `.env` dengan pengaturan produksi
4. Jalankan server dengan supervisor atau systemd

Contoh konfigurasi systemd (`/etc/systemd/system/stopjudol.service`):

```ini
[Unit]
Description=StopJudol JSON-RPC Server
After=network.target

[Service]
User=yourusername
WorkingDirectory=/path/to/stopjudol
ExecStart=/path/to/stopjudol/venv/bin/python run_server.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Kemudian aktifkan dan jalankan service:

```bash
sudo systemctl enable stopjudol
sudo systemctl start stopjudol
```

### Opsi 3: Deployment dengan Docker

Untuk deployment server menggunakan Docker:

1. Buat file `Dockerfile` di direktori `stopjudol`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY . /app/
RUN pip install --no-cache-dir -r server/requirements.txt

EXPOSE 5000

CMD ["python", "run_server.py"]
```

2. Build dan jalankan container Docker:

```bash
docker build -t stopjudol-server .
docker run -p 5000:5000 -v $(pwd)/server/.env:/app/server/.env stopjudol-server
```

## Deployment Client

### Opsi 1: Distribusi Executable

Untuk membuat executable Windows dari client:

1. Instal PyInstaller:

```bash
pip install pyinstaller
```

2. Buat executable:

```bash
pyinstaller --onefile --windowed --icon=main-app/assets/icons/app_icon.ico --add-data "client/src;src" run_client.py
```

3. Executable akan dibuat di direktori `dist`

### Opsi 2: Instalasi Manual

Pengguna dapat menginstal client secara manual dengan:

1. Menginstal Python 3.8+
2. Menginstal dependensi client:

```bash
pip install -r client/requirements.txt
```

3. Menjalankan client:

```bash
python run_client.py
```

## Konfigurasi Produksi

### Konfigurasi Server

Edit file `server/.env` untuk lingkungan produksi:

```
# Server settings
PORT=5000
HOST=0.0.0.0  # Untuk akses dari luar

# Authentication
JWT_SECRET_KEY=GANTI_DENGAN_KUNCI_RAHASIA_YANG_KUAT
API_USERNAME=admin
API_PASSWORD=GANTI_DENGAN_PASSWORD_YANG_KUAT

# YouTube API settings
YOUTUBE_API_KEY=your_api_key_here
CLIENT_SECRET_PATH=path_to_client_secret.json
```

### Konfigurasi Client

Pengguna perlu mengkonfigurasi client untuk terhubung ke server produksi:

1. Buka aplikasi client
2. Buka menu Settings
3. Masukkan URL server produksi (misalnya `https://your-server-domain.com`)
4. Simpan pengaturan

## Keamanan

### Keamanan Server

1. Selalu gunakan HTTPS untuk server produksi
2. Ganti `JWT_SECRET_KEY` dengan kunci yang kuat dan unik
3. Ganti kredensial default (`API_USERNAME` dan `API_PASSWORD`)
4. Batasi akses ke port server dengan firewall
5. Jangan menyimpan kredensial YouTube API di repositori kode

### Keamanan Client

1. Pastikan client hanya berkomunikasi dengan server melalui HTTPS
2. Simpan kredensial pengguna dengan aman menggunakan keyring
3. Jangan menyimpan token JWT dalam file teks biasa

## Pemeliharaan

### Backup

Lakukan backup reguler untuk:
- File konfigurasi server (`.env`)
- Database kredensial (jika ada)
- Konfigurasi blacklist dan whitelist

### Pembaruan

Untuk memperbarui aplikasi:

1. Backup konfigurasi yang ada
2. Tarik perubahan terbaru dari repositori
3. Instal dependensi baru (jika ada)
4. Restart server dan client

## Pemecahan Masalah

### Masalah Server

- **Server tidak dapat dimulai**: Periksa log untuk detail kesalahan
- **Kesalahan koneksi database**: Verifikasi pengaturan koneksi database
- **Kesalahan YouTube API**: Periksa kuota API dan validitas kredensial

### Masalah Client

- **Tidak dapat terhubung ke server**: Periksa URL server dan koneksi jaringan
- **Kesalahan autentikasi**: Verifikasi kredensial pengguna
- **Aplikasi crash**: Periksa log client untuk detail kesalahan
