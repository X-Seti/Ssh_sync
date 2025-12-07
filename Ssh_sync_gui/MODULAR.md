#X-Seti - November06 2025 - SSH File Sync - Modular Code Structure
#this belongs in root/ - version 1

## Overview

The code has been organized into modular files for better maintainability and reusability.

## Directory Structure

```
apps/
├── components/
│   └── Ssh_sync/
│       ├── ssh_sync_gui.py      # Main GUI application
│       ├── methods/             # Shared methods
│       │   └── icon_methods.py  # SVG icon creation
│       └── core/                # Single-purpose functions
│           ├── ssh_core.py      # SSH operations
│           └── file_ops_core.py # File operations
```

## Module Descriptions

### 1. icon_methods.py (Shared Methods)
**Purpose:** SVG icon creation and management

**Functions:**
- `svg_to_icon(svg_data, size)` - Convert SVG to QIcon
- `create_info_icon()` - Info button icon
- `create_settings_icon()` - Settings gear icon
- `create_theme_icon()` - Theme palette icon
- `create_minimize_icon()` - Window minimize
- `create_maximize_icon()` - Window maximize
- `create_close_icon()` - Window close
- `create_import_icon()` - Import arrow
- `create_export_icon()` - Export arrow
- `create_rename_icon()` - Rename pencil
- `create_ignore_icon()` - Ignore eye-slash
- `create_find_icon()` - Search magnifying glass
- `create_replace_icon()` - Replace swap arrows
- `create_adddir_icon()` - Add directory folder
- `create_delete_icon()` - Delete trash can
- `create_app_icon_pixmap()` - Application icon

**Usage:**
```python
from methods.icon_methods import create_delete_icon

delete_btn.setIcon(create_delete_icon(size=20))
```

---

### 2. ssh_core.py (Core Functions)
**Purpose:** SSH and rsync operations

**Functions:**
- `build_ssh_cmd_prefix()` - Build SSH command
- `build_rsync_ssh_option()` - Build rsync SSH option
- `test_ssh_connection()` - Test connection
- `list_remote_files()` - List remote directory
- `rsync_to_remote()` - Sync to remote
- `rsync_from_remote()` - Sync from remote
- `remote_rename_file()` - Rename remote file
- `remote_delete_file()` - Delete remote file
- `remote_create_directory()` - Create remote directory
- `remote_file_info()` - Get remote file info
- `check_sshpass_installed()` - Check for sshpass
- `check_rsync_installed()` - Check for rsync

**Usage:**
```python
from core.ssh_core import test_ssh_connection

success, error = test_ssh_connection(
    remote_host="example.com",
    remote_user="user",
    remote_port=22,
    use_password=False,
    ssh_key_path="~/.ssh/id_rsa"
)
```

---

### 3. file_ops_core.py (Core Functions)
**Purpose:** Local file system operations

**Functions:**
- `list_local_files()` - List directory contents
- `get_file_info()` - Get file statistics
- `rename_local_file()` - Rename file
- `delete_local_file()` - Delete file/directory
- `create_local_directory()` - Create directory
- `replace_local_file()` - Replace file
- `get_directory_size()` - Calculate directory size
- `ensure_directory_exists()` - Create if missing
- `is_valid_filename()` - Validate filename
- `find_files()` - Search for files

**Usage:**
```python
from core.file_ops_core import rename_local_file

success, message = rename_local_file(
    directory="/home/user/files",
    old_name="old.txt",
    new_name="new.txt"
)
```

---

## Integration with Main GUI

### Current State
All functions are currently in `ssh_sync_gui.py` as methods.

### Migration Plan

**Step 1: Create Directories**
```bash
cd apps/components/Ssh_sync
mkdir methods
mkdir core
```

**Step 2: Copy Modules**
```bash
cp icon_methods.py methods/
cp ssh_core.py core/
cp file_ops_core.py core/
```

**Step 3: Update Imports in ssh_sync_gui.py**

Replace internal methods with imports:

```python
# At top of ssh_sync_gui.py
from methods.icon_methods import (
    create_info_icon,
    create_settings_icon,
    create_theme_icon,
    create_delete_icon,
    # ... etc
)

from core.ssh_core import (
    test_ssh_connection,
    list_remote_files,
    rsync_to_remote,
    # ... etc
)

from core.file_ops_core import (
    list_local_files,
    rename_local_file,
    delete_local_file,
    # ... etc
)
```

**Step 4: Replace Method Calls**

