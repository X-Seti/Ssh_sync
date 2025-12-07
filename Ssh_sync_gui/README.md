#X-Seti - November06 2025 - ssh_sync_gui - Root Launcher
#this belongs in root /launch_ssh_sync.py - version 1

A PyQt6-based GUI application for bidirectional file synchronization between two Linux machines over SSH.

## Features

### Window Controls
- **Custom titlebar** with app icon in center
- **Settings button** on left (gear icon)
- **Info button** and system controls on right
- **Frameless window** with full resize support:
  - Click and drag title area to move window
  - Resize from all 4 corners
  - Resize from all 4 edges
  - Visual cursor feedback for resize zones

### Three-Panel Layout

#### Panel 1: Local Files (Export)
- Browse `~/Desktop/export/` directory
- **Alternating row colors** for easy reading
- File list with multi-selection (Ctrl/Shift+Click)
- **Icon Toolbar (30x30 icons):**
  - **Rename**: Rename selected file
  - **Ignore File**: Mark file to be ignored during sync (stays in destination)
  - **Find**: Search/filter files
  - **Replace**: Replace file with another
  - **Delete**: Delete selected file(s)
  - **Add Dir**: Create new directory
  - **Info**: Show file information
- Refresh button
- Displays current path

#### Panel 2: Remote Files (Import)
- Browse remote `~/Desktop/import/` directory via SSH
- **Alternating row colors** for easy reading
- Connection status indicator
- **Icon Toolbar (30x30 icons):**
  - **Rename**: Rename remote file via SSH
  - **Ignore File**: Mark file to ignore (future feature)
  - **Find**: Search remote files
  - **Replace**: Replace remote file (future feature)
  - **Delete**: Delete remote file(s) via SSH
  - **Add Dir**: Create remote directory via SSH
  - **Info**: Show remote file information
  - Buttons enabled when connected
- Connect/Disconnect button
- Refresh button

#### Panel 3: Sync Controls & Status
- **Sync Actions:**
  - Sync to Remote → (local export → remote import)
  - ← Sync from Remote (remote export → local import)
  - Sync Both ↔ (bidirectional)

- **Advanced Operations:**
  - **Mirror Local → Remote**: Makes remote identical to local (ALWAYS DESTRUCTIVE)
  - **Clone Remote → Local**: Makes local identical to remote (ALWAYS DESTRUCTIVE)
  - **Copy Selected Files**: Copy only selected files from local to remote (NEVER deletes)

- **Auto-Sync:**
  - Enable/disable automatic syncing
  - Configurable interval

- **Status Log:**
  - Timestamped activity log
  - Clear log button

- **Quick Actions:**
  - 4 placeholder buttons for future features

### Settings Dialog (2 Tabs)

#### 1. Connection Tab
**SSH Connection:**
- Remote Host (IP or hostname)
- Remote User
- Port (default: 22)
- **Authentication Method:**
  - SSH Key (with file browser)
  - Password (stored securely, session-only by default)
  - Show/hide password toggle

**Sync Paths:**
- Local Export path (default: `~/Desktop/export`)
- Local Import path (default: `~/Desktop/import`)
- Remote Export path (default: `~/Desktop/export`)
- Remote Import path (default: `~/Desktop/import`)

**Test Connection** button to verify SSH setup

#### 2. Sync Options Tab
**Auto-Sync:**
- Enable/disable Auto-Sync
- Sync interval (10-3600 seconds)

**Sync Behavior:**
- **Delete files not in source** checkbox
  - When ENABLED: Regular sync operations use `rsync --delete` (removes extra files)
  - When DISABLED: Regular sync operations preserve extra files (safer)
  - WARNING: Note: Mirror and Clone operations ALWAYS delete (destructive by design)
  - Copy Selected operation NEVER deletes files

### Theme Integration

**Fully theme-aware** - integrates with `utils/app_system_settings.py`:
- Automatically uses colors from app_settings if available
- Falls back to default dark theme if standalone
- **Alternating row colors** in file lists calculated from theme
- All UI elements respect theme colors:
  - Background color
  - Text color
  - Accent color
  - Button colors
  - Selection colors

**Fonts from app_settings:**
- Title font
- Panel font
- Button font
- Infobar font
- Default font

### Status Bar
- Connection indicator (* Green = Connected, * Red = Disconnected)
- File count statistics (Local/Remote)

## Requirements

```bash
# Core dependencies
sudo pacman -S python-pyqt6 rsync openssh  # Arch/Garuda
# or
sudo apt install python3-pyqt6 rsync openssh-client  # Ubuntu

# Optional: For password authentication
sudo pacman -S sshpass  # Arch/Garuda
# or
sudo apt install sshpass  # Ubuntu
```

## SSH Setup

### Using SSH Keys (Recommended)

1. Generate SSH key if you don't have one:
```bash
ssh-keygen -t ed25519
```

2. Copy public key to remote machine:
```bash
ssh-copy-id user@remote-host
```

3. Test connection:
```bash
ssh user@remote-host
```

### Using Password (Alternative)

Install `sshpass` and enter password in settings. Password is stored in memory only during the session (not persistent by default).

For persistent password storage, you can modify the code to use `python-keyring`:
```bash
pip install keyring --break-system-packages
```

## Usage

1. **Launch the application:**
```bash
python ssh_sync_gui.py
```

2. **Configure connection:**
   - Click Settings (gear icon)
   - Go to "Connection" tab
   - Enter remote host, user, and authentication details
   - Set local and remote paths
   - Test connection

