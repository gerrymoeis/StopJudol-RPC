# StopJudol - Context Document (Python Desktop Edition - Focused)

## 1. Pendahuluan

Dokumen ini adalah **panduan konteks teknis definitif** untuk pengembangan Aplikasi Desktop **StopJudol** menggunakan **Python**. Tujuannya adalah membantu kreator konten YouTube memerangi komentar spam, judi online (judol), dan ilegal lainnya secara otomatis melalui YouTube Data API v3. Dokumen ini menetapkan tumpukan teknologi, metodologi, struktur, pengujian, dan proses deployment yang digunakan, serta mencatat perkembangan dan tantangan yang dihadapi selama pengembangan.

## 2. Tujuan Proyek

*   Mengotomatiskan identifikasi dan penghapusan komentar YouTube yang melanggar.
*   Menghemat waktu dan usaha kreator dalam moderasi komentar.
*   Meningkatkan kebersihan dan keamanan kolom komentar.
*   Menyediakan aplikasi desktop **`.exe`** yang mudah diinstal dan digunakan di **Windows**.

## 3. Pengguna Target

Kreator Konten YouTube yang menggunakan sistem operasi **Windows** dan membutuhkan solusi moderasi komentar otomatis yang berdiri sendiri (standalone).

## 4. Fungsionalitas Inti

1.  **Otentikasi Pengguna:** Login aman via Google/YouTube OAuth 2.0.
2.  **Input Video:** Input URL video YouTube tunggal (atau multipel di versi mendatang).

## 4.1. Catatan Pengembangan

1. **Virtual Environment:** Proyek ini menggunakan Python virtual environment dengan folder `venv` untuk mengelola paket lokal.
   - Semua dependensi diinstal di `stopjudol/venv/`
   - Untuk menjalankan atau menguji aplikasi, selalu gunakan Python dari virtual environment (`venv/Scripts/python.exe` pada Windows)
   - Aktivasi virtual environment: `venv\Scripts\activate` (Windows) atau `source venv/bin/activate` (Linux/Mac)
3.  **Pengambilan Komentar:** Mengambil data komentar via YouTube Data API v3.
4.  **Analisis Komentar:** Identifikasi pelanggaran menggunakan **Regex**, **Keyword Matching (JSON config)**, dan **Normalisasi Teks**.
5.  **Peninjauan (Opsional):** Menampilkan daftar komentar teridentifikasi untuk review pengguna sebelum dihapus.
6.  **Penghapusan Komentar:** Mengeksekusi penghapusan via API setelah konfirmasi.

## 5. Tumpukan Teknologi (Tech Stack) - Python

*   **Bahasa Pemrograman:** **Python 3.8+**
*   **GUI Framework:** **PyQt6** (Gunakan Qt Designer untuk layout UI jika diinginkan)
*   **Interaksi Google API:**
    *   `google-api-python-client`
    *   `google-auth-oauthlib`
    *   `google-auth`
*   **Pemrosesan Teks:**
    *   Modul `re` (Built-in)
    *   Fungsi string built-in Python
*   **HTTP Requests (Cadangan):** `requests`
*   **Packaging & Deployment (.exe):** **PyInstaller**
*   **Manajemen Konfigurasi:** **JSON** (menggunakan modul `json` built-in) untuk menyimpan blacklist keywords, whitelist, dan pengaturan lainnya.
*   **Logging:** Modul `logging` (Built-in)
*   **Concurrency:** Modul **`threading`** (Built-in) untuk tugas background (API calls).
*   **Version Control:** **Git**
*   **Platform Kolaborasi:** GitHub / GitLab / Bitbucket (pilih salah satu)
*   **(Sangat Direkomendasikan) Secure Token Storage:** `keyring` (untuk menyimpan token OAuth secara aman di penyimpanan kredensial OS).

## 6. Metodologi Pengembangan

