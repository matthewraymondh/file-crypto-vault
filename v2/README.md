# Version 2.0 - Advanced Encryption

Professional-grade file encryption with advanced security features and batch processing.

## Features

### Core Encryption
- AES-256-GCM encryption
- ChaCha20-Poly1305 encryption
- Multi-layer encryption (ChaCha20 + AES cascade)
- SHA-256 file integrity verification

### Advanced Security
- Argon2id key derivation (memory-hard, GPU-resistant)
- Fallback to PBKDF2 if Argon2 unavailable
- Password strength meter with real-time feedback
- Secure file deletion (DoD 5220.22-M standard)

### Performance
- Zstandard compression (30-70% size reduction)
- Batch processing for multiple files
- Folder encryption with recursion
- Progress tracking for large operations

### User Interface
- Advanced GUI with scrollable layout
- Dark/light theme support
- Advanced options panel
- Real-time password strength analysis

## Quick Start

```bash
# Run advanced GUI
python crypto_gui_advanced.py

# Or use batch file (Windows)
run_advanced_gui.bat
```

## Usage

### Basic Encryption

```python
from crypto_advanced import AdvancedCrypto

# Encrypt with compression and Argon2
crypto = AdvancedCrypto("AES", use_argon2=True, compress=True)
crypto.encrypt_file("video.mp4", "video.mp4.encrypted", "password123")

# Decrypt
crypto.decrypt_file("video.mp4.encrypted", "video.mp4", "password123")
```

### Multi-Layer Encryption

```python
# Maximum security: ChaCha20 + AES cascade
crypto = AdvancedCrypto("MULTI", use_argon2=True, compress=True)
crypto.encrypt_file("sensitive.doc", "sensitive.doc.encrypted", "strong_password")
```

### Batch Processing

```python
from batch_crypto import BatchCrypto

batch = BatchCrypto("AES", use_argon2=True, compress=True)

# Encrypt multiple files
results = batch.encrypt_files(
    ["file1.mp4", "file2.pdf", "file3.docx"],
    "output_folder",
    "password123"
)

# Encrypt entire folder
results = batch.encrypt_folder(
    "my_folder",
    "encrypted_output",
    "password123",
    recursive=True
)
```

## When to Use v2

Use v2 if you need:
- Maximum security with Argon2id
- Compressed encrypted files (smaller size)
- Multi-layer encryption for sensitive data
- Batch processing of multiple files/folders
- Password strength validation
- Secure file deletion
- Professional-grade encryption

## Security Features

### Argon2id
- Memory-hard key derivation
- Resistant to GPU/ASIC attacks
- Configurable memory cost (64 MB default)
- 3 iterations, 4 parallel threads

### Compression
- Zstandard algorithm
- 30-70% typical size reduction
- Encrypted after compression
- Automatic decompression on decrypt

### Multi-Layer Encryption
- ChaCha20-Poly1305 (first layer)
- AES-256-GCM (second layer)
- Two independent keys derived
- Double authentication tags

### Secure Deletion
- DoD 5220.22-M standard
- 3-pass overwrite (0xFF, 0x00, random)
- Metadata overwrite
- File truncation and deletion

## Performance

Typical encryption speeds on modern hardware:
- Single file (100 MB): ~2-3 seconds
- With compression: ~3-5 seconds
- With Argon2: +1-2 seconds (key derivation)
- Multi-layer: +50% time

Compression ratios:
- Text files: 60-70% reduction
- Documents: 40-60% reduction
- Videos: 5-15% reduction
- Already compressed: minimal

---

**For basic encryption, see [v1](../v1/)**
