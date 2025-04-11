# StopJudol - Context Document (Python Desktop Edition - Focused)

## 1. Pendahuluan

Dokumen ini adalah **panduan konteks teknis definitif** untuk pengembangan Aplikasi Desktop **StopJudol** menggunakan **Python**. Tujuannya adalah membantu kreator konten YouTube memerangi komentar spam, judi online (judol), dan ilegal lainnya secara otomatis melalui YouTube Data API v3. Dokumen ini menetapkan tumpukan teknologi, metodologi, struktur, pengujian, dan proses deployment yang akan digunakan.

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