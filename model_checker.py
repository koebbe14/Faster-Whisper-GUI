"""
Model status checker for Faster Whisper GUI.
Checks which models are available and provides download information.
"""

import os
import sys
from pathlib import Path
import json


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


def get_user_data_dir():
    """Get the user-specific data directory for extracted files and models."""
    if getattr(sys, 'frozen', False):
        # Use AppData\Local\FasterWhisperGUI for user-specific data
        appdata_local = os.getenv('LOCALAPPDATA', os.path.expanduser('~'))
        user_data_dir = Path(appdata_local) / "FasterWhisperGUI"
        user_data_dir.mkdir(parents=True, exist_ok=True)
        return user_data_dir
    else:
        # Running as script - use script directory
        return Path(__file__).parent


def get_model_dir():
    """Get the default model directory."""
    user_data_dir = get_user_data_dir()
    model_dir = user_data_dir / "_models"
    return model_dir


def check_model_status(model_name):
    """
    Check if a model is available locally.
    
    Returns:
        dict with keys:
        - available: bool
        - path: Path to model directory if available
        - has_config: bool (has config.json)
        - has_model_bin: bool (has model.bin or similar)
    """
    model_dir = get_model_dir()
    model_path = model_dir / f"faster-whisper-{model_name}"
    
    status = {
        "available": False,
        "path": None,
        "has_config": False,
        "has_model_bin": False,
        "model_name": model_name
    }
    
    if model_path.exists() and model_path.is_dir():
        status["available"] = True
        status["path"] = model_path
        
        # Check for config.json
        config_file = model_path / "config.json"
        status["has_config"] = config_file.exists()
        
        # Check for model files (could be model.bin, model.safetensors, etc.)
        model_files = list(model_path.glob("model.*"))
        status["has_model_bin"] = len(model_files) > 0
    
    return status


def get_all_model_statuses():
    """Get status for all common models."""
    models = [
        "large-v3",           # Latest full model
        "large-v3-turbo",     # Latest turbo model
        "large-v2",           # Previous generation
        "large-v1",           # Older large model
        "medium",             # Balanced
        "small",              # Smaller
        "base",               # Base
        "tiny",               # Smallest
        "turbo"               # Legacy turbo (may be same as large-v3-turbo)
    ]
    return {model: check_model_status(model) for model in models}


def get_model_download_info(model_name):
    """
    Get download information for a model.
    
    Returns dict with download URLs and instructions.
    """
    # Map model names to their HuggingFace repository names
    model_repo_map = {
        "large-v3": "guillaumekln/faster-whisper-large-v3",
        "large-v3-turbo": "guillaumekln/faster-whisper-large-v3-turbo",
        "large-v2": "guillaumekln/faster-whisper-large-v2",
        "large-v1": "guillaumekln/faster-whisper-large-v1",
        "medium": "guillaumekln/faster-whisper-medium",
        "small": "guillaumekln/faster-whisper-small",
        "base": "guillaumekln/faster-whisper-base",
        "tiny": "guillaumekln/faster-whisper-tiny",
        "turbo": "guillaumekln/faster-whisper-large-v3-turbo"  # Legacy alias
    }
    
    # Get the repository name, default to standard format if not in map
    repo_name = model_repo_map.get(model_name, f"guillaumekln/faster-whisper-{model_name}")
    huggingface_url = f"https://huggingface.co/{repo_name}/tree/main"
    
    # Get model directory (relative path for instructions)
    model_dir_name = f"faster-whisper-{model_name}"
    model_path_relative = f"_models\\{model_dir_name}"
    
    info = {
        "model_name": model_name,
        "huggingface_url": huggingface_url,
        "download_instructions": f"""Manual Download Instructions for {model_name}:

1. Visit the model repository:
   {huggingface_url}

2. Download the following files:
   - config.json
   - model.bin (or model.safetensors)
   - tokenizer.json
   - vocabulary.txt (if available)
   - preprocessor_config.json (for large-v3 models, if available)

3. Create the model folder:
   Create a folder named "{model_dir_name}" inside the "_models" folder.
   The full path should be: [Your Project Folder]\\_models\\{model_dir_name}\\

4. Place all downloaded files in this folder.

AUTOMATIC DOWNLOAD:
Alternatively, the model will be downloaded automatically on first use if you have internet connectivity. The program will create the necessary folders and download files automatically.

Note: Make sure the "_models" folder exists in the same directory as faster-whisper-xxl.exe""",
        "auto_download": True  # Faster-whisper can auto-download
    }
    
    return info


def check_for_model_updates():
    """
    Check if there are updates available for models.
    This is a placeholder - in a real implementation, you'd check against
    a version API or compare checksums.
    
    Returns:
        dict with model names as keys and update info as values
    """
    # This would typically check against an API or version file
    # For now, return empty dict (no updates detected)
    # In a real implementation, you might:
    # 1. Check a version file online
    # 2. Compare local model versions with remote
    # 3. Check model file checksums
    
    return {}


def get_model_info_display(model_name):
    """Get a formatted string for model status display."""
    status = check_model_status(model_name)
    
    if status["available"]:
        parts = ["✓ Available"]
        if status["has_config"] and status["has_model_bin"]:
            parts.append("(Complete)")
        elif status["has_config"] or status["has_model_bin"]:
            parts.append("(Partial)")
        return " ".join(parts)
    else:
        return "✗ Not Available"

def get_model_recommendations():
    """Get recommendations for model selection based on use case."""
    return {
        "maximum_accuracy": {
            "models": ["large-v3", "large-v3-turbo", "large-v2"],
            "description": "Best for important transcriptions, professional work, diarization"
        },
        "balanced": {
            "models": ["large-v3-turbo", "large-v2", "medium"],
            "description": "Good balance of accuracy and speed for most users"
        },
        "speed_priority": {
            "models": ["medium", "small", "base"],
            "description": "Faster processing with acceptable accuracy"
        },
        "fast_processing": {
            "models": ["base", "tiny"],
            "description": "Very fast but lower accuracy, for quick drafts"
        }
    }

