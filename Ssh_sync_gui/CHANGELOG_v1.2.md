# SSH File Sync v1.2 - Changelog

## New Features

### Icon Toolbars (30x30 icons)
Added comprehensive file management toolbars to both Local and Remote panels:

**7 Icon Buttons Per Panel:**
1. **Rename** - Edit file names (local/remote)
2. **Ignore File** - Mark files to exclude from sync (stays in destination)
3. **Find** - Search and filter files
4. **Replace** - Replace files with new versions
5. **Delete** - Remove files with confirmation
6. **Add Directory** - Create new folders
7. **Info** - Display file details and statistics

**Features:**
- All icons created as SVG with theme color support
- Remote buttons enabled/disabled based on connection status
- Full SSH integration for remote operations
- Multi-file support for delete operations
- Search highlights matching files

## Bug Fixes

### Window Dragging
**Problem:** Window couldn't be dragged by clicking toolbar
**Solution:** 
- Added proper child widget detection in `mousePressEvent`
- Checks if click is on toolbar, title, or icon (not buttons)
- Stores toolbar reference for geometry checking
- Excludes QPushButton widgets from drag start

### App Icon
**Problem:** No icon visible in title bar or taskbar
**Solution:**
- Created 64x64 app icon pixmap after UI setup
- Set window icon using `setWindowIcon(QIcon(pixmap))`
- Icon shows two computers with sync arrows and lock symbol

### Theme Integration
**Problem:** Theme system didn't work with `app_settings_system.py`
**Solution:**
- Reads `current_settings` dictionary properly
- Gets theme name: `app_settings.current_settings.get('theme')`
- Loads theme colors from: `app_settings.themes[theme_name]['colors']`
- Extracts colors: `bg_primary`, `text_primary`, `accent_primary`
- Gets fonts from settings: `font_family`, `font_size`, `panel_font_family`, etc.
- Creates QFont objects with correct sizes and weights
- Applies `setBold(True)` when `button_font_weight == 'bold'`

## Theme System Integration

### Font Loading
```python
font_family = app_settings.current_settings.get('font_family', 'Segoe UI')
font_size = app_settings.current_settings.get('font_size', 9)
panel_font_family = app_settings.current_settings.get('panel_font_family', 'Segoe UI')
panel_font_size = app_settings.current_settings.get('panel_font_size', 9)
button_font_family = app_settings.current_settings.get('button_font_family', 'Segoe UI')
button_font_size = app_settings.current_settings.get('button_font_size', 9)
button_font_weight = app_settings.current_settings.get('button_font_weight', 'bold')
```

### Color Loading
```python
theme_name = app_settings.current_settings.get('theme', 'dark')
theme_colors = app_settings.themes[theme_name].get('colors', {})
bg_color = theme_colors.get('bg_primary', '#2a2a2a')
text_color = theme_colors.get('text_primary', '#e0e0e0')
accent_color = theme_colors.get('accent_primary', '#4a90d9')
```

### Alternating Row Colors
- Automatically calculated from theme background
- Uses `QColor.lighter(110)` for dark themes
- Uses `QColor.darker(110)` for light themes
- Applied to both file list widgets

## File Operations Details

### Rename Operation
- **Local:** Uses `Path.rename()` 
- **Remote:** SSH command: `mv 'old' 'new'`
- Input dialog for new name
- Validates name change before executing
- Refreshes file list after rename

### Delete Operation
- **Local:** Uses `Path.unlink()` for files, `shutil.rmtree()` for directories
- **Remote:** SSH command: `rm -rf filename`
- Confirmation dialog showing files to delete
- Supports multiple selection
- Shows first 5 files in confirmation
- Logs each deletion result

### Add Directory
- **Local:** Uses `Path.mkdir(parents=True, exist_ok=True)`
- **Remote:** SSH command: `mkdir -p dirname`
- Input dialog for directory name
- Creates parent directories if needed
- Refreshes file list after creation

### Find Files
- Uses `QListWidget.findItems(text, Qt.MatchFlag.MatchContains)`
- Clears previous selection
- Selects all matching items
- Scrolls to first match
- Logs number of matches found

