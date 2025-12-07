#!/usr/bin/env python3
"""
X-Seti - July03 2023 - SSH File Sync GUI - Version: 4
this belongs in apps/components/Ssh_sync/ssh_sync_gui.py

SSH File Sync - Bidirectional file synchronization between two Linux machines
"""

import os
import tempfile
import subprocess
import shutil
import struct
import sys
import io
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from PyQt6.QtWidgets import (QApplication, QSlider, QCheckBox,
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QListWidget, QDialog, QFormLayout, QSpinBox,  QListWidgetItem, QLabel, QPushButton, QFrame, QFileDialog, QLineEdit, QTextEdit, QMessageBox, QScrollArea, QGroupBox, QTableWidget, QTableWidgetItem, QColorDialog, QHeaderView, QAbstractItemView, QMenu, QComboBox, QInputDialog, QTabWidget, QDoubleSpinBox, QRadioButton
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPoint, QRect, QByteArray, QTimer
from PyQt6.QtGui import QFont, QIcon, QPixmap, QImage, QPainter, QPen, QBrush, QColor, QCursor
from PyQt6.QtSvg import QSvgRenderer

# Add root directory to path
App_name = "SSH File Sync"
DEBUG_STANDALONE = True

class SSHSyncGUI(QWidget):
    """SSH File Sync - Main window"""

    sync_completed = pyqtSignal()

    def __init__(self, parent=None, main_window=None): #vers 1
        """initialize_features"""
        if DEBUG_STANDALONE and main_window is None:
            print(f"{App_name} Initializing ...")

        super().__init__(parent)

        self.main_window = main_window

        self.button_display_mode = 'both'
        
        # SSH Connection settings
        self.remote_host = ""
        self.remote_user = ""
        self.remote_port = 22
        self.remote_password = ""  # Will be stored securely
        self.use_password = False  # Use password instead of key
        self.ssh_key_path = str(Path.home() / ".ssh" / "id_ed25519")
        self.local_export_path = str(Path.home() / "Desktop" / "export")
        self.local_import_path = str(Path.home() / "Desktop" / "import")
        self.remote_export_path = "~/Desktop/export"
        self.remote_import_path = "~/Desktop/import"
        self.auto_sync_enabled = False
        self.sync_interval = 60  # seconds
        self.delete_extra_files = False  # Whether to delete files not in source
        
        # Sync state
        self.connected = False
        self.syncing = False
        
        # Auto-sync timer
        self.sync_timer = QTimer()
        self.sync_timer.timeout.connect(self._auto_sync)
        
        # App settings reference (if available)
        self.app_settings = None
        if main_window and hasattr(main_window, 'app_settings'):
            self.app_settings = main_window.app_settings

        # Set default fonts - will be overridden by app_settings if available
        from PyQt6.QtGui import QFont
        
        # Check if we have app_settings for fonts
        if self.app_settings and hasattr(self.app_settings, 'current_settings'):
            try:
                # Get font settings from app_settings
                font_family = self.app_settings.current_settings.get('font_family', 'Segoe UI')
                font_size = self.app_settings.current_settings.get('font_size', 12)
                panel_font_family = self.app_settings.current_settings.get('panel_font_family', 'Segoe UI')
                panel_font_size = self.app_settings.current_settings.get('panel_font_size', 12)
                button_font_family = self.app_settings.current_settings.get('button_font_family', 'Segoe UI')
                button_font_size = self.app_settings.current_settings.get('button_font_size', 12)
                button_font_weight = self.app_settings.current_settings.get('button_font_weight', 'normal')
                
                default_font = QFont(font_family, font_size)
                self.title_font = QFont(font_family, font_size + 2)
                self.panel_font = QFont(panel_font_family, panel_font_size)
                self.button_font = QFont(button_font_family, button_font_size)
                if button_font_weight == 'bold':
                    self.button_font.setBold(True)
                self.infobar_font = QFont("Courier New", 12)
            except Exception as e:
                print(f"Error loading fonts from app_settings: {e}")
                # Fallback to defaults
                default_font = QFont("Segoe UI", 9)
                self.title_font = QFont("Segoe UI", 12)
                self.panel_font = QFont("Segoe UI", 11)
                self.button_font = QFont("Segoe UI", 11)
                self.button_font.setBold(True)
                self.infobar_font = QFont("Courier New", 11)
        else:
            # Use default fonts
            default_font = QFont("Segoe UI", 9)
            self.title_font = QFont("Segoe UI", 12)
            self.panel_font = QFont("Segoe UI", 11)
            self.button_font = QFont("Segoe UI", 11)
            self.button_font.setBold(True)
            self.infobar_font = QFont("Courier New", 11)
        
        self.setFont(default_font)

        self.background_color = QColor(42, 42, 42)
        self.setMinimumSize(200, 200)

        # Docking state
        self.is_docked = (main_window is not None)
        self.dock_widget = None

        self.setWindowTitle(App_name + ": Disconnected")
        self.resize(1400, 800)
        self.use_system_titlebar = False
        self.window_always_on_top = False

        # Window flags
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self._initialize_features()

        # Corner resize variables
        self.dragging = False
        self.drag_position = None
        self.resizing = False
        self.resize_corner = None
        self.corner_size = 20
        self.hover_corner = None

        if parent:
            parent_pos = parent.pos()
            self.move(parent_pos.x() + 50, parent_pos.y() + 80)

        # Setup UI FIRST
        self.setup_ui()

        # Set window icon
        icon_pixmap = self._create_app_icon_pixmap(64)
        from PyQt6.QtGui import QIcon
        self.setWindowIcon(QIcon(icon_pixmap))

        # Setup hotkeys
        self._setup_hotkeys()

        # Apply theme ONCE at the end
        self._apply_theme()

        if hasattr(self, '_update_dock_button_visibility'):
            self._update_dock_button_visibility()

        if self.main_window and hasattr(self.main_window, 'app_settings'):
            self.update()  # Force widget repaint

        # Enable mouse tracking
        self.setMouseTracking(True)

        if DEBUG_STANDALONE:
            print(f"{App_name} initialized")

    def setup_ui(self): #vers 1
        """Setup the main UI layout"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Toolbar
        toolbar = self._create_toolbar()
        main_layout.addWidget(toolbar)

        # Main splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Create all panels
        left_panel = self._create_left_panel()      # Local files
        middle_panel = self._create_middle_panel()  # Remote files
        right_panel = self._create_right_panel()    # Status & Controls

        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(middle_panel)
        main_splitter.addWidget(right_panel)
        
        # Set proportions (2:2:3)
        main_splitter.setStretchFactor(0, 2)
        main_splitter.setStretchFactor(1, 2)
        main_splitter.setStretchFactor(2, 3)

        main_layout.addWidget(main_splitter)

        # Status indicators
        status_frame = self._setup_status_indicators()
        main_layout.addWidget(status_frame)


    def _initialize_features(self): #vers 1
        """Initialize all features after UI setup"""
        try:
            self._apply_theme()
            self._update_status_indicators()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message("All features initialized")

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Feature init error: {str(e)}")


    def _create_status_bar(self): #vers 1
        """Create bottom status bar - single line compact"""
        from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel

        status_bar = QFrame()
        status_bar.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        status_bar.setFixedHeight(22)

        layout = QHBoxLayout(status_bar)
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(15)

        # Left: Ready
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

        return status_bar


    def _show_workshop_settings(self): #vers 1
        """Show SSH Sync settings dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("SSH Sync Settings")
        dialog.setMinimumSize(600, 500)

        layout = QVBoxLayout(dialog)

        # Create tab widget
        tabs = QTabWidget()

        # Connection Tab
        connection_tab = self._create_connection_settings_tab()
        tabs.addTab(connection_tab, "Connection")

        # Sync Tab
        sync_tab = self._create_sync_settings_tab()
        tabs.addTab(sync_tab, "Sync Options")

        layout.addWidget(tabs)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._apply_settings()
            self._apply_theme()


    def _create_connection_settings_tab(self): #vers 1
        """Create Connection settings tab for SSH configuration"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Connection group
        conn_group = QGroupBox("SSH Connection")
        conn_layout = QFormLayout()

        # Remote Host
        self.host_input = QLineEdit(self.remote_host)
        self.host_input.setPlaceholderText("192.168.1.100 or hostname")
        conn_layout.addRow("Remote Host:", self.host_input)

        # Remote User
        self.user_input = QLineEdit(self.remote_user)
        self.user_input.setPlaceholderText("username")
        conn_layout.addRow("Remote User:", self.user_input)

        # Port
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(self.remote_port)
        conn_layout.addRow("Port:", self.port_input)

        # Authentication method
        auth_label = QLabel("Authentication:")
        conn_layout.addRow(auth_label, QLabel(""))
        
        self.auth_key_radio = QRadioButton("SSH Key")
        self.auth_password_radio = QRadioButton("Password")
        self.auth_key_radio.setChecked(not self.use_password)
        self.auth_password_radio.setChecked(self.use_password)
        
        auth_layout = QHBoxLayout()
        auth_layout.addWidget(self.auth_key_radio)
        auth_layout.addWidget(self.auth_password_radio)
        conn_layout.addRow("", auth_layout)

        # SSH Key Path
        key_layout = QHBoxLayout()
        self.key_path_input = QLineEdit(self.ssh_key_path)
        key_browse_btn = QPushButton("Browse...")
        key_browse_btn.clicked.connect(self._browse_ssh_key)
        key_layout.addWidget(self.key_path_input)
        key_layout.addWidget(key_browse_btn)
        conn_layout.addRow("SSH Key:", key_layout)

        # Password
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("SSH password (stored securely)")
        conn_layout.addRow("Password:", self.password_input)
        
        # Toggle password visibility button
        show_password_btn = QPushButton("Show")
        show_password_btn.setFixedWidth(50)
        show_password_btn.setCheckable(True)
        show_password_btn.toggled.connect(
            lambda checked: self.password_input.setEchoMode(
                QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
            )
        )
        show_password_btn.toggled.connect(
            lambda checked: show_password_btn.setText("Hide" if checked else "Show")
        )
        
        # Enable/disable based on auth method
        self.auth_key_radio.toggled.connect(lambda checked: self.key_path_input.setEnabled(checked))
        self.auth_key_radio.toggled.connect(lambda checked: key_browse_btn.setEnabled(checked))
        self.auth_password_radio.toggled.connect(lambda checked: self.password_input.setEnabled(checked))

        conn_group.setLayout(conn_layout)
        layout.addWidget(conn_group)

        # Paths group
        paths_group = QGroupBox("Sync Paths")
        paths_layout = QFormLayout()

        # Local Export
        local_export_layout = QHBoxLayout()
        self.local_export_input = QLineEdit(self.local_export_path)
        local_export_browse = QPushButton("Browse...")
        local_export_browse.clicked.connect(lambda: self._browse_local_path(self.local_export_input))
        local_export_layout.addWidget(self.local_export_input)
        local_export_layout.addWidget(local_export_browse)
        paths_layout.addRow("Local Export:", local_export_layout)

        # Local Import
        local_import_layout = QHBoxLayout()
        self.local_import_input = QLineEdit(self.local_import_path)
        local_import_browse = QPushButton("Browse...")
        local_import_browse.clicked.connect(lambda: self._browse_local_path(self.local_import_input))
        local_import_layout.addWidget(self.local_import_input)
        local_import_layout.addWidget(local_import_browse)
        paths_layout.addRow("Local Import:", local_import_layout)

        # Remote Export
        self.remote_export_input = QLineEdit(self.remote_export_path)
        paths_layout.addRow("Remote Export:", self.remote_export_input)

        # Remote Import
        self.remote_import_input = QLineEdit(self.remote_import_path)
        paths_layout.addRow("Remote Import:", self.remote_import_input)

        paths_group.setLayout(paths_layout)
        layout.addWidget(paths_group)

        # Test connection button
        test_btn = QPushButton("Test Connection")
        test_btn.clicked.connect(self._test_ssh_connection)
        layout.addWidget(test_btn)

        layout.addStretch()
        return tab


    def _create_sync_settings_tab(self): #vers 1
        """Create Sync Options settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Auto-sync group
        sync_group = QGroupBox("Auto-Sync")
        sync_layout = QFormLayout()

        # Enable auto-sync
        self.auto_sync_checkbox = QCheckBox("Enable Auto-Sync")
        self.auto_sync_checkbox.setChecked(self.auto_sync_enabled)
        sync_layout.addRow("", self.auto_sync_checkbox)

        # Sync interval
        self.sync_interval_input = QSpinBox()
        self.sync_interval_input.setRange(10, 3600)
        self.sync_interval_input.setValue(self.sync_interval)
        self.sync_interval_input.setSuffix(" seconds")
        sync_layout.addRow("Sync Interval:", self.sync_interval_input)

        sync_group.setLayout(sync_layout)
        layout.addWidget(sync_group)

        # Sync behavior group
        behavior_group = QGroupBox("Sync Behavior")
        behavior_layout = QVBoxLayout()

        # Delete extra files option
        self.delete_extra_checkbox = QCheckBox("Delete files not in source")
        self.delete_extra_checkbox.setChecked(self.delete_extra_files)
        self.delete_extra_checkbox.setToolTip(
            "When enabled, sync operations will delete files in destination\n"
            "that don't exist in source (uses rsync --delete flag).\n\n"
            "[WARN] Warning: This can permanently delete files!"
        )
        behavior_layout.addWidget(self.delete_extra_checkbox)
        
        # Info label
        info_label = QLabel(
            "Warning: When 'Delete files not in source' is enabled:\n"
            "  - Sync operations will remove extra files from destination\n"
            "  - Mirror and Clone operations always delete (destructive by design)\n"
            "  - Copy Selected never deletes files"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #ff9800; padding: 10px;")
        behavior_layout.addWidget(info_label)

        behavior_group.setLayout(behavior_layout)
        layout.addWidget(behavior_group)

        layout.addStretch()
        return tab


    def _browse_ssh_key(self): #vers 1
        """Browse for SSH key file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select SSH Private Key",
            str(Path.home() / ".ssh"),
            "All Files (*)"
        )
        if file_path:
            self.key_path_input.setText(file_path)


    def _browse_local_path(self, line_edit):
        """Browse for local directory"""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Select Directory",
            str(Path.home())
        )
        if dir_path:
            line_edit.setText(dir_path)


    def _test_ssh_connection(self): #vers 1
        """Test SSH connection to remote host"""
        host = self.host_input.text()
        user = self.user_input.text()
        port = self.port_input.value()
        use_password = self.auth_password_radio.isChecked()
        key_path = self.key_path_input.text()
        password = self.password_input.text()

        if not host or not user:
            QMessageBox.warning(self, "Missing Information", "Please enter host and user")
            return

        try:
            # Build SSH command based on auth method
            if use_password:
                if not password:
                    QMessageBox.warning(self, "Missing Password", "Please enter a password")
                    return
                cmd = [
                    "sshpass", "-p", password,
                    "ssh",
                    "-p", str(port),
                    "-o", "ConnectTimeout=5",
                    "-o", "StrictHostKeyChecking=no",
                    f"{user}@{host}",
                    "echo 'Connection successful'"
                ]
            else:
                cmd = [
                    "ssh",
                    "-i", key_path,
                    "-p", str(port),
                    "-o", "ConnectTimeout=5",
                    "-o", "StrictHostKeyChecking=no",
                    f"{user}@{host}",
                    "echo 'Connection successful'"
                ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                QMessageBox.information(self, "Success", "SSH connection successful!")
            else:
                error_msg = result.stderr
                if "sshpass: not found" in error_msg or "command not found" in error_msg:
                    QMessageBox.warning(self, "Missing Dependency", 
                        "Password authentication requires 'sshpass'.\n\n"
                        "Install with:\nsudo pacman -S sshpass  (Arch)\n"
                        "sudo apt install sshpass  (Ubuntu)")
                else:
                    QMessageBox.warning(self, "Connection Failed", 
                        f"Failed to connect:\n{error_msg}")
                
        except subprocess.TimeoutExpired:
            QMessageBox.warning(self, "Timeout", "Connection timed out")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection error:\n{str(e)}")


    def _apply_settings(self): #vers 1
        """Apply settings from dialog"""
        self.remote_host = self.host_input.text()
        self.remote_user = self.user_input.text()
        self.remote_port = self.port_input.value()
        self.use_password = self.auth_password_radio.isChecked()
        self.ssh_key_path = self.key_path_input.text()
        
        # Store password securely if provided
        if self.use_password and self.password_input.text():
            self.remote_password = self.password_input.text()
            self._save_password_securely()
        
        self.local_export_path = self.local_export_input.text()
        self.local_import_path = self.local_import_input.text()
        self.remote_export_path = self.remote_export_input.text()
        self.remote_import_path = self.remote_import_input.text()
        self.auto_sync_enabled = self.auto_sync_checkbox.isChecked()
        self.sync_interval = self.sync_interval_input.value()
        self.delete_extra_files = self.delete_extra_checkbox.isChecked()
        
        # Update auto-sync timer
        if self.auto_sync_enabled and self.connected:
            self.sync_timer.start(self.sync_interval * 1000)
        else:
            self.sync_timer.stop()
        
        # Refresh file lists
        self._refresh_local_files()
        self._log_status("Settings applied")
        
        # Log delete setting status
        if self.delete_extra_files:
            self._log_status("[WARN] Delete mode enabled - extra files will be removed during sync")
        else:
            self._log_status("[OK] Delete mode disabled - extra files will be preserved")

    def _save_password_securely(self): #vers 1
        """Save password securely using basic encryption"""
        # Note: For production, use python-keyring library
        # For now, we store it in memory only (not persistent)
        # To make it persistent, you'd want to use keyring:
        # import keyring
        # keyring.set_password("ssh_file_sync", self.remote_host, self.remote_password)
        self._log_status("Password saved (session only)")

    def _load_password_securely(self): #vers 1
        """Load password from secure storage"""
        # For production use keyring:
        # import keyring
        # return keyring.get_password("ssh_file_sync", self.remote_host)
        return self.remote_password

    def _build_ssh_cmd_prefix(self): #vers 1
        """Build SSH command prefix based on authentication method"""
        if self.use_password:
            password = self._load_password_securely()
            return ["sshpass", "-p", password, "ssh", "-p", str(self.remote_port)]
        else:
            return ["ssh", "-i", self.ssh_key_path, "-p", str(self.remote_port)]

    def _build_rsync_ssh_option(self): #vers 1
        """Build rsync -e SSH option based on authentication method"""
        if self.use_password:
            password = self._load_password_securely()
            return f"sshpass -p '{password}' ssh -p {self.remote_port}"
        else:
            return f"ssh -i {self.ssh_key_path} -p {self.remote_port}"


    def _create_toolbar(self): #vers 1
        """Create top toolbar with controls"""
        self.toolbar = QFrame()
        self.toolbar.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.toolbar.setMinimumHeight(40)
        toolbar_layout = QHBoxLayout(self.toolbar)
        toolbar_layout.setContentsMargins(5, 2, 5, 2)
        toolbar_layout.setSpacing(5)

        # Left side - Settings and Theme buttons
        settings_btn = QPushButton()
        settings_btn.setIcon(self._create_settings_icon())
        settings_btn.setToolTip("Connection Settings")
        settings_btn.setFixedSize(32, 32)
        settings_btn.clicked.connect(self._show_workshop_settings)
        toolbar_layout.addWidget(settings_btn)

        theme_btn = QPushButton()
        theme_btn.setIcon(self._create_theme_icon())
        theme_btn.setToolTip("Theme & Appearance Settings")
        theme_btn.setFixedSize(32, 32)
        theme_btn.clicked.connect(self._show_theme_settings)
        toolbar_layout.addWidget(theme_btn)

        toolbar_layout.addStretch()

        # Center - App icon and title
        center_widget = QWidget()
        center_layout = QHBoxLayout(center_widget)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(8)
        
        # App icon
        icon_label = QLabel()
        icon_pixmap = self._create_app_icon_pixmap(32)
        icon_label.setPixmap(icon_pixmap)
        center_layout.addWidget(icon_label)
        
        # Title label - make it draggable
        self.title_label = QLabel(App_name)
        self.title_label.setFont(self.title_font)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(self.title_label)
        
        toolbar_layout.addWidget(center_widget)

        toolbar_layout.addStretch()

        # Right side - Info and window controls
        info_btn = QPushButton()
        info_btn.setIcon(self._create_info_icon())
        info_btn.setToolTip("About")
        info_btn.setFixedSize(32, 32)
        info_btn.clicked.connect(self._show_about)
        toolbar_layout.addWidget(info_btn)

        toolbar_layout.addSpacing(10)

        # Window controls
        minimize_btn = QPushButton()
        minimize_btn.setIcon(self._create_minimize_icon())
        minimize_btn.setFixedSize(32, 32)
        minimize_btn.clicked.connect(self.showMinimized)
        toolbar_layout.addWidget(minimize_btn)

        maximize_btn = QPushButton()
        maximize_btn.setIcon(self._create_maximize_icon())
        maximize_btn.setFixedSize(32, 32)
        maximize_btn.clicked.connect(self._toggle_maximize)
        toolbar_layout.addWidget(maximize_btn)

        close_btn = QPushButton()
        close_btn.setIcon(self._create_close_icon())
        close_btn.setFixedSize(32, 32)
        close_btn.clicked.connect(self.close)
        toolbar_layout.addWidget(close_btn)

        return self.toolbar


    def _create_left_panel(self): #vers 1
        """Create left panel - Local file browser"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        layout = QVBoxLayout(panel)

        # Header
        header = QLabel("Local Files (Export)")
        header.setFont(self.title_font)
        layout.addWidget(header)

        # Path display
        self.local_path_label = QLabel(self.local_export_path)
        self.local_path_label.setFont(self.panel_font)
        layout.addWidget(self.local_path_label)

        # Icon toolbar
        toolbar = QFrame()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(2, 2, 2, 2)
        toolbar_layout.setSpacing(2)

        # Create icon buttons (30x30)
        self.local_rename_btn = QPushButton()
        self.local_rename_btn.setIcon(self._create_rename_icon())
        self.local_rename_btn.setToolTip("Rename")
        self.local_rename_btn.setFixedSize(30, 30)
        self.local_rename_btn.clicked.connect(lambda: self._rename_file("local"))
        toolbar_layout.addWidget(self.local_rename_btn)

        self.local_ignore_btn = QPushButton()
        self.local_ignore_btn.setIcon(self._create_ignore_icon())
        self.local_ignore_btn.setToolTip("Ignore File")
        self.local_ignore_btn.setFixedSize(30, 30)
        self.local_ignore_btn.clicked.connect(lambda: self._ignore_file("local"))
        toolbar_layout.addWidget(self.local_ignore_btn)

        self.local_find_btn = QPushButton()
        self.local_find_btn.setIcon(self._create_find_icon())
        self.local_find_btn.setToolTip("Find")
        self.local_find_btn.setFixedSize(30, 30)
        self.local_find_btn.clicked.connect(lambda: self._find_file("local"))
        toolbar_layout.addWidget(self.local_find_btn)

        self.local_replace_btn = QPushButton()
        self.local_replace_btn.setIcon(self._create_replace_icon())
        self.local_replace_btn.setToolTip("Replace")
        self.local_replace_btn.setFixedSize(30, 30)
        self.local_replace_btn.clicked.connect(lambda: self._replace_file("local"))
        toolbar_layout.addWidget(self.local_replace_btn)

        self.local_delete_btn = QPushButton()
        self.local_delete_btn.setIcon(self._create_delete_icon())
        self.local_delete_btn.setToolTip("Delete")
        self.local_delete_btn.setFixedSize(30, 30)
        self.local_delete_btn.clicked.connect(lambda: self._delete_file("local"))
        toolbar_layout.addWidget(self.local_delete_btn)

        self.local_adddir_btn = QPushButton()
        self.local_adddir_btn.setIcon(self._create_adddir_icon())
        self.local_adddir_btn.setToolTip("Add Directory")
        self.local_adddir_btn.setFixedSize(30, 30)
        self.local_adddir_btn.clicked.connect(lambda: self._add_directory("local"))
        toolbar_layout.addWidget(self.local_adddir_btn)

        self.local_info_btn = QPushButton()
        self.local_info_btn.setIcon(self._create_info_icon())
        self.local_info_btn.setToolTip("Info")
        self.local_info_btn.setFixedSize(30, 30)
        self.local_info_btn.clicked.connect(lambda: self._show_file_info("local"))
        toolbar_layout.addWidget(self.local_info_btn)

        toolbar_layout.addStretch()
        layout.addWidget(toolbar)

        # File list
        self.local_file_list = QListWidget()
        self.local_file_list.setFont(self.panel_font)
        self.local_file_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.local_file_list.setAlternatingRowColors(True)
        layout.addWidget(self.local_file_list)

        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._refresh_local_files)
        layout.addWidget(refresh_btn)

        return panel


    def _create_middle_panel(self): #vers 1
        """Create middle panel - Remote file browser"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        layout = QVBoxLayout(panel)

        # Header
        header = QLabel("Remote Files (Import)")
        header.setFont(self.title_font)
        layout.addWidget(header)

        # Connection status
        self.connection_status_label = QLabel("Not Connected")
        self.connection_status_label.setFont(self.panel_font)
        layout.addWidget(self.connection_status_label)

        # Icon toolbar
        toolbar = QFrame()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(2, 2, 2, 2)
        toolbar_layout.setSpacing(2)

        # Create icon buttons (30x30)
        self.remote_rename_btn = QPushButton()
        self.remote_rename_btn.setIcon(self._create_rename_icon())
        self.remote_rename_btn.setToolTip("Rename")
        self.remote_rename_btn.setFixedSize(30, 30)
        self.remote_rename_btn.clicked.connect(lambda: self._rename_file("remote"))
        self.remote_rename_btn.setEnabled(False)
        toolbar_layout.addWidget(self.remote_rename_btn)

        self.remote_ignore_btn = QPushButton()
        self.remote_ignore_btn.setIcon(self._create_ignore_icon())
        self.remote_ignore_btn.setToolTip("Ignore File")
        self.remote_ignore_btn.setFixedSize(30, 30)
        self.remote_ignore_btn.clicked.connect(lambda: self._ignore_file("remote"))
        self.remote_ignore_btn.setEnabled(False)
        toolbar_layout.addWidget(self.remote_ignore_btn)

        self.remote_find_btn = QPushButton()
        self.remote_find_btn.setIcon(self._create_find_icon())
        self.remote_find_btn.setToolTip("Find")
        self.remote_find_btn.setFixedSize(30, 30)
        self.remote_find_btn.clicked.connect(lambda: self._find_file("remote"))
        self.remote_find_btn.setEnabled(False)
        toolbar_layout.addWidget(self.remote_find_btn)

        self.remote_replace_btn = QPushButton()
        self.remote_replace_btn.setIcon(self._create_replace_icon())
        self.remote_replace_btn.setToolTip("Replace")
        self.remote_replace_btn.setFixedSize(30, 30)
        self.remote_replace_btn.clicked.connect(lambda: self._replace_file("remote"))
        self.remote_replace_btn.setEnabled(False)
        toolbar_layout.addWidget(self.remote_replace_btn)

        self.remote_delete_btn = QPushButton()
        self.remote_delete_btn.setIcon(self._create_delete_icon())
        self.remote_delete_btn.setToolTip("Delete")
        self.remote_delete_btn.setFixedSize(30, 30)
        self.remote_delete_btn.clicked.connect(lambda: self._delete_file("remote"))
        self.remote_delete_btn.setEnabled(False)
        toolbar_layout.addWidget(self.remote_delete_btn)

        self.remote_adddir_btn = QPushButton()
        self.remote_adddir_btn.setIcon(self._create_adddir_icon())
        self.remote_adddir_btn.setToolTip("Add Directory")
        self.remote_adddir_btn.setFixedSize(30, 30)
        self.remote_adddir_btn.clicked.connect(lambda: self._add_directory("remote"))
        self.remote_adddir_btn.setEnabled(False)
        toolbar_layout.addWidget(self.remote_adddir_btn)

        self.remote_info_btn = QPushButton()
        self.remote_info_btn.setIcon(self._create_info_icon())
        self.remote_info_btn.setToolTip("Info")
        self.remote_info_btn.setFixedSize(30, 30)
        self.remote_info_btn.clicked.connect(lambda: self._show_file_info("remote"))
        self.remote_info_btn.setEnabled(False)
        toolbar_layout.addWidget(self.remote_info_btn)

        toolbar_layout.addStretch()
        layout.addWidget(toolbar)

        # File list
        self.remote_file_list = QListWidget()
        self.remote_file_list.setFont(self.panel_font)
        self.remote_file_list.setAlternatingRowColors(True)
        layout.addWidget(self.remote_file_list)

        # Connect/Refresh buttons
        button_layout = QHBoxLayout()
        
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self._toggle_connection)
        button_layout.addWidget(self.connect_btn)
        
        self.refresh_remote_btn = QPushButton("Refresh")
        self.refresh_remote_btn.clicked.connect(self._refresh_remote_files)
        self.refresh_remote_btn.setEnabled(False)
        button_layout.addWidget(self.refresh_remote_btn)
        
        layout.addLayout(button_layout)

        return panel


    def _create_right_panel(self): #vers 1
        """Create right panel - Status, controls, and placeholders"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        layout = QVBoxLayout(panel)

        # Header
        header = QLabel("Sync Controls")
        header.setFont(self.title_font)
        layout.addWidget(header)

        # Sync buttons
        sync_group = QGroupBox("Sync Actions")
        sync_layout = QVBoxLayout()

        self.sync_to_remote_btn = QPushButton("Sync to Remote ->")
        self.sync_to_remote_btn.setIcon(self._create_export_icon())
        self.sync_to_remote_btn.clicked.connect(self._sync_to_remote)
        self.sync_to_remote_btn.setEnabled(False)
        sync_layout.addWidget(self.sync_to_remote_btn)

        self.sync_from_remote_btn = QPushButton("<- Sync from Remote")
        self.sync_from_remote_btn.setIcon(self._create_import_icon())
        self.sync_from_remote_btn.clicked.connect(self._sync_from_remote)
        self.sync_from_remote_btn.setEnabled(False)
        sync_layout.addWidget(self.sync_from_remote_btn)

        self.sync_both_btn = QPushButton("Sync Both <->")
        self.sync_both_btn.clicked.connect(self._sync_bidirectional)
        self.sync_both_btn.setEnabled(False)
        sync_layout.addWidget(self.sync_both_btn)

        sync_group.setLayout(sync_layout)
        layout.addWidget(sync_group)

        # Advanced operations
        advanced_group = QGroupBox("Advanced Operations")
        advanced_layout = QVBoxLayout()
        
        self.mirror_btn = QPushButton("Mirror Local -> Remote")
        self.mirror_btn.setToolTip("Make remote identical to local (destructive)")
        self.mirror_btn.clicked.connect(self._mirror_to_remote)
        self.mirror_btn.setEnabled(False)
        advanced_layout.addWidget(self.mirror_btn)
        
        self.clone_btn = QPushButton("Clone Remote -> Local")
        self.clone_btn.setToolTip("Make local identical to remote (destructive)")
        self.clone_btn.clicked.connect(self._clone_from_remote)
        self.clone_btn.setEnabled(False)
        advanced_layout.addWidget(self.clone_btn)
        
        self.copy_selected_btn = QPushButton("Copy Selected Files")
        self.copy_selected_btn.setToolTip("Copy selected files only")
        self.copy_selected_btn.clicked.connect(self._copy_selected)
        self.copy_selected_btn.setEnabled(False)
        advanced_layout.addWidget(self.copy_selected_btn)
        
        advanced_group.setLayout(advanced_layout)
        layout.addWidget(advanced_group)

        # Auto-sync control
        auto_sync_group = QGroupBox("Auto-Sync")
        auto_sync_layout = QVBoxLayout()
        
        self.auto_sync_toggle = QCheckBox("Enable Auto-Sync")
        self.auto_sync_toggle.stateChanged.connect(self._toggle_auto_sync)
        auto_sync_layout.addWidget(self.auto_sync_toggle)
        
        auto_sync_group.setLayout(auto_sync_layout)
        layout.addWidget(auto_sync_group)

        # Status/Log area
        status_group = QGroupBox("Status Log")
        status_layout = QVBoxLayout()

        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setFont(self.infobar_font)
        self.status_text.setMaximumHeight(150)
        status_layout.addWidget(self.status_text)

        clear_log_btn = QPushButton("Clear Log")
        clear_log_btn.clicked.connect(self.status_text.clear)
        status_layout.addWidget(clear_log_btn)

        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        layout.addStretch()

        return panel


    def _setup_status_indicators(self): #vers 1
        """Setup status indicators at bottom"""
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        status_frame.setFixedHeight(24)

        layout = QHBoxLayout(status_frame)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(10)

        # Status label
        self.status_indicator = QLabel("[DISCONNECTED]")
        self.status_indicator.setFont(self.infobar_font)
        layout.addWidget(self.status_indicator)

        layout.addStretch()

        # Stats
        self.stats_label = QLabel("Local: 0 files | Remote: 0 files")
        self.stats_label.setFont(self.infobar_font)
        layout.addWidget(self.stats_label)

        return status_frame


    def _update_status_indicators(self): #vers 1
        """Update status bar indicators"""
        if self.connected:
            self.status_indicator.setText("[CONNECTED]")
            self.status_indicator.setStyleSheet("color: #00ff00;")
        else:
            self.status_indicator.setText("[DISCONNECTED]")
            self.status_indicator.setStyleSheet("color: #ff0000;")


    def _refresh_local_files(self): #vers 1
        """Refresh local file list"""
        self.local_file_list.clear()
        
        export_path = Path(self.local_export_path)
        if export_path.exists():
            try:
                files = sorted(export_path.iterdir())
                for file in files:
                    self.local_file_list.addItem(file.name)
                self._log_status(f"Loaded {len(files)} local files")
                self._update_file_stats()
            except Exception as e:
                self._log_status(f"Error reading local files: {e}")
        else:
            self._log_status(f"Local export path does not exist: {export_path}")


    def _refresh_remote_files(self): #vers 1
        """Refresh remote file list via SSH"""
        if not self.connected:
            self._log_status("Not connected to remote")
            return

        self.remote_file_list.clear()
        
        try:
            # List remote files
            ssh_cmd = self._build_ssh_cmd_prefix()
            cmd = ssh_cmd + [
                f"{self.remote_user}@{self.remote_host}",
                f"ls -1 {self.remote_import_path}"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                files = result.stdout.strip().split('\n')
                for file in files:
                    if file:  # Skip empty lines
                        self.remote_file_list.addItem(file)
                self._log_status(f"Loaded {len(files)} remote files")
                self._update_file_stats()
            else:
                self._log_status(f"Error listing remote files: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            self._log_status("Remote file list timed out")
        except Exception as e:
            self._log_status(f"Error listing remote files: {e}")


    def _toggle_connection(self): #vers 1
        """Toggle SSH connection"""
        if self.connected:
            self._disconnect()
        else:
            self._connect()


    def _connect(self): #vers 1
        """Connect to remote host"""
        if not self.remote_host or not self.remote_user:
            QMessageBox.warning(self, "Configuration Required", 
                "Please configure connection settings first")
            self._show_workshop_settings()
            return

        try:
            # Build SSH command based on auth method
            if self.use_password:
                # Using password authentication (requires sshpass)
                password = self._load_password_securely()
                if not password:
                    QMessageBox.warning(self, "Password Required", 
                        "Please set a password in settings")
                    return
                
                # Test with sshpass
                cmd = [
                    "sshpass", "-p", password,
                    "ssh",
                    "-p", str(self.remote_port),
                    "-o", "ConnectTimeout=5",
                    "-o", "StrictHostKeyChecking=no",
                    f"{self.remote_user}@{self.remote_host}",
                    "echo 'OK'"
                ]
            else:
                # Using key authentication
                cmd = [
                    "ssh",
                    "-i", self.ssh_key_path,
                    "-p", str(self.remote_port),
                    "-o", "ConnectTimeout=5",
                    "-o", "StrictHostKeyChecking=no",
                    f"{self.remote_user}@{self.remote_host}",
                    "echo 'OK'"
                ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.connected = True
                self.connect_btn.setText("Disconnect")
                self.connection_status_label.setText(f"Connected to {self.remote_host}")
                self.refresh_remote_btn.setEnabled(True)
                self.sync_to_remote_btn.setEnabled(True)
                self.sync_from_remote_btn.setEnabled(True)
                self.sync_both_btn.setEnabled(True)
                self.mirror_btn.setEnabled(True)
                self.clone_btn.setEnabled(True)
                self.copy_selected_btn.setEnabled(True)
                
                # Enable remote file operation buttons
                self.remote_rename_btn.setEnabled(True)
                self.remote_ignore_btn.setEnabled(True)
                self.remote_find_btn.setEnabled(True)
                self.remote_replace_btn.setEnabled(True)
                self.remote_delete_btn.setEnabled(True)
                self.remote_adddir_btn.setEnabled(True)
                self.remote_info_btn.setEnabled(True)
                
                self._update_status_indicators()
                self._log_status(f"Connected to {self.remote_user}@{self.remote_host}")
                self._refresh_remote_files()
                
                # Start auto-sync if enabled
                if self.auto_sync_enabled:
                    self.sync_timer.start(self.sync_interval * 1000)
            else:
                error_msg = result.stderr
                if "sshpass: not found" in error_msg or "command not found" in error_msg:
                    QMessageBox.warning(self, "Missing Dependency", 
                        "Password authentication requires 'sshpass' to be installed.\n\n"
                        "Install it with:\nsudo pacman -S sshpass  (Arch)\n"
                        "sudo apt install sshpass  (Ubuntu)")
                else:
                    QMessageBox.warning(self, "Connection Failed", 
                        f"Could not connect:\n{error_msg}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection error:\n{str(e)}")


    def _disconnect(self): #vers 1
        """Disconnect from remote host"""
        self.connected = False
        self.connect_btn.setText("Connect")
        self.connection_status_label.setText("Not Connected")
        self.refresh_remote_btn.setEnabled(False)
        self.sync_to_remote_btn.setEnabled(False)
        self.sync_from_remote_btn.setEnabled(False)
        self.sync_both_btn.setEnabled(False)
        self.mirror_btn.setEnabled(False)
        self.clone_btn.setEnabled(False)
        self.copy_selected_btn.setEnabled(False)
        
        # Disable remote file operation buttons
        self.remote_rename_btn.setEnabled(False)
        self.remote_ignore_btn.setEnabled(False)
        self.remote_find_btn.setEnabled(False)
        self.remote_replace_btn.setEnabled(False)
        self.remote_delete_btn.setEnabled(False)
        self.remote_adddir_btn.setEnabled(False)
        self.remote_info_btn.setEnabled(False)
        
        self.sync_timer.stop()
        self._update_status_indicators()
        self._log_status("Disconnected")


    def _sync_to_remote(self): #vers 1
        """Sync local export to remote import"""
        if not self.connected:
            return

        self._log_status("Syncing to remote...")
        try:
            cmd = [
                "rsync",
                "-avz",
            ]
            
            # Only add --delete if option is enabled
            if self.delete_extra_files:
                cmd.append("--delete")
                self._log_status("  (delete mode: removing extra files)")
            else:
                self._log_status("  (preserve mode: keeping extra files)")
            
            cmd.extend([
                "-e", self._build_rsync_ssh_option(),
                f"{self.local_export_path}/",
                f"{self.remote_user}@{self.remote_host}:{self.remote_import_path}/"
            ])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self._log_status("[OK] Sync to remote completed")
                self._refresh_remote_files()
            else:
                self._log_status(f"[FAIL] Sync failed: {result.stderr}")
                
        except Exception as e:
            self._log_status(f"[FAIL] Sync error: {e}")


    def _sync_from_remote(self): #vers 1
        """Sync remote export to local import"""
        if not self.connected:
            return

        self._log_status("Syncing from remote...")
        try:
            cmd = [
                "rsync",
                "-avz",
            ]
            
            # Only add --delete if option is enabled
            if self.delete_extra_files:
                cmd.append("--delete")
                self._log_status("  (delete mode: removing extra files)")
            else:
                self._log_status("  (preserve mode: keeping extra files)")
            
            cmd.extend([
                "-e", self._build_rsync_ssh_option(),
                f"{self.remote_user}@{self.remote_host}:{self.remote_export_path}/",
                f"{self.local_import_path}/"
            ])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self._log_status("[OK] Sync from remote completed")
                self._refresh_local_files()
            else:
                self._log_status(f"[FAIL] Sync failed: {result.stderr}")
                
        except Exception as e:
            self._log_status(f"[FAIL] Sync error: {e}")


    def _sync_bidirectional(self): #vers 1
        """Sync both directions"""
        self._sync_to_remote()
        self._sync_from_remote()

    def _mirror_to_remote(self): #vers 1
        """Mirror local to remote - makes remote identical to local (DESTRUCTIVE)"""
        if not self.connected:
            return
        
        reply = QMessageBox.warning(
            self,
            "Confirm Mirror",
            "This will make the remote directory IDENTICAL to local.\n"
            "All files on remote not in local will be DELETED!\n\n"
            "WARNING: This operation ALWAYS deletes extra files (--delete flag),\n"
            "regardless of your sync settings.\n\n"
            "Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        self._log_status("Mirroring local to remote (DESTRUCTIVE)...")
        try:
            cmd = [
                "rsync",
                "-avz",
                "--delete",  # ALWAYS delete for mirror operation
                "-e", self._build_rsync_ssh_option(),
                f"{self.local_export_path}/",
                f"{self.remote_user}@{self.remote_host}:{self.remote_import_path}/"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self._log_status("[OK] Mirror to remote completed")
                self._refresh_remote_files()
            else:
                self._log_status(f"[FAIL] Mirror failed: {result.stderr}")
                
        except Exception as e:
            self._log_status(f"[FAIL] Mirror error: {e}")

    def _clone_from_remote(self): #vers 1
        """Clone remote to local - makes local identical to remote (DESTRUCTIVE)"""
        if not self.connected:
            return
        
        reply = QMessageBox.warning(
            self,
            "Confirm Clone",
            "This will make the local directory IDENTICAL to remote.\n"
            "All files locally not on remote will be DELETED!\n\n"
            "WARNING: This operation ALWAYS deletes extra files (--delete flag),\n"
            "regardless of your sync settings.\n\n"
            "Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        self._log_status("Cloning remote to local (DESTRUCTIVE)...")
        try:
            cmd = [
                "rsync",
                "-avz",
                "--delete",  # ALWAYS delete for clone operation
                "-e", self._build_rsync_ssh_option(),
                f"{self.remote_user}@{self.remote_host}:{self.remote_export_path}/",
                f"{self.local_import_path}/"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self._log_status("[OK] Clone from remote completed")
                self._refresh_local_files()
            else:
                self._log_status(f"[FAIL] Clone failed: {result.stderr}")
                
        except Exception as e:
            self._log_status(f"[FAIL] Clone error: {e}")

    def _copy_selected(self): #vers 1
        """Copy selected files from local to remote"""
        if not self.connected:
            return
        
        selected_items = self.local_file_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select files to copy")
            return
        
        file_list = [item.text() for item in selected_items]
        self._log_status(f"Copying {len(file_list)} selected files...")
        
        try:
            for filename in file_list:
                local_file = Path(self.local_export_path) / filename
                if local_file.exists():
                    cmd = [
                        "rsync",
                        "-avz",
                        "-e", self._build_rsync_ssh_option(),
                        str(local_file),
                        f"{self.remote_user}@{self.remote_host}:{self.remote_import_path}/"
                    ]
                    
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                    
                    if result.returncode == 0:
                        self._log_status(f"[OK] Copied: {filename}")
                    else:
                        self._log_status(f"[FAIL] Failed: {filename}")
            
            self._refresh_remote_files()
            
        except Exception as e:
            self._log_status(f"[FAIL] Copy error: {e}")

    def _rename_file(self, location): #vers 2
        """Rename selected file"""
        file_list = self.local_file_list if location == "local" else self.remote_file_list
        selected = file_list.selectedItems()
        
        if not selected:
            QMessageBox.information(self, "No Selection", "Please select a file to rename")
            return
        
        old_name = selected[0].text()
        new_name, ok = QInputDialog.getText(self, "Rename File", 
            f"Rename '{old_name}' to:", text=old_name)
        
        if ok and new_name and new_name != old_name:
            if location == "local":
                try:
                    old_path = Path(self.local_export_path) / old_name
                    new_path = Path(self.local_export_path) / new_name
                    old_path.rename(new_path)
                    self._log_status(f"[OK] Renamed: {old_name} to {new_name}")
                    self._refresh_local_files()
                except Exception as e:
                    self._log_status(f"[FAIL] Rename failed: {e}")
            else:
                # Remote rename via SSH
                if not self.connected:
                    return
                try:
                    ssh_cmd = self._build_ssh_cmd_prefix()
                    cmd = ssh_cmd + [
                        f"{self.remote_user}@{self.remote_host}",
                        f"cd {self.remote_import_path} && mv '{old_name}' '{new_name}'"
                    ]
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        self._log_status(f"[OK] Renamed: {old_name} to {new_name}")
                        self._refresh_remote_files()
                    else:
                        self._log_status(f"[FAIL] Remote rename failed: {result.stderr}")
                except Exception as e:
                    self._log_status(f"[FAIL] Rename error: {e}")

    def _ignore_file(self, location): #vers 2
        """Mark file to be ignored during sync"""
        file_list = self.local_file_list if location == "local" else self.remote_file_list
        selected = file_list.selectedItems()
        
        if not selected:
            QMessageBox.information(self, "No Selection", "Please select a file to ignore")
            return
        
        filename = selected[0].text()
        # TODO: Implement ignore list functionality
        self._log_status(f"Ignore feature: {filename} (not yet implemented)")
        QMessageBox.information(self, "Not Implemented", 
            "File ignore functionality will be added in a future version.\n"
            "This will allow files to remain in destination but be excluded from sync.")

    def _find_file(self, location): #vers 1
        """Find/search files"""
        search_text, ok = QInputDialog.getText(self, "Find File", "Search for:")
        
        if ok and search_text:
            file_list = self.local_file_list if location == "local" else self.remote_file_list
            items = file_list.findItems(search_text, Qt.MatchFlag.MatchContains)
            
            if items:
                file_list.clearSelection()
                for item in items:
                    item.setSelected(True)
                file_list.scrollToItem(items[0])
                self._log_status(f"Found {len(items)} matches for '{search_text}'")
            else:
                self._log_status(f"No matches found for '{search_text}'")

    def _replace_file(self, location): #vers 1
        """Replace file with another"""
        file_list = self.local_file_list if location == "local" else self.remote_file_list
        selected = file_list.selectedItems()
        
        if not selected:
            QMessageBox.information(self, "No Selection", "Please select a file to replace")
            return
        
        target_file = selected[0].text()
        
        if location == "local":
            source_file, _ = QFileDialog.getOpenFileName(
                self, f"Select file to replace '{target_file}'", str(Path.home())
            )
            if source_file:
                try:
                    import shutil
                    dest = Path(self.local_export_path) / target_file
                    shutil.copy2(source_file, dest)
                    self._log_status(f"[OK] Replaced {target_file}")
                    self._refresh_local_files()
                except Exception as e:
                    self._log_status(f"[FAIL] Replace failed: {e}")
        else:
            QMessageBox.information(self, "Not Supported", 
                "Remote file replace not yet supported.\nUse local replace then sync.")

    def _delete_file(self, location): #vers 1
        """Delete selected file"""
        file_list = self.local_file_list if location == "local" else self.remote_file_list
        selected = file_list.selectedItems()
        
        if not selected:
            QMessageBox.information(self, "No Selection", "Please select a file to delete")
            return
        
        files_to_delete = [item.text() for item in selected]
        reply = QMessageBox.warning(
            self, "Confirm Delete",
            f"Delete {len(files_to_delete)} file(s)?\n\n" + "\n".join(files_to_delete[:5]),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        if location == "local":
            for filename in files_to_delete:
                try:
                    file_path = Path(self.local_export_path) / filename
                    if file_path.is_file():
                        file_path.unlink()
                        self._log_status(f"[OK] Deleted: {filename}")
                    elif file_path.is_dir():
                        import shutil
                        shutil.rmtree(file_path)
                        self._log_status(f"[OK] Deleted directory: {filename}")
                except Exception as e:
                    self._log_status(f"[FAIL] Delete failed {filename}: {e}")
            self._refresh_local_files()
        else:
            if not self.connected:
                return
            for filename in files_to_delete:
                try:
                    ssh_cmd = self._build_ssh_cmd_prefix()
                    cmd = ssh_cmd + [
                        f"{self.remote_user}@{self.remote_host}",
                        f"rm -rf {self.remote_import_path}/{filename}"
                    ]
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        self._log_status(f"[OK] Deleted: {filename}")
                    else:
                        self._log_status(f"[FAIL] Delete failed: {result.stderr}")
                except Exception as e:
                    self._log_status(f"[FAIL] Delete error: {e}")
            self._refresh_remote_files()

    def _add_directory(self, location): #vers 1
        """Create new directory"""
        dir_name, ok = QInputDialog.getText(self, "Add Directory", "Directory name:")
        
        if ok and dir_name:
            if location == "local":
                try:
                    new_dir = Path(self.local_export_path) / dir_name
                    new_dir.mkdir(parents=True, exist_ok=True)
                    self._log_status(f"[OK] Created directory: {dir_name}")
                    self._refresh_local_files()
                except Exception as e:
                    self._log_status(f"[FAIL] Create directory failed: {e}")
            else:
                if not self.connected:
                    return
                try:
                    ssh_cmd = self._build_ssh_cmd_prefix()
                    cmd = ssh_cmd + [
                        f"{self.remote_user}@{self.remote_host}",
                        f"mkdir -p {self.remote_import_path}/{dir_name}"
                    ]
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        self._log_status(f"[OK] Created directory: {dir_name}")
                        self._refresh_remote_files()
                    else:
                        self._log_status(f"[FAIL] Create directory failed: {result.stderr}")
                except Exception as e:
                    self._log_status(f"[FAIL] Directory error: {e}")

    def _show_file_info(self, location): #vers 2
        """Show file information"""
        file_list = self.local_file_list if location == "local" else self.remote_file_list
        selected = file_list.selectedItems()
        
        if not selected:
            QMessageBox.information(self, "No Selection", "Please select a file")
            return
        
        filename = selected[0].text()
        
        if location == "local":
            try:
                file_path = Path(self.local_export_path) / filename
                if file_path.exists():
                    stat = file_path.stat()
                    size = stat.st_size
                    modified = QDateTime.fromSecsSinceEpoch(int(stat.st_mtime)).toString()
                    is_dir = "Directory" if file_path.is_dir() else "File"
                    
                    info = f"""
File: {filename} n/
Type: {is_dir} n/
Size: {size:,} bytes ({size/1024:.2f} KB) n/
Modified: {modified} n/
Path: {file_path} n/
                    """
                    QMessageBox.information(self, "File Info", info)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not get file info: {e}")
        else:
            if not self.connected:
                return
            try:
                ssh_cmd = self._build_ssh_cmd_prefix()
                cmd = ssh_cmd + [
                    f"{self.remote_user}@{self.remote_host}",
                    f"stat {self.remote_import_path}/{filename}"
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    QMessageBox.information(self, "Remote File Info", result.stdout)
                else:
                    QMessageBox.warning(self, "Error", f"Could not get file info: {result.stderr}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"File info error: {e}")


    def _auto_sync(self): #vers 1
        """Auto-sync timer callback"""
        if self.connected and not self.syncing:
            self._log_status("Auto-sync triggered")
            self._sync_bidirectional()


    def _toggle_auto_sync(self, state): #vers 1
        """Toggle auto-sync on/off"""
        enabled = (state == Qt.CheckState.Checked.value)
        self.auto_sync_enabled = enabled
        
        if enabled and self.connected:
            self.sync_timer.start(self.sync_interval * 1000)
            self._log_status("Auto-sync enabled")
        else:
            self.sync_timer.stop()
            self._log_status("Auto-sync disabled")


    def _log_status(self, message): #vers 1
        """Add message to status log"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_text.append(f"[{timestamp}] {message}")
        # Auto-scroll to bottom
        self.status_text.verticalScrollBar().setValue(
            self.status_text.verticalScrollBar().maximum()
        )


    def _update_file_stats(self): #vers 1
        """Update file count statistics"""
        local_count = self.local_file_list.count()
        remote_count = self.remote_file_list.count()
        self.stats_label.setText(f"Local: {local_count} files | Remote: {remote_count} files")


    def _show_about(self): #vers 1
        """Show about dialog"""
        QMessageBox.about(self, "About SSH File Sync",
            f"{App_name}\n\n"
            "Bidirectional file synchronization between Linux machines.\n\n"
            "Version 1.2")

    def _show_theme_settings(self): #vers 1
        """Launch the main theme settings dialog from app_settings_system"""
        try:
            # Try to import from utils directory
            import sys
            from pathlib import Path
            
            # Add parent directory to path if needed
            utils_path = Path(__file__).parent.parent.parent / "utils"
            if str(utils_path) not in sys.path:
                sys.path.insert(0, str(utils_path))
            
            # Import the theme settings system
            try:
                from app_settings_system import AppSettings, SettingsDialog
                
                # Create or get app_settings instance
                if not self.app_settings:
                    self.app_settings = AppSettings()
                
                # Show the main settings dialog
                dialog = SettingsDialog(self.app_settings, self)
                if dialog.exec():
                    # Reapply theme after settings change
                    self._apply_theme()
                    self._log_status("Theme settings applied")
                    
            except ImportError as e:
                QMessageBox.warning(
                    self,
                    "Theme Settings Not Available",
                    f"Could not load theme settings system.\n\n"
                    f"Error: {e}\n\n"
                    "Make sure app_settings_system.py is in the utils folder."
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open theme settings:\n{e}"
            )


    def _setup_hotkeys(self): #vers 1
        """Setup keyboard shortcuts"""
        from PyQt6.QtGui import QShortcut, QKeySequence
        
        # Ctrl+R to refresh
        refresh_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        refresh_shortcut.activated.connect(self._refresh_local_files)
        
        # Ctrl+Q to quit
        quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        quit_shortcut.activated.connect(self.close)


    def _toggle_maximize(self): #vers 1
        """Toggle window maximize state"""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()


    def mousePressEvent(self, event): #vers 1
        """Handle mouse press for window dragging and resizing"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if clicking on resize corner
            corner = self._get_corner_at_pos(event.pos())
            if corner:
                self.resizing = True
                self.resize_corner = corner
                self.drag_position = event.globalPosition().toPoint()
                event.accept()
                return
            
            # Check if clicking on resize edge
            edge = self._get_edge_at_pos(event.pos())
            if edge:
                self.resizing = True
                self.resize_corner = edge
                self.drag_position = event.globalPosition().toPoint()
                event.accept()
                return
            
            # Check if clicking in toolbar area for dragging
            # Get the child widget at click position
            child = self.childAt(event.pos())
            
            # Allow dragging if clicking on toolbar, title label, icon label, or central widget
            if hasattr(self, 'toolbar') and (
                child == self.toolbar or 
                child == self.title_label or
                (child and child.parent() == self.toolbar) or
                event.pos().y() < 45  # Fallback: top 45 pixels
            ):
                # Don't start drag if clicking on a button
                if not isinstance(child, QPushButton):
                    self.dragging = True
                    self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                    event.accept()
                    return
            
            event.accept()


    def mouseMoveEvent(self, event): #vers 1
        """Handle mouse move for dragging/resizing"""
        if self.resizing and self.resize_corner:
            self._handle_resize(event.globalPosition().toPoint())
        elif self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)
        else:
            # Update cursor for corner/edge hover
            corner = self._get_corner_at_pos(event.pos())
            edge = self._get_edge_at_pos(event.pos())
            
            if corner:
                if corner in ['top-left', 'bottom-right']:
                    self.setCursor(QCursor(Qt.CursorShape.SizeFDiagCursor))
                else:
                    self.setCursor(QCursor(Qt.CursorShape.SizeBDiagCursor))
            elif edge:
                if edge in ['top', 'bottom']:
                    self.setCursor(QCursor(Qt.CursorShape.SizeVerCursor))
                else:
                    self.setCursor(QCursor(Qt.CursorShape.SizeHorCursor))
            else:
                self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))


    def mouseReleaseEvent(self, event): #vers 1
        """Handle mouse release"""
        self.dragging = False
        self.resizing = False
        self.resize_corner = None


    def _get_corner_at_pos(self, pos): #vers 1
        """Determine which corner (if any) is at the given position"""
        rect = self.rect()
        corner_size = self.corner_size
        
        if pos.x() < corner_size and pos.y() < corner_size:
            return 'top-left'
        elif pos.x() > rect.width() - corner_size and pos.y() < corner_size:
            return 'top-right'
        elif pos.x() < corner_size and pos.y() > rect.height() - corner_size:
            return 'bottom-left'
        elif pos.x() > rect.width() - corner_size and pos.y() > rect.height() - corner_size:
            return 'bottom-right'
        return None

    def _get_edge_at_pos(self, pos): #vers 1
        """Determine which edge (if any) is at the given position"""
        rect = self.rect()
        edge_size = 5  # pixels from edge
        
        # Don't detect edges in corner regions
        if self._get_corner_at_pos(pos):
            return None
        
        if pos.x() < edge_size:
            return 'left'
        elif pos.x() > rect.width() - edge_size:
            return 'right'
        elif pos.y() < edge_size:
            return 'top'
        elif pos.y() > rect.height() - edge_size:
            return 'bottom'
        return None


    def _handle_resize(self, global_pos): #vers 1
        """Handle window resize from corner or edge drag"""
        if not self.resize_corner:
            return
            
        delta = global_pos - self.drag_position
        self.drag_position = global_pos
        
        geo = self.geometry()
        
        # Handle corners
        if 'right' in self.resize_corner:
            geo.setWidth(max(self.minimumWidth(), geo.width() + delta.x()))
        if 'left' in self.resize_corner:
            new_left = geo.left() + delta.x()
            new_width = geo.width() - delta.x()
            if new_width >= self.minimumWidth():
                geo.setLeft(new_left)
        if 'bottom' in self.resize_corner:
            geo.setHeight(max(self.minimumHeight(), geo.height() + delta.y()))
        if 'top' in self.resize_corner:
            new_top = geo.top() + delta.y()
            new_height = geo.height() - delta.y()
            if new_height >= self.minimumHeight():
                geo.setTop(new_top)
            
        self.setGeometry(geo)


    # Theme and icon methods
    def _apply_theme(self): #vers 1
        """Apply current theme to the window - integrates with app_settings"""
        # Try to get theme from app_settings if available
        if self.app_settings and hasattr(self.app_settings, 'current_settings'):
            try:
                # Get colors from theme
                theme_name = self.app_settings.current_settings.get('theme', 'dark')
                
                # Try to get theme colors if theme system has them
                if hasattr(self.app_settings, 'themes') and theme_name in self.app_settings.themes:
                    theme_colors = self.app_settings.themes[theme_name].get('colors', {})
                    bg_color = theme_colors.get('bg_primary', '#2a2a2a')
                    text_color = theme_colors.get('text_primary', '#e0e0e0')
                    accent_color = theme_colors.get('accent_primary', '#4a90d9')
                else:
                    # Fallback
                    bg_color = '#2a2a2a'
                    text_color = '#e0e0e0'
                    accent_color = '#4a90d9'
                
                # Get fonts from settings
                font_family = self.app_settings.current_settings.get('font_family', 'Segoe UI')
                font_size = self.app_settings.current_settings.get('font_size', 12)
                panel_font_family = self.app_settings.current_settings.get('panel_font_family', 'Segoe UI')
                panel_font_size = self.app_settings.current_settings.get('panel_font_size', 11)
                button_font_family = self.app_settings.current_settings.get('button_font_family', 'Segoe UI')
                button_font_size = self.app_settings.current_settings.get('button_font_size', 11)
                button_font_weight = self.app_settings.current_settings.get('button_font_weight', 'bold')
                
                # Update fonts
                from PyQt6.QtGui import QFont
                self.title_font = QFont(font_family, font_size + 2)
                self.panel_font = QFont(panel_font_family, panel_font_size)
                self.button_font = QFont(button_font_family, button_font_size)
                if button_font_weight == 'bold':
                    self.button_font.setBold(True)
                self.infobar_font = QFont("Courier New", 9)
                
            except Exception as e:
                print(f"Error loading theme from app_settings: {e}")
                # Fallback to defaults
                bg_color = '#2a2a2a'
                text_color = '#e0e0e0'
                accent_color = '#4a90d9'
        else:
            # Use default dark theme
            bg_color = '#2a2a2a'
            text_color = '#e0e0e0'
            accent_color = '#4a90d9'
        
        # Calculate alternating row colors
        from PyQt6.QtGui import QColor
        bg_qcolor = QColor(bg_color)
        
        # Make alternate row slightly lighter or darker
        alternate_color = bg_qcolor.lighter(110) if bg_qcolor.lightness() < 128 else bg_qcolor.darker(110)
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                color: {text_color};
            }}
            QPushButton {{
                background-color: {QColor(bg_color).lighter(120).name()};
                border: 1px solid #555;
                padding: 5px;
                border-radius: 3px;
                color: {text_color};
            }}
            QPushButton:hover {{
                background-color: {QColor(bg_color).lighter(140).name()};
            }}
            QPushButton:pressed {{
                background-color: {bg_color};
            }}
            QPushButton:disabled {{
                background-color: {bg_color};
                color: #666;
            }}
            QListWidget {{
                background-color: {QColor(bg_color).darker(120).name()};
                border: 1px solid #555;
                alternate-background-color: {alternate_color.name()};
                color: {text_color};
            }}
            QListWidget::item:selected {{
                background-color: {accent_color};
                color: white;
            }}
            QListWidget::item:hover {{
                background-color: {QColor(accent_color).darker(150).name()};
            }}
            QTextEdit {{
                background-color: {QColor(bg_color).darker(120).name()};
                border: 1px solid #555;
                color: {text_color};
            }}
            QGroupBox {{
                border: 1px solid #555;
                margin-top: 10px;
                padding-top: 10px;
                color: {text_color};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                padding: 0 5px;
                color: {text_color};
            }}
            QLineEdit {{
                background-color: {QColor(bg_color).darker(120).name()};
                border: 1px solid #555;
                padding: 3px;
                color: {text_color};
            }}
            QSpinBox {{
                background-color: {QColor(bg_color).darker(120).name()};
                border: 1px solid #555;
                padding: 3px;
                color: {text_color};
            }}
            QCheckBox {{
                color: {text_color};
            }}
            QRadioButton {{
                color: {text_color};
            }}
            QLabel {{
                color: {text_color};
            }}
            QTabWidget::pane {{
                border: 1px solid #555;
            }}
            QTabBar::tab {{
                background-color: {QColor(bg_color).lighter(110).name()};
                border: 1px solid #555;
                padding: 5px 10px;
                color: {text_color};
            }}
            QTabBar::tab:selected {{
                background-color: {accent_color};
                color: white;
            }}
        """)


    def _create_info_icon(self): #vers 1
        """Info icon"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="10" cy="10" r="8" stroke="currentColor" stroke-width="2"/>
            <path d="M10 6v4M10 14h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_settings_icon(self): #vers 1
        """Settings/gear icon"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="10" cy="10" r="3" stroke="currentColor" stroke-width="2"/>
            <path d="M10 2v2M10 16v2M2 10h2M16 10h2M4.93 4.93l1.41 1.41M13.66 13.66l1.41 1.41M4.93 15.07l1.41-1.41M13.66 6.34l1.41-1.41" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_theme_icon(self): #vers 1
        """Theme/palette icon"""
        svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M10 2C5.58 2 2 5.58 2 10c0 4.42 3.58 8 8 8 .5 0 1-.4 1-1 0-.25-.1-.48-.24-.65-.14-.17-.24-.42-.24-.65 0-.55.45-1 1-1h1.5c2.48 0 4.5-2.02 4.5-4.5C17.52 5.58 14.42 2 10 2z" stroke="currentColor" stroke-width="1.5" fill="none"/>
            <circle cx="5.5" cy="10" r="1" fill="currentColor"/>
            <circle cx="8" cy="7" r="1" fill="currentColor"/>
            <circle cx="12" cy="7" r="1" fill="currentColor"/>
            <circle cx="14.5" cy="10" r="1" fill="currentColor"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_minimize_icon(self): #vers 1
        """Minimize - Horizontal line icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <line x1="5" y1="12" x2="19" y2="12"
                stroke="currentColor" stroke-width="2"
                stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_maximize_icon(self): #vers 1
        """Maximize - Square icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <rect x="5" y="5" width="14" height="14"
                stroke="currentColor" stroke-width="2"
                fill="none" rx="2"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_close_icon(self): #vers 1
        """Close - X icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <line x1="6" y1="6" x2="18" y2="18"
                stroke="currentColor" stroke-width="2"
                stroke-linecap="round"/>
            <line x1="18" y1="6" x2="6" y2="18"
                stroke="currentColor" stroke-width="2"
                stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_import_icon(self): #vers 1
        """Import - Download arrow icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"
                stroke="currentColor" stroke-width="2"
                fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            <polyline points="7 10 12 15 17 10"
                    stroke="currentColor" stroke-width="2"
                    fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="12" y1="15" x2="12" y2="3"
                stroke="currentColor" stroke-width="2"
                stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)


    def _create_export_icon(self): #vers 1
        """Export - Upload arrow icon"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"
                stroke="currentColor" stroke-width="2"
                fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            <polyline points="17 8 12 3 7 8"
                    stroke="currentColor" stroke-width="2"
                    fill="none" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="12" y1="3" x2="12" y2="15"
                stroke="currentColor" stroke-width="2"
                stroke-linecap="round"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_rename_icon(self): #vers 1
        """Rename icon - pencil/edit"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"
                stroke="currentColor" stroke-width="2" fill="none"/>
            <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"
                stroke="currentColor" stroke-width="2" fill="none"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_ignore_icon(self): #vers 1
        """Ignore icon - eye with slash"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"
                stroke="currentColor" stroke-width="2" fill="none"/>
            <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2" fill="none"/>
            <line x1="1" y1="1" x2="23" y2="23" stroke="currentColor" stroke-width="2"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_find_icon(self): #vers 1
        """Find icon - magnifying glass"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="2" fill="none"/>
            <line x1="21" y1="21" x2="16.65" y2="16.65" stroke="currentColor" stroke-width="2"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_replace_icon(self): #vers 1
        """Replace icon - swap arrows"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <polyline points="17 1 21 5 17 9" stroke="currentColor" stroke-width="2" fill="none"/>
            <path d="M3 11V9a4 4 0 014-4h14" stroke="currentColor" stroke-width="2" fill="none"/>
            <polyline points="7 23 3 19 7 15" stroke="currentColor" stroke-width="2" fill="none"/>
            <path d="M21 13v2a4 4 0 01-4 4H3" stroke="currentColor" stroke-width="2" fill="none"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_adddir_icon(self): #vers 1
        """Add Directory icon - folder with plus"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"
                stroke="currentColor" stroke-width="2" fill="none"/>
            <line x1="12" y1="11" x2="12" y2="17" stroke="currentColor" stroke-width="2"/>
            <line x1="9" y1="14" x2="15" y2="14" stroke="currentColor" stroke-width="2"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _create_delete_icon(self): #vers 1
        """Delete icon - trash can"""
        svg_data = b'''<svg viewBox="0 0 24 24">
            <polyline points="3 6 5 6 21 6" stroke="currentColor" stroke-width="2" fill="none"/>
            <path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"
                stroke="currentColor" stroke-width="2" fill="none"/>
            <line x1="10" y1="11" x2="10" y2="17" stroke="currentColor" stroke-width="2"/>
            <line x1="14" y1="11" x2="14" y2="17" stroke="currentColor" stroke-width="2"/>
        </svg>'''
        return self._svg_to_icon(svg_data, size=20)

    def _svg_to_icon(self, svg_data, size=24): #vers 1
        """Convert SVG data to QIcon with theme color support"""
        from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
        from PyQt6.QtSvg import QSvgRenderer
        from PyQt6.QtCore import QByteArray

        try:
            # Get current text color from palette
            text_color = self.palette().color(self.foregroundRole())

            # Replace currentColor with actual color
            svg_str = svg_data.decode('utf-8')
            svg_str = svg_str.replace('currentColor', text_color.name())
            svg_data = svg_str.encode('utf-8')

            renderer = QSvgRenderer(QByteArray(svg_data))
            pixmap = QPixmap(size, size)
            pixmap.fill(QColor(0, 0, 0, 0))  # Transparent background

            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()

            return QIcon(pixmap)
        except:
            # Fallback to no icon if SVG fails
            return QIcon()

    def _create_app_icon_pixmap(self, size=32): #vers 2
        """Create app icon pixmap - SSH/Sync symbol"""
        svg_data = b'''<svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <!-- Computer 1 -->
            <rect x="2" y="8" width="10" height="8" stroke="currentColor" stroke-width="1.5" fill="none" rx="1"/>
            <line x1="4" y1="16" x2="10" y2="16" stroke="currentColor" stroke-width="1"/>
            
            <!-- Computer 2 -->
            <rect x="20" y="8" width="10" height="8" stroke="currentColor" stroke-width="1.5" fill="none" rx="1"/>
            <line x1="22" y1="16" x2="28" y2="16" stroke="currentColor" stroke-width="1"/>
            
            <!-- Sync arrows -->
            <path d="M 12 10 L 19 10" stroke="currentColor" stroke-width="1.5" fill="none"/>
            <path d="M 17 8 L 19 10 L 17 12" stroke="currentColor" stroke-width="1.5" fill="none"/>
            
            <path d="M 20 14 L 13 14" stroke="currentColor" stroke-width="1.5" fill="none"/>
            <path d="M 15 12 L 13 14 L 15 16" stroke="currentColor" stroke-width="1.5" fill="none"/>
            
            <!-- Lock symbol (security) -->
            <rect x="14" y="22" width="4" height="4" stroke="currentColor" stroke-width="1" fill="none" rx="0.5"/>
            <path d="M 15 22 L 15 20 Q 15 19 16 19 Q 17 19 17 20 L 17 22" stroke="currentColor" stroke-width="1" fill="none"/>
        </svg>'''
        
        try:
            text_color = self.palette().color(self.foregroundRole())
            svg_str = svg_data.decode('utf-8')
            svg_str = svg_str.replace('currentColor', text_color.name())
            svg_data = svg_str.encode('utf-8')

            renderer = QSvgRenderer(QByteArray(svg_data))
            pixmap = QPixmap(size, size)
            pixmap.fill(QColor(0, 0, 0, 0))

            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()

            return pixmap
        except:
            # Return blank pixmap on error
            pixmap = QPixmap(size, size)
            pixmap.fill(QColor(0, 0, 0, 0))
            return pixmap


if __name__ == "__main__": #vers 1
    import sys
    import traceback

    print(f"{App_name} Starting.")

    try:
        app = QApplication(sys.argv)
        print("QApplication created")

        window = SSHSyncGUI()
        print(f"{App_name} instance created")

        window.setWindowTitle(f"{App_name} - Standalone")
        window.resize(1200, 800)
        window.show()
        print("Window shown, entering event loop")
        print(f"Window visible: {window.isVisible()}")
        print(f"Window geometry: {window.geometry()}")

        sys.exit(app.exec())

    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)
