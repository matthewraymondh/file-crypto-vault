"""
Modern Minimalist GUI for File Encryption & Decryption
Design: Dark/Light theme with modern aesthetics

Author: Matthew Raymond Hartono
NIM: A11.2021.13275
"""

import os
import threading
from pathlib import Path
from tkinter import filedialog, messagebox
import customtkinter as ctk
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DRAG_DROP_AVAILABLE = True
except ImportError:
    DRAG_DROP_AVAILABLE = False
from crypto_file import FileCrypto


# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class CryptoGUI(ctk.CTk):
    """Main GUI Application"""

    def __init__(self):
        super().__init__()

        # Window configuration
        self.title("File Crypto - Encryption & Decryption")
        self.geometry("900x750")
        self.resizable(True, True)

        # Set minimum size
        self.minsize(800, 750)

        # Variables
        self.input_file_path = ctk.StringVar()
        self.output_file_path = ctk.StringVar()
        self.password_var = ctk.StringVar()
        self.algorithm_var = ctk.StringVar(value="AES")
        self.operation_var = ctk.StringVar(value="Encrypt")
        self.theme_var = ctk.StringVar(value="dark")

        # Create UI
        self.create_widgets()

        # Center window
        self.center_window()

    def center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        """Create all GUI widgets"""

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ============ HEADER ============
        self.create_header()

        # ============ MAIN CONTENT ============
        self.create_main_content()

        # ============ FOOTER ============
        self.create_footer()

    def create_header(self):
        """Create header section"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="🔐 File Encryption & Decryption",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 5))

        # Subtitle
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Secure your files with AES-256 or ChaCha20 encryption",
            font=ctk.CTkFont(size=13),
            text_color="gray"
        )
        subtitle_label.grid(row=1, column=0, columnspan=2)

        # Theme toggle button (top right)
        self.theme_button = ctk.CTkButton(
            header_frame,
            text="🌙",
            width=40,
            height=40,
            font=ctk.CTkFont(size=20),
            command=self.toggle_theme
        )
        self.theme_button.grid(row=0, column=2, rowspan=2, padx=(10, 0))

    def create_main_content(self):
        """Create main content area"""
        main_frame = ctk.CTkFrame(self, corner_radius=15)
        main_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)

        # ============ OPERATION SELECTION ============
        operation_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        operation_frame.grid(row=0, column=0, padx=30, pady=(20, 15), sticky="ew")
        operation_frame.grid_columnconfigure((0, 1), weight=1)

        # Encrypt/Decrypt Toggle
        encrypt_button = ctk.CTkRadioButton(
            operation_frame,
            text="🔒 Encrypt",
            variable=self.operation_var,
            value="Encrypt",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.on_operation_change
        )
        encrypt_button.grid(row=0, column=0, padx=10, sticky="w")

        decrypt_button = ctk.CTkRadioButton(
            operation_frame,
            text="🔓 Decrypt",
            variable=self.operation_var,
            value="Decrypt",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.on_operation_change
        )
        decrypt_button.grid(row=0, column=1, padx=10, sticky="w")

        # ============ ALGORITHM SELECTION ============
        algo_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        algo_frame.grid(row=1, column=0, padx=30, pady=(0, 15), sticky="ew")
        algo_frame.grid_columnconfigure((0, 1), weight=1)

        algo_label = ctk.CTkLabel(
            algo_frame,
            text="Algorithm:",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        algo_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        aes_button = ctk.CTkRadioButton(
            algo_frame,
            text="AES-256-GCM",
            variable=self.algorithm_var,
            value="AES",
            font=ctk.CTkFont(size=13)
        )
        aes_button.grid(row=1, column=0, padx=10, sticky="w")

        chacha_button = ctk.CTkRadioButton(
            algo_frame,
            text="ChaCha20-Poly1305",
            variable=self.algorithm_var,
            value="ChaCha20",
            font=ctk.CTkFont(size=13)
        )
        chacha_button.grid(row=1, column=1, padx=10, sticky="w")

        # ============ FILE INPUT ============
        input_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        input_frame.grid(row=2, column=0, padx=30, pady=(0, 15), sticky="ew")
        input_frame.grid_columnconfigure(1, weight=1)

        input_label = ctk.CTkLabel(
            input_frame,
            text="Input File:",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        input_label.grid(row=0, column=0, sticky="w", pady=(0, 8))

        # Drag and drop area
        self.input_drop_frame = ctk.CTkFrame(
            input_frame,
            height=60,
            corner_radius=10,
            border_width=2,
            border_color="gray40"
        )
        self.input_drop_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        self.input_drop_frame.grid_columnconfigure(0, weight=1)
        self.input_drop_frame.grid_propagate(False)

        # Register drag and drop if available
        if DRAG_DROP_AVAILABLE:
            try:
                self.input_drop_frame.drop_target_register(DND_FILES)
                self.input_drop_frame.dnd_bind('<<Drop>>', self.on_drop_input)
                drop_text = "📁 Drag & Drop file here or click Browse"
            except:
                drop_text = "📁 Click Browse to select file"
        else:
            drop_text = "📁 Click Browse to select file"

        self.input_drop_label = ctk.CTkLabel(
            self.input_drop_frame,
            text=drop_text,
            font=ctk.CTkFont(size=13),
            text_color="gray"
        )
        self.input_drop_label.grid(row=0, column=0, pady=20)

        # Input entry
        self.input_entry = ctk.CTkEntry(
            input_frame,
            textvariable=self.input_file_path,
            placeholder_text="No file selected",
            height=35,
            font=ctk.CTkFont(size=12)
        )
        self.input_entry.grid(row=2, column=0, columnspan=2, sticky="ew", padx=(0, 10))

        # Browse button
        browse_input_btn = ctk.CTkButton(
            input_frame,
            text="Browse",
            width=100,
            height=35,
            command=self.browse_input_file
        )
        browse_input_btn.grid(row=2, column=2)

        # ============ OUTPUT FILE ============
        output_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        output_frame.grid(row=3, column=0, padx=30, pady=(0, 12), sticky="ew")
        output_frame.grid_columnconfigure(1, weight=1)

        output_label = ctk.CTkLabel(
            output_frame,
            text="Output File:",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        output_label.grid(row=0, column=0, sticky="w", pady=(0, 8))

        # Output entry
        self.output_entry = ctk.CTkEntry(
            output_frame,
            textvariable=self.output_file_path,
            placeholder_text="Auto-generated from input file",
            height=35,
            font=ctk.CTkFont(size=12)
        )
        self.output_entry.grid(row=1, column=0, columnspan=2, sticky="ew", padx=(0, 10))

        # Browse button
        browse_output_btn = ctk.CTkButton(
            output_frame,
            text="Browse",
            width=100,
            height=35,
            command=self.browse_output_file
        )
        browse_output_btn.grid(row=1, column=2)

        # ============ PASSWORD ============
        password_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        password_frame.grid(row=4, column=0, padx=30, pady=(0, 12), sticky="ew")
        password_frame.grid_columnconfigure(0, weight=1)

        password_label = ctk.CTkLabel(
            password_frame,
            text="Password:",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        password_label.grid(row=0, column=0, sticky="w", pady=(0, 8))

        # Password entry
        self.password_entry = ctk.CTkEntry(
            password_frame,
            textvariable=self.password_var,
            placeholder_text="Enter strong password (min 8 characters)",
            show="•",
            height=40,
            font=ctk.CTkFont(size=13)
        )
        self.password_entry.grid(row=1, column=0, sticky="ew", padx=(0, 10))

        # Show/Hide password button
        self.show_password_btn = ctk.CTkButton(
            password_frame,
            text="👁",
            width=40,
            height=40,
            font=ctk.CTkFont(size=18),
            command=self.toggle_password_visibility
        )
        self.show_password_btn.grid(row=1, column=1)
        self.password_visible = False

        # ============ PROGRESS BAR ============
        self.progress_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.progress_frame.grid(row=5, column=0, padx=30, pady=(0, 12), sticky="ew")
        self.progress_frame.grid_columnconfigure(0, weight=1)

        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.progress_label.grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, height=8)
        self.progress_bar.grid(row=1, column=0, sticky="ew")
        self.progress_bar.set(0)
        self.progress_frame.grid_remove()  # Hide initially

        # ============ ACTION BUTTON ============
        self.action_button = ctk.CTkButton(
            main_frame,
            text="🔒 ENCRYPT FILE",
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.process_file,
            fg_color="#1f6aa5",
            hover_color="#144870"
        )
        self.action_button.grid(row=6, column=0, padx=30, pady=(0, 20), sticky="ew")

    def create_footer(self):
        """Create footer section"""
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="ew")

        # Info label
        info_label = ctk.CTkLabel(
            footer_frame,
            text="✨ Supported: Video files (MP4, AVI, MKV, MOV, etc.) and all other file types",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        info_label.pack()

        # Credit label
        credit_label = ctk.CTkLabel(
            footer_frame,
            text="Created by: Matthew Raymond Hartono | NIM: A11.2021.13275",
            font=ctk.CTkFont(size=10),
            text_color="gray60"
        )
        credit_label.pack(pady=(5, 0))

    def on_operation_change(self):
        """Handle operation change (Encrypt/Decrypt)"""
        if self.operation_var.get() == "Encrypt":
            self.action_button.configure(
                text="🔒 ENCRYPT FILE",
                fg_color="#1f6aa5",
                hover_color="#144870"
            )
        else:
            self.action_button.configure(
                text="🔓 DECRYPT FILE",
                fg_color="#2d7a3e",
                hover_color="#1e5229"
            )

    def toggle_theme(self):
        """Toggle between dark and light theme"""
        if self.theme_var.get() == "dark":
            ctk.set_appearance_mode("light")
            self.theme_var.set("light")
            self.theme_button.configure(text="☀️")
        else:
            ctk.set_appearance_mode("dark")
            self.theme_var.set("dark")
            self.theme_button.configure(text="🌙")

    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.password_visible:
            self.password_entry.configure(show="•")
            self.password_visible = False
        else:
            self.password_entry.configure(show="")
            self.password_visible = True

    def on_drop_input(self, event):
        """Handle file drop event"""
        # Get file path (remove curly braces if present)
        file_path = event.data.strip('{}')
        self.input_file_path.set(file_path)
        self.update_drop_label()
        self.auto_generate_output_path()

    def update_drop_label(self):
        """Update drag and drop label"""
        if self.input_file_path.get():
            filename = Path(self.input_file_path.get()).name
            self.input_drop_label.configure(
                text=f"✓ {filename}",
                text_color="green"
            )
        else:
            self.input_drop_label.configure(
                text="📁 Drag & Drop file here or click Browse",
                text_color="gray"
            )

    def browse_input_file(self):
        """Browse for input file"""
        filename = filedialog.askopenfilename(
            title="Select Input File",
            filetypes=[
                ("All Files", "*.*"),
                ("Video Files", "*.mp4 *.avi *.mkv *.mov *.flv *.wmv"),
                ("Encrypted Files", "*.encrypted")
            ]
        )
        if filename:
            self.input_file_path.set(filename)
            self.update_drop_label()
            self.auto_generate_output_path()

    def browse_output_file(self):
        """Browse for output file"""
        operation = self.operation_var.get()

        if operation == "Encrypt":
            filename = filedialog.asksaveasfilename(
                title="Save Encrypted File As",
                defaultextension=".encrypted",
                filetypes=[("Encrypted Files", "*.encrypted"), ("All Files", "*.*")]
            )
        else:
            filename = filedialog.asksaveasfilename(
                title="Save Decrypted File As",
                filetypes=[("All Files", "*.*")]
            )

        if filename:
            self.output_file_path.set(filename)

    def auto_generate_output_path(self):
        """Auto-generate output file path"""
        input_path = self.input_file_path.get()
        if not input_path:
            return

        operation = self.operation_var.get()

        if operation == "Encrypt":
            output_path = input_path + ".encrypted"
        else:
            if input_path.endswith(".encrypted"):
                # Remove .encrypted and restore original extension
                output_path = input_path[:-10]  # Remove ".encrypted"
                # Add _decrypted before the extension
                path_obj = Path(output_path)
                if path_obj.suffix:
                    # Has extension: video.mp4 -> video_decrypted.mp4
                    output_path = str(path_obj.with_stem(path_obj.stem + "_decrypted"))
                else:
                    # No extension: just add _decrypted
                    output_path = output_path + "_decrypted"
            else:
                # If not .encrypted file, just add _decrypted before extension
                path_obj = Path(input_path)
                if path_obj.suffix:
                    output_path = str(path_obj.with_stem(path_obj.stem + "_decrypted"))
                else:
                    output_path = input_path + "_decrypted"

        self.output_file_path.set(output_path)

    def validate_inputs(self):
        """Validate user inputs"""
        if not self.input_file_path.get():
            messagebox.showerror("Error", "Please select an input file!")
            return False

        if not Path(self.input_file_path.get()).exists():
            messagebox.showerror("Error", "Input file does not exist!")
            return False

        if not self.password_var.get():
            messagebox.showerror("Error", "Please enter a password!")
            return False

        if len(self.password_var.get()) < 8:
            result = messagebox.askyesno(
                "Weak Password",
                "Password is less than 8 characters. It's recommended to use a stronger password.\n\nContinue anyway?"
            )
            if not result:
                return False

        if not self.output_file_path.get():
            self.auto_generate_output_path()

        return True

    def show_progress(self, message):
        """Show progress bar with message"""
        self.progress_frame.grid()
        self.progress_label.configure(text=message)
        self.progress_bar.set(0)
        self.progress_bar.start()

    def hide_progress(self):
        """Hide progress bar"""
        self.progress_bar.stop()
        self.progress_bar.set(0)
        self.progress_frame.grid_remove()

    def process_file(self):
        """Process file (encrypt or decrypt)"""
        if not self.validate_inputs():
            return

        # Disable button during processing
        self.action_button.configure(state="disabled")

        # Run in separate thread to avoid GUI freeze
        thread = threading.Thread(target=self._process_file_thread)
        thread.daemon = True
        thread.start()

    def _process_file_thread(self):
        """Process file in separate thread"""
        try:
            operation = self.operation_var.get()
            algorithm = self.algorithm_var.get()
            input_file = self.input_file_path.get()
            output_file = self.output_file_path.get()
            password = self.password_var.get()

            # Show progress
            self.after(0, lambda: self.show_progress(f"{operation}ing file..."))

            # Create crypto instance
            crypto = FileCrypto(algorithm)

            # Perform operation
            if operation == "Encrypt":
                result = crypto.encrypt_file(input_file, output_file, password)

                # Success message
                self.after(0, lambda: self.hide_progress())
                self.after(0, lambda: messagebox.showinfo(
                    "Success",
                    f"File encrypted successfully!\n\n"
                    f"Algorithm: {result['algorithm']}\n"
                    f"Output: {result['output_file']}\n"
                    f"Original Size: {result['original_size']:,} bytes\n"
                    f"Encrypted Size: {result['encrypted_size']:,} bytes\n"
                    f"File Type: {'VIDEO' if result['is_video'] else 'OTHER'}"
                ))
            else:
                result = crypto.decrypt_file(input_file, output_file, password)

                # Success message
                self.after(0, lambda: self.hide_progress())
                self.after(0, lambda: messagebox.showinfo(
                    "Success",
                    f"File decrypted successfully!\n\n"
                    f"Algorithm: {result['algorithm']}\n"
                    f"Output: {result['output_file']}\n"
                    f"Original Filename: {result['original_filename']}\n"
                    f"File Type: {result['file_type'].upper()}\n"
                    f"Size: {result['decrypted_size']:,} bytes"
                ))

        except FileNotFoundError as e:
            self.after(0, lambda: self.hide_progress())
            self.after(0, lambda: messagebox.showerror("Error", f"File not found: {str(e)}"))
        except ValueError as e:
            self.after(0, lambda: self.hide_progress())
            self.after(0, lambda: messagebox.showerror("Error", f"Decryption failed: {str(e)}\n\nPassword may be incorrect or file is corrupted."))
        except Exception as e:
            self.after(0, lambda: self.hide_progress())
            self.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
        finally:
            # Re-enable button
            self.after(0, lambda: self.action_button.configure(state="normal"))


def main():
    """Run the GUI application"""
    app = CryptoGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
