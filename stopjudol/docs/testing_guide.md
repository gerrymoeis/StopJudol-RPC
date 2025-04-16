# StopJudol JSON-RPC Testing Guide

## Persiapan Pengujian

Sebelum menguji aplikasi StopJudol yang telah dikonversi ke arsitektur JSON-RPC, pastikan Anda telah menginstal semua dependensi yang diperlukan:

```bash
# Aktifkan virtual environment
venv\Scripts\activate

# Instal dependensi
python install_dependencies.py
```

## Pengujian Komponen

### 1. Pengujian Koneksi RPC

Untuk menguji koneksi antara client dan server, gunakan script `test_rpc.py`:

```bash
python test_rpc.py --url http://localhost:5000 --username admin --password password
```

Script ini akan menguji:
- Koneksi ke server
- Autentikasi dengan server
- Permintaan terautentikasi ke server

### 2. Menjalankan Server

Untuk menjalankan server JSON-RPC:

```bash
python run_server.py
```

Server akan berjalan di port 5000 secara default (dapat dikonfigurasi di file `.env`).

### 3. Menjalankan Client

Untuk menjalankan client:

```bash
python run_client.py
```

## Pengujian Fungsional

### 1. Autentikasi YouTube

1. Jalankan server dan client
2. Klik tombol "Login" pada client
3. Ikuti alur autentikasi OAuth dengan Google/YouTube
4. Verifikasi bahwa client berhasil mendapatkan token akses

### 2. Mengambil dan Menganalisis Komentar

1. Masukkan URL video YouTube di kolom input
2. Klik tombol "Scan Comments"
3. Verifikasi bahwa komentar berhasil diambil dan dianalisis
4. Periksa bahwa komentar yang berisi spam atau konten judi ditandai dengan benar

### 3. Menghapus Komentar

1. Pilih komentar yang ingin dihapus dari daftar komentar yang ditandai
2. Klik tombol "Delete Selected"
3. Konfirmasi penghapusan
4. Verifikasi bahwa komentar berhasil dihapus

## Pengujian Kesalahan

### 1. Kesalahan Koneksi

1. Matikan server
2. Coba menggunakan client untuk mengambil komentar
3. Verifikasi bahwa client menampilkan pesan kesalahan koneksi yang sesuai

### 2. Kesalahan Autentikasi

1. Ubah token autentikasi menjadi tidak valid
2. Coba menggunakan client untuk mengambil komentar
3. Verifikasi bahwa client menampilkan pesan kesalahan autentikasi yang sesuai

### 3. Kesalahan API YouTube

1. Gunakan kredensial YouTube yang tidak valid
2. Coba mengambil komentar
3. Verifikasi bahwa client menampilkan pesan kesalahan API YouTube yang sesuai

## Pengujian Performa

### 1. Pengujian Beban

1. Gunakan video dengan banyak komentar (>1000)
2. Ukur waktu yang diperlukan untuk mengambil dan menganalisis komentar
3. Verifikasi bahwa aplikasi tetap responsif selama operasi yang membutuhkan waktu lama

### 2. Pengujian Konkurensi

1. Jalankan beberapa instance client yang terhubung ke server yang sama
2. Verifikasi bahwa server dapat menangani beberapa permintaan secara bersamaan

## Catatan Penting

- Selalu gunakan Python dari virtual environment (`venv/Scripts/python.exe` pada Windows)
- Pastikan file `.env` dikonfigurasi dengan benar di direktori server
- Perhatikan batas kuota YouTube API untuk menghindari kesalahan "Quota Exceeded"
