# Changelog

## [2.0.0] - 2025-01-04

### Added
- Argon2id key derivation (more secure than PBKDF2)
- Zstandard compression for smaller encrypted files
- Multi-layer encryption (ChaCha20 + AES cascade)
- Password strength meter using zxcvbn
- Batch processing for multiple files/folders
- SHA-256 file integrity verification
- Secure file deletion (DoD 5220.22-M standard)
- Advanced GUI with scrollable interface
- Progress callbacks for large file operations

### Changed
- Improved error handling
- Better metadata structure
- Enhanced GUI layout and UX

### Fixed
- Division by zero on empty files
- Unicode encoding issues in console output
- Better exception handling in secure delete

## [1.0.0] - 2025-01-03

### Added
- AES-256-GCM encryption
- ChaCha20-Poly1305 encryption
- PBKDF2 key derivation (100k iterations)
- CustomTkinter GUI with dark/light theme
- Video file format support
- Metadata preservation
- Drag & drop support (optional)
- Auto-restore original file extensions

---

**Author:** Matthew Raymond Hartono | NIM: A11.2021.13275
