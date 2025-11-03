# File Encryption & Decryption System

Sistem enkripsi dan dekripsi file yang mendukung berbagai format termasuk file video, menggunakan algoritma kriptografi modern dengan GUI yang modern dan minimalist.

**Created by:** Matthew Raymond Hartono
**NIM:** A11.2021.13275

---

## 📋 Fitur Utama

### Algoritma Kriptografi
- **AES-256-GCM** (Advanced Encryption Standard)
- **ChaCha20-Poly1305** (Modern stream cipher)

### Support File
- **Video**: MP4, AVI, MKV, MOV, FLV, WMV, WEBM, M4V, MPEG
- **Semua format file lainnya**

### Keamanan
- PBKDF2 key derivation (100,000 iterasi)
- Authenticated encryption (GCM & Poly1305)
- Random salt dan nonce untuk setiap enkripsi
- Password-based encryption

### GUI Modern
- Dark/Light theme toggle 🌙☀️
- Drag & drop file support 📁
- Progress bar real-time 📊
- Show/hide password 👁
- Auto-restore ekstensi file original

---

## 🚀 Quick Start

### 1. Install Dependencies

**Windows (Otomatis):**
```bash
install_dependencies.bat
```

**Manual:**
```bash
pip install -r requirements.txt
```

### 2. Jalankan Aplikasi

**GUI (Recommended):**
```bash
run_gui.bat
```
atau
```bash
python crypto_gui.py
```

**CLI:**
```bash
python crypto_file.py
```

---

## 💻 Cara Penggunaan GUI

### Enkripsi File

1. **Buka aplikasi** → Jalankan `run_gui.bat`
2. **Pilih "Encrypt"** (default)
3. **Pilih algoritma** → AES-256-GCM atau ChaCha20-Poly1305
4. **Browse file** → Pilih file yang akan dienkripsi
5. **Masukkan password** → Minimal 8 karakter
6. **Klik "ENCRYPT FILE"** → Tunggu selesai

**Hasil:**
```
Input:  video.mp4
Output: video.mp4.encrypted
```

### Dekripsi File

1. **Pilih "Decrypt"**
2. **Pilih algoritma yang sama** dengan saat enkripsi
3. **Browse file** → Pilih file `.encrypted`
4. **Masukkan password** yang sama
5. **Klik "DECRYPT FILE"**

**Hasil:**
```
Input:  video.mp4.encrypted
Output: video_decrypted.mp4  ← Bisa langsung dibuka!
```

---

## 🎯 Fitur GUI

| Fitur | Deskripsi |
|-------|-----------|
| 🔒/🔓 | Toggle Encrypt/Decrypt mode |
| 🎨 | Dark/Light theme switch |
| 📁 | Drag & drop file atau browse |
| 👁 | Show/hide password |
| 📊 | Progress bar saat proses |
| ✨ | Auto-generate output path |
| 🔐 | Restore ekstensi file original |

---

## 📖 Penggunaan Programmatic

### Contoh Enkripsi dengan AES

```python
from crypto_file import FileCrypto

# Inisialisasi dengan AES
crypto = FileCrypto(algorithm="AES")

# Enkripsi file
result = crypto.encrypt_file(
    input_file="video.mp4",
    output_file="video.mp4.encrypted",
    password="MySecurePassword123"
)

print(f"Encrypted: {result['output_file']}")
```

### Contoh Dekripsi dengan AES

```python
from crypto_file import FileCrypto

# Inisialisasi dengan AES
crypto = FileCrypto(algorithm="AES")

# Dekripsi file
result = crypto.decrypt_file(
    input_file="video.mp4.encrypted",
    output_file="video_decrypted.mp4",
    password="MySecurePassword123"
)

print(f"Decrypted: {result['output_file']}")
```

### Contoh dengan ChaCha20

```python
from crypto_file import FileCrypto

# Enkripsi dengan ChaCha20
crypto = FileCrypto(algorithm="ChaCha20")
crypto.encrypt_file("movie.avi", "movie.avi.encrypted", "password")

# Dekripsi
crypto.decrypt_file("movie.avi.encrypted", "movie_decrypted.avi", "password")
```

---

## 🔐 Perbandingan Algoritma

### AES-256-GCM
✅ Standar industri yang terpercaya
✅ Hardware acceleration di CPU modern
✅ Sangat cepat dengan AES-NI
❌ Lebih lambat tanpa hardware support

### ChaCha20-Poly1305
✅ Performa konsisten di semua perangkat
✅ Sangat cepat di mobile/embedded
✅ Aman terhadap timing attacks
❌ Kurang hardware acceleration

**Rekomendasi:**
- **Desktop/Laptop modern** → AES-256-GCM
- **Mobile/Embedded** → ChaCha20-Poly1305

