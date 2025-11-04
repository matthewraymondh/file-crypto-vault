"""
Advanced File Encryption & Decryption Engine
Features: Argon2, Compression, Streaming, Multi-layer, Secure Delete

Author: Matthew Raymond Hartono
NIM: A11.2021.13275
"""

import os
import json
import secrets
import hashlib
from pathlib import Path
from typing import Tuple, Optional, Callable
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

try:
    from argon2 import PasswordHasher
    from argon2.low_level import hash_secret_raw, Type
    ARGON2_AVAILABLE = True
except ImportError:
    ARGON2_AVAILABLE = False

try:
    import zstandard as zstd
    COMPRESSION_AVAILABLE = True
except ImportError:
    COMPRESSION_AVAILABLE = False

try:
    import zxcvbn
    PASSWORD_STRENGTH_AVAILABLE = True
except ImportError:
    PASSWORD_STRENGTH_AVAILABLE = False


class AdvancedFileCrypto:
    """Advanced encryption with Argon2, compression, streaming, etc."""

    CHUNK_SIZE = 64 * 1024  # 64KB chunks for streaming
    LARGE_FILE_THRESHOLD = 100 * 1024 * 1024  # 100MB
    SUPPORTED_VIDEO_FORMATS = {'.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv', '.webm', '.m4v', '.mpeg', '.mpg'}

    def __init__(self,
                 algorithm: str = "AES",
                 use_argon2: bool = True,
                 use_compression: bool = True,
                 multi_layer: bool = False):
        """
        Initialize Advanced FileCrypto

        Args:
            algorithm: "AES" for AES-256-GCM or "ChaCha20" for ChaCha20-Poly1305
            use_argon2: Use Argon2 instead of PBKDF2 (more secure)
            use_compression: Compress file before encryption
            multi_layer: Use multi-layer encryption (AES + ChaCha20)
        """
        if algorithm.upper() not in ["AES", "CHACHA20"]:
            raise ValueError("Algorithm harus 'AES' atau 'ChaCha20'")

        self.algorithm = algorithm.upper()
        self.use_argon2 = use_argon2 and ARGON2_AVAILABLE
        self.use_compression = use_compression and COMPRESSION_AVAILABLE
        self.multi_layer = multi_layer

        # Fallback warnings (BUG FIX: Remove unicode to avoid encoding issues)
        if use_argon2 and not ARGON2_AVAILABLE:
            print("WARNING: Argon2 not available, falling back to PBKDF2")
        if use_compression and not COMPRESSION_AVAILABLE:
            print("WARNING: Zstandard not available, compression disabled")

    def check_password_strength(self, password: str) -> dict:
        """
        Check password strength using zxcvbn

        Returns:
            dict: {
                'score': 0-4 (0=weak, 4=strong),
                'crack_time': estimated time to crack,
                'feedback': suggestions
            }
        """
        if not PASSWORD_STRENGTH_AVAILABLE:
            return {'score': -1, 'message': 'zxcvbn not available'}

        result = zxcvbn.zxcvbn(password)
        return {
            'score': result['score'],  # 0-4
            'crack_time': result['crack_times_display']['offline_slow_hashing_1e4_per_second'],
            'warning': result['feedback']['warning'],
            'suggestions': result['feedback']['suggestions']
        }

    def _derive_key_argon2(self, password: str, salt: bytes) -> bytes:
        """
        Derive key using Argon2id (modern, memory-hard)

        Args:
            password: Password string
            salt: Salt bytes (16 bytes)

        Returns:
            32-byte key
        """
        key = hash_secret_raw(
            secret=password.encode(),
            salt=salt,
            time_cost=3,  # iterations
            memory_cost=65536,  # 64 MB
            parallelism=4,  # threads
            hash_len=32,
            type=Type.ID  # Argon2id (hybrid)
        )
        return key

    def _derive_key_pbkdf2(self, password: str, salt: bytes) -> bytes:
        """
        Derive key using PBKDF2 (fallback)

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

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive key using configured method"""
        if self.use_argon2:
            return self._derive_key_argon2(password, salt)
        else:
            return self._derive_key_pbkdf2(password, salt)

    def _compress_data(self, data: bytes) -> bytes:
        """Compress data using Zstandard"""
        if not self.use_compression:
            return data

        cctx = zstd.ZstdCompressor(level=3)  # Fast compression
        return cctx.compress(data)

    def _decompress_data(self, data: bytes) -> bytes:
        """Decompress data using Zstandard"""
        if not self.use_compression:
            return data

        dctx = zstd.ZstdDecompressor()
        return dctx.decompress(data)

    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(self.CHUNK_SIZE):
                sha256.update(chunk)
        return sha256.hexdigest()

    def encrypt_file(self,
                     input_file: str,
                     output_file: str,
                     password: str,
                     progress_callback: Optional[Callable[[int], None]] = None) -> dict:
        """
        Encrypt file with advanced features

        Args:
            input_file: Path to file to encrypt
            output_file: Path to output encrypted file
            password: Password for encryption
            progress_callback: Optional callback(percentage: int)

        Returns:
            dict: Encryption result info
        """
        input_path = Path(input_file)

        if not input_path.exists():
            raise FileNotFoundError(f"File tidak ditemukan: {input_file}")

        # Check password strength
        pwd_strength = self.check_password_strength(password)

        # Check if video file
        is_video = input_path.suffix.lower() in self.SUPPORTED_VIDEO_FORMATS

        # Calculate original hash
        if progress_callback:
            progress_callback(10)
        original_hash = self._calculate_file_hash(input_file)

        # Read file
        if progress_callback:
            progress_callback(20)
        with open(input_file, 'rb') as f:
            plaintext = f.read()

        original_size = len(plaintext)

        # Compress if enabled
        if progress_callback:
            progress_callback(30)
        if self.use_compression:
            plaintext = self._compress_data(plaintext)
            compressed_size = len(plaintext)
            # BUG FIX: Prevent division by zero for empty files
            if original_size > 0:
                compression_ratio = (1 - compressed_size / original_size) * 100
            else:
                compression_ratio = 0
        else:
            compressed_size = original_size
            compression_ratio = 0

        # Generate salt and derive key
        if progress_callback:
            progress_callback(40)
        salt = secrets.token_bytes(16)
        key = self._derive_key(password, salt)

        # Multi-layer encryption
        if progress_callback:
            progress_callback(50)

        if self.multi_layer:
            # Layer 1: ChaCha20
            nonce1 = secrets.token_bytes(12)
            cipher1 = ChaCha20Poly1305(key)
            ciphertext = cipher1.encrypt(nonce1, plaintext, None)

            # Layer 2: AES (with different key derivation)
            salt2 = secrets.token_bytes(16)
            key2 = self._derive_key(password + "_layer2", salt2)
            nonce2 = secrets.token_bytes(12)
            cipher2 = AESGCM(key2)
            ciphertext = cipher2.encrypt(nonce2, ciphertext, None)

            # Store both salts and nonces
            crypto_data = {
                'salt1': salt.hex(),
                'nonce1': nonce1.hex(),
                'salt2': salt2.hex(),
                'nonce2': nonce2.hex()
            }
        else:
            # Single layer encryption
            nonce = secrets.token_bytes(12)
            if self.algorithm == "AES":
                cipher = AESGCM(key)
            else:
                cipher = ChaCha20Poly1305(key)
            ciphertext = cipher.encrypt(nonce, plaintext, None)

            crypto_data = {
                'salt': salt.hex(),
                'nonce': nonce.hex()
            }

        if progress_callback:
            progress_callback(70)

        # Metadata
        metadata = {
            'algorithm': 'MULTI-LAYER' if self.multi_layer else self.algorithm,
            'key_derivation': 'Argon2id' if self.use_argon2 else 'PBKDF2',
            'compression': self.use_compression,
            'compression_ratio': f"{compression_ratio:.2f}%",
            'original_filename': input_path.name,
            'original_extension': input_path.suffix,
            'file_type': 'video' if is_video else 'other',
            'file_size': original_size,
            'compressed_size': compressed_size,
            'original_hash': original_hash,
            'crypto_data': crypto_data
        }
        metadata_json = json.dumps(metadata).encode()
        metadata_length = len(metadata_json)

        # Write encrypted file
        if progress_callback:
            progress_callback(80)

        with open(output_file, 'wb') as f_out:
            f_out.write(metadata_length.to_bytes(4, 'big'))
            f_out.write(metadata_json)
            f_out.write(ciphertext)

        if progress_callback:
            progress_callback(100)

        return {
            'status': 'success',
            'algorithm': metadata['algorithm'],
            'key_derivation': metadata['key_derivation'],
            'input_file': input_file,
            'output_file': output_file,
            'original_size': original_size,
            'compressed_size': compressed_size,
            'encrypted_size': os.path.getsize(output_file),
            'compression_ratio': compression_ratio,
            'is_video': is_video,
            'password_strength': pwd_strength,
            'original_hash': original_hash
        }

    def decrypt_file(self,
                     input_file: str,
                     output_file: str,
                     password: str,
                     progress_callback: Optional[Callable[[int], None]] = None) -> dict:
        """
        Decrypt file with advanced features

        Args:
            input_file: Path to encrypted file
            output_file: Path to output decrypted file
            password: Password for decryption
            progress_callback: Optional callback(percentage: int)

        Returns:
            dict: Decryption result info
        """
        if not Path(input_file).exists():
            raise FileNotFoundError(f"File tidak ditemukan: {input_file}")

        if progress_callback:
            progress_callback(10)

        # Read encrypted file
        with open(input_file, 'rb') as f_in:
            metadata_length = int.from_bytes(f_in.read(4), 'big')
            metadata_json = f_in.read(metadata_length)
            metadata = json.loads(metadata_json.decode())
            ciphertext = f_in.read()

        if progress_callback:
            progress_callback(30)

        crypto_data = metadata['crypto_data']
        is_multi_layer = metadata['algorithm'] == 'MULTI-LAYER'

        # Decrypt
        if progress_callback:
            progress_callback(50)

        if is_multi_layer:
            # Multi-layer decryption (reverse order)
            # Layer 2: AES
            salt2 = bytes.fromhex(crypto_data['salt2'])
            nonce2 = bytes.fromhex(crypto_data['nonce2'])
            key2 = self._derive_key(password + "_layer2", salt2)
            cipher2 = AESGCM(key2)
            ciphertext = cipher2.decrypt(nonce2, ciphertext, None)

            # Layer 1: ChaCha20
            salt1 = bytes.fromhex(crypto_data['salt1'])
            nonce1 = bytes.fromhex(crypto_data['nonce1'])
            key1 = self._derive_key(password, salt1)
            cipher1 = ChaCha20Poly1305(key1)
            plaintext = cipher1.decrypt(nonce1, ciphertext, None)
        else:
            # Single layer decryption
            salt = bytes.fromhex(crypto_data['salt'])
            nonce = bytes.fromhex(crypto_data['nonce'])
            key = self._derive_key(password, salt)

            if metadata['algorithm'] == "AES":
                cipher = AESGCM(key)
            else:
                cipher = ChaCha20Poly1305(key)

            plaintext = cipher.decrypt(nonce, ciphertext, None)

        if progress_callback:
            progress_callback(70)

        # Decompress if was compressed
        if metadata.get('compression', False):
            plaintext = self._decompress_data(plaintext)

        if progress_callback:
            progress_callback(80)

        # Write decrypted file
        with open(output_file, 'wb') as f_out:
            f_out.write(plaintext)

        # Verify hash
        decrypted_hash = self._calculate_file_hash(output_file)
        hash_match = decrypted_hash == metadata.get('original_hash', '')

        if progress_callback:
            progress_callback(100)

        return {
            'status': 'success',
            'algorithm': metadata['algorithm'],
            'key_derivation': metadata.get('key_derivation', 'PBKDF2'),
            'input_file': input_file,
            'output_file': output_file,
            'original_filename': metadata['original_filename'],
            'original_extension': metadata['original_extension'],
            'file_type': metadata['file_type'],
            'decrypted_size': len(plaintext),
            'compression_used': metadata.get('compression', False),
            'compression_ratio': metadata.get('compression_ratio', '0%'),
            'hash_verified': hash_match,
            'original_hash': metadata.get('original_hash', 'N/A')
        }

    def secure_delete(self, file_path: str, passes: int = 3) -> dict:
        """
        Securely delete file by overwriting with random data

        Args:
            file_path: Path to file to delete
            passes: Number of overwrite passes (default 3)

        Returns:
            dict: Deletion result
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File tidak ditemukan: {file_path}")

        file_size = os.path.getsize(file_path)

        # BUG FIX: Add exception handling for file access issues
        try:
            for pass_num in range(passes):
                with open(file_path, 'r+b') as f:
                    # Overwrite with random data
                    f.seek(0)
                    f.write(secrets.token_bytes(file_size))
                    f.flush()
                    os.fsync(f.fileno())

            # Delete file
            os.remove(file_path)

            return {
                'status': 'success',
                'file': file_path,
                'passes': passes,
                'size_overwritten': file_size
            }
        except PermissionError:
            raise PermissionError(f"Permission denied: Cannot delete {file_path}")
        except OSError as e:
            raise OSError(f"OS error during secure delete: {str(e)}")
