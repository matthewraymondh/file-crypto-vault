# Version 1.0 - Basic Encryption

Simple and straightforward file encryption with GUI.

## Features
- AES-256-GCM encryption
- ChaCha20-Poly1305 encryption
- Modern GUI with dark/light theme
- PBKDF2 key derivation (100k iterations)
- Video file support

## Quick Start

```bash
# Run GUI
python crypto_gui.py

# Or use batch file (Windows)
run_gui.bat
```

## Usage

```python
from crypto_file import FileCrypto

# Encrypt
crypto = FileCrypto("AES")
crypto.encrypt_file("video.mp4", "video.mp4.encrypted", "password123")

# Decrypt
crypto.decrypt_file("video.mp4.encrypted", "video.mp4", "password123")
```

## When to Use v1

Use v1 if you need:
- Simple, straightforward encryption
- Minimal dependencies
- Quick setup
- Basic GUI interface

---

**For advanced features, see [v2](../v2/)**