### File Info
- **Local:** 
  - File/Directory type
  - Size in bytes and KB
  - Modified timestamp
  - Full path
- **Remote:** 
  - SSH `stat` command output
  - Shows all available file metadata

### Replace File
- **Local:** 
  - File dialog to select replacement
  - Uses `shutil.copy2()` to preserve metadata
  - Refreshes file list
- **Remote:** 
  - Not yet implemented
  - Shows message to use local replace + sync

### Ignore File (Placeholder)
- UI implemented with icon button
- Shows info dialog about future implementation
- Will allow files to stay in destination but be excluded from sync
- Useful for destination-specific files

## Code Organization

### New Methods Added
- `_create_rename_icon()` - Pencil/edit icon
- `_create_ignore_icon()` - Eye with slash
- `_create_find_icon()` - Magnifying glass
- `_create_replace_icon()` - Swap arrows
- `_create_adddir_icon()` - Folder with plus
- `_rename_file(location)` - Rename handler
- `_ignore_file(location)` - Ignore handler (placeholder)
- `_find_file(location)` - Search handler
- `_replace_file(location)` - Replace handler
- `_delete_file(location)` - Delete handler
- `_add_directory(location)` - Create directory handler
- `_show_file_info(location)` - Info display handler

### Modified Methods
- `_create_left_panel()` - Added icon toolbar
- `_create_middle_panel()` - Added icon toolbar with disabled buttons
- `_create_toolbar()` - Stores toolbar reference as `self.toolbar`
- `_connect()` - Enables remote file operation buttons
- `_disconnect()` - Disables remote file operation buttons
- `_apply_theme()` - Proper app_settings integration
- `mousePressEvent()` - Fixed window dragging logic
- `__init__()` - Sets window icon after UI setup

## Testing Notes

### Tested Scenarios
- ✅ Window dragging from title area
- ✅ Window dragging from icon area  
- ✅ Window dragging from toolbar gaps
- ✅ Button clicks don't trigger dragging
- ✅ Corner resizing (all 4 corners)
- ✅ Edge resizing (all 4 edges)
- ✅ App icon visible in title bar
- ✅ Theme colors applied correctly
- ✅ Fonts loaded from app_settings
- ✅ Alternating row colors visible
- ✅ Local file rename
- ✅ Remote file rename (when connected)
- ✅ Local file delete
- ✅ Remote file delete (when connected)
- ✅ Local directory creation
- ✅ Remote directory creation (when connected)
- ✅ File search/find
- ✅ File info display (local)
- ✅ File info display (remote)
- ✅ Remote buttons disabled when not connected
- ✅ Remote buttons enabled when connected

### Known Limitations - TODOs
- Ignore file feature is placeholder (UI only) TODO
- Remote file replace not implemented
- Requires active SSH connection for remote operations
- No drag-and-drop file support yet

## Integration with app_settings_system.py

The application now properly integrates with the theme engine:

**Reads from:**
- `app_settings.current_settings` - Dictionary of current settings
- `app_settings.themes` - Dictionary of available themes
- Theme colors from `themes[theme_name]['colors']`

**Uses these settings:**
- `theme` - Current theme name
- `font_family` - Main font
- `font_size` - Main font size
- `panel_font_family` - Panel font
- `panel_font_size` - Panel font size
- `button_font_family` - Button font
- `button_font_size` - Button font size
- `button_font_weight` - normal or bold

### Planned Features
- [ ] Full ignore file implementation with .syncignore file
- [ ] Remote file replace via upload
- [ ] Drag-and-drop file support
- [ ] File type icons in list
- [ ] Sort by name, size, date
- [ ] Batch operations
- [ ] Sync conflict resolution
- [ ] File preview pane
- [ ] Transfer progress bars
- [ ] Bandwidth limiting options

## Version History

**v1.2** (Current)
- Added icon toolbars for file operations
- Fixed window dragging
- Fixed app icon display
- Proper theme system integration
- 7 file operations per panel

**v1.1**
- Added theme integration
- Alternating row colors
- Configurable delete behavior

**v1.0**
- Initial ported release
- Basic SSH sync functionality
- Connection management
- Auto-sync support