---

## 🛡️ Keamanan

### Best Practices

**Password Kuat:**
```
❌ Lemah:   password123
✅ Kuat:    MyV1de0!2025@Secure
```

**Tips Keamanan:**
1. Gunakan password minimal 12-16 karakter
2. Kombinasi huruf besar, kecil, angka, simbol
3. Simpan password di password manager
4. Jangan hardcode password di kode
5. Backup file original sebelum enkripsi
6. Gunakan algoritma yang sama untuk dekripsi

### Fitur Keamanan

| Fitur | Spesifikasi |
|-------|-------------|
| Key Derivation | PBKDF2-HMAC-SHA256 |
| Iterasi | 100,000 |
| Salt | 16 bytes (random) |
| Nonce | 12 bytes (random) |
| Encryption | AEAD (Authenticated Encryption) |

---

## 🧪 Testing

Jalankan unit tests:

```bash
python test_crypto.py
```

Test coverage:
- ✅ Enkripsi/Dekripsi AES
- ✅ Enkripsi/Dekripsi ChaCha20
- ✅ Deteksi file video
- ✅ Password salah
- ✅ Algoritma berbeda
- ✅ File besar (1MB+)
- ✅ File kosong
- ✅ Metadata preservation

---

## 📂 Struktur File

```
crypto/
├── crypto_file.py              # Core encryption engine
├── crypto_gui.py               # Modern GUI application
├── test_crypto.py              # Unit tests
├── requirements.txt            # Python dependencies
├── install_dependencies.bat    # Auto installer (Windows)
├── run_gui.bat                 # GUI launcher (Windows)
├── .gitignore                  # Git ignore rules
└── README.md                   # Documentation (this file)
```

---

## ⚠️ Troubleshooting

### "Password salah atau file corrupt"
- Pastikan password **sama persis** dengan saat enkripsi
- Pastikan algoritma sama (AES/ChaCha20)
- Periksa file tidak corrupt

### "File tidak ditemukan"
- Periksa path file
- Gunakan absolute path
- Periksa permission read/write

### "Import Error"
```bash
# Install ulang dependencies
pip install --upgrade -r requirements.txt
```

### GUI tidak muncul
```bash
# Install ulang customtkinter
pip install --upgrade customtkinter
```

---

## 📊 Format Video yang Didukung

Program secara otomatis mendeteksi file video:

| Format | Extension | Deskripsi |
|--------|-----------|-----------|
| MP4 | `.mp4` | MPEG-4 Part 14 |
| AVI | `.avi` | Audio Video Interleave |
| MKV | `.mkv` | Matroska Video |
| MOV | `.mov` | QuickTime Movie |
| FLV | `.flv` | Flash Video |
| WMV | `.wmv` | Windows Media Video |
| WEBM | `.webm` | WebM Video |
| M4V | `.m4v` | iTunes Video |
| MPEG | `.mpeg`, `.mpg` | MPEG Video |

**Plus semua format file lainnya!**

---

## 📝 Dependencies

```
cryptography>=41.0.0      # Core encryption
customtkinter>=5.2.0      # Modern GUI
Pillow>=10.0.0           # Image support
tkinterdnd2>=0.3.0       # Drag & drop (optional)
```

---

## ❓ FAQ

**Q: Apakah file original akan terhapus?**
A: Tidak! File original tetap aman. Enkripsi membuat file baru.

**Q: Bisakah membuka file terenkripsi tanpa password?**
A: Tidak mungkin. Password wajib untuk dekripsi.

**Q: Lupa password, bagaimana?**
A: Tidak ada cara untuk recover. Pastikan simpan password dengan aman!

**Q: File hasil dekripsi berbeda dari original?**
A: Jika password dan algoritma benar, file 100% identik.

**Q: Berapa lama proses enkripsi?**
A:
- 10MB: < 5 detik
- 100MB: < 30 detik
- 1GB: 1-3 menit

**Q: Apakah aman untuk cloud storage?**
A: Ya! File terenkripsi sangat aman untuk cloud.

---

## 📜 Lisensi

Program ini dibuat untuk tujuan edukatif dan dapat digunakan secara bebas.

---

## 👨‍💻 Author

**Matthew Raymond Hartono**
- NIM: A11.2021.13275
- Program: File Encryption & Decryption System
- Algoritma: AES-256-GCM & ChaCha20-Poly1305

---

## ⚖️ Disclaimer

- Program ini untuk tujuan edukatif dan penggunaan personal
- Selalu backup file penting sebelum enkripsi
- Developer tidak bertanggung jawab atas kehilangan data
- Pastikan menyimpan password dengan aman
- Gunakan untuk tujuan legal dan etis

---

**© 2025 Matthew Raymond Hartono - A11.2021.13275**
