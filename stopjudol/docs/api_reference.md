# StopJudol API Reference

## Gambaran Umum API

StopJudol menggunakan protokol JSON-RPC 2.0 untuk komunikasi antara client dan server. Semua permintaan dikirim ke endpoint `/rpc` menggunakan metode HTTP POST, kecuali untuk autentikasi yang menggunakan endpoint `/token`.

## Format Permintaan

```json
{
  "jsonrpc": "2.0",
  "method": "nama_metode",
  "params": {
    "param1": "nilai1",
    "param2": "nilai2"
  },
  "id": 1
}
```

## Format Respons

### Sukses
```json
{
  "jsonrpc": "2.0",
  "result": {
    "key1": "value1",
    "key2": "value2"
  },
  "id": 1
}
```

### Error
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": 123,
    "message": "Pesan error"
  },
  "id": 1
}
```

## Autentikasi

Semua endpoint kecuali `/token` memerlukan autentikasi. Token JWT harus disertakan dalam header `Authorization` dengan format `Bearer {token}`.

### Mendapatkan Token

**Endpoint:** `/token`

**Metode:** POST

**Body:**
```json
{
  "username": "admin",
  "password": "password"
}
```

**Respons:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## Endpoint JSON-RPC

### 1. get_client_secret

Mendapatkan client secret untuk autentikasi OAuth dengan YouTube API.

**Metode:** `get_client_secret`

**Parameter:** Tidak ada

**Respons:**
```json
{
  "client_id": "your-client-id.apps.googleusercontent.com",
  "client_secret": "your-client-secret",
  "redirect_uris": ["http://localhost"],
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token"
}
```

### 2. fetch_comments

Mengambil komentar dari video YouTube.

**Metode:** `fetch_comments`

**Parameter:**
- `video_id` (string): ID video YouTube
- `credentials_json` (string, opsional): Kredensial OAuth sebagai string JSON

**Respons:**
```json
{
  "comments": [
    {
      "id": "comment-thread-id",
      "snippet": {
        "topLevelComment": {
          "id": "comment-id",
          "snippet": {
            "textDisplay": "Isi komentar",
            "authorDisplayName": "Nama Penulis",
            "publishedAt": "2025-04-15T12:00:00Z"
          }
        }
      }
    }
  ],
  "nextPageToken": "token-halaman-berikutnya"
}
```

### 3. analyze_comments

Menganalisis komentar untuk mengidentifikasi spam, iklan perjudian, dll.

**Metode:** `analyze_comments`

**Parameter:**
- `comments` (array): Daftar komentar untuk dianalisis
- `credentials_json` (string, opsional): Kredensial OAuth sebagai string JSON

**Respons:**
```json
{
  "results": [
    {
      "comment_id": "comment-id",
      "is_spam": true,
      "spam_score": 0.95,
      "categories": ["gambling", "phishing"],
      "highlighted_text": "Teks yang disorot sebagai spam"
    }
  ]
}
```

### 4. delete_comment

Menghapus komentar YouTube.

**Metode:** `delete_comment`

**Parameter:**
- `comment_id` (string): ID komentar yang akan dihapus
- `thread_id` (string, opsional): ID thread komentar, digunakan untuk moderasi
- `credentials_json` (string): Kredensial OAuth sebagai string JSON

**Respons:**
```json
{
  "action_type": "deleted",
  "success": true,
  "message": "Comment deleted successfully"
}
```

### 5. get_channel_info

Mendapatkan informasi tentang channel pengguna yang terautentikasi.

**Metode:** `get_channel_info`

**Parameter:**
- `credentials_json` (string): Kredensial OAuth sebagai string JSON

**Respons:**
```json
{
  "channel_id": "channel-id",
  "title": "Nama Channel",
  "description": "Deskripsi channel",
  "thumbnail_url": "https://example.com/thumbnail.jpg",
  "video_count": 42,
  "subscriber_count": 1000
}
```

### 6. get_config

Mendapatkan konfigurasi server.

**Metode:** `get_config`

**Parameter:** Tidak ada

**Respons:**
```json
{
  "spam_detection": {
    "threshold": 0.7,
    "enabled_categories": ["gambling", "phishing", "scam"]
  },
  "youtube_api": {
    "quota_limit": 10000,
    "quota_reset_time": "00:00:00 UTC"
  },
  "server": {
    "max_comments_per_request": 100,
    "cache_duration_seconds": 3600
  }
}
```

### 7. update_config

Memperbarui konfigurasi server.

**Metode:** `update_config`

**Parameter:**
- `config` (object): Objek konfigurasi baru

**Respons:**
```json
{
  "success": true,
  "message": "Configuration updated successfully"
}
```

## Kode Error

| Kode | Deskripsi |
|------|-----------|
| 401 | Tidak terautentikasi |
| 403 | Tidak memiliki izin |
| 404 | Sumber daya tidak ditemukan |
| 422 | Parameter tidak valid |
| 429 | Terlalu banyak permintaan |
| 500 | Kesalahan server internal |
| 1000 | Kesalahan YouTube API |
| 1001 | Kuota YouTube API terlampaui |
| 1002 | Kesalahan autentikasi YouTube |
| 1003 | Kesalahan izin YouTube |
| 2000 | Komentar tidak ditemukan |
| 2001 | Gagal menghapus komentar |
| 2002 | Gagal menganalisis komentar |
| 3000 | Kesalahan RPC |
| 3001 | Kesalahan koneksi RPC |
| 3002 | Kesalahan autentikasi RPC |
