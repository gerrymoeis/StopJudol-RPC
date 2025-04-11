# StopJudol - Moderator Komentar YouTube

## Gambaran Umum

StopJudol adalah aplikasi desktop yang dirancang untuk membantu kreator konten YouTube mengidentifikasi dan menghapus secara otomatis komentar spam, iklan judi online (judol), dan konten ilegal lainnya dari video mereka. Aplikasi ini menggunakan YouTube Data API v3 untuk memindai komentar dan menyediakan antarmuka yang mudah digunakan untuk meninjau dan menghapus konten yang tidak diinginkan.

## Fitur

- **Otentikasi Aman**: Login melalui Google/YouTube OAuth 2.0
- **Pemindaian Komentar**: Analisis komentar dari video YouTube manapun menggunakan URL video
- **Deteksi Cerdas**: Identifikasi konten spam dan perjudian menggunakan pola regex dan pencocokan kata kunci
- **Sistem Peninjauan**: Tinjau komentar yang ditandai sebelum penghapusan
- **Penghapusan Massal**: Hapus beberapa komentar sekaligus
- **Pengaturan yang Dapat Disesuaikan**: Konfigurasi kata kunci blacklist dan whitelist

## Persyaratan

- Sistem operasi Windows
- Koneksi internet
- Akun YouTube/Google dengan akses ke komentar video

## Instalasi

1. Unduh rilis terbaru dari halaman releases
2. Jalankan installer atau ekstrak file ZIP
3. Luncurkan aplikasi dengan menjalankan `StopJudol.exe`

## Pengaturan Pertama Kali

1. Saat pertama kali menjalankan aplikasi, Anda perlu melakukan otentikasi dengan akun YouTube Anda
2. Klik tombol "Login with YouTube" dan ikuti petunjuk di browser
3. Setelah otentikasi, Anda dapat mulai memindai video Anda untuk komentar yang tidak diinginkan

## Penggunaan

1. **Otentikasi**: Masuk ke akun YouTube Anda menggunakan tombol "Login with YouTube"
2. **Pindai Komentar**: Masukkan URL video YouTube dan klik "Scan Comments"
3. **Tinjau Komentar**: Tinjau komentar yang ditandai dalam tabel
4. **Hapus Komentar**: Pilih komentar yang ingin Anda hapus dan klik "Delete Selected"

## Konfigurasi

Aplikasi ini menggunakan file konfigurasi yang terletak di `%APPDATA%\Local\StopJudol\settings.json`. Anda dapat menyesuaikan:

- Kata kunci blacklist (istilah yang memicu penandaan komentar)
- Kata kunci whitelist (istilah yang mengesampingkan kecocokan blacklist)
- Pengaturan aplikasi

## Privasi & Keamanan

- Token OAuth Anda disimpan dengan aman di Windows Credential Manager
- Aplikasi hanya meminta izin minimum yang diperlukan untuk berfungsi
- Tidak ada data yang dikirim ke server pihak ketiga

## Pemecahan Masalah

- Jika otentikasi gagal, pastikan Anda memiliki koneksi internet yang stabil
- Jika komentar tidak dimuat, verifikasi bahwa URL video benar dan video memiliki komentar publik
- Periksa log di `%APPDATA%\Local\StopJudol\logs\` untuk informasi kesalahan terperinci

## Lisensi

Proyek ini dilisensikan di bawah Lisensi MIT - lihat file LICENSE untuk detailnya.

## Ucapan Terima Kasih

- Dibangun dengan Python dan PyQt6
- Menggunakan YouTube Data API v3
