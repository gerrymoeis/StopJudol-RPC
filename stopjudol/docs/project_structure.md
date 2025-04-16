# Struktur Proyek StopJudol

## Gambaran Umum

Proyek StopJudol diorganisir dalam struktur modular yang memisahkan komponen client dan server. Struktur ini dirancang untuk meningkatkan pemeliharaan, skalabilitas, dan pemisahan tanggung jawab.

```
stopjudol/
├── client/                 # Komponen client (GUI)
│   ├── config/             # Konfigurasi client
│   └── src/                # Kode sumber client
│       ├── auth/           # Modul autentikasi
│       ├── ui/             # Komponen UI
│       ├── worker/         # Thread worker
│       ├── client.py       # Aplikasi client utama
│       ├── error_handler.py # Penanganan error
│       └── rpc_client.py   # Klien JSON-RPC
│
├── server/                 # Komponen server
│   ├── config/             # Konfigurasi server
│   ├── core/               # Logika bisnis inti
│   │   ├── analysis.py     # Analisis komentar
│   │   ├── config_manager.py # Pengelolaan konfigurasi
│   │   └── youtube_api.py  # Wrapper YouTube API
│   ├── rpc/                # Modul JSON-RPC
│   │   ├── auth.py         # Autentikasi RPC
│   │   └── handler.py      # Handler metode RPC
│   └── main.py             # Aplikasi server utama
│
├── shared/                 # Kode yang dibagi antara client dan server
│   ├── models/             # Model data
│   └── utils/              # Utilitas umum
│
├── docs/                   # Dokumentasi
│   ├── architecture.md     # Dokumentasi arsitektur
│   ├── api_reference.md    # Referensi API
│   └── images/             # Diagram dan gambar
│
├── .env                    # Variabel lingkungan
├── run_client.py           # Script untuk menjalankan client
└── run_server.py           # Script untuk menjalankan server
```

## Komponen Utama

### 1. Client

#### 1.1 Modul Autentikasi (`client/src/auth/`)

Menangani autentikasi dengan YouTube API menggunakan OAuth 2.0.

- **oauth_handler.py**: Mengelola alur OAuth, termasuk mendapatkan dan menyegarkan token.

#### 1.2 Komponen UI (`client/src/ui/`)

Berisi komponen antarmuka pengguna.

- **settings_dialog.py**: Dialog pengaturan aplikasi.
- **comment_table.py**: Tabel untuk menampilkan komentar.
- **progress_dialog.py**: Dialog kemajuan untuk operasi yang berjalan lama.

#### 1.3 Thread Worker (`client/src/worker/`)

Menangani operasi yang berjalan lama di thread terpisah untuk menjaga UI tetap responsif.

- **FetchCommentsWorker**: Worker untuk mengambil komentar.
- **DeleteCommentsWorker**: Worker untuk menghapus komentar.
- **AnalyzeCommentsWorker**: Worker untuk menganalisis komentar.

#### 1.4 File Utama

- **client.py**: Kelas MainWindow dan logika aplikasi utama.
- **rpc_client.py**: Klien JSON-RPC untuk berkomunikasi dengan server.
- **error_handler.py**: Penanganan dan pelaporan error.

### 2. Server

#### 2.1 Logika Bisnis Inti (`server/core/`)

Berisi logika bisnis inti aplikasi.

- **youtube_api.py**: Wrapper untuk YouTube API, menangani permintaan ke API.
- **analysis.py**: Menganalisis komentar untuk mengidentifikasi spam dan konten yang tidak diinginkan.
- **config_manager.py**: Mengelola konfigurasi server.

#### 2.2 Modul JSON-RPC (`server/rpc/`)

Menangani permintaan JSON-RPC.

- **handler.py**: Berisi metode yang diekspos melalui JSON-RPC.
- **auth.py**: Menangani autentikasi dan otorisasi.

#### 2.3 File Utama

- **main.py**: Aplikasi server utama, mengatur middleware dan endpoint.

### 3. Shared (`shared/`)

Berisi kode yang digunakan oleh client dan server.

- **models/**: Model data yang digunakan di seluruh aplikasi.
- **utils/**: Fungsi utilitas umum.

## Alur Data

1. **Client → Server**:
   - Permintaan JSON-RPC dikirim dari `rpc_client.py` ke server.
   - Token JWT disertakan dalam header untuk autentikasi.

2. **Server → YouTube API**:
   - Server membuat permintaan ke YouTube API menggunakan `youtube_api.py`.
   - Token OAuth dari client digunakan untuk autentikasi.

3. **Server → Client**:
   - Respons JSON-RPC dikirim kembali ke client.
   - Data diproses dan ditampilkan di UI.

## Penanganan Error

1. **Client-side**:
   - `error_handler.py` menangani dan menampilkan error ke pengguna.
   - Error dikategorikan berdasarkan jenisnya (jaringan, autentikasi, dll.).

2. **Server-side**:
   - Error ditangkap dan dikonversi ke format JSON-RPC.
   - Kode error dan pesan yang deskriptif dikembalikan ke client.

## Konfigurasi

1. **Client**:
   - Konfigurasi disimpan menggunakan `QSettings`.
   - Pengaturan dapat diubah melalui dialog pengaturan.

2. **Server**:
   - Konfigurasi disimpan dalam file JSON dan variabel lingkungan.
   - `config_manager.py` menyediakan API untuk mengakses dan memperbarui konfigurasi.