*   **Metode:** **Kanban**. Fokus pada visualisasi alur kerja (misalnya: Backlog, To Do, In Progress, Testing, Done) menggunakan papan Kanban digital (Trello, GitHub Projects, dll.) dan membatasi Work-in-Progress (WIP) untuk menjaga fokus.

## 7. Struktur Proyek (Direkomendasikan)
stopjudol/
├── .gitignore
├── README.md
├── requirements.txt
├── context.md # Dokumen ini
├── main.py # Entry point aplikasi (inisialisasi QApplication & window utama)
├── assets/
│ ├── icons/
│ │ └── app_icon.ico # Ikon untuk aplikasi dan .exe
│ └── ui/
│ └── main_window.ui # File UI dari Qt Designer (opsional)
├── config/
│ └── default_settings.json # Contoh file konfigurasi (blacklist, dll)
├── docs/
│ └── user_guide.md # Panduan pengguna sederhana
├── src/ # Kode sumber utama
│ ├── init.py
│ ├── app.py # Kelas Window Utama (MainWindow) PyQt6
│ ├── ui_main_window.py # Kode Python hasil konversi .ui (jika pakai Qt Designer)
│ ├── core/ # Logika bisnis
│ │ ├── init.py
│ │ ├── youtube_api.py # Wrapper interaksi YouTube API
│ │ ├── analysis.py # Mesin analisis komentar
│ │ └── config_manager.py # Mengelola load/save file config JSON
│ ├── auth/ # Modul Otentikasi
│ │ ├── init.py
│ │ └── oauth_handler.py # Penanganan alur OAuth 2.0 & token (gunakan keyring!)
│ └── utils/ # Fungsi utilitas
│ ├── init.py
│ └── helpers.py
│ └── logger_config.py # Setup konfigurasi logging
└── tests/ # Unit & Integration Tests (gunakan pytest/unittest)
├── init.py
├── test_analysis.py
└── test_youtube_api_mocked.py # Tes API dengan mocking



## 8. Alur Pengembangan (Fase Prioritas)

1.  **Fase 0: Setup & Init:** Setup venv Python, Git, PyQt6, dapatkan kredensial API, buat struktur dasar.
2.  **Fase 1: Otentikasi Inti:** Implementasi OAuth 2.0 dengan `google-auth-oauthlib` dan penyimpanan token aman menggunakan `keyring`. UI Login/Logout dasar.
3.  **Fase 2: UI Dasar & Fetch Komentar:** Buat UI utama (dengan PyQt6, bisa pakai Qt Designer), input URL, tombol Pindai. Implementasi `youtube_api.py` untuk fetch `commentThreads` di *background thread* (`threading`). Tampilkan komentar mentah di UI (misal: `QListWidget` atau `QTableWidget`). Tambahkan progress bar.
4.  **Fase 3: Analisis & Identifikasi:** Implementasi `analysis.py` (normalisasi, regex, keyword dari file JSON). Integrasikan ke alur setelah fetch. Tandai/tampilkan komentar teridentifikasi di UI.
5.  **Fase 4: Penghapusan & Review:** Implementasi API `comments.delete`. Tambahkan UI review (misal: centang di tabel) dan tombol konfirmasi hapus. Implementasi logging aksi.
6.  **Fase 5: Konfigurasi & UX:** Buat UI setting untuk mengelola blacklist/whitelist di file JSON. Tangani error (API limit, network, dll). Perhalus UI/UX.
7.  **Fase 6: Testing:** Tulis Unit Test (`pytest` direkomendasikan) untuk `analysis.py`, `config_manager.py`. Lakukan Manual Testing intensif.
8.  **Fase 7: Build & Deploy:** Siapkan ikon, gunakan **PyInstaller** untuk build `.exe` (`--onefile --windowed --icon=...`). Uji `.exe` di Windows bersih. Buat `README.md`.

## 9. Strategi Pengujian

