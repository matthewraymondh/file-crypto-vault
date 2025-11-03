"""
Unit Tests untuk File Crypto System
"""

import os
import tempfile
import unittest
from pathlib import Path
from crypto_file import FileCrypto


class TestFileCrypto(unittest.TestCase):
    """Test cases untuk FileCrypto class"""

    def setUp(self):
        """Setup test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.test_content = b"This is test content for encryption and decryption"
        self.password = "TestPassword123!@#"

    def tearDown(self):
        """Cleanup test files"""
        # Clean up test directory
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def create_test_file(self, filename, content=None, extension=".txt"):
        """Helper untuk membuat test file"""
        filepath = os.path.join(self.test_dir, filename + extension)
        with open(filepath, 'wb') as f:
            f.write(content if content else self.test_content)
        return filepath

    def test_aes_encrypt_decrypt(self):
        """Test enkripsi dan dekripsi dengan AES"""
        crypto = FileCrypto("AES")

        # Create test file
        input_file = self.create_test_file("test_aes")
        encrypted_file = os.path.join(self.test_dir, "test_aes.encrypted")
        decrypted_file = os.path.join(self.test_dir, "test_aes.decrypted")

        # Encrypt
        encrypt_result = crypto.encrypt_file(input_file, encrypted_file, self.password)
        self.assertEqual(encrypt_result['status'], 'success')
        self.assertEqual(encrypt_result['algorithm'], 'AES')
        self.assertTrue(os.path.exists(encrypted_file))

        # Decrypt
        decrypt_result = crypto.decrypt_file(encrypted_file, decrypted_file, self.password)
        self.assertEqual(decrypt_result['status'], 'success')
        self.assertEqual(decrypt_result['algorithm'], 'AES')

        # Verify content
        with open(decrypted_file, 'rb') as f:
            decrypted_content = f.read()
        self.assertEqual(decrypted_content, self.test_content)

    def test_chacha20_encrypt_decrypt(self):
        """Test enkripsi dan dekripsi dengan ChaCha20"""
        crypto = FileCrypto("ChaCha20")

        # Create test file
        input_file = self.create_test_file("test_chacha20")
        encrypted_file = os.path.join(self.test_dir, "test_chacha20.encrypted")
        decrypted_file = os.path.join(self.test_dir, "test_chacha20.decrypted")

        # Encrypt
        encrypt_result = crypto.encrypt_file(input_file, encrypted_file, self.password)
        self.assertEqual(encrypt_result['status'], 'success')
        self.assertEqual(encrypt_result['algorithm'], 'CHACHA20')
        self.assertTrue(os.path.exists(encrypted_file))

        # Decrypt
        decrypt_result = crypto.decrypt_file(encrypted_file, decrypted_file, self.password)
        self.assertEqual(decrypt_result['status'], 'success')
        self.assertEqual(decrypt_result['algorithm'], 'CHACHA20')

        # Verify content
        with open(decrypted_file, 'rb') as f:
            decrypted_content = f.read()
        self.assertEqual(decrypted_content, self.test_content)

    def test_video_file_detection(self):
        """Test deteksi file video"""
        crypto = FileCrypto("AES")

        # Create test video file
        input_file = self.create_test_file("test_video", extension=".mp4")
        encrypted_file = os.path.join(self.test_dir, "test_video.encrypted")

        # Encrypt
        result = crypto.encrypt_file(input_file, encrypted_file, self.password)
        self.assertTrue(result['is_video'])

        # Decrypt and check metadata
        decrypted_file = os.path.join(self.test_dir, "test_video.decrypted")
        decrypt_result = crypto.decrypt_file(encrypted_file, decrypted_file, self.password)
        self.assertEqual(decrypt_result['file_type'], 'video')
        self.assertEqual(decrypt_result['original_extension'], '.mp4')

    def test_multiple_video_formats(self):
        """Test berbagai format video"""
        crypto = FileCrypto("AES")
        video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv']

        for ext in video_extensions:
            with self.subTest(extension=ext):
                input_file = self.create_test_file(f"test_video{ext}", extension="")
                encrypted_file = os.path.join(self.test_dir, f"test_video{ext}.encrypted")

                result = crypto.encrypt_file(input_file, encrypted_file, self.password)
                self.assertTrue(result['is_video'], f"{ext} should be detected as video")

    def test_wrong_password(self):
        """Test dekripsi dengan password salah"""
        crypto = FileCrypto("AES")

        # Create and encrypt file
        input_file = self.create_test_file("test_wrong_pass")
        encrypted_file = os.path.join(self.test_dir, "test_wrong_pass.encrypted")
        crypto.encrypt_file(input_file, encrypted_file, self.password)

        # Try to decrypt with wrong password
        decrypted_file = os.path.join(self.test_dir, "test_wrong_pass.decrypted")
        with self.assertRaises(ValueError):
            crypto.decrypt_file(encrypted_file, decrypted_file, "WrongPassword123")

    def test_wrong_algorithm(self):
        """Test dekripsi dengan algoritma berbeda"""
        crypto_aes = FileCrypto("AES")
        crypto_chacha = FileCrypto("ChaCha20")

        # Encrypt with AES
        input_file = self.create_test_file("test_wrong_algo")
        encrypted_file = os.path.join(self.test_dir, "test_wrong_algo.encrypted")
        crypto_aes.encrypt_file(input_file, encrypted_file, self.password)

        # Try to decrypt with ChaCha20
        decrypted_file = os.path.join(self.test_dir, "test_wrong_algo.decrypted")
        with self.assertRaises(ValueError):
            crypto_chacha.decrypt_file(encrypted_file, decrypted_file, self.password)

    def test_large_file(self):
        """Test enkripsi file besar (simulasi)"""
        crypto = FileCrypto("AES")

        # Create large file (1MB)
        large_content = b"X" * (1024 * 1024)
        input_file = self.create_test_file("test_large", large_content)
        encrypted_file = os.path.join(self.test_dir, "test_large.encrypted")
        decrypted_file = os.path.join(self.test_dir, "test_large.decrypted")

        # Encrypt
        encrypt_result = crypto.encrypt_file(input_file, encrypted_file, self.password)
        self.assertEqual(encrypt_result['original_size'], len(large_content))

        # Decrypt
        crypto.decrypt_file(encrypted_file, decrypted_file, self.password)

        # Verify
        with open(decrypted_file, 'rb') as f:
            decrypted_content = f.read()
        self.assertEqual(decrypted_content, large_content)

    def test_empty_file(self):
        """Test enkripsi file kosong"""
        crypto = FileCrypto("AES")

        # Create empty file
        input_file = self.create_test_file("test_empty", b"")
        encrypted_file = os.path.join(self.test_dir, "test_empty.encrypted")
        decrypted_file = os.path.join(self.test_dir, "test_empty.decrypted")

        # Encrypt
        result = crypto.encrypt_file(input_file, encrypted_file, self.password)
        self.assertEqual(result['original_size'], 0)

        # Decrypt
        crypto.decrypt_file(encrypted_file, decrypted_file, self.password)

        # Verify
        self.assertEqual(os.path.getsize(decrypted_file), 0)

    def test_file_not_found(self):
        """Test enkripsi file yang tidak ada"""
        crypto = FileCrypto("AES")

        with self.assertRaises(FileNotFoundError):
            crypto.encrypt_file("nonexistent.txt", "output.enc", self.password)

    def test_invalid_algorithm(self):
        """Test inisialisasi dengan algoritma invalid"""
        with self.assertRaises(ValueError):
            FileCrypto("InvalidAlgorithm")

    def test_metadata_preservation(self):
        """Test preservasi metadata file"""
        crypto = FileCrypto("AES")

        # Create test file
        original_name = "important_video.mp4"
        input_file = os.path.join(self.test_dir, original_name)
        with open(input_file, 'wb') as f:
            f.write(self.test_content)

        encrypted_file = os.path.join(self.test_dir, "encrypted.enc")
        decrypted_file = os.path.join(self.test_dir, "decrypted.mp4")

        # Encrypt
        crypto.encrypt_file(input_file, encrypted_file, self.password)

        # Decrypt
        result = crypto.decrypt_file(encrypted_file, decrypted_file, self.password)

        # Verify metadata
        self.assertEqual(result['original_filename'], original_name)
        self.assertEqual(result['original_extension'], '.mp4')
        self.assertEqual(result['file_type'], 'video')

    def test_different_passwords(self):
        """Test enkripsi dengan password berbeda menghasilkan ciphertext berbeda"""
        crypto = FileCrypto("AES")

        # Create test file
        input_file = self.create_test_file("test_diff_pass")

        # Encrypt with password 1
        encrypted_file1 = os.path.join(self.test_dir, "encrypted1.enc")
        crypto.encrypt_file(input_file, encrypted_file1, "Password1")

        # Encrypt with password 2
        encrypted_file2 = os.path.join(self.test_dir, "encrypted2.enc")
        crypto.encrypt_file(input_file, encrypted_file2, "Password2")

        # Read encrypted contents
        with open(encrypted_file1, 'rb') as f:
            content1 = f.read()
        with open(encrypted_file2, 'rb') as f:
            content2 = f.read()

        # They should be different
        self.assertNotEqual(content1, content2)

    def test_case_insensitive_algorithm(self):
        """Test algoritma case-insensitive"""
        crypto1 = FileCrypto("aes")
        crypto2 = FileCrypto("AES")
        crypto3 = FileCrypto("Aes")

        self.assertEqual(crypto1.algorithm, "AES")
        self.assertEqual(crypto2.algorithm, "AES")
        self.assertEqual(crypto3.algorithm, "AES")


def run_tests():
    """Jalankan semua test"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestFileCrypto)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
