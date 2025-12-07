#!/usr/bin/env python3

#X-Seti - November06 2025 - ssh_sync_gui - Root Launcher - version 1
##this belongs in root /launch_ssh_sync.py


import sys
import os
from pathlib import Path

def find_project_root(): #vers 1
    """Find the project root by looking for apps directory"""
    current = Path.cwd()
    
    # Check current directory
    if (current / "apps").exists():
        return current
    
    # Check parent directories
    for parent in current.parents:
        if (parent / "apps").exists():
            return parent
    
    # Check if we're already in the right place
    if (current.parent / "apps").exists():
        return current.parent
        
    return current

def find_gui_module(): #vers 1
    """Find ssh_sync_gui.py in the apps structure"""
    root = find_project_root()
    
    # Look for the GUI file in common locations
    search_paths = [
        root / "apps" / "components" / "Ssh_sync" / "ssh_sync_gui.py",
        root / "ssh_sync_gui.py",  # Direct in root
    ]
    
    for path in search_paths:
        if path.exists():
            return path.parent, path.stem
    
    return None, None

# Find the project structure
root_dir = find_project_root()
gui_path, module_name = find_gui_module()

if gui_path is None:
    print("Error: Could not find ssh_sync_gui.py")
    print(f"\nSearched in: {root_dir}")
    print("\nExpected locations:")
    print("  apps/components/Ssh_sync/ssh_sync_gui.py")
    print("  ssh_sync_gui.py")
    sys.exit(1)

# Add paths for imports
sys.path.insert(0, str(gui_path))
sys.path.insert(0, str(root_dir / "apps" / "utils"))

print(f"Loading from: {gui_path}")

try:
    # Import app settings system
    try:
        from app_settings_system import AppSettings
        has_app_settings = True
        print("App settings system loaded")
    except ImportError as e:
        print(f"Warning: Could not load app_settings_system: {e}")
        print("Running without theme system...")
        has_app_settings = False
    
    # Import SSH sync GUI
    import ssh_sync_gui
    from ssh_sync_gui import SSHSyncGUI
    
    # Create QApplication
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Create SSH sync GUI
    window = SSHSyncGUI()
    
    # Add app settings if available
    if has_app_settings:
        app_settings = AppSettings()
        window.app_settings = app_settings
        window._apply_theme()
        print("Theme applied from app_settings")
    else:
        print("Using default theme")
    
    # Show window
    window.show()
    
    print(f"SSH File Sync started successfully")
    sys.exit(app.exec())
    
except ImportError as e:
    print(f"\nImport Error: {e}")
    print(f"\nPython path:")
    for p in sys.path[:5]:
        print(f"  {p}")
    print(f"\nCurrent directory: {Path.cwd()}")
    print(f"Project root: {root_dir}")
    print(f"GUI path: {gui_path}")
    sys.exit(1)
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
