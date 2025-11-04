"""
Program Enkripsi dan Dekripsi File dengan Multiple Algoritma
Mendukung: AES-256-GCM dan ChaCha20-Poly1305
Support untuk file video: mp4, avi, mkv, mov, flv, wmv, dll

Author: Matthew Raymond Hartono
NIM: A11.2021.13275
"""

import os
import json
import hashlib
import secrets
from pathlib import Path
from typing import Tuple, Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class FileCrypto:
    """Kelas untuk enkripsi dan dekripsi file"""

    CHUNK_SIZE = 64 * 1024  # 64KB chunks untuk file besar
    SUPPORTED_VIDEO_FORMATS = {'.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv', '.webm', '.m4v', '.mpeg', '.mpg'}

    def __init__(self, algorithm: str = "AES"):
        """
        Inisialisasi FileCrypto

        Args:
            algorithm: "AES" untuk AES-256-GCM atau "ChaCha20" untuk ChaCha20-Poly1305
        """
        if algorithm.upper() not in ["AES", "CHACHA20"]:
            raise ValueError("Algorithm harus 'AES' atau 'ChaCha20'")

        self.algorithm = algorithm.upper()

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """
        Derive encryption key dari password menggunakan PBKDF2

        Args:
            password: Password string
            salt: Salt bytes (16 bytes)

        Returns:
            32-byte key
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return kdf.derive(password.encode())

    def encrypt_file(self, input_file: str, output_file: str, password: str) -> dict:
        """
        Enkripsi file dengan algoritma yang dipilih

        Args:
            input_file: Path file yang akan dienkripsi
            output_file: Path file hasil enkripsi
            password: Password untuk enkripsi

        Returns:
            Dictionary berisi informasi enkripsi
        """
        input_path = Path(input_file)

        if not input_path.exists():
            raise FileNotFoundError(f"File tidak ditemukan: {input_file}")

        # Check if it's a video file
        is_video = input_path.suffix.lower() in self.SUPPORTED_VIDEO_FORMATS

        # Generate salt dan nonce
        salt = secrets.token_bytes(16)

        # Derive key dari password
        key = self._derive_key(password, salt)

        # Buat cipher berdasarkan algoritma
        if self.algorithm == "AES":
            cipher = AESGCM(key)
            nonce = secrets.token_bytes(12)  # AES-GCM uses 12-byte nonce
        else:  # ChaCha20
            cipher = ChaCha20Poly1305(key)
            nonce = secrets.token_bytes(12)  # ChaCha20 uses 12-byte nonce

        # Baca dan enkripsi file
        with open(input_file, 'rb') as f_in:
            plaintext = f_in.read()

        # Enkripsi data
        ciphertext = cipher.encrypt(nonce, plaintext, None)

        # Metadata
        metadata = {
            'algorithm': self.algorithm,
            'original_filename': input_path.name,
            'original_extension': input_path.suffix,
            'file_type': 'video' if is_video else 'other',
            'file_size': len(plaintext)
        }
        metadata_json = json.dumps(metadata).encode()
        metadata_length = len(metadata_json)

        # Tulis ke output file
        # Format: [salt(16)][nonce(12)][metadata_length(4)][metadata][ciphertext]
        with open(output_file, 'wb') as f_out:
            f_out.write(salt)
            f_out.write(nonce)
            f_out.write(metadata_length.to_bytes(4, 'big'))
            f_out.write(metadata_json)
            f_out.write(ciphertext)

        return {
            'status': 'success',
            'algorithm': self.algorithm,
            'input_file': input_file,
            'output_file': output_file,
            'original_size': len(plaintext),
            'encrypted_size': os.path.getsize(output_file),
            'is_video': is_video
        }

    def decrypt_file(self, input_file: str, output_file: str, password: str) -> dict:
        """
        Dekripsi file yang telah dienkripsi

        Args:
            input_file: Path file terenkripsi
            output_file: Path file hasil dekripsi
            password: Password untuk dekripsi

        Returns:
            Dictionary berisi informasi dekripsi
        """
        if not Path(input_file).exists():
            raise FileNotFoundError(f"File tidak ditemukan: {input_file}")

        with open(input_file, 'rb') as f_in:
            # Baca salt dan nonce
            salt = f_in.read(16)
            nonce = f_in.read(12)

            # Baca metadata
            metadata_length = int.from_bytes(f_in.read(4), 'big')
            metadata_json = f_in.read(metadata_length)
            metadata = json.loads(metadata_json.decode())

            # Baca ciphertext
            ciphertext = f_in.read()

        # Verify algorithm
        if metadata['algorithm'] != self.algorithm:
            raise ValueError(f"File dienkripsi dengan {metadata['algorithm']}, tetapi menggunakan {self.algorithm}")

        # Derive key dari password
        key = self._derive_key(password, salt)

        # Buat cipher berdasarkan algoritma
        if self.algorithm == "AES":
            cipher = AESGCM(key)
        else:  # ChaCha20
            cipher = ChaCha20Poly1305(key)

        try:
            # Dekripsi data
            plaintext = cipher.decrypt(nonce, ciphertext, None)

            # Tulis ke output file
            with open(output_file, 'wb') as f_out:
                f_out.write(plaintext)

            return {
                'status': 'success',
                'algorithm': metadata['algorithm'],
                'input_file': input_file,
                'output_file': output_file,
                'original_filename': metadata['original_filename'],
                'original_extension': metadata['original_extension'],
                'file_type': metadata['file_type'],
                'decrypted_size': len(plaintext)
            }
        except Exception as e:
            raise ValueError(f"Dekripsi gagal. Password salah atau file corrupt: {str(e)}")


def print_banner():
    """Print banner aplikasi"""
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║          FILE ENCRYPTION & DECRYPTION SYSTEM            ║
    ║              Support Video & All File Types              ║
    ║                                                          ║
    ║  Algorithms: AES-256-GCM & ChaCha20-Poly1305            ║
    ╚══════════════════════════════════════════════════════════╝
    """
    print(banner)


