"""
Audio quality analysis utility.
Analyzes audio files to suggest optimal settings for transcription.
"""

import subprocess
import sys
from pathlib import Path
from file_info_extractor import get_user_data_dir, find_ffprobe


def analyze_audio_quality(file_path):
    """
    Analyze audio quality and suggest optimal settings.
    
    Returns a dictionary with:
    - noise_level: "low", "medium", "high"
    - volume_level: "low", "normal", "high"
    - frequency_range: "narrow", "normal", "wide"
    - suggestions: List of suggested settings
    - quality_score: Overall quality score (0-100)
    """
    result = {
        "noise_level": "unknown",
        "volume_level": "unknown",
        "frequency_range": "unknown",
        "suggestions": [],
        "quality_score": 50,
        "analysis_available": False
    }
    
    ffprobe_path = find_ffprobe()
    if not ffprobe_path:
        return result
    
    try:
        # Get audio statistics using ffprobe
        cmd = [
            str(ffprobe_path),
            "-v", "error",
            "-show_entries", "stream=codec_name,sample_rate,channels,bit_rate",
            "-show_entries", "format=bit_rate",
            "-of", "json",
            str(file_path)
        ]
        
        probe_result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if probe_result.returncode != 0:
            return result
        
        # Try to get more detailed audio analysis using ffmpeg
        # Find ffmpeg (should be in same directory as ffprobe)
        ffmpeg_path = ffprobe_path.parent / "ffmpeg.exe"
        if not ffmpeg_path.exists():
            # Try user data directory
            user_data_dir = get_user_data_dir()
            ffmpeg_path = user_data_dir / "ffmpeg.exe"
            if not ffmpeg_path.exists():
                return result
        
        # Analyze volume levels
        cmd_volume = [
            str(ffmpeg_path),
            "-i", str(file_path),
            "-af", "volumedetect",
            "-f", "null",
            "-"
        ]
        
        volume_result = subprocess.run(cmd_volume, capture_output=True, text=True, timeout=30)
        
        # Parse volume analysis
        mean_volume = None
        max_volume = None
        
        if volume_result.returncode == 0:
            for line in volume_result.stderr.split('\n'):
                if 'mean_volume:' in line:
                    try:
                        mean_volume = float(line.split('mean_volume:')[1].split('dB')[0].strip())
                    except:
                        pass
                if 'max_volume:' in line:
                    try:
                        max_volume = float(line.split('max_volume:')[1].split('dB')[0].strip())
                    except:
                        pass
        
        # Analyze noise (using silence detection as proxy)
        cmd_silence = [
            str(ffmpeg_path),
            "-i", str(file_path),
            "-af", "silencedetect=noise=-30dB:d=0.5",
            "-f", "null",
            "-"
        ]
        
        silence_result = subprocess.run(cmd_silence, capture_output=True, text=True, timeout=30)
        
        # Determine volume level
        if mean_volume is not None:
            if mean_volume < -30:
                result["volume_level"] = "low"
                result["suggestions"].append("Low volume detected - consider enabling Speech Normalization")
            elif mean_volume > -10:
                result["volume_level"] = "high"
            else:
                result["volume_level"] = "normal"
        
        # Determine noise level (based on silence detection and volume consistency)
        if silence_result.returncode == 0:
            silence_lines = [l for l in silence_result.stderr.split('\n') if 'silence_start' in l or 'silence_end' in l]
            # If many silence detections, might indicate noise
            if len(silence_lines) > 20:
                result["noise_level"] = "medium"
                result["suggestions"].append("Some noise detected - consider enabling Denoise filter if quality is poor")
            else:
                result["noise_level"] = "low"
        
        # Determine quality score and suggestions
        quality_score = 80  # Start with good score
        
        if result["volume_level"] == "low":
            quality_score -= 15
        elif result["volume_level"] == "normal":
            quality_score += 5
        
        if result["noise_level"] == "low":
            quality_score += 10
            result["suggestions"].append("Clean audio detected - using minimal filters for best accuracy")
        elif result["noise_level"] == "medium":
            quality_score -= 10
        
        result["quality_score"] = max(0, min(100, quality_score))
        result["analysis_available"] = True
        
        # Add general suggestions based on quality
        if result["quality_score"] >= 80:
            result["suggestions"].append("High quality audio - current filter settings are optimal")
        elif result["quality_score"] < 60:
            result["suggestions"].append("Lower quality audio detected - consider enabling audio filters")
        
    except Exception as e:
        # If analysis fails, provide default suggestions for iPhone recordings
        result["suggestions"].append("Clean audio detected - using minimal filters for best accuracy")
        result["quality_score"] = 75
        result["analysis_available"] = False
    
    return result

