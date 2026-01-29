"""
Command builder for Faster Whisper GUI.
Converts GUI selections to command-line arguments for faster-whisper-xxl.exe
"""

import os
import shlex
import sys
from pathlib import Path


def get_script_dir():
    """Get the directory where bundled files are located (for finding faster-whisper-xxl.exe, etc.)."""
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


def build_command(input_files, output_dir, options):
    """
    Build command-line arguments for faster-whisper-xxl.exe
    
    Args:
        input_files: List of input file paths
        output_dir: Output directory path
        options: Dictionary of option values from GUI
    
    Returns:
        Tuple of (executable_path, args_list) for subprocess
    """
    # Find executable in user data directory (extracted files)
    user_data_dir = get_user_data_dir()
    exe_path = user_data_dir / "faster-whisper-xxl.exe"
    
    if not exe_path.exists():
        raise FileNotFoundError(
            f"faster-whisper-xxl.exe not found in {user_data_dir}. "
            "Please run the application once to extract required files."
        )
    
    args = []
    
    # Input files (positional arguments)
    for file_path in input_files:
        # Properly quote paths with spaces
        args.append(str(Path(file_path).absolute()))
    
    # Output directory
    if output_dir:
        output_path = Path(output_dir).absolute()
        if str(output_path) == ".":
            args.append("-o")
            args.append(".")
        elif str(output_path.name).lower() == "source":
            args.append("-o")
            args.append("source")
        else:
            args.append("-o")
            args.append(str(output_path))
    
    # Model
    if options.get("model"):
        args.append("-m")
        args.append(str(options["model"]))
    
    # Model directory - ensure models download to _models folder in user data directory
    model_dir = user_data_dir / "_models"
    args.append("--model_dir")
    args.append(str(model_dir))
    
    # Task
    if options.get("task"):
        args.append("--task")
        args.append(str(options["task"]))
    
    # Language
    if options.get("language") and options["language"] != "auto" and options["language"] != "None":
        args.append("-l")
        args.append(str(options["language"]))
    
    # Output formats
    if options.get("output_formats"):
        formats = options["output_formats"]
        if isinstance(formats, list):
            args.append("-f")
            args.extend(formats)
        else:
            args.append("-f")
            args.append(str(formats))
    
    # VAD settings
    if options.get("vad_enable", True):  # Default is True
        if options.get("vad_method"):
            args.append("--vad_method")
            args.append(str(options["vad_method"]))
        
        if options.get("vad_threshold") is not None:
            args.append("--vad_threshold")
            args.append(str(options["vad_threshold"]))
    else:
        args.append("--vad_filter")
        args.append("False")
    
    # Diarization
    if options.get("diarize_enable"):
        if options.get("diarize_method"):
            args.append("--diarize")
            args.append(str(options["diarize_method"]))
        
        if options.get("num_speakers"):
            args.append("--num_speakers")
            args.append(str(int(options["num_speakers"])))
        
        if options.get("min_speakers"):
            args.append("--min_speakers")
            args.append(str(int(options["min_speakers"])))
        
        if options.get("max_speakers"):
            args.append("--max_speakers")
            args.append(str(int(options["max_speakers"])))
        
        if options.get("speaker_label") and options["speaker_label"] != "SPEAKER":
            args.append("--speaker")
            args.append(str(options["speaker_label"]))
        
        if options.get("diarize_device"):
            device = options["diarize_device"]
            if device and device != "auto":
                args.append("--diarize_device")
                args.append(str(device))
        
        if options.get("diarize_threads") and options["diarize_threads"] != 0:
            args.append("--diarize_threads")
            args.append(str(int(options["diarize_threads"])))
        
        if options.get("diarize_only"):
            args.append("--diarize_only")
        
        if options.get("return_embeddings"):
            args.append("--return_embeddings")
        
        if options.get("diarize_ff") is not None:
            args.append("--diarize_ff")
            args.append(str(options["diarize_ff"]))
        
        if options.get("diarize_dump"):
            args.append("--diarize_dump")
    
    # Word timestamps
    if options.get("word_timestamps", True):  # Default is True
        args.append("--word_timestamps")
        args.append("True")
    else:
        args.append("--word_timestamps")
        args.append("False")
    
    # Highlight words
    if options.get("highlight_words"):
        args.append("--highlight_words")
        args.append("True")
    
    # Audio filters
    if options.get("ff_speechnorm"):
        args.append("--ff_speechnorm")
    
    if options.get("ff_loudnorm"):
        args.append("--ff_loudnorm")
    
    if options.get("ff_lowhighpass"):
        args.append("--ff_lowhighpass")
    
    if options.get("ff_tempo") and options["ff_tempo"] != 1.0:
        args.append("--ff_tempo")
        args.append(str(float(options["ff_tempo"])))
    
    if options.get("ff_fftdn") and options["ff_fftdn"] != 0:
        args.append("--ff_fftdn")
        args.append(str(int(options["ff_fftdn"])))
    
    # Advanced options
    if options.get("temperature") is not None:
        args.append("--temperature")
        args.append(str(float(options["temperature"])))
    
    if options.get("beam_size"):
        args.append("--beam_size")
        args.append(str(int(options["beam_size"])))
    
    if options.get("patience"):
        args.append("--patience")
        args.append(str(float(options["patience"])))
    
    # Device
    if options.get("device") and options["device"] != "auto":
        args.append("-d")
        args.append(str(options["device"]))
    
    # Compute type
    if options.get("compute_type"):
        args.append("-ct")
        args.append(str(options["compute_type"]))
    
    # Standard preset
    if options.get("standard"):
        args.append("--standard")
    else:
        # Subtitle formatting options (only if Standard Preset is not enabled)
        # Max line width
        if options.get("max_line_width"):
            args.append("--max_line_width")
            args.append(str(int(options["max_line_width"])))
        
        # Max line count
        if options.get("max_line_count"):
            args.append("--max_line_count")
            args.append(str(int(options["max_line_count"])))
        
        # Max comma percentage
        if options.get("max_comma_cent"):
            args.append("--max_comma_cent")
            args.append(str(int(options["max_comma_cent"])))
    
    # Sentence mode (auto-enabled with diarization, Standard Preset, or if explicitly set)
    if options.get("sentence") or options.get("diarize_enable") or options.get("standard"):
        args.append("--sentence")
    
    # Note: When diarization is enabled, --sentence is automatically activated by the program
    
    # Batch processing
    if options.get("batch_recursive"):
        args.append("--batch_recursive")
    
    if options.get("check_files"):
        args.append("--check_files")
    
    # Progress
    if options.get("print_progress"):
        args.append("-pp")
    
    # Verbose
    if options.get("verbose"):
        args.append("-v")
        args.append("True")
    
    return str(exe_path), args


def validate_options(options):
    """
    Validate options dictionary for common issues.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check diarization settings
    if options.get("diarize_enable"):
        if not options.get("diarize_method"):
            return False, "Diarization method must be selected when diarization is enabled."
        
        num_speakers = options.get("num_speakers")
        min_speakers = options.get("min_speakers")
        max_speakers = options.get("max_speakers")
        
        if num_speakers and (min_speakers or max_speakers):
            return False, "Cannot set both exact speaker count and min/max speakers."
        
        if min_speakers and max_speakers and min_speakers > max_speakers:
            return False, "Minimum speakers cannot be greater than maximum speakers."
    
    # Check audio filter tempo range
    if options.get("ff_tempo"):
        tempo = float(options["ff_tempo"])
        if tempo < 0.5 or tempo > 2.0:
            return False, "Tempo must be between 0.5 and 2.0"
    
    # Check denoise range
    if options.get("ff_fftdn"):
        denoise = int(options["ff_fftdn"])
        if denoise < 0 or denoise > 97:
            return False, "Denoise value must be between 0 and 97"
    
    return True, ""