def main():
    """Fungsi utama program"""
    print_banner()

    while True:
        print("\n=== MENU UTAMA ===")
        print("1. Enkripsi File (AES-256-GCM)")
        print("2. Enkripsi File (ChaCha20-Poly1305)")
        print("3. Dekripsi File (AES-256-GCM)")
        print("4. Dekripsi File (ChaCha20-Poly1305)")
        print("5. Info File Terenkripsi")
        print("0. Keluar")

        choice = input("\nPilih menu (0-5): ").strip()

        if choice == '0':
            print("Terima kasih! Program selesai.")
            break

        elif choice in ['1', '2']:
            # Enkripsi
            algorithm = "AES" if choice == '1' else "ChaCha20"
            print(f"\n=== ENKRIPSI FILE ({algorithm}) ===")

            input_file = input("Masukkan path file yang akan dienkripsi: ").strip()
            output_file = input("Masukkan path file output (kosongkan untuk auto): ").strip()

            if not output_file:
                output_file = input_file + '.encrypted'

            password = input("Masukkan password: ").strip()
            password_confirm = input("Konfirmasi password: ").strip()

            if password != password_confirm:
                print("❌ Password tidak cocok!")
                continue

            if len(password) < 8:
                print("⚠️  Warning: Password sebaiknya minimal 8 karakter!")
                confirm = input("Lanjutkan? (y/n): ").strip().lower()
                if confirm != 'y':
                    continue

            try:
                crypto = FileCrypto(algorithm)
                print("\n⏳ Mengenkripsi file...")
                result = crypto.encrypt_file(input_file, output_file, password)

                print("\n✅ ENKRIPSI BERHASIL!")
                print(f"   Algorithm: {result['algorithm']}")
                print(f"   Input: {result['input_file']}")
                print(f"   Output: {result['output_file']}")
                print(f"   Original Size: {result['original_size']:,} bytes")
                print(f"   Encrypted Size: {result['encrypted_size']:,} bytes")
                print(f"   File Type: {'VIDEO' if result['is_video'] else 'OTHER'}")

            except Exception as e:
                print(f"\n❌ ERROR: {str(e)}")

        elif choice in ['3', '4']:
            # Dekripsi
            algorithm = "AES" if choice == '3' else "ChaCha20"
            print(f"\n=== DEKRIPSI FILE ({algorithm}) ===")

            input_file = input("Masukkan path file terenkripsi: ").strip()
            output_file = input("Masukkan path file output (kosongkan untuk auto): ").strip()

            if not output_file:
                output_file = input_file.replace('.encrypted', '.decrypted')

            password = input("Masukkan password: ").strip()

            try:
                crypto = FileCrypto(algorithm)
                print("\n⏳ Mendekripsi file...")
                result = crypto.decrypt_file(input_file, output_file, password)

                print("\n✅ DEKRIPSI BERHASIL!")
                print(f"   Algorithm: {result['algorithm']}")
                print(f"   Input: {result['input_file']}")
                print(f"   Output: {result['output_file']}")
                print(f"   Original Filename: {result['original_filename']}")
                print(f"   File Type: {result['file_type'].upper()}")
                print(f"   Decrypted Size: {result['decrypted_size']:,} bytes")

            except Exception as e:
                print(f"\n❌ ERROR: {str(e)}")

        elif choice == '5':
            # Info file
            print("\n=== INFO FILE TERENKRIPSI ===")
            input_file = input("Masukkan path file terenkripsi: ").strip()

            try:
                with open(input_file, 'rb') as f:
                    f.read(16)  # Skip salt
                    f.read(12)  # Skip nonce
                    metadata_length = int.from_bytes(f.read(4), 'big')
                    metadata_json = f.read(metadata_length)
                    metadata = json.loads(metadata_json.decode())

                print("\n📄 INFORMASI FILE:")
                print(f"   Algorithm: {metadata['algorithm']}")
                print(f"   Original Filename: {metadata['original_filename']}")
                print(f"   Original Extension: {metadata['original_extension']}")
                print(f"   File Type: {metadata['file_type'].upper()}")
                print(f"   Original Size: {metadata['file_size']:,} bytes")

            except Exception as e:
                print(f"\n❌ ERROR: {str(e)}")

        else:
            print("❌ Pilihan tidak valid!")


if __name__ == "__main__":
    main()
