# File Encryption System

A modern file encryption tool supporting AES-256-GCM and ChaCha20-Poly1305 with GUI interface.

**Author:** Matthew Raymond Hartono
**NIM:** A11.2021.13275

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.x](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/)

## Choose Your Version

This project has two versions to suit different needs:

### [v1 - Basic Encryption](v1/)
Simple and straightforward encryption for everyday use.
- ✓ AES-256-GCM and ChaCha20-Poly1305
- ✓ Modern GUI with dark/light theme
- ✓ PBKDF2 key derivation
- ✓ Quick setup, minimal dependencies
- **Use if:** You need simple, reliable encryption

### [v2 - Advanced Encryption](v2/)
Professional-grade security with advanced features.
- ✓ All v1 features PLUS:
- ✓ Argon2id key derivation (GPU-resistant)
- ✓ Zstandard compression (30-70% smaller files)
- ✓ Multi-layer encryption (ChaCha20 + AES)
- ✓ Batch processing for multiple files/folders
- ✓ Password strength meter
- ✓ Secure file deletion
- **Use if:** You need maximum security or batch operations

**Quick Decision:** Start with v1 for basic needs, upgrade to v2 for advanced features.

## Features

### Encryption
- **AES-256-GCM** - Industry standard encryption
- **ChaCha20-Poly1305** - Fast modern cipher
- **Argon2id** key derivation (optional PBKDF2)
- **Zstandard compression** - Reduce file size before encryption
- **Multi-layer encryption** - Double encryption for extra security

### Interface
- Modern GUI with dark/light theme
- CLI for command-line usage
- Batch processing for multiple files
- Real-time progress tracking
- Password strength indicator

### Security
- Authenticated encryption (AEAD)
- Random salt and nonce per encryption
- SHA-256 file integrity verification
- Secure file deletion (3-pass overwrite)

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or use the installer (Windows)
install_dependencies.bat
```

## Quick Start

### GUI (Recommended)
```bash
# Basic GUI (v1)
cd v1
python crypto_gui.py

# Advanced GUI (v2)
cd v2
python crypto_gui_advanced.py
```

**Windows Users:** Use `run_gui.bat` (v1) or `run_advanced_gui.bat` (v2)

### CLI Usage

**v1 - Basic:**
```python
from v1.crypto_file import FileCrypto

crypto = FileCrypto("AES")
crypto.encrypt_file("document.pdf", "document.pdf.encrypted", "password")
```

**v2 - Advanced:**
```python
from v2.crypto_advanced import AdvancedCrypto

crypto = AdvancedCrypto("AES", use_argon2=True, compress=True)
crypto.encrypt_file("video.mp4", "video.mp4.encrypted", "password")
```

See [v1/README.md](v1/) or [v2/README.md](v2/) for detailed examples.

## Supported Formats

Works with all file types, optimized for:
- Video: MP4, AVI, MKV, MOV, FLV, WMV, WEBM
- Documents: PDF, DOCX, XLSX
- Images: JPG, PNG, GIF
- Archives: ZIP, RAR, 7Z

## Algorithm Comparison

| Feature | AES-256-GCM | ChaCha20-Poly1305 |
|---------|-------------|-------------------|
| Speed (with AES-NI) | Very Fast | Fast |
| Speed (without) | Moderate | Very Fast |
| Security | Excellent | Excellent |
| Best For | Desktop/Server | Mobile/Embedded |

## Security Best Practices

**Strong Passwords:**
- Minimum 12 characters
- Mix of upper/lowercase, numbers, symbols
- Example: `MySecure!Pass2025`

**Usage:**
- Never reuse passwords
- Store encrypted files separately from password
- Use password manager
- Backup original files

## Development

### Run Tests
```bash
python test_crypto.py
```

### File Structure
```
crypto/
├── v1/                         # Basic version
│   ├── crypto_file.py          # Core encryption
│   ├── crypto_gui.py           # Basic GUI
│   ├── run_gui.bat             # Windows launcher
│   └── README.md               # v1 documentation
├── v2/                         # Advanced version
│   ├── crypto_advanced.py      # Advanced encryption
│   ├── batch_crypto.py         # Batch processing
│   ├── crypto_gui_advanced.py  # Advanced GUI
│   ├── run_advanced_gui.bat    # Windows launcher
│   └── README.md               # v2 documentation
├── test_crypto.py              # Tests
├── requirements.txt            # Dependencies
├── CHANGELOG.md                # Version history
├── LICENSE                     # MIT license
└── README.md                   # This file
```

## Changelog

### v2.0 (Current)
- Added Argon2id key derivation
- Added Zstandard compression
- Added multi-layer encryption
- Added password strength meter
- Added batch processing
- Added file integrity verification
- Improved GUI with advanced options

### v1.0
- AES-256-GCM and ChaCha20-Poly1305
- Basic GUI with theme support
- PBKDF2 key derivation
- Video file optimization

## Dependencies

```
cryptography>=41.0.0
customtkinter>=5.2.0
argon2-cffi>=23.1.0
zstandard>=0.22.0
zxcvbn>=4.4.28
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Author

**Matthew Raymond Hartono**
NIM: A11.2021.13275

Created for Cryptography course project.

## Disclaimer

- For educational and personal use
- Always backup important files
- Developer not responsible for data loss
- Use at your own risk

---

**© 2025 Matthew Raymond Hartono**
