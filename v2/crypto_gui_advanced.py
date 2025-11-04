"""
Advanced Modern GUI for File Encryption & Decryption
Ultra-Modern Minimalist Design with Premium UX

Author: Matthew Raymond Hartono
NIM: A11.2021.13275
"""

import os
import sys
import threading
import json
import time
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox
import customtkinter as ctk

from crypto_advanced import AdvancedFileCrypto, PASSWORD_STRENGTH_AVAILABLE
from batch_crypto import BatchCrypto

# Try to import drag & drop support
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DRAG_DROP_AVAILABLE = True
except ImportError:
    DRAG_DROP_AVAILABLE = False


# Premium color palette
COLORS = {
    'primary': '#3b82f6',
    'primary_dark': '#2563eb',
    'success': '#10b981',
    'success_dark': '#059669',
    'warning': '#f59e0b',
    'danger': '#ef4444',
}

# History file path
HISTORY_FILE = Path.home() / '.crypto_history.json'
CONFIG_FILE = Path.home() / '.crypto_config.json'

# Set appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class HistoryManager:
    """Manage encryption/decryption history"""

    def __init__(self, history_file=HISTORY_FILE, max_items=10):
        self.history_file = history_file
        self.max_items = max_items
        self.history = self._load_history()

    def _load_history(self):
        """Load history from file"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception:
            return []

    def _save_history(self):
        """Save history to file"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def add_entry(self, operation, input_file, output_file, algorithm, success=True):
        """Add a new history entry"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'input_file': str(input_file),
            'output_file': str(output_file),
            'algorithm': algorithm,
            'success': success
        }

        # Add to beginning of list
        self.history.insert(0, entry)

        # Keep only max_items
        self.history = self.history[:self.max_items]

        # Save to file
        self._save_history()

    def get_recent_files(self, limit=5):
        """Get recent files"""
        return self.history[:limit]

    def clear_history(self):
        """Clear all history"""
        self.history = []
        self._save_history()


class ConfigManager:
    """Manage user configuration and preferences"""

    DEFAULT_CONFIG = {
        'theme': 'auto',  # Auto-detect system theme by default
        'algorithm': 'AES',
        'use_argon2': True,
        'use_compression': True,
        'multi_layer': False,
        'batch_mode': False,
        'shred_after_encrypt': False
    }

    def __init__(self, config_file=CONFIG_FILE):
        self.config_file = config_file
        self.config = self._load_config()
        self._apply_auto_theme()

    def _load_config(self):
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with defaults to handle new settings
                    return {**self.DEFAULT_CONFIG, **loaded}
            return self.DEFAULT_CONFIG.copy()
        except Exception:
            return self.DEFAULT_CONFIG.copy()

    def _save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def get(self, key, default=None):
        """Get configuration value"""
        return self.config.get(key, default)

    def set(self, key, value):
        """Set configuration value"""
        self.config[key] = value
        self._save_config()

    def update(self, settings_dict):
        """Update multiple settings at once"""
        self.config.update(settings_dict)
        self._save_config()

    def reset(self):
        """Reset to default configuration"""
        self.config = self.DEFAULT_CONFIG.copy()
        self._save_config()

    def _detect_system_theme(self):
        """Detect system theme (Windows only for now)"""
        try:
            import platform
            if platform.system() == "Windows":
                try:
                    import winreg
                    # Check Windows registry for theme
                    registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
                    key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
                    value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                    winreg.CloseKey(key)
                    return "light" if value == 1 else "dark"
                except:
                    pass
        except:
            pass
        # Default to dark if detection fails
        return "dark"

    def _apply_auto_theme(self):
        """Apply auto-detected theme if set to 'auto'"""
        if self.config.get('theme') == 'auto':
            detected = self._detect_system_theme()
            self.config['theme'] = detected


class ModernCryptoGUI(ctk.CTk):
    """Ultra-Modern GUI for File Encryption"""

    def __init__(self):
        super().__init__()

        # Window configuration
        self.title("File Crypto v2.0")
        self.geometry("900x950")
        self.resizable(True, True)
        self.minsize(900, 920)

        # Configuration manager
        self.config = ConfigManager()

        # Variables
        self.input_file_path = ctk.StringVar()
        self.output_file_path = ctk.StringVar()
        self.password_var = ctk.StringVar()
        self.algorithm_var = ctk.StringVar(value=self.config.get('algorithm', 'AES'))
        self.operation_var = ctk.StringVar(value="Encrypt")
        self.theme_var = ctk.StringVar(value=self.config.get('theme', 'dark'))

        # Advanced options - load from config
        self.use_argon2_var = ctk.BooleanVar(value=self.config.get('use_argon2', True))
        self.use_compression_var = ctk.BooleanVar(value=self.config.get('use_compression', True))
        self.multi_layer_var = ctk.BooleanVar(value=self.config.get('multi_layer', False))
        self.batch_mode_var = ctk.BooleanVar(value=self.config.get('batch_mode', False))
        self.shred_after_encrypt_var = ctk.BooleanVar(value=self.config.get('shred_after_encrypt', False))

        # State
        self.password_strength_score = 0
        self.is_processing = False
        self.password_visible = False
        self.batch_files = []
        self.current_batch_index = 0

        # Time tracking for ETA
        self.process_start_time = None
        self.last_progress_time = None
        self.last_progress_pct = 0

        # Clipboard security
        self.clipboard_timer = None

        # History manager
        self.history = HistoryManager()

        # Apply saved theme
        ctk.set_appearance_mode(self.theme_var.get())

        # Create UI
        self.create_widgets()
        self.center_window()

        # Bind events
        self.password_var.trace('w', self.on_password_change)
        self.input_file_path.trace('w', self.on_input_file_change)

        # Save preferences on close
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def center_window(self):
        """Center window on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        """Create all GUI widgets"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main container
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=0, column=0, sticky="nsew", padx=35, pady=35)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)

        # Header
        self.create_header(container)

        # Content
        self.create_content(container)

        # Footer
        self.create_footer(container)

    def create_header(self, parent):
        """Create premium header"""
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 35))
        header.grid_columnconfigure(0, weight=1)

        # Title row
        title_row = ctk.CTkFrame(header, fg_color="transparent")
        title_row.grid(row=0, column=0, sticky="ew")
        title_row.grid_columnconfigure(0, weight=1)

        # Brand
        brand = ctk.CTkFrame(title_row, fg_color="transparent")
        brand.pack(side="left")

        title = ctk.CTkLabel(
            brand,
            text="File Crypto",
            font=ctk.CTkFont(size=34, weight="bold"),
            text_color=("#2563eb", "#60a5fa")
        )
        title.pack(side="left")

        badge = ctk.CTkLabel(
            brand,
            text="PRO",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=("#2563eb", "#60a5fa"),
            fg_color=("#dbeafe", "#1e3a8a"),
            corner_radius=6,
            padx=8,
            pady=4
        )
        badge.pack(side="left", padx=(10, 0), pady=(8, 0))

        # Theme toggle
        theme_container = ctk.CTkFrame(title_row, fg_color="transparent")
        theme_container.pack(side="right")

        theme_label = ctk.CTkLabel(
            theme_container,
            text="Theme",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="gray"
        )
        theme_label.pack(side="left", padx=(0, 8))

        self.theme_toggle = ctk.CTkSwitch(
            theme_container,
            text="",
            width=50,
            height=26,
            switch_width=50,
            switch_height=26,
            command=self.toggle_theme,
            progress_color=("#3b82f6", "#1e293b"),
            button_color=("#ffffff", "#475569"),
            button_hover_color=("#f1f5f9", "#334155")
        )
        self.theme_toggle.pack(side="left")
        self.theme_toggle.select()  # Dark mode by default

        # Tagline
        tagline = ctk.CTkLabel(
            header,
            text="Military-grade encryption with modern cryptographic standards",
            font=ctk.CTkFont(size=13),
            text_color=("gray50", "gray60")
        )
        tagline.grid(row=1, column=0, sticky="w", pady=(10, 0))

    def create_content(self, parent):
        """Create premium content area"""
        scroll = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent",
            scrollbar_button_color=("gray75", "gray30"),
            scrollbar_button_hover_color=("gray65", "gray40")
        )
        scroll.grid(row=1, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        row = 0

        # Operation selector
        self.create_operation_section(scroll, row)
        row += 1

        # File section
        self.create_file_section(scroll, row)
        row += 1

        # Password section
        self.create_password_section(scroll, row)
        row += 1

        # Advanced section
        self.create_advanced_section(scroll, row)
        row += 1

        # Recent files section
        self.create_recent_files_section(scroll, row)
        row += 1

        # Progress
        self.progress_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self.progress_frame.grid(row=row, column=0, sticky="ew", pady=(0, 24))
        self.progress_frame.grid_columnconfigure(0, weight=1)

        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="Processing...",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#3b82f6", "#60a5fa")
        )
        self.progress_label.grid(row=0, column=0, sticky="w", pady=(0, 10))

        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame,
            height=10,
            corner_radius=5,
            progress_color=("#3b82f6", "#60a5fa")
        )
        self.progress_bar.grid(row=1, column=0, sticky="ew")
        self.progress_bar.set(0)
        self.progress_frame.grid_remove()

        row += 1

        # Action button
        self.action_button = ctk.CTkButton(
            scroll,
            text="Encrypt File",
            height=60,
            corner_radius=14,
            font=ctk.CTkFont(size=17, weight="bold"),
            command=self.process_file,
            fg_color=("#3b82f6", "#3b82f6"),
            hover_color=("#2563eb", "#2563eb"),
            border_width=0
        )
        self.action_button.grid(row=row, column=0, sticky="ew", pady=(0, 10))

    def create_operation_section(self, parent, row):
        """Create premium operation selector"""
        section = ctk.CTkFrame(
            parent,
            fg_color=("#ffffff", "#1e293b"),
            corner_radius=18,
            border_width=0
        )
        section.grid(row=row, column=0, sticky="ew", pady=(0, 24))
        section.grid_columnconfigure((0, 2, 4), weight=1)

        # Encrypt card
        encrypt_card = ctk.CTkFrame(section, fg_color="transparent")
        encrypt_card.grid(row=0, column=0, sticky="nsew", padx=28, pady=28)

        self.encrypt_radio = ctk.CTkRadioButton(
            encrypt_card,
            text="",
            variable=self.operation_var,
            value="Encrypt",
            command=self.on_operation_change,
            radiobutton_width=22,
            radiobutton_height=22,
            border_width_unchecked=2,
            border_width_checked=6
        )
        self.encrypt_radio.pack(anchor="w")

        enc_title = ctk.CTkLabel(
            encrypt_card,
            text="Encrypt",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        enc_title.pack(anchor="w", pady=(12, 6))

        enc_desc = ctk.CTkLabel(
            encrypt_card,
            text="Secure your files with\nmilitary-grade encryption",
            font=ctk.CTkFont(size=12),
            text_color=("gray50", "gray60"),
            justify="left"
        )
        enc_desc.pack(anchor="w")

        # Divider 1
        divider1 = ctk.CTkFrame(
            section,
            fg_color=("gray90", "gray20"),
            width=2
        )
        divider1.grid(row=0, column=1, sticky="ns", pady=28)

        # Decrypt card
        decrypt_card = ctk.CTkFrame(section, fg_color="transparent")
        decrypt_card.grid(row=0, column=2, sticky="nsew", padx=28, pady=28)

        self.decrypt_radio = ctk.CTkRadioButton(
            decrypt_card,
            text="",
            variable=self.operation_var,
            value="Decrypt",
            command=self.on_operation_change,
            radiobutton_width=22,
            radiobutton_height=22,
            border_width_unchecked=2,
            border_width_checked=6
        )
        self.decrypt_radio.pack(anchor="w")

        dec_title = ctk.CTkLabel(
            decrypt_card,
            text="Decrypt",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        dec_title.pack(anchor="w", pady=(12, 6))

        dec_desc = ctk.CTkLabel(
            decrypt_card,
            text="Unlock and restore your\nencrypted files",
            font=ctk.CTkFont(size=12),
            text_color=("gray50", "gray60"),
            justify="left"
        )
        dec_desc.pack(anchor="w")

        # Divider 2
        divider2 = ctk.CTkFrame(
            section,
            fg_color=("gray90", "gray20"),
            width=2
        )
        divider2.grid(row=0, column=3, sticky="ns", pady=28)

        # Verify card
        verify_card = ctk.CTkFrame(section, fg_color="transparent")
        verify_card.grid(row=0, column=4, sticky="nsew", padx=28, pady=28)

        self.verify_radio = ctk.CTkRadioButton(
            verify_card,
            text="",
            variable=self.operation_var,
            value="Verify",
            command=self.on_operation_change,
            radiobutton_width=22,
            radiobutton_height=22,
            border_width_unchecked=2,
            border_width_checked=6
        )
        self.verify_radio.pack(anchor="w")

        verify_title = ctk.CTkLabel(
            verify_card,
            text="Verify",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        verify_title.pack(anchor="w", pady=(12, 6))

        verify_desc = ctk.CTkLabel(
            verify_card,
            text="Check file integrity\nwithout decrypting",
            font=ctk.CTkFont(size=12),
            text_color=("gray50", "gray60"),
            justify="left"
        )
        verify_desc.pack(anchor="w")

    def create_file_section(self, parent, row):
        """Create premium file section"""
        section = ctk.CTkFrame(
            parent,
            fg_color=("#ffffff", "#1e293b"),
            corner_radius=18
        )
        section.grid(row=row, column=0, sticky="ew", pady=(0, 24))
        section.grid_columnconfigure(0, weight=1)

        # Input
        input_container = ctk.CTkFrame(section, fg_color="transparent")
        input_container.grid(row=0, column=0, sticky="ew", padx=28, pady=(28, 20))
        input_container.grid_columnconfigure(0, weight=1)

        input_header = ctk.CTkFrame(input_container, fg_color="transparent")
        input_header.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        input_label = ctk.CTkLabel(
            input_header,
            text="Input File",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        input_label.pack(side="left")

        input_row = ctk.CTkFrame(input_container, fg_color="transparent")
        input_row.grid(row=1, column=0, sticky="ew")
        input_row.grid_columnconfigure(0, weight=1)

        self.input_entry = ctk.CTkEntry(
            input_row,
            textvariable=self.input_file_path,
            placeholder_text="Select a file to encrypt or decrypt (or drag & drop here)",
            height=48,
            corner_radius=12,
            border_width=2,
            font=ctk.CTkFont(size=13),
            border_color=("gray85", "gray25")
        )
        self.input_entry.grid(row=0, column=0, sticky="ew", padx=(0, 12))

        # Enable drag & drop for input
        self._enable_drag_drop(self.input_entry, self.on_input_drop)

        self.browse_btn = ctk.CTkButton(
            input_row,
            text="Browse",
            width=110,
            height=48,
            corner_radius=12,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.browse_input_file,
            fg_color=("gray90", "gray20"),
            hover_color=("gray80", "gray30"),
            text_color=("#1e293b", "#f1f5f9")
        )
        self.browse_btn.grid(row=0, column=1)

        # Output
        output_container = ctk.CTkFrame(section, fg_color="transparent")
        output_container.grid(row=1, column=0, sticky="ew", padx=28, pady=(0, 28))
        output_container.grid_columnconfigure(0, weight=1)

        output_header = ctk.CTkFrame(output_container, fg_color="transparent")
        output_header.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        output_label = ctk.CTkLabel(
            output_header,
            text="Output Location",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        output_label.pack(side="left")

        optional_badge = ctk.CTkLabel(
            output_header,
            text="OPTIONAL",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=("gray60", "gray50"),
            fg_color=("gray95", "gray15"),
            corner_radius=5,
            padx=10,
            pady=3
        )
        optional_badge.pack(side="left", padx=(10, 0))

        output_row = ctk.CTkFrame(output_container, fg_color="transparent")
        output_row.grid(row=1, column=0, sticky="ew")
        output_row.grid_columnconfigure(0, weight=1)

        self.output_entry = ctk.CTkEntry(
            output_row,
            textvariable=self.output_file_path,
            placeholder_text="Auto-generated if left empty (or drag & drop here)",
            height=48,
            corner_radius=12,
            border_width=2,
            font=ctk.CTkFont(size=13),
            border_color=("gray85", "gray25")
        )
        self.output_entry.grid(row=0, column=0, sticky="ew", padx=(0, 12))

        # Enable drag & drop for output
        self._enable_drag_drop(self.output_entry, self.on_output_drop)

        output_btn = ctk.CTkButton(
            output_row,
            text="Browse",
            width=110,
            height=48,
            corner_radius=12,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.browse_output_file,
            fg_color=("gray90", "gray20"),
            hover_color=("gray80", "gray30"),
            text_color=("#1e293b", "#f1f5f9")
        )
        output_btn.grid(row=0, column=1)

    def create_password_section(self, parent, row):
        """Create premium password section"""
        section = ctk.CTkFrame(
            parent,
            fg_color=("#ffffff", "#1e293b"),
            corner_radius=18
        )
        section.grid(row=row, column=0, sticky="ew", pady=(0, 24))
        section.grid_columnconfigure(0, weight=1)

        container = ctk.CTkFrame(section, fg_color="transparent")
        container.grid(row=0, column=0, sticky="ew", padx=28, pady=28)
        container.grid_columnconfigure(0, weight=1)

        # Header
        pwd_header = ctk.CTkFrame(container, fg_color="transparent")
        pwd_header.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        pwd_label = ctk.CTkLabel(
            pwd_header,
            text="Password",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        pwd_label.pack(side="left")

        # Input row
        pwd_row = ctk.CTkFrame(container, fg_color="transparent")
        pwd_row.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        pwd_row.grid_columnconfigure(0, weight=1)

        self.password_entry = ctk.CTkEntry(
            pwd_row,
            textvariable=self.password_var,
            placeholder_text="Enter a strong password (min. 12 characters recommended)",
            show="•",
            height=48,
            corner_radius=12,
            border_width=2,
            font=ctk.CTkFont(size=13),
            border_color=("gray85", "gray25")
        )
        self.password_entry.grid(row=0, column=0, sticky="ew", padx=(0, 12))

        self.copy_pwd_btn = ctk.CTkButton(
            pwd_row,
            text="Copy",
            width=80,
            height=48,
            corner_radius=12,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.copy_password_to_clipboard,
            fg_color=("gray90", "gray20"),
            hover_color=("gray80", "gray30"),
            text_color=("#1e293b", "#f1f5f9")
        )
        self.copy_pwd_btn.grid(row=0, column=1, padx=(0, 12))

        self.show_pwd_btn = ctk.CTkButton(
            pwd_row,
            text="Show",
            width=80,
            height=48,
            corner_radius=12,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.toggle_password_visibility,
            fg_color=("gray90", "gray20"),
            hover_color=("gray80", "gray30"),
            text_color=("#1e293b", "#f1f5f9")
        )
        self.show_pwd_btn.grid(row=0, column=2)

        # Strength indicator
        if PASSWORD_STRENGTH_AVAILABLE:
            self.strength_label = ctk.CTkLabel(
                container,
                text="Password strength: Not set",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=("gray60", "gray50")
            )
            self.strength_label.grid(row=2, column=0, sticky="w", pady=(0, 8))

            self.strength_bar = ctk.CTkProgressBar(
                container,
                height=8,
                corner_radius=4,
                progress_color=("gray75", "gray45")
            )
            self.strength_bar.grid(row=3, column=0, sticky="ew")
            self.strength_bar.set(0)

    def create_advanced_section(self, parent, row):
        """Create premium advanced section"""
        section = ctk.CTkFrame(
            parent,
            fg_color=("#ffffff", "#1e293b"),
            corner_radius=18
        )
        section.grid(row=row, column=0, sticky="ew", pady=(0, 28))
        section.grid_columnconfigure(0, weight=1)

        container = ctk.CTkFrame(section, fg_color="transparent")
        container.grid(row=0, column=0, sticky="ew", padx=28, pady=28)
        container.grid_columnconfigure(0, weight=1)

        # Header
        header = ctk.CTkFrame(container, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))

        adv_label = ctk.CTkLabel(
            header,
            text="Advanced Settings",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        adv_label.pack(side="left")

        pro_badge = ctk.CTkLabel(
            header,
            text="PRO",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=("#2563eb", "#60a5fa"),
            fg_color=("#dbeafe", "#1e3a8a"),
            corner_radius=5,
            padx=10,
            pady=3
        )
        pro_badge.pack(side="left", padx=(10, 0))

        # Algorithm
        algo_container = ctk.CTkFrame(container, fg_color="transparent")
        algo_container.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        algo_container.grid_columnconfigure(0, weight=1)

        algo_label = ctk.CTkLabel(
            algo_container,
            text="Encryption Algorithm",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("gray50", "gray60")
        )
        algo_label.grid(row=0, column=0, sticky="w", pady=(0, 10))

        self.algo_display_var = ctk.StringVar(value="AES-256-GCM")

        algo_selector = ctk.CTkSegmentedButton(
            algo_container,
            values=["AES-256-GCM", "ChaCha20-Poly1305"],
            variable=self.algo_display_var,
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=10,
            height=40,
            command=self.on_algorithm_change
        )
        algo_selector.grid(row=1, column=0, sticky="ew")

        # Security features
        features = ctk.CTkFrame(container, fg_color="transparent")
        features.grid(row=2, column=0, sticky="ew")
        features.grid_columnconfigure(0, weight=1)

        # Argon2
        argon2_check = ctk.CTkCheckBox(
            features,
            text="Argon2id key derivation (GPU-resistant, recommended)",
            variable=self.use_argon2_var,
            font=ctk.CTkFont(size=12),
            checkbox_width=22,
            checkbox_height=22,
            corner_radius=7,
            border_width=2
        )
        argon2_check.grid(row=0, column=0, sticky="w", pady=8)

        # Compression
        compress_check = ctk.CTkCheckBox(
            features,
            text="Zstandard compression (reduce file size 30-70%)",
            variable=self.use_compression_var,
            font=ctk.CTkFont(size=12),
            checkbox_width=22,
            checkbox_height=22,
            corner_radius=7,
            border_width=2
        )
        compress_check.grid(row=1, column=0, sticky="w", pady=8)

        # Multi-layer
        multi_check = ctk.CTkCheckBox(
            features,
            text="Multi-layer encryption (ChaCha20 + AES cascade)",
            variable=self.multi_layer_var,
            font=ctk.CTkFont(size=12),
            checkbox_width=22,
            checkbox_height=22,
            corner_radius=7,
            border_width=2,
            command=self.on_multilayer_change
        )
        multi_check.grid(row=2, column=0, sticky="w", pady=8)

        # Batch mode
        batch_check = ctk.CTkCheckBox(
            features,
            text="Batch mode (process multiple files or folders)",
            variable=self.batch_mode_var,
            font=ctk.CTkFont(size=12),
            checkbox_width=22,
            checkbox_height=22,
            corner_radius=7,
            border_width=2,
            command=self.on_batch_mode_change
        )
        batch_check.grid(row=3, column=0, sticky="w", pady=8)

        # Shred after encrypt
        shred_check = ctk.CTkCheckBox(
            features,
            text="Securely delete original file after encryption",
            variable=self.shred_after_encrypt_var,
            font=ctk.CTkFont(size=12),
            checkbox_width=22,
            checkbox_height=22,
            corner_radius=7,
            border_width=2
        )
        shred_check.grid(row=4, column=0, sticky="w", pady=8)

    def create_recent_files_section(self, parent, row):
        """Create recent files section"""
        section = ctk.CTkFrame(
            parent,
            fg_color=("#ffffff", "#1e293b"),
            corner_radius=18
        )
        section.grid(row=row, column=0, sticky="ew", pady=(0, 24))
        section.grid_columnconfigure(0, weight=1)

        # Header
        header_frame = ctk.CTkFrame(section, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=28, pady=(28, 16))
        header_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header_frame,
            text="Recent Files",
            font=ctk.CTkFont(size=17, weight="bold")
        )
        title.pack(side="left")

        # Clear history button
        clear_btn = ctk.CTkButton(
            header_frame,
            text="Clear History",
            width=100,
            height=28,
            corner_radius=8,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=("gray90", "gray20"),
            hover_color=("gray80", "gray30"),
            text_color=("#1e293b", "#f1f5f9"),
            command=self.clear_history
        )
        clear_btn.pack(side="right")

        # Recent files container
        self.recent_files_container = ctk.CTkFrame(section, fg_color="transparent")
        self.recent_files_container.grid(row=1, column=0, sticky="ew", padx=28, pady=(0, 28))
        self.recent_files_container.grid_columnconfigure(0, weight=1)

        # Load recent files
        self.refresh_recent_files()

    def refresh_recent_files(self):
        """Refresh recent files display"""
        # Clear existing widgets
        for widget in self.recent_files_container.winfo_children():
            widget.destroy()

        # Get recent files
        recent = self.history.get_recent_files(limit=5)

        if not recent:
            # Show empty state
            empty_label = ctk.CTkLabel(
                self.recent_files_container,
                text="No recent files yet. Start encrypting or decrypting files!",
                font=ctk.CTkFont(size=12),
                text_color=("gray50", "gray60")
            )
            empty_label.grid(row=0, column=0, pady=16)
        else:
            # Display recent files
            for idx, entry in enumerate(recent):
                self._create_history_item(self.recent_files_container, entry, idx)

    def _create_history_item(self, parent, entry, row):
        """Create a history item widget"""
        item_frame = ctk.CTkFrame(
            parent,
            fg_color=("gray95", "gray15"),
            corner_radius=12,
            height=70
        )
        item_frame.grid(row=row, column=0, sticky="ew", pady=(0, 8))
        item_frame.grid_columnconfigure(1, weight=1)
        item_frame.grid_propagate(False)

        # Icon/Status
        status_color = COLORS['success'] if entry.get('success', True) else COLORS['danger']
        status_icon = "✓" if entry.get('success', True) else "✗"

        status_label = ctk.CTkLabel(
            item_frame,
            text=status_icon,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=status_color,
            width=40
        )
        status_label.grid(row=0, column=0, rowspan=2, padx=(16, 8), pady=12)

        # Operation and algorithm
        op_text = f"{entry['operation']} • {entry['algorithm']}"
        op_label = ctk.CTkLabel(
            item_frame,
            text=op_text,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=("gray70", "gray50"),
            anchor="w"
        )
        op_label.grid(row=0, column=1, sticky="w", padx=(0, 12), pady=(12, 0))

        # File path (truncated)
        input_file = Path(entry['input_file']).name
        if len(input_file) > 40:
            input_file = input_file[:37] + "..."

        file_label = ctk.CTkLabel(
            item_frame,
            text=input_file,
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        file_label.grid(row=1, column=1, sticky="w", padx=(0, 12), pady=(0, 12))

        # Load button
        load_btn = ctk.CTkButton(
            item_frame,
            text="Load",
            width=70,
            height=32,
            corner_radius=8,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=("#3b82f6", "#3b82f6"),
            hover_color=("#2563eb", "#2563eb"),
            command=lambda e=entry: self.load_history_item(e)
        )
        load_btn.grid(row=0, column=2, rowspan=2, padx=16, pady=12)

    def load_history_item(self, entry):
        """Load a history item into the form"""
        # Set input file
        if Path(entry['output_file']).exists():
            self.input_file_path.set(entry['output_file'])
        elif Path(entry['input_file']).exists():
            self.input_file_path.set(entry['input_file'])
        else:
            messagebox.showwarning(
                "File Not Found",
                "The file from this history entry no longer exists."
            )
            return

        # Set operation (toggle if it was encrypt, now decrypt)
        if entry['operation'] == 'Encrypt':
            self.operation_var.set('Decrypt')
        else:
            self.operation_var.set('Encrypt')

        # Update UI
        self.on_operation_change()

        # Show success message
        messagebox.showinfo(
            "History Loaded",
            f"Loaded file from history:\n\n{Path(entry['input_file']).name}\n\n"
            f"Ready to {self.operation_var.get().lower()}!"
        )

    def clear_history(self):
        """Clear all history"""
        result = messagebox.askyesno(
            "Clear History",
            "Are you sure you want to clear all recent files history?\n\n"
            "This action cannot be undone."
        )
        if result:
            self.history.clear_history()
            self.refresh_recent_files()
            messagebox.showinfo("History Cleared", "All recent files history has been cleared.")

    def create_footer(self, parent):
        """Create premium footer"""
        footer = ctk.CTkFrame(parent, fg_color="transparent")
        footer.grid(row=2, column=0, sticky="ew", pady=(25, 0))

        credit = ctk.CTkLabel(
            footer,
            text="© 2025 Matthew Raymond Hartono • A11.2021.13275 • MIT License",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray60")
        )
        credit.pack()

    def on_operation_change(self):
        """Handle operation change"""
        operation = self.operation_var.get()

        if operation == "Encrypt":
            self.action_button.configure(
                text="Encrypt File",
                fg_color=("#3b82f6", "#3b82f6"),
                hover_color=("#2563eb", "#2563eb")
            )
        elif operation == "Decrypt":
            self.action_button.configure(
                text="Decrypt File",
                fg_color=("#10b981", "#34d399"),
                hover_color=("#059669", "#10b981")
            )
        else:  # Verify
            self.action_button.configure(
                text="Verify File",
                fg_color=("#f59e0b", "#fbbf24"),
                hover_color=("#d97706", "#f59e0b")
            )
            # Disable output field for verify mode
            self.output_entry.configure(state="disabled")

        # Re-enable output for encrypt/decrypt
        if operation != "Verify":
            self.output_entry.configure(state="normal")

        self.on_input_file_change()

    def on_algorithm_change(self, value):
        """Handle algorithm selection change"""
        if "AES" in value:
            self.algorithm_var.set("AES")
        else:
            self.algorithm_var.set("ChaCha20")

    def on_multilayer_change(self):
        """Handle multi-layer toggle"""
        if self.multi_layer_var.get():
            messagebox.showinfo(
                "Multi-Layer Encryption",
                "Multi-layer encryption provides maximum security:\n\n"
                "✓ ChaCha20-Poly1305 encryption (first layer)\n"
                "✓ AES-256-GCM encryption (second layer)\n"
                "✓ Two independent encryption keys\n"
                "✓ Double authentication tags\n\n"
                "Note: Processing time increases by ~50%"
            )

    def on_batch_mode_change(self):
        """Handle batch mode toggle"""
        if self.batch_mode_var.get():
            # Update UI for batch mode
            self.action_button.configure(
                text=f"{'Encrypt' if self.operation_var.get() == 'Encrypt' else 'Decrypt'} Folder"
            )
            messagebox.showinfo(
                "Batch Mode Enabled",
                "Batch mode allows you to:\n\n"
                "✓ Process entire folders\n"
                "✓ Encrypt/decrypt multiple files at once\n"
                "✓ See detailed progress for each file\n\n"
                "Click 'Browse' to select a folder."
            )
        else:
            # Reset to single file mode
            self.action_button.configure(
                text=f"{'Encrypt' if self.operation_var.get() == 'Encrypt' else 'Decrypt'} File"
            )

    def on_input_file_change(self, *args):
        """Auto-generate output path"""
        input_path = self.input_file_path.get()
        if not input_path or self.output_file_path.get():
            return

        try:
            if self.operation_var.get() == "Encrypt":
                self.output_file_path.set(input_path + ".encrypted")
            else:
                if input_path.endswith(".encrypted"):
                    base = input_path[:-10]
                    self.output_file_path.set(base + "_decrypted" + Path(base).suffix)
        except:
            pass

    def on_password_change(self, *args):
        """Handle password strength"""
        if not PASSWORD_STRENGTH_AVAILABLE:
            return

        password = self.password_var.get()
        if not password:
            self.strength_label.configure(
                text="Password strength: Not set",
                text_color=("gray60", "gray50")
            )
            self.strength_bar.configure(progress_color=("gray75", "gray45"))
            self.strength_bar.set(0)
            return

        try:
            crypto = AdvancedFileCrypto()
            strength = crypto.check_password_strength(password)
            score = strength['score']
            self.password_strength_score = score

            configs = [
                ("Very weak", "#ef4444", 0.2),
                ("Weak", "#f97316", 0.4),
                ("Fair", "#eab308", 0.6),
                ("Strong", "#22c55e", 0.8),
                ("Very strong", "#10b981", 1.0)
            ]

            if 0 <= score <= 4:
                text, color, value = configs[score]
                self.strength_label.configure(
                    text=f"Password strength: {text.capitalize()}",
                    text_color=color
                )
                self.strength_bar.configure(progress_color=color)
                self.strength_bar.set(value)
        except:
            pass

    def toggle_theme(self):
        """Toggle theme"""
        if self.theme_var.get() == "dark":
            ctk.set_appearance_mode("light")
            self.theme_var.set("light")
        else:
            ctk.set_appearance_mode("dark")
            self.theme_var.set("dark")

        # Save theme preference
        self.config.set('theme', self.theme_var.get())

    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.password_visible:
            self.password_entry.configure(show="•")
            self.show_pwd_btn.configure(text="Show")
            self.password_visible = False
        else:
            self.password_entry.configure(show="")
            self.show_pwd_btn.configure(text="Hide")
            self.password_visible = True

    def copy_password_to_clipboard(self):
        """Copy password to clipboard with auto-clear"""
        password = self.password_var.get()

        if not password:
            messagebox.showwarning(
                "No Password",
                "Please enter a password first before copying."
            )
            return

        # Cancel existing timer if any
        if self.clipboard_timer is not None:
            self.after_cancel(self.clipboard_timer)

        # Copy to clipboard
        self.clipboard_clear()
        self.clipboard_append(password)
        self.update()

        # Update button to show copied state
        original_text = self.copy_pwd_btn.cget("text")
        self.copy_pwd_btn.configure(text="✓ Copied", fg_color=("#10b981", "#10b981"))

        # Clear clipboard after 30 seconds
        def clear_clipboard_and_reset():
            try:
                # Only clear if clipboard still contains the password
                current_clipboard = self.clipboard_get()
                if current_clipboard == password:
                    self.clipboard_clear()
            except:
                pass  # Clipboard already cleared or changed

            # Reset button
            self.copy_pwd_btn.configure(text=original_text, fg_color=("gray90", "gray20"))
            self.clipboard_timer = None

        # Schedule auto-clear after 30 seconds
        self.clipboard_timer = self.after(30000, clear_clipboard_and_reset)

        # Show info to user
        messagebox.showinfo(
            "Password Copied",
            "Password copied to clipboard!\n\n"
            "⏱ It will be automatically cleared in 30 seconds\n"
            "for security reasons."
        )

    def browse_input_file(self):
        """Browse input file or folder"""
        if self.batch_mode_var.get():
            # Folder selection for batch mode
            folder = filedialog.askdirectory(title="Select Folder")
            if folder:
                self.input_file_path.set(folder)
                self.output_file_path.set("")
                # Count files in folder
                all_files = list(Path(folder).rglob("*")) if Path(folder).exists() else []
                file_count = len([f for f in all_files if f.is_file()])
                if file_count > 0:
                    messagebox.showinfo("Folder Selected", f"Found {file_count} file(s) in folder.")
        else:
            # Single file selection
            if self.operation_var.get() == "Decrypt":
                filename = filedialog.askopenfilename(
                    title="Select Encrypted File",
                    filetypes=[
                        ("Encrypted Files", "*.encrypted"),
                        ("All Files", "*.*")
                    ]
                )
            else:
                filename = filedialog.askopenfilename(
                    title="Select File to Encrypt",
                    filetypes=[
                        ("All Files", "*.*"),
                        ("Video Files", "*.mp4 *.avi *.mkv *.mov *.flv *.wmv"),
                        ("Documents", "*.pdf *.docx *.xlsx *.txt *.pptx"),
                        ("Images", "*.jpg *.jpeg *.png *.gif *.bmp *.svg"),
                        ("Archives", "*.zip *.rar *.7z *.tar *.gz")
                    ]
                )
            if filename:
                self.input_file_path.set(filename)
                self.output_file_path.set("")

    def browse_output_file(self):
        """Browse output file or folder"""
        if self.batch_mode_var.get():
            # Folder selection for batch output
            folder = filedialog.askdirectory(title="Select Output Folder")
            if folder:
                self.output_file_path.set(folder)
        else:
            # Single file output
            if self.operation_var.get() == "Encrypt":
                filename = filedialog.asksaveasfilename(
                    title="Save Encrypted File",
                    defaultextension=".encrypted",
                    filetypes=[("Encrypted Files", "*.encrypted"), ("All Files", "*.*")]
                )
            else:
                suggested = ""
                input_path = self.input_file_path.get()
                if input_path.endswith(".encrypted"):
                    suggested = os.path.basename(input_path[:-10])

                filename = filedialog.asksaveasfilename(
                    title="Save Decrypted File",
                    initialfile=suggested,
                    filetypes=[("All Files", "*.*")]
                )
            if filename:
                self.output_file_path.set(filename)

    def validate_inputs(self):
        """Validate inputs"""
        if not self.input_file_path.get():
            item_type = "folder" if self.batch_mode_var.get() else "file"
            messagebox.showerror(
                f"No {item_type.title()} Selected",
                f"Please select a {item_type} to process.\n\nClick the 'Browse' button to choose a {item_type}."
            )
            return False

        input_path = Path(self.input_file_path.get())
        if not input_path.exists():
            item_type = "folder" if self.batch_mode_var.get() else "file"
            messagebox.showerror(
                f"{item_type.title()} Not Found",
                f"The selected {item_type} does not exist:\n\n{self.input_file_path.get()}\n\n"
                f"Please select a valid {item_type}."
            )
            return False

        # Batch mode: validate folder
        if self.batch_mode_var.get():
            if not input_path.is_dir():
                messagebox.showerror(
                    "Not a Folder",
                    f"Batch mode requires a folder, but you selected a file:\n\n{self.input_file_path.get()}\n\n"
                    "Please select a folder or disable batch mode."
                )
                return False

            # Count files in folder
            all_files = [f for f in input_path.rglob('*') if f.is_file()]
            if len(all_files) == 0:
                messagebox.showerror(
                    "Empty Folder",
                    f"The selected folder contains no files:\n\n{self.input_file_path.get()}\n\n"
                    "Please select a folder with files to process."
                )
                return False
        else:
            # Single file mode: validate file
            if not input_path.is_file():
                messagebox.showerror(
                    "Not a File",
                    f"Please select a file, not a folder:\n\n{self.input_file_path.get()}\n\n"
                    "Enable batch mode to process folders."
                )
                return False

        if not self.password_var.get():
            messagebox.showerror(
                "No Password",
                "Please enter a password to encrypt/decrypt your file.\n\n"
                "Your password is required to secure your data."
            )
            self.password_entry.focus()
            return False

        if len(self.password_var.get()) < 8:
            result = messagebox.askyesno(
                "Weak Password Warning",
                f"Your password has only {len(self.password_var.get())} characters.\n\n"
                "Passwords under 8 characters are not secure.\n\n"
                "Recommended:\n"
                "• At least 12 characters\n"
                "• Mix of uppercase & lowercase\n"
                "• Numbers and symbols\n\n"
                "Continue anyway?",
                icon='warning'
            )
            if not result:
                self.password_entry.focus()
                return False

        if PASSWORD_STRENGTH_AVAILABLE and self.password_strength_score < 2:
            result = messagebox.askyesno(
                "Very Weak Password",
                "Your password strength is very weak!\n\n"
                "A strong password should:\n"
                "• Be at least 12 characters long\n"
                "• Include uppercase & lowercase letters\n"
                "• Include numbers & symbols\n"
                "• Not be a common word or pattern\n\n"
                "Continue with this weak password?",
                icon='warning'
            )
            if not result:
                self.password_entry.focus()
                return False

        output_path = self.output_file_path.get()
        if output_path:
            if Path(output_path).resolve() == Path(self.input_file_path.get()).resolve():
                messagebox.showerror(
                    "Invalid Output Path",
                    "Output path cannot be the same as input path.\n\n"
                    "This would overwrite your original file!"
                )
                return False

        return True

    def show_progress(self, message, percentage=None):
        """Show progress with ETA"""
        self.progress_frame.grid()

        # Calculate ETA if percentage is provided
        if percentage is not None and percentage > 0:
            current_time = time.time()

            # Initialize start time
            if self.process_start_time is None:
                self.process_start_time = current_time
                self.last_progress_time = current_time
                self.last_progress_pct = 0

            # Calculate ETA
            elapsed = current_time - self.process_start_time
            if percentage > 5:  # Only show ETA after 5% to get accurate estimate
                progress_rate = percentage / elapsed  # percent per second
                remaining_pct = 100 - percentage
                eta_seconds = remaining_pct / progress_rate if progress_rate > 0 else 0

                # Format ETA
                if eta_seconds < 60:
                    eta_str = f"{int(eta_seconds)}s"
                elif eta_seconds < 3600:
                    eta_str = f"{int(eta_seconds / 60)}m {int(eta_seconds % 60)}s"
                else:
                    hours = int(eta_seconds / 3600)
                    minutes = int((eta_seconds % 3600) / 60)
                    eta_str = f"{hours}h {minutes}m"

                message = f"{message} • ETA: {eta_str}"

            self.progress_bar.set(percentage / 100)
        else:
            # Reset timing for new operations
            self.process_start_time = None

        self.progress_label.configure(text=message)
        self.update_idletasks()

    def hide_progress(self):
        """Hide progress"""
        self.progress_bar.set(0)
        self.progress_frame.grid_remove()
        # Reset timing
        self.process_start_time = None
        self.last_progress_time = None
        self.last_progress_pct = 0

    def process_file(self):
        """Process file"""
        if self.is_processing:
            messagebox.showwarning(
                "Already Processing",
                "Please wait for the current operation to complete."
            )
            return

        if not self.validate_inputs():
            return

        self.is_processing = True
        self.action_button.configure(state="disabled", text="Processing...")
        thread = threading.Thread(target=self._process_file_thread, daemon=True)
        thread.start()

    def _process_file_thread(self):
        """Process in background"""
        try:
            operation = self.operation_var.get()
            algorithm = self.algorithm_var.get()
            input_path = self.input_file_path.get()
            output_path = self.output_file_path.get()
            password = self.password_var.get()

            # Create crypto engine
            crypto = AdvancedFileCrypto(
                algorithm=algorithm,
                use_argon2=self.use_argon2_var.get(),
                use_compression=self.use_compression_var.get(),
                multi_layer=self.multi_layer_var.get()
            )

            # Check if batch mode
            if self.batch_mode_var.get():
                self._process_batch(crypto, input_path, output_path, password, operation)
            else:
                self._process_single_file(crypto, input_path, output_path, password, operation)

        except PermissionError as e:
            error_msg = str(e)
            self.after(0, lambda: self.hide_progress())
            self.after(0, lambda msg=error_msg: messagebox.showerror(
                "Permission Denied",
                f"Cannot access the file:\n\n{msg}\n\n"
                "Please close any programs using this file and try again."
            ))
        except ValueError as e:
            error_msg = str(e)
            self.after(0, lambda: self.hide_progress())
            self.after(0, lambda msg=error_msg: messagebox.showerror(
                "Wrong Password",
                "Decryption failed - incorrect password!\n\n"
                "Please check your password and try again.\n\n"
                "Other possible causes:\n"
                "• File is corrupted\n"
                "• File was not encrypted with this tool"
            ))
        except Exception as e:
            error_msg = str(e)
            self.after(0, lambda: self.hide_progress())
            self.after(0, lambda msg=error_msg: messagebox.showerror(
                "Error",
                f"An error occurred:\n\n{msg}\n\n"
                "Please check your inputs and try again."
            ))
        finally:
            self.is_processing = False
            op_text = "Encrypt File" if self.operation_var.get() == "Encrypt" else "Decrypt File"
            if self.batch_mode_var.get():
                op_text = op_text.replace("File", "Folder")
            self.after(0, lambda text=op_text: self.action_button.configure(state="normal", text=text))

    def _process_single_file(self, crypto, input_path, output_path, password, operation):
        """Process single file"""
        # Auto-generate output
        if not output_path:
            if operation == "Encrypt":
                output_path = input_path + ".encrypted"
            else:
                if input_path.endswith(".encrypted"):
                    base = input_path[:-10]
                    output_path = base + "_decrypted" + Path(base).suffix
                else:
                    output_path = input_path + "_decrypted"

        def progress_callback(pct):
            self.after(0, lambda p=pct: self.show_progress(f"{operation}ing... {p}%", p))

        if operation == "Verify":
            # Verify mode - check integrity without decrypting
            self.after(0, lambda: self.show_progress("Verifying file integrity...", 0))

            try:
                # Read file header to verify metadata
                import struct
                with open(input_path, 'rb') as f:
                    # Check magic bytes
                    magic = f.read(8)
                    if magic != b'CRYPTV2\x00':
                        raise ValueError("Not a valid encrypted file")

                    # Read metadata size
                    meta_size = struct.unpack('>I', f.read(4))[0]
                    metadata_json = f.read(meta_size).decode('utf-8')
                    import json
                    metadata = json.loads(metadata_json)

                self.after(0, lambda: self.hide_progress())

                # Show verification result
                file_mb = Path(input_path).stat().st_size / 1024 / 1024
                msg = (
                    f"✓ File integrity verified!\n\n"
                    f"File is a valid encrypted file\n"
                    f"Algorithm: {metadata.get('algorithm', 'Unknown')}\n"
                    f"Original Filename: {metadata.get('original_filename', 'Unknown')}\n"
                    f"Compression: {'Yes' if metadata.get('compression_used', False) else 'No'}\n"
                    f"File Size: {file_mb:.2f} MB\n\n"
                    f"Note: Password verification requires decryption."
                )
                self.after(0, lambda m=msg: messagebox.showinfo("Verification Complete", m))

            except Exception as e:
                self.after(0, lambda: self.hide_progress())
                error_msg = str(e)
                self.after(0, lambda msg=error_msg: messagebox.showerror(
                    "Verification Failed",
                    f"File verification failed:\n\n{msg}\n\n"
                    "The file may be:\n"
                    "• Not an encrypted file\n"
                    "• Corrupted or damaged\n"
                    "• Created with a different tool"
                ))

        elif operation == "Encrypt":
            self.after(0, lambda: self.show_progress("Starting encryption...", 0))
            result = crypto.encrypt_file(input_path, output_path, password, progress_callback)
            self.after(0, lambda: self.hide_progress())

            # Secure delete original if requested
            if self.shred_after_encrypt_var.get():
                self.after(0, lambda: self.show_progress("Securely deleting original file...", 0))
                from crypto_advanced import secure_delete
                secure_delete(input_path)
                self.after(0, lambda: self.hide_progress())

            orig_mb = result['original_size'] / 1024 / 1024
            final_mb = result['encrypted_size'] / 1024 / 1024

            # Add to history
            self.history.add_entry(
                operation="Encrypt",
                input_file=input_path,
                output_file=result['output_file'],
                algorithm=result['algorithm'],
                success=True
            )
            self.after(0, lambda: self.refresh_recent_files())

            msg = (
                f"✓ File encrypted successfully!\n\n"
                f"Algorithm: {result['algorithm']}\n"
                f"Key Derivation: {result['key_derivation']}\n"
                f"Original Size: {orig_mb:.2f} MB\n"
                f"Encrypted Size: {final_mb:.2f} MB\n"
                f"Compression: {result['compression_ratio']:.1f}% reduction\n"
            )
            if self.shred_after_encrypt_var.get():
                msg += f"\n✓ Original file securely deleted\n"
            msg += f"\nSaved to:\n{result['output_file']}"

            self.after(0, lambda m=msg: messagebox.showinfo("Encryption Complete", m))
        else:  # Decrypt
            self.after(0, lambda: self.show_progress("Starting decryption...", 0))
            result = crypto.decrypt_file(input_path, output_path, password, progress_callback)
            self.after(0, lambda: self.hide_progress())

            file_mb = Path(result['output_file']).stat().st_size / 1024 / 1024

            # Add to history
            self.history.add_entry(
                operation="Decrypt",
                input_file=input_path,
                output_file=result['output_file'],
                algorithm=result['algorithm'],
                success=True
            )
            self.after(0, lambda: self.refresh_recent_files())

            msg = (
                f"✓ File decrypted successfully!\n\n"
                f"Algorithm: {result['algorithm']}\n"
                f"Original Name: {result['original_filename']}\n"
                f"Integrity Check: {'✓ Verified' if result['hash_verified'] else '✗ Failed'}\n"
                f"Compression Used: {'Yes' if result['compression_used'] else 'No'}\n"
                f"File Size: {file_mb:.2f} MB\n\n"
                f"Saved to:\n{result['output_file']}"
            )
            self.after(0, lambda m=msg: messagebox.showinfo("Decryption Complete", m))

    def _process_batch(self, crypto, input_folder, output_folder, password, operation):
        """Process batch folder"""
        from batch_crypto import BatchCrypto

        # Auto-generate output folder
        if not output_folder:
            if operation == "Encrypt":
                output_folder = input_folder + "_encrypted"
            else:
                output_folder = input_folder + "_decrypted"

        # Create batch processor
        batch = BatchCrypto(crypto)

        # Batch progress callback
        def batch_progress(current, total, filename):
            pct = int((current / total) * 100)
            self.after(0, lambda c=current, t=total, f=filename, p=pct:
                      self.show_progress(f"{operation}ing {c}/{t}: {f}", p))

        # Process folder
        self.after(0, lambda: self.show_progress(f"Scanning folder...", 0))

        if operation == "Encrypt":
            results = batch.encrypt_folder(
                input_folder,
                output_folder,
                password,
                recursive=True,
                progress_callback=batch_progress
            )
        else:
            # For decryption, collect all .encrypted files
            input_path = Path(input_folder)
            encrypted_files = [str(f) for f in input_path.rglob('*.encrypted') if f.is_file()]

            if not encrypted_files:
                self.after(0, lambda: self.hide_progress())
                self.after(0, lambda: messagebox.showerror(
                    "No Encrypted Files",
                    f"No .encrypted files found in:\n\n{input_folder}\n\n"
                    "Please select a folder containing encrypted files."
                ))
                return

            results = batch.decrypt_files(
                encrypted_files,
                output_folder,
                password,
                progress_callback=batch_progress
            )

        self.after(0, lambda: self.hide_progress())

        # Secure delete originals if requested (encryption only)
        if operation == "Encrypt" and self.shred_after_encrypt_var.get() and results['success'] > 0:
            self.after(0, lambda: self.show_progress("Securely deleting original files...", 0))
            from crypto_advanced import secure_delete
            for file_info in results['files']:
                if file_info['status'] == 'success':
                    try:
                        secure_delete(file_info['file'])
                    except Exception:
                        pass  # Continue even if deletion fails
            self.after(0, lambda: self.hide_progress())

        # Show summary
        total_size = sum(f.get('size', 0) for f in results['files'] if f['status'] == 'success') / 1024 / 1024

        msg = (
            f"✓ Batch {operation.lower()} complete!\n\n"
            f"Total Files: {results['total']}\n"
            f"✓ Success: {results['success']}\n"
            f"✗ Failed: {results['failed']}\n"
        )
        if operation == "Encrypt":
            msg += f"Total Size: {total_size:.2f} MB\n"
            if self.shred_after_encrypt_var.get() and results['success'] > 0:
                msg += f"\n✓ Original files securely deleted\n"
        msg += f"\nSaved to:\n{output_folder}"

        if results['failed'] > 0:
            msg += f"\n\n⚠ {results['failed']} file(s) failed to process."

        self.after(0, lambda m=msg: messagebox.showinfo("Batch Processing Complete", m))

    def save_preferences(self):
        """Save current preferences to config"""
        self.config.update({
            'theme': self.theme_var.get(),
            'algorithm': self.algorithm_var.get(),
            'use_argon2': self.use_argon2_var.get(),
            'use_compression': self.use_compression_var.get(),
            'multi_layer': self.multi_layer_var.get(),
            'batch_mode': self.batch_mode_var.get(),
            'shred_after_encrypt': self.shred_after_encrypt_var.get()
        })

    def on_closing(self):
        """Handle window close event"""
        # Save preferences before closing
        self.save_preferences()
        # Close the window
        self.destroy()

    def _enable_drag_drop(self, widget, callback):
        """Enable drag and drop for a widget"""
        if not DRAG_DROP_AVAILABLE:
            # Drag & drop not available, skip silently
            return

        try:
            # Register the widget as a drop target
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind('<<Drop>>', callback)

            # Visual feedback on drag over
            widget.dnd_bind('<<DragEnter>>', lambda e: self._on_drag_enter(widget))
            widget.dnd_bind('<<DragLeave>>', lambda e: self._on_drag_leave(widget))
        except Exception:
            # If drag & drop setup fails, continue without it
            pass

    def _on_drag_enter(self, widget):
        """Visual feedback when dragging over widget"""
        widget.configure(border_color=("#3b82f6", "#60a5fa"))

    def _on_drag_leave(self, widget):
        """Reset visual feedback when leaving widget"""
        widget.configure(border_color=("gray85", "gray25"))

    def on_input_drop(self, event):
        """Handle file/folder drop on input field"""
        try:
            # Get dropped file path
            dropped_path = event.data

            # Handle Windows format (may have curly braces)
            if dropped_path.startswith('{') and dropped_path.endswith('}'):
                dropped_path = dropped_path[1:-1]

            # Remove quotes if present
            dropped_path = dropped_path.strip('"').strip("'")

            # Validate path exists
            if Path(dropped_path).exists():
                self.input_file_path.set(dropped_path)

                # Auto-detect batch mode
                if Path(dropped_path).is_dir():
                    if not self.batch_mode_var.get():
                        # Auto-enable batch mode for folders
                        self.batch_mode_var.set(True)
                        self.on_batch_mode_change()
                else:
                    if self.batch_mode_var.get():
                        # Ask user if they want to disable batch mode
                        result = messagebox.askyesno(
                            "Disable Batch Mode?",
                            "You dropped a single file, but batch mode is enabled.\n\n"
                            "Do you want to disable batch mode?"
                        )
                        if result:
                            self.batch_mode_var.set(False)
                            self.on_batch_mode_change()

                # Clear output path
                self.output_file_path.set("")

                # Reset border color
                self._on_drag_leave(self.input_entry)
            else:
                messagebox.showerror(
                    "Invalid Path",
                    f"The dropped path does not exist:\n\n{dropped_path}"
                )
                self._on_drag_leave(self.input_entry)
        except Exception as e:
            messagebox.showerror(
                "Drop Error",
                f"Failed to process dropped file:\n\n{str(e)}"
            )
            self._on_drag_leave(self.input_entry)

    def on_output_drop(self, event):
        """Handle file/folder drop on output field"""
        try:
            # Get dropped file path
            dropped_path = event.data

            # Handle Windows format (may have curly braces)
            if dropped_path.startswith('{') and dropped_path.endswith('}'):
                dropped_path = dropped_path[1:-1]

            # Remove quotes if present
            dropped_path = dropped_path.strip('"').strip("'")

            # For output, accept both files and folders
            if Path(dropped_path).exists():
                # If it's a file, use its parent directory for batch mode
                if self.batch_mode_var.get() and Path(dropped_path).is_file():
                    dropped_path = str(Path(dropped_path).parent)

                self.output_file_path.set(dropped_path)
                self._on_drag_leave(self.output_entry)
            else:
                messagebox.showerror(
                    "Invalid Path",
                    f"The dropped path does not exist:\n\n{dropped_path}"
                )
                self._on_drag_leave(self.output_entry)
        except Exception as e:
            messagebox.showerror(
                "Drop Error",
                f"Failed to process dropped file:\n\n{str(e)}"
            )
            self._on_drag_leave(self.output_entry)


def main():
    """Launch application"""
    try:
        app = ModernCryptoGUI()
        app.mainloop()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"Application failed to start:\n\n{str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
