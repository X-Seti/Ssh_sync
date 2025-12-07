#!/usr/bin/env python3
"""
X-Seti - July03 2023 - SSH File Sync - File Operations Core - version 2
this belongs in apps/core/sshsync_opscore.py

Single-purpose functions for local file operations
"""

import os
import shutil
from pathlib import Path
from datetime import datetime


def list_local_files(directory_path): #vers 1
    """List files in local directory"""
    try:
        path = Path(directory_path)
        if not path.exists():
            return False, f"Directory does not exist: {directory_path}"
        
        items = []
        for item in sorted(path.iterdir()):
            items.append(item.name)
        
        return True, items
        
    except Exception as e:
        return False, str(e)


def get_file_info(file_path): #vers 1
    """Get information about a local file"""
    try:
        path = Path(file_path)
        if not path.exists():
            return False, "File not found"
        
        stat = path.stat()
        info = {
            'name': path.name,
            'size': stat.st_size,
            'size_kb': stat.st_size / 1024,
            'size_mb': stat.st_size / (1024 * 1024),
            'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            'is_dir': path.is_dir(),
            'is_file': path.is_file(),
            'path': str(path.absolute())
        }
        
        return True, info
        
    except Exception as e:
        return False, str(e)


def rename_local_file(directory, old_name, new_name): #vers 1
    """Rename a local file"""
    try:
        old_path = Path(directory) / old_name
        new_path = Path(directory) / new_name
        
        if not old_path.exists():
            return False, f"File not found: {old_name}"
        
        if new_path.exists():
            return False, f"File already exists: {new_name}"
        
        old_path.rename(new_path)
        return True, f"Renamed {old_name} to {new_name}"
        
    except Exception as e:
        return False, str(e)


def delete_local_file(directory, filename): #vers 1
    """Delete a local file or directory"""
    try:
        path = Path(directory) / filename
        
        if not path.exists():
            return False, f"File not found: {filename}"
        
        if path.is_file():
            path.unlink()
            return True, f"Deleted file: {filename}"
        elif path.is_dir():
            shutil.rmtree(path)
            return True, f"Deleted directory: {filename}"
        else:
            return False, f"Unknown file type: {filename}"
            
    except Exception as e:
        return False, str(e)


def create_local_directory(directory, dirname): #vers 1
    """Create a new local directory"""
    try:
        new_dir = Path(directory) / dirname
        
        if new_dir.exists():
            return False, f"Directory already exists: {dirname}"
        
        new_dir.mkdir(parents=True, exist_ok=False)
        return True, f"Created directory: {dirname}"
        
    except Exception as e:
        return False, str(e)


def replace_local_file(directory, target_file, source_file): #vers 1
    """Replace a local file with another file"""
    try:
        dest = Path(directory) / target_file
        source = Path(source_file)
        
        if not source.exists():
            return False, f"Source file not found: {source_file}"
        
        shutil.copy2(source, dest)
        return True, f"Replaced {target_file}"
        
    except Exception as e:
        return False, str(e)


def get_directory_size(directory): #vers 1
    """Calculate total size of directory"""
    try:
        path = Path(directory)
        total_size = 0
        file_count = 0
        
        for item in path.rglob('*'):
            if item.is_file():
                total_size += item.stat().st_size
                file_count += 1
        
        return True, {
            'total_bytes': total_size,
            'total_kb': total_size / 1024,
            'total_mb': total_size / (1024 * 1024),
            'file_count': file_count
        }
        
    except Exception as e:
        return False, str(e)


def ensure_directory_exists(directory): #vers 1
    """Ensure a directory exists, create if it doesn't"""
    try:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        return True, f"Directory ready: {directory}"
        
    except Exception as e:
        return False, str(e)


def is_valid_filename(filename): #vers 1
    """Check if filename is valid (no path traversal, etc.)"""
    if not filename:
        return False
    
    # Check for path traversal attempts
    if '..' in filename or '/' in filename or '\\' in filename:
        return False
    
    # Check for hidden files (optional - you might want to allow these)
    # if filename.startswith('.'):
    #     return False
    
    return True


def find_files(directory, search_term, case_sensitive=False): #vers 1
    """Find files matching search term"""
    try:
        path = Path(directory)
        matches = []
        
        if not case_sensitive:
            search_term = search_term.lower()
        
        for item in path.iterdir():
            name = item.name if case_sensitive else item.name.lower()
            if search_term in name:
                matches.append(item.name)
        
        return True, matches
        
    except Exception as e:
        return False, str(e)