*   **Unit Testing (`pytest`):** Tes fungsi individual di `analysis.py`, `utils`, `config_manager.py`. Gunakan mocking untuk dependensi eksternal (API).
*   **Integration Testing:** Tes alur utama secara terbatas, fokus pada interaksi antar modul (misal: UI memicu API call via `threading`). Mocking API tetap penting.
*   **Manual / UAT:** **Kritis.** Uji semua fungsionalitas di lingkungan mirip pengguna akhir (Windows), berbagai skenario video/komentar, penanganan error, dan hasil build `.exe`.

## 10. Deployment (.exe) Menggunakan PyInstaller

1.  **Instal:** `pip install pyinstaller PyQt6 google-api-python-client google-auth-oauthlib google-auth requests keyring` (dan dependensi lain).
2.  **Build Command:**
    ```bash
    pyinstaller --name StopJudol \
                --onefile \
                --windowed \
                --icon=assets/icons/app_icon.ico \
                --add-data "config/default_settings.json;config" \
                --add-data "assets;assets" \
                # Tambahkan --hidden-import=pkg_resources.py2_warn jika perlu
                # Tambahkan --hidden-import lainnya jika PyInstaller gagal deteksi
                main.py
    ```
    *(Sesuaikan path `--add-data` sesuai struktur proyek Anda. Format: `SOURCE;DESTINATION_IN_BUNDLE`)*
3.  **Testing Build:** Jalankan `.exe` dari folder `dist/` di mesin Windows bersih.
4.  **Distribusi:** Zip folder `dist/` (atau file `.exe`) atau gunakan **Inno Setup** / **NSIS** untuk membuat installer `.msi`/`.exe` yang lebih profesional (opsional lanjutan).

## 11. Rencana Pengembangan (Fitur Masa Depan / V2)

*   Dukungan input multiple URL (Batch processing).
*   Penjadwalan scan otomatis.
*   Integrasi opsi 'Report Comment' ke YouTube.
*   Filter/analisis lebih canggih (mungkin ML dasar jika ada data).
*   Dukungan Multi-Bahasa (Internasionalisasi).
*   Fitur auto-update.

## 12. Implementasi dan Tantangan Pengembangan

### 12.1 Implementasi YouTube API

#### 12.1.1 Otentikasi dan Keamanan

* **Implementasi OAuth 2.0**: Berhasil mengimplementasikan alur otentikasi OAuth 2.0 dengan Google menggunakan `google-auth-oauthlib`.
* **Penyimpanan Token Aman**: Menggunakan library `keyring` untuk menyimpan token OAuth secara aman di Windows Credential Manager, memastikan token tidak disimpan dalam plaintext.
* **Refresh Token Otomatis**: Implementasi mekanisme refresh token otomatis ketika token kedaluwarsa.

#### 12.1.2 Pengambilan dan Analisis Komentar

* **Paginasi API**: Implementasi pengambilan komentar dengan paginasi untuk menangani video dengan jumlah komentar besar.
* **Threading**: Menggunakan `threading` untuk menjalankan operasi API di background, mencegah UI freeze selama pengambilan data.
* **Analisis Konten**: Pengembangan sistem deteksi berbasis regex dan keyword matching untuk mengidentifikasi konten spam dan judi online.

#### 12.1.3 Tantangan Moderasi Komentar

* **Batasan API YouTube**: Menemukan dan mengatasi batasan penting dalam YouTube API terkait penghapusan komentar:
  * Pengguna hanya dapat menghapus komentar yang mereka buat sendiri menggunakan `comments().delete()`
  * Untuk komentar di video milik pengguna yang dibuat oleh orang lain, diperlukan pendekatan moderasi khusus
* **Solusi Moderasi Komentar**: Mengimplementasikan dua pendekatan untuk mengatasi batasan API:
  * Menggunakan endpoint `comments/setModerationStatus` dengan status "rejected" untuk menyembunyikan komentar di video milik pengguna
  * Menggunakan `comments().markAsSpam()` sebagai fallback jika metode pertama gagal