3. **Configure sync behavior:**
   - Go to "Sync Options" tab
   - Choose whether to delete extra files during sync
   - **Default (UNCHECKED)**: Safer - preserves files not in source
   - **Checked**: Matches rsync --delete behavior - removes extra files

4. **Connect:**
   - Click "Connect" button in the Remote Files panel
   - Status indicator turns green when connected

5. **Sync files:**
   - **Simple sync:** Use arrow buttons (respects delete setting)
   - **Bidirectional:** Use "Sync Both" button (respects delete setting)
   - **Selective:** Select files in local list, click "Copy Selected Files" (never deletes)
   - **Mirror/Clone:** For destructive full sync (ALWAYS deletes, confirms first)

6. **Auto-sync:**
   - Enable in settings or via checkbox
   - Files sync automatically at set interval
   - Uses your delete setting

## File Operations

### Local & Remote File Management

Both panels have identical icon toolbars for file management:

**Rename** ([EDIT])
- Renames selected file locally or remotely
- Remote rename executed via SSH

**Ignore File** ([IGN])
- Marks file to be ignored during sync operations
- File stays in destination but is excluded from sync
- (Feature placeholder - full implementation coming)

**Find** ([FIND])
- Search/filter files by name
- Selects all matching files
- Works on both local and remote lists

**Replace** ([REPL])
- Local: Browse and select replacement file
- Remote: Not yet supported (use local replace + sync)

**Delete** ([DEL])
- Delete selected file(s) with confirmation
- Local: Direct file deletion
- Remote: Deletion via SSH
- Supports multiple selection

**Add Directory** ([+DIR])
- Create new directory
- Local: Direct directory creation
- Remote: Directory creation via SSH

**Info** ([i])
- Display file information
- Local: Shows size, modified date, path
- Remote: Shows SSH stat output

## Keyboard Shortcuts

- **Ctrl+R**: Refresh local files
- **Ctrl+Q**: Quit application

## Security Notes

- SSH key authentication is recommended over password
- Password authentication requires `sshpass` (less secure)
- Default password storage is session-only (in memory)
- For production use, integrate `python-keyring` for secure password storage
- Always use SSH keys with proper permissions (chmod 600)

## Delete Behavior Explained

### Regular Sync Operations
When "Delete files not in source" is:
- **UNCHECKED (Default)**: Only adds/updates files, keeps extras
  - Safer for most use cases
  - Files in destination not in source are preserved
  
- **CHECKED**: Makes destination match source exactly
  - Uses `rsync --delete`
  - Files in destination not in source are DELETED
  - More aggressive sync

### Mirror & Clone (Always Destructive)
- These operations ALWAYS use `--delete` flag
- Purpose is to make one side identical to the other
- Confirmation dialog warns before execution
- Not affected by delete setting

### Copy Selected (Never Deletes)
- Only copies selected files
- Never removes any files
- Safe for selective transfers

## Advanced Features

### Alternating Row Colors
- File lists use zebra striping for easy reading
- Colors automatically calculated from theme
- Works in both light and dark themes

### Theme Integration
- Seamlessly integrates with app_system_settings
- Respects all color and font settings
- Falls back to defaults if standalone
- All UI elements theme-aware

## Customization

The GUI fully integrates with the app theme system:
- Uses colors from `app_settings`
- Uses fonts from `app_settings`
- Calculates alternating row colors from theme
- All theme methods intact for integration

## File Paths

**Default Local:**
- Export: `~/Desktop/export/`
- Import: `~/Desktop/import/`

**Default Remote:**
- Export: `~/Desktop/export/`
- Import: `~/Desktop/import/`

All paths are configurable in settings.

## Troubleshooting

**Connection fails:**
- Check SSH key permissions (should be 600)
- Verify remote host is accessible: `ping remote-host`
- Test SSH manually: `ssh user@remote-host`

**sshpass not found:**
- Install sshpass package
- Or switch to SSH key authentication

**Permission denied:**
- Ensure directories exist on both machines
- Check directory permissions
- Verify SSH key is authorized on remote

**Sync fails:**
- Check rsync is installed on both machines
- Verify paths exist and are accessible
- Check log for specific error messages

**Files getting deleted unexpectedly:**
- Check "Delete files not in source" setting in Sync Options
- Uncheck for safer behavior (default)
- Mirror/Clone operations always delete (by design)

## Development

Based on the base_gui_example.py template with:
- Full theme system integration with app_settings
- SVG icon generation
- Custom window controls
- Modular panel architecture
- Settings persistence framework
- Alternating row colors for readability

## Integration with App System

When used as part of a larger application:
```python
from utils import app_system_settings

# Create main window with settings
main_window = MainWindow()
main_window.app_settings = app_system_settings

# Create SSH sync GUI
ssh_sync = SSHSyncGUI(main_window=main_window)
# Will automatically use theme and fonts from app_settings
```

## License

This is a development tool. Modify as needed for your use case.

## Bug Fixes (v1.2)

**Fixed:**
- Window dragging now works properly (checks for toolbar clicks vs button clicks)
- App icon now displays correctly in title bar and window icon
- Theme integration properly uses `app_settings_system.py` structure
- Fonts loaded from `current_settings` dictionary
- Theme colors loaded from `themes[theme_name]['colors']`

## Version

1.2 - Added file operation icons, fixed window dragging, app icon, proper theme integration