Change from:
```python
self._create_delete_icon()
```

To:
```python
create_delete_icon(size=20)
```

---

## Benefits of Modular Structure

### 1. Code Reusability
- Icon functions can be used by other applications
- SSH operations available to other tools
- File operations shareable across projects

### 2. Easier Testing
```python
# Test individual functions
from core.ssh_core import test_ssh_connection

def test_connection():
    success, error = test_ssh_connection(...)
    assert success, f"Connection failed: {error}"
```

### 3. Better Organization
- Related functions grouped together
- Clear separation of concerns
- Easier to find and modify code

### 4. Maintainability
- Update icons in one place
- Fix SSH bugs in one module
- File operations centralized

---

## Current vs Modular Comparison

### Current (Monolithic)
```
ssh_sync_gui.py (2,258 lines)
  ├── GUI code
  ├── Icon methods
  ├── SSH operations
  ├── File operations
  ├── Settings
  └── Event handlers
```

### Modular (Organized)
```
ssh_sync_gui.py (1,500 lines)
  ├── GUI code
  ├── Settings
  └── Event handlers

methods/
  └── icon_methods.py (220 lines)

core/
  ├── ssh_core.py (180 lines)
  └── file_ops_core.py (160 lines)
```

---

## Usage Examples

### Example 1: Using Icons in Another App
```python
from methods.icon_methods import create_delete_icon, create_rename_icon

# Create toolbar buttons
delete_btn = QPushButton()
delete_btn.setIcon(create_delete_icon(size=24))

rename_btn = QPushButton()
rename_btn.setIcon(create_rename_icon(size=24))
```

### Example 2: Standalone SSH Script
```python
from core.ssh_core import rsync_to_remote, test_ssh_connection

# Test connection
if test_ssh_connection("server.com", "user", 22, False, ssh_key_path="~/.ssh/id_rsa")[0]:
    # Sync files
    success, stdout, stderr = rsync_to_remote(
        local_path="/local/dir",
        remote_host="server.com",
        remote_user="user",
        remote_path="/remote/dir",
        remote_port=22,
        use_password=False,
        ssh_key_path="~/.ssh/id_rsa"
    )
```

### Example 3: Batch File Operations
```python
from core.file_ops_core import list_local_files, delete_local_file

# List files
success, files = list_local_files("/path/to/dir")

# Delete old files
for filename in files:
    if filename.endswith('.tmp'):
        delete_local_file("/path/to/dir", filename)
```

---

## Migration Checklist

- [ ] Create `methods/` directory
- [ ] Create `core/` directory
- [ ] Copy `icon_methods.py` to `methods/`
- [ ] Copy `ssh_core.py` to `core/`
- [ ] Copy `file_ops_core.py` to `core/`
- [ ] Add `__init__.py` to each directory
- [ ] Update imports in `ssh_sync_gui.py`
- [ ] Replace self.method() calls with function() calls
- [ ] Test all functionality
- [ ] Remove old methods from gui file

---

## Future Enhancements

### Additional Modules

**settings_core.py**
- Load/save settings
- Theme management
- Configuration validation

**sync_core.py**
- Sync strategies
- Conflict resolution
- Ignore patterns

**network_core.py**
- Connection management
- Bandwidth monitoring
- Transfer statistics

---

## Testing Strategy

Each module can be tested independently:

```bash
# Test icon generation
python3 -c "from methods.icon_methods import create_delete_icon; print(create_delete_icon())"

# Test SSH functions
python3 -c "from core.ssh_core import check_rsync_installed; print(check_rsync_installed())"

# Test file operations
python3 -c "from core.file_ops_core import list_local_files; print(list_local_files('.'))"
```

---

## Documentation

Each module includes:
- Module docstring
- Function docstrings
- Type hints (can be added)
- Usage examples
- Return value documentation

---

## Notes

- All modules are standalone Python files
- No dependencies between modules (except icon_methods uses PyQt6)
- Each function returns (success: bool, result: data/message)
- Error handling included in all functions
- Compatible with Python 3.8+

---

## Quick Start

**To use modular structure immediately:**

1. Create directories:
```bash
mkdir -p methods core
```

2. Copy modules:
```bash
cp icon_methods.py methods/
cp ssh_core.py core/
cp file_ops_core.py core/
```

3. Import in your code:
```python
from methods.icon_methods import create_delete_icon
from core.ssh_core import test_ssh_connection
from core.file_ops_core import list_local_files
```

Done!