* **Implementasi Direct API Call**: Mengembangkan metode untuk memanggil endpoint API yang tidak tersedia di library klien standar

### 12.2 Pengembangan Antarmuka Pengguna

#### 12.2.1 Desain UI Responsif

* **Implementasi PyQt6**: Berhasil mengembangkan antarmuka pengguna yang responsif dan intuitif menggunakan PyQt6.
* **Threading dan Signals**: Menggunakan sistem signal/slot PyQt untuk komunikasi antar thread, memastikan UI tetap responsif selama operasi API.
* **Progress Feedback**: Implementasi progress bar dan status updates untuk memberikan feedback visual kepada pengguna selama proses scanning dan penghapusan.

#### 12.2.2 Pengalaman Pengguna

* **Error Handling**: Pengembangan sistem penanganan error yang komprehensif dengan pesan yang informatif dan user-friendly.
* **Feedback Aksi**: Implementasi dialog konfirmasi dan notifikasi hasil untuk memberikan feedback yang jelas tentang aksi yang dilakukan.
* **Persistent Settings**: Menyimpan pengaturan pengguna antar sesi menggunakan file JSON.

### 12.3 Tantangan Teknis dan Solusi

#### 12.3.1 Batasan YouTube API

* **Tantangan Izin**: Mengatasi batasan izin YouTube API dengan implementasi strategi fallback bertingkat.
* **Quota Management**: Implementasi mekanisme untuk menghindari melebihi kuota API dengan batching dan throttling requests.
* **Error Handling**: Pengembangan sistem penanganan error yang robust untuk berbagai kasus error API (400, 403, 404, dll).

#### 12.3.2 Keamanan dan Privasi

* **Secure Token Storage**: Implementasi penyimpanan token OAuth yang aman menggunakan Windows Credential Manager.
* **Minimal Permission Scope**: Menggunakan scope OAuth minimal yang diperlukan untuk fungsi aplikasi.
* **Data Privacy**: Memastikan tidak ada data pengguna yang disimpan di luar sistem lokal pengguna.

#### 12.3.3 Deployment dan Distribusi

* **PyInstaller Packaging**: Pengembangan script build yang komprehensif untuk menghasilkan executable standalone dengan PyInstaller.
* **Resource Bundling**: Implementasi bundling resource (icons, config files) ke dalam executable.
* **Cross-Version Compatibility**: Memastikan aplikasi berfungsi di berbagai versi Windows dengan dependensi minimal.

### 12.4 Hasil dan Pencapaian

* **Aplikasi Fungsional**: Berhasil mengembangkan aplikasi desktop yang memenuhi semua persyaratan fungsional inti.
* **Solusi Inovatif**: Mengembangkan pendekatan inovatif untuk mengatasi batasan YouTube API dalam penghapusan komentar.
* **Antarmuka Intuitif**: Menciptakan antarmuka pengguna yang mudah digunakan bahkan untuk pengguna non-teknis.
* **Performa Optimal**: Memastikan aplikasi tetap responsif bahkan saat memproses video dengan ribuan komentar.
* **Keamanan Terjamin**: Mengimplementasikan praktik keamanan terbaik untuk melindungi data dan kredensial pengguna.

### 12.5 Pembelajaran dan Praktik Terbaik

* **API Exploration**: Pentingnya memahami batasan API pihak ketiga secara mendalam sebelum implementasi.
* **Fallback Strategies**: Nilai dari mengimplementasikan strategi fallback untuk mengatasi keterbatasan API.
* **User-Centric Design**: Fokus pada pengalaman pengguna dan feedback yang jelas meningkatkan kegunaan aplikasi.
* **Robust Error Handling**: Penanganan error yang komprehensif sangat penting untuk aplikasi yang bergantung pada layanan eksternal.
* **Documentation**: Pentingnya dokumentasi yang baik untuk memudahkan pengembangan dan pemeliharaan di masa depan.