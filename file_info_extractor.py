"""
Extract file information for display in the GUI.
Uses ffprobe if available, otherwise provides basic info.
"""

import os
from pathlib import Path
import subprocess
import sys


def get_script_dir():
    """Get the directory where the script or executable is located."""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        if hasattr(sys, '_MEIPASS'):
            # --onefile mode: files are extracted to temporary directory
            return Path(sys._MEIPASS)
        else:
            # --onedir mode: files are in the same directory as the executable
            return Path(sys.executable).parent
    else:
        # Running as script
        return Path(__file__).parent


def get_file_info(file_path):
    """
    Get information about an audio/video file.
    
    Returns a dictionary with:
    - size: File size in bytes
    - size_formatted: Human-readable size
    - format: File extension/format
    - duration: Duration in seconds (if available)
    - duration_formatted: Human-readable duration (if available)
    - codec: Audio/video codec (if available)
    - bitrate: Bitrate (if available)
    - has_info: Whether detailed info is available
    """
    info = {
        "size": 0,
        "size_formatted": "Unknown",
        "format": "",
        "duration": None,
        "duration_formatted": "Unknown",
        "codec": "Unknown",
        "bitrate": "Unknown",
        "has_info": False
    }
    
    try:
        path = Path(file_path)
        if not path.exists():
            return info
        
        # Basic file info
        info["size"] = path.stat().st_size
        info["size_formatted"] = format_size(info["size"])
        info["format"] = path.suffix.upper().lstrip('.') or "Unknown"
        
        # Try to get detailed info using ffprobe
        ffprobe_path = find_ffprobe()
        if ffprobe_path:
            detailed_info = get_ffprobe_info(ffprobe_path, file_path)
            if detailed_info:
                info.update(detailed_info)
                info["has_info"] = True
        
    except Exception as e:
        print(f"Error getting file info: {e}")
    
    return info


def get_user_data_dir():
    """Get the user-specific data directory for extracted files."""
    if getattr(sys, 'frozen', False):
        # Use AppData\Local\FasterWhisperGUI for user-specific data
        appdata_local = os.getenv('LOCALAPPDATA', os.path.expanduser('~'))
        user_data_dir = Path(appdata_local) / "FasterWhisperGUI"
        user_data_dir.mkdir(parents=True, exist_ok=True)
        return user_data_dir
    else:
        # Running as script - use script directory
        return Path(__file__).parent


def find_ffprobe():
    """Find ffprobe executable."""
    # Check in user data directory first (extracted files)
    user_data_dir = get_user_data_dir()
    ffprobe = user_data_dir / "ffprobe.exe"
    if ffprobe.exists():
        return str(ffprobe)
    
    # Check in same directory as script/executable (for non-frozen or legacy)
    script_dir = get_script_dir()
    ffprobe = script_dir / "ffprobe.exe"
    if ffprobe.exists():
        return str(ffprobe)
    
    # Check if ffprobe is in PATH
    try:
        result = subprocess.run(["ffprobe", "-version"], 
                              capture_output=True, 
                              creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
        if result.returncode == 0:
            return "ffprobe"
    except:
        pass
    
    return None


def get_ffprobe_info(ffprobe_path, file_path):
    """Get detailed file info using ffprobe."""
    try:
        cmd = [
            ffprobe_path,
            "-v", "error",
            "-show_entries", "format=duration,bit_rate,format_name",
            "-show_entries", "stream=codec_name,codec_type",
            "-of", "default=noprint_wrappers=1",
            str(file_path)
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0,
            timeout=5
        )
        
        if result.returncode != 0:
            return None
        
        info = {}
        lines = result.stdout.split('\n')
        
        for line in lines:
            if '=' in line:
                key, value = line.split('=', 1)
                if key == 'duration' and value:
                    try:
                        duration = float(value)
                        info["duration"] = duration
                        info["duration_formatted"] = format_duration(duration)
                    except:
                        pass
                elif key == 'bit_rate' and value:
                    try:
                        bitrate = int(value)
                        info["bitrate"] = format_bitrate(bitrate)
                    except:
                        pass
                elif key == 'codec_name' and 'codec_type' in line:
                    # This is simplified - real parsing would be more complex
                    if 'audio' in line.lower() or not info.get("codec"):
                        info["codec"] = value
        
        return info if info else None
        
    except Exception as e:
        print(f"Error running ffprobe: {e}")
        return None


def format_size(size_bytes):
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def format_duration(seconds):
    """Format duration in human-readable format."""
    if seconds is None:
        return "Unknown"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def format_bitrate(bitrate_bps):
    """Format bitrate in human-readable format."""
    if bitrate_bps < 1000:
        return f"{bitrate_bps} bps"
    elif bitrate_bps < 1000000:
        return f"{bitrate_bps / 1000:.1f} kbps"
    else:
        return f"{bitrate_bps / 1000000:.1f} Mbps"

