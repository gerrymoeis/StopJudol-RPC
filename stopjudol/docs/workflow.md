# Alur Kerja StopJudol

## Gambaran Umum

Dokumen ini menjelaskan alur kerja utama dalam aplikasi StopJudol, termasuk autentikasi, pengambilan komentar, analisis, dan penghapusan komentar spam.

## 1. Alur Autentikasi

### 1.1 Autentikasi Server

```
+----------------+                                  +----------------+
|                |         1. Login Request         |                |
|     Client     |--------------------------------->|     Server     |
|                |  (username, password)            |                |
|                |                                  |                |
|                |         2. JWT Token             |                |
|                |<---------------------------------|                |
+----------------+                                  +----------------+
```

1. Client mengirim kredensial (username, password) ke endpoint `/token`
2. Server memvalidasi kredensial
3. Server menghasilkan token JWT dan mengembalikannya ke client
4. Client menyimpan token dan menggunakannya untuk permintaan selanjutnya

### 1.2 Autentikasi YouTube

```
+----------------+                                  +----------------+                              +----------------+
|                |      1. Get Client Secret        |                |                              |                |
|     Client     |--------------------------------->|     Server     |                              |    YouTube     |
|                |                                  |                |                              |                |
|                |      2. Client Secret            |                |                              |                |
|                |<---------------------------------|                |                              |                |
|                |                                  |                |                              |                |
|                |      3. OAuth Flow               |                |                              |                |
|                |----------------------------------------------------------------+                |                |
|                |                                  |                |             |                |                |
|                |                                  |                |             v                |                |
|                |                                  |                |      4. Authorization        |                |
|                |                                  |                |---------------------------------->|                |
|                |                                  |                |                              |                |
|                |                                  |                |      5. Access Token         |                |
|                |                                  |                |<----------------------------------|                |
|                |<---------------------------------------------------------------+                |                |
+----------------+                                  +----------------+                              +----------------+
```

1. Client meminta client secret dari server
2. Server mengembalikan client secret
3. Client memulai alur OAuth dengan YouTube
4. Pengguna memberikan otorisasi di browser
5. YouTube mengembalikan token akses ke client
6. Client menyimpan token akses untuk permintaan YouTube API selanjutnya

## 2. Alur Pengambilan dan Analisis Komentar

```
+----------------+                                  +----------------+                              +----------------+
|                |      1. Fetch Comments           |                |                              |                |
|     Client     |--------------------------------->|     Server     |      2. API Request          |    YouTube     |
|                |  (video_id, credentials)         |                |---------------------------------->|     API       |
|                |                                  |                |                              |                |
|                |                                  |                |      3. Comments Data        |                |
|                |                                  |                |<----------------------------------|                |
|                |      4. Comments Data            |                |                              |                |
|                |<---------------------------------|                |                              |                |
|                |                                  |                |                              |                |
|                |      5. Analyze Comments         |                |                              |                |
|                |--------------------------------->|                |                              |                |
|                |  (comments, credentials)         |                |                              |                |
|                |                                  |                |                              |                |
|                |      6. Analysis Results         |                |                              |                |
|                |<---------------------------------|                |                              |                |
+----------------+                                  +----------------+                              +----------------+
```

1. Client mengirim permintaan `fetch_comments` ke server dengan ID video
2. Server membuat permintaan ke YouTube API menggunakan kredensial yang diberikan
3. YouTube API mengembalikan data komentar
4. Server meneruskan data komentar ke client
5. Client mengirim permintaan `analyze_comments` ke server
6. Server menganalisis komentar dan mengembalikan hasil ke client
7. Client menampilkan komentar dan hasil analisis kepada pengguna

## 3. Alur Penghapusan Komentar

```
+----------------+                                  +----------------+                              +----------------+
|                |      1. Delete Comment           |                |                              |                |
|     Client     |--------------------------------->|     Server     |      2. Delete Request       |    YouTube     |
|                |  (comment_id, thread_id,         |                |---------------------------------->|     API       |
|                |   credentials)                   |                |                              |                |
|                |                                  |                |      3. Delete Response      |                |
|                |                                  |                |<----------------------------------|                |
|                |      4. Delete Result            |                |                              |                |
|                |<---------------------------------|                |                              |                |
+----------------+                                  +----------------+                              +----------------+
```

1. Client mengirim permintaan `delete_comment` ke server dengan ID komentar
2. Server mencoba menghapus komentar melalui YouTube API menggunakan kredensial yang diberikan
3. YouTube API mengembalikan respons (sukses atau error)
4. Server meneruskan hasil ke client
5. Client memperbarui UI untuk mencerminkan hasil penghapusan

## 4. Strategi Penghapusan Komentar

Berdasarkan keterbatasan API YouTube, StopJudol mengimplementasikan strategi multi-level untuk penghapusan komentar:

### 4.1 Penghapusan Langsung

Untuk komentar yang dibuat oleh pengguna yang terautentikasi, StopJudol menggunakan metode `comments().delete()` dari YouTube API. Ini adalah metode yang paling efektif karena komentar langsung dihapus.

```python
request = youtube.comments().delete(id=comment_id)
response = request.execute()
```

### 4.2 Moderasi Komentar

Untuk komentar pada video yang dimiliki oleh pengguna yang terautentikasi tetapi dibuat oleh orang lain, StopJudol mencoba menggunakan endpoint `comments/setModerationStatus` dengan status "rejected".

```python
url = "https://www.googleapis.com/youtube/v3/comments/setModerationStatus"
params = {
    'id': comment_id,
    'moderationStatus': 'rejected',
    'banAuthor': 'false'
}
```

### 4.3 Penandaan Spam

Sebagai upaya terakhir, jika kedua metode di atas gagal, StopJudol akan menandai komentar sebagai spam menggunakan metode `comments().markAsSpam()`.

```python
request = youtube.comments().markAsSpam(id=comment_id)
response = request.execute()
```

## 5. Penanganan Error

StopJudol mengimplementasikan strategi penanganan error yang komprehensif:

### 5.1 Error Jaringan

Error jaringan ditangkap dan dilaporkan kepada pengguna dengan opsi untuk mencoba lagi.

### 5.2 Error Autentikasi

Jika token kedaluwarsa, StopJudol secara otomatis mencoba menyegarkan token dan mencoba lagi permintaan.

### 5.3 Error Kuota API

Jika kuota YouTube API terlampaui, StopJudol memberikan pesan yang jelas kepada pengguna dan saran untuk mencoba lagi nanti.

### 5.4 Error Izin

Untuk error izin, StopJudol mencoba metode alternatif (seperti menandai sebagai spam alih-alih menghapus) dan memberikan umpan balik yang jelas kepada pengguna.
