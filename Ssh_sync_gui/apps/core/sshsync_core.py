#!/usr/bin/env python3
"""
X-Seti - July03 2023 - SSH File Sync - Core SSH Functionse - version 1
this belongs in apps/core/sshsync_core.py

Single-purpose functions for SSH operations
"""

import subprocess
from pathlib import Path


def build_ssh_cmd_prefix(use_password, password, ssh_key_path, remote_port): #vers 1
    """Build SSH command prefix based on authentication method"""
    if use_password and password:
        return [
            "sshpass", "-p", password,
            "ssh",
            "-p", str(remote_port),
            "-o", "StrictHostKeyChecking=no"
        ]
    else:
        return [
            "ssh",
            "-i", ssh_key_path,
            "-p", str(remote_port),
            "-o", "StrictHostKeyChecking=no"
        ]


def build_rsync_ssh_option(use_password, password, ssh_key_path, remote_port): #vers 1
    """Build rsync SSH option based on authentication method"""
    if use_password and password:
        return f"sshpass -p {password} ssh -p {remote_port} -o StrictHostKeyChecking=no"
    else:
        return f"ssh -i {ssh_key_path} -p {remote_port} -o StrictHostKeyChecking=no"


def test_ssh_connection(remote_host, remote_user, remote_port, use_password, password=None,
    ssh_key_path=None): #vers 1
    """Test SSH connection to remote host"""
    try:
        cmd = build_ssh_cmd_prefix(use_password, password, ssh_key_path, remote_port)
        cmd.extend([
            f"{remote_user}@{remote_host}",
            "echo 'OK'"
        ])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stderr
        
    except subprocess.TimeoutExpired:
        return False, "Connection timeout"
    except Exception as e:
        return False, str(e)


def list_remote_files(remote_host, remote_user, remote_path, remote_port, use_password,
    password=None, ssh_key_path=None): #vers 1
    """List files in remote directory"""
    try:
        cmd = build_ssh_cmd_prefix(use_password, password, ssh_key_path, remote_port)
        cmd.extend([
            f"{remote_user}@{remote_host}",
            f"ls -1 {remote_path}"
        ])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
            return True, files
        else:
            return False, result.stderr
            
    except Exception as e:
        return False, str(e)


def rsync_to_remote(local_path, remote_host, remote_user, remote_path, remote_port,
    use_password, delete_extra=False, password=None, ssh_key_path=None): #vers 1
    """Sync files to remote using rsync"""
    try:
        cmd = [
            "rsync",
            "-avz",
            "-e", build_rsync_ssh_option(use_password, password, ssh_key_path, remote_port)
        ]
        
        if delete_extra:
            cmd.append("--delete")
        
        cmd.extend([
            f"{local_path}/",
            f"{remote_user}@{remote_host}:{remote_path}/"
        ])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return result.returncode == 0, result.stdout, result.stderr
        
    except Exception as e:
        return False, "", str(e)


def rsync_from_remote(remote_host, remote_user, remote_path, local_path, remote_port,
    use_password, delete_extra=False, password=None, ssh_key_path=None): #vers 1
    """Sync files from remote using rsync"""
    try:
        cmd = [
            "rsync",
            "-avz",
            "-e", build_rsync_ssh_option(use_password, password, ssh_key_path, remote_port)
        ]
        
        if delete_extra:
            cmd.append("--delete")
        
        cmd.extend([
            f"{remote_user}@{remote_host}:{remote_path}/",
            f"{local_path}/"
        ])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return result.returncode == 0, result.stdout, result.stderr
        
    except Exception as e:
        return False, "", str(e)


def remote_rename_file(remote_host, remote_user, remote_path, old_name, new_name, 
    remote_port, use_password, password=None, ssh_key_path=None): #vers 1
    """Rename file on remote host"""
    try:
        cmd = build_ssh_cmd_prefix(use_password, password, ssh_key_path, remote_port)
        cmd.extend([
            f"{remote_user}@{remote_host}",
            f"cd {remote_path} && mv '{old_name}' '{new_name}'"
        ])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stderr
        
    except Exception as e:
        return False, str(e)


def remote_delete_file(remote_host, remote_user, remote_path, filename,
    remote_port, use_password, password=None, ssh_key_path=None): #vers 1
    """Delete file on remote host"""
    try:
        cmd = build_ssh_cmd_prefix(use_password, password, ssh_key_path, remote_port)
        cmd.extend([
            f"{remote_user}@{remote_host}",
            f"rm -rf {remote_path}/{filename}"
        ])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stderr
        
    except Exception as e:
        return False, str(e)


def remote_create_directory(remote_host, remote_user, remote_path, dirname,
    remote_port, use_password, password=None, ssh_key_path=None): #vers 1
    """Create directory on remote host"""
    try:
        cmd = build_ssh_cmd_prefix(use_password, password, ssh_key_path, remote_port)
        cmd.extend([
            f"{remote_user}@{remote_host}",
            f"mkdir -p {remote_path}/{dirname}"
        ])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stderr
        
    except Exception as e:
        return False, str(e)


def remote_file_info(remote_host, remote_user, remote_path, filename,
    remote_port, use_password, password=None, ssh_key_path=None): #vers 1
    """Get file information from remote host"""
    try:
        cmd = build_ssh_cmd_prefix(use_password, password, ssh_key_path, remote_port)
        cmd.extend([
            f"{remote_user}@{remote_host}",
            f"stat {remote_path}/{filename}"
        ])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr
            
    except Exception as e:
        return False, str(e)


def check_sshpass_installed(): #vers 1
    """Check if sshpass is installed"""
    try:
        result = subprocess.run(['which', 'sshpass'], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False


def check_rsync_installed(): #vers 1
    """Check if rsync is installed"""
    try:
        result = subprocess.run(['which', 'rsync'], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False
