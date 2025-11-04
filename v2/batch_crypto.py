"""
Batch File Encryption Module
Encrypt/decrypt multiple files and folders

Author: Matthew Raymond Hartono
NIM: A11.2021.13275
"""

import os
from pathlib import Path
from typing import List, Callable, Optional
from crypto_advanced import AdvancedFileCrypto


class BatchCrypto:
    """Batch encryption/decryption for multiple files"""

    def __init__(self, crypto_engine: AdvancedFileCrypto):
        """
        Initialize batch crypto

        Args:
            crypto_engine: AdvancedFileCrypto instance
        """
        self.crypto = crypto_engine

    def encrypt_files(self,
                      file_paths: List[str],
                      output_dir: str,
                      password: str,
                      progress_callback: Optional[Callable[[int, int, str], None]] = None) -> dict:
        """
        Encrypt multiple files

        Args:
            file_paths: List of file paths to encrypt
            output_dir: Directory to save encrypted files
            password: Password for encryption
            progress_callback: Optional callback(current_index, total, filename)

        Returns:
            dict: Batch encryption results
        """
        os.makedirs(output_dir, exist_ok=True)

        results = {
            'total': len(file_paths),
            'success': 0,
            'failed': 0,
            'files': []
        }

        for idx, file_path in enumerate(file_paths, 1):
            try:
                input_path = Path(file_path)
                output_file = os.path.join(output_dir, input_path.name + '.encrypted')

                if progress_callback:
                    progress_callback(idx, len(file_paths), input_path.name)

                result = self.crypto.encrypt_file(file_path, output_file, password)
                results['success'] += 1
                results['files'].append({
                    'file': file_path,
                    'status': 'success',
                    'output': output_file,
                    'size': result['original_size'],
                    'compressed': result['compressed_size'],
                    'ratio': result['compression_ratio']
                })

            except Exception as e:
                results['failed'] += 1
                results['files'].append({
                    'file': file_path,
                    'status': 'failed',
                    'error': str(e)
                })

        return results

    def decrypt_files(self,
                      file_paths: List[str],
                      output_dir: str,
                      password: str,
                      progress_callback: Optional[Callable[[int, int, str], None]] = None) -> dict:
        """
        Decrypt multiple files

        Args:
            file_paths: List of encrypted file paths
            output_dir: Directory to save decrypted files
            password: Password for decryption
            progress_callback: Optional callback(current_index, total, filename)

        Returns:
            dict: Batch decryption results
        """
        os.makedirs(output_dir, exist_ok=True)

        results = {
            'total': len(file_paths),
            'success': 0,
            'failed': 0,
            'files': []
        }

        for idx, file_path in enumerate(file_paths, 1):
            try:
                input_path = Path(file_path)

                if progress_callback:
                    progress_callback(idx, len(file_paths), input_path.name)

                # Get original filename from metadata
                result = self.crypto.decrypt_file(
                    file_path,
                    os.path.join(output_dir, 'temp_decrypt'),  # Temporary
                    password
                )

                # Rename to original name
                final_output = os.path.join(
                    output_dir,
                    Path(result['original_filename']).stem + '_decrypted' + result['original_extension']
                )
                os.rename(os.path.join(output_dir, 'temp_decrypt'), final_output)

                results['success'] += 1
                results['files'].append({
                    'file': file_path,
                    'status': 'success',
                    'output': final_output,
                    'original': result['original_filename'],
                    'verified': result['hash_verified']
                })

            except Exception as e:
                results['failed'] += 1
                results['files'].append({
                    'file': file_path,
                    'status': 'failed',
                    'error': str(e)
                })

        return results

    def encrypt_folder(self,
                       folder_path: str,
                       output_dir: str,
                       password: str,
                       recursive: bool = True,
                       file_patterns: Optional[List[str]] = None,
                       progress_callback: Optional[Callable[[int, int, str], None]] = None) -> dict:
        """
        Encrypt entire folder

        Args:
            folder_path: Path to folder to encrypt
            output_dir: Directory to save encrypted files
            password: Password for encryption
            recursive: Include subfolders
            file_patterns: Optional list of patterns (e.g., ['*.mp4', '*.avi'])
            progress_callback: Optional callback(current_index, total, filename)

        Returns:
            dict: Batch encryption results
        """
        folder = Path(folder_path)

        if not folder.exists() or not folder.is_dir():
            raise ValueError(f"Folder tidak ditemukan: {folder_path}")

        # Collect all files
        if recursive:
            all_files = [str(f) for f in folder.rglob('*') if f.is_file()]
        else:
            all_files = [str(f) for f in folder.glob('*') if f.is_file()]

        # Filter by patterns if provided
        if file_patterns:
            filtered_files = []
            for pattern in file_patterns:
                filtered_files.extend([str(f) for f in folder.rglob(pattern) if f.is_file()])
            all_files = list(set(filtered_files))  # Remove duplicates

        # BUG FIX: Validate that we have files to process
        if not all_files:
            return {
                'total': 0,
                'success': 0,
                'failed': 0,
                'files': [],
                'message': 'No files found matching criteria'
            }

        return self.encrypt_files(all_files, output_dir, password, progress_callback)
