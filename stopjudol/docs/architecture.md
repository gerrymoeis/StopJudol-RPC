# StopJudol - Arsitektur JSON-RPC

## Gambaran Umum

StopJudol adalah aplikasi yang membantu kreator konten YouTube untuk mengidentifikasi dan menghapus komentar spam, iklan perjudian, dan konten yang tidak diinginkan lainnya dari video mereka. Aplikasi ini telah dikonversi dari arsitektur monolitik menjadi arsitektur client-server berbasis JSON-RPC untuk meningkatkan skalabilitas, pemeliharaan, dan modularitas.

```
+----------------+        JSON-RPC        +----------------+         +----------------+
|                |<--------------------->|                |<------->|                |
|  Client (GUI)  |        HTTP/HTTPS     |  RPC Server    |   API   |  YouTube API   |
|                |<--------------------->|                |<------->|                |
+----------------+                       +----------------+         +----------------+
```

## Komponen Utama

### 1. Client
- Implementasi GUI menggunakan PyQt6
- Menangani interaksi pengguna
- Berkomunikasi dengan server melalui JSON-RPC
- Menampilkan hasil analisis komentar
- Mengelola autentikasi OAuth dengan YouTube

### 2. Server
- Menyediakan endpoint JSON-RPC
- Menangani autentikasi dan otorisasi
- Mengelola permintaan ke YouTube API
- Melakukan analisis komentar
- Mengelola konfigurasi sistem

### 3. Shared
- Berisi kode dan utilitas yang digunakan oleh client dan server
- Definisi model data
- Utilitas umum

## Alur Komunikasi

1. **Autentikasi**:
   - Client melakukan login ke server menggunakan kredensial
   - Server memvalidasi kredensial dan mengembalikan token JWT
   - Client menyimpan token dan menggunakannya untuk permintaan selanjutnya

2. **Autentikasi YouTube**:
   - Client meminta client_secret dari server
   - Client menjalankan alur OAuth dengan YouTube API
   - Token akses YouTube disimpan di client

3. **Pengambilan Komentar**:
   - Client mengirim permintaan ke server dengan ID video dan token YouTube
   - Server mengambil komentar dari YouTube API
   - Server mengembalikan komentar ke client

4. **Analisis Komentar**:
   - Client mengirim permintaan analisis ke server
   - Server menganalisis komentar untuk mengidentifikasi spam
   - Server mengembalikan hasil analisis ke client

5. **Penghapusan Komentar**:
   - Client mengirim permintaan penghapusan ke server dengan ID komentar
   - Server mencoba menghapus komentar melalui YouTube API
   - Server mengembalikan hasil penghapusan ke client

## Endpoint JSON-RPC

| Metode | Deskripsi | Parameter | Hasil |
|--------|-----------|-----------|-------|
| `login` | Autentikasi ke server | `username`, `password` | Token JWT |
| `get_client_secret` | Mendapatkan client secret untuk OAuth | - | Client secret |
| `fetch_comments` | Mengambil komentar dari video | `video_id`, `credentials_json` | Daftar komentar |
| `analyze_comments` | Menganalisis komentar untuk spam | `comments`, `credentials_json` | Hasil analisis |
| `delete_comment` | Menghapus komentar | `comment_id`, `thread_id`, `credentials_json` | Status penghapusan |
| `get_channel_info` | Mendapatkan info channel | `credentials_json` | Info channel |
| `get_config` | Mendapatkan konfigurasi | - | Konfigurasi |
| `update_config` | Memperbarui konfigurasi | `config` | Status |

## Keamanan

1. **Autentikasi Server**:
   - Menggunakan JWT (JSON Web Token)
   - Token kedaluwarsa setelah 24 jam
   - Middleware autentikasi untuk semua endpoint kecuali `/token`

2. **Autentikasi YouTube**:
   - Menggunakan OAuth 2.0
   - Menyimpan token dengan aman menggunakan keyring
   - Refresh token otomatis

3. **Perlindungan Data**:
   - HTTPS untuk komunikasi client-server
   - Validasi input untuk semua endpoint
   - Penanganan kesalahan yang aman
