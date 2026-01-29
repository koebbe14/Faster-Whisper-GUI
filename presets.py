"""
Preset configurations for Faster Whisper GUI.
These presets match the existing .bat file configurations.
"""

PRESETS = {
    "Standard": {
        # Model: Use large-v2 for maximum reliability and accuracy (fewer hallucinations than v3)
        "model": "large-v2",
        
        # Language: Default to English
        "language": "en",
        
        # VAD: Enable and use most accurate method for clean interview audio
        "vad_enable": True,
        "vad_method": "pyannote_v3",  # Most accurate VAD method for interview recordings
        
        # Transcription Accuracy: Optimized for MAXIMUM accuracy in controlled interview environments
        # (quiet rooms, vehicles, iPhone recordings with minimal background noise)
        "temperature": 0.0,  # Deterministic (0.0) for consistent, accurate results
        "beam_size": 10,  # Maximum beam size (10) for highest accuracy in clean audio (range: 1-10)
        "patience": 5.0,  # Maximum patience (5.0) for best sentence completeness and accuracy in interviews
        
        # Word-level features: Enable for precise timestamps
        "word_timestamps": True,  # Enable word timestamps for better accuracy and precision
        
        # Audio Filters: Minimal processing for clean iPhone recordings in controlled environments
        # Strategy: iPhone recordings in quiet rooms/vehicles are typically high quality with minimal noise
        # Using only loudness normalization - aggressive denoising can actually REDUCE accuracy for clean audio
        # DO NOT enable ff_fftdn (denoise) or ff_lowhighpass for clean recordings - they can degrade quality
        "ff_loudnorm": True,  # Normalize audio volume to broadcast standard (helps with consistency)
        # ff_fftdn (denoise) is NOT enabled - reduces accuracy for clean audio
        # ff_lowhighpass is NOT enabled - not needed for clean recordings, can reduce quality
        # ff_speechnorm is NOT enabled - iPhone recordings are typically loud enough
        
        # Output: Standard text formats
        "output_formats": ["text", "txt"],
        
        # Subtitle formatting: Option 1 settings for better sentence breaks
        "standard": False,  # Disabled - using custom formatting instead
        "max_line_width": 70,  # Increased from 42 for longer sentences
        "max_line_count": 3,  # Increased from 2 to allow more lines per segment
        "max_comma_cent": 90,  # Increased from 70 to reduce comma breaks
        "sentence": True,  # Enable sentence mode for better segmentation
        
        "batch_recursive": True,
        "check_files": True,
        "print_progress": True,
        "output_dir": "source"
    },
    "Turbo": {
        # Model: Use turbo for speed while maintaining good accuracy
        "model": "turbo",  # Fast model optimized for speed
        
        # Language: Default to English
        "language": "en",
        
        # VAD: Enable for better accuracy even in fast mode
        "vad_enable": True,
        "vad_method": "silero_v4_fw",  # Faster VAD method, still accurate for interviews
        
        # Transcription Accuracy: Balance speed and accuracy
        "temperature": 0.0,  # Deterministic (0.0) for consistent results
        "beam_size": 5,  # Default beam size (5) - balanced for speed and accuracy
        "patience": 2.0,  # Default patience (2.0) - standard setting for speed
        
        # Word-level features: Enable for timestamps
        "word_timestamps": True,  # Enable word timestamps
        
        # Audio Filters: Light normalization for interview recordings
        "ff_loudnorm": True,  # Normalize audio volume for consistency
        
        # Output: Standard text formats
        "output_formats": ["text", "txt"],
        
        # Subtitle formatting: Option 1 settings for better sentence breaks
        "standard": False,  # Disabled - using custom formatting instead
        "max_line_width": 70,  # Increased from 42 for longer sentences
        "max_line_count": 3,  # Increased from 2 to allow more lines per segment
        "max_comma_cent": 90,  # Increased from 70 to reduce comma breaks
        "sentence": True,  # Enable sentence mode for better segmentation
        
        "batch_recursive": True,
        "check_files": True,
        "print_progress": True,
        "output_dir": "source"
    },
    "Diarize": {
        # Model: Use large-v2 for maximum reliability and accuracy (fewer hallucinations than v3)
        "model": "large-v2",
        
        # Language: Default to English
        "language": "en",
        
        # VAD: Enable and use most accurate method for clean interview audio
        "vad_enable": True,
        "vad_method": "pyannote_v3",  # Most accurate VAD method for interview recordings
        
        # Diarization: Use latest method optimized for accuracy
        "diarize": "pyannote_v3.1",  # Latest and most accurate diarization method
        "diarize_ff": True,  # Apply diarization AFTER audio filters for better accuracy
        
        # Transcription Accuracy: Optimized for MAXIMUM accuracy in controlled interview environments
        # (quiet rooms, vehicles, iPhone recordings with minimal background noise)
        "temperature": 0.0,  # Deterministic (0.0) for consistent, accurate results
        "beam_size": 10,  # Maximum beam size (10) for highest accuracy in clean audio (range: 1-10)
        "patience": 5.0,  # Maximum patience (5.0) for best sentence completeness and accuracy in interviews
        
        # Word-level features: Enable for precise timestamps and better accuracy
        "word_timestamps": True,  # Enable word timestamps for better accuracy and precision
        
        # Audio Filters: Minimal processing for clean iPhone recordings in controlled environments
        # Strategy: iPhone recordings in quiet rooms/vehicles are typically high quality with minimal noise
        # Using only loudness normalization - aggressive denoising can actually REDUCE accuracy for clean audio
        # DO NOT enable ff_fftdn (denoise) or ff_lowhighpass for clean recordings - they can degrade quality
        "ff_loudnorm": True,  # Normalize audio volume to broadcast standard (helps with consistency)
        # ff_fftdn (denoise) is NOT enabled - reduces accuracy for clean audio
        # ff_lowhighpass is NOT enabled - not needed for clean recordings, can reduce quality
        # ff_speechnorm is NOT enabled - iPhone recordings are typically loud enough
        
        # Output: Include multiple formats for flexibility
        "output_formats": ["text", "txt", "srt", "vtt"],  # Multiple formats including SRT/VTT for speaker labeling
        
        # Subtitle formatting: Option 1 settings for better sentence breaks
        # Note: Sentence mode is auto-enabled with diarization, but we set it explicitly for clarity
        "standard": False,  # Disabled - using custom formatting instead
        "max_line_width": 70,  # Increased from 42 for longer sentences
        "max_line_count": 3,  # Increased from 2 to allow more lines per segment
        "max_comma_cent": 90,  # Increased from 70 to reduce comma breaks
        "sentence": True,  # Enable sentence mode (also auto-enabled by diarization)
        
        "batch_recursive": True,
        "check_files": True,
        "print_progress": True,
        "output_dir": "source"
        
        # IMPORTANT: Speaker count (num_speakers) should be set by user based on their specific interview.
        # Most interviews have 2 speakers, but this varies - users should set this manually for best accuracy.
        # Setting the exact speaker count dramatically improves diarization accuracy.
    },
    "Phone Conversation Audio": {
        # Model: Use large-v2 for maximum reliability with low-quality/noisy audio
        "model": "large-v2",  # More robust than smaller models for degraded audio
        
        # Language: Default to English
        "language": "en",
        
        # VAD: Enable and use most accurate method for noisy phone audio
        "vad_enable": True,
        "vad_method": "pyannote_v3",  # Most accurate VAD, important for noisy audio
        
        # Diarization: Enable for phone conversations (typically 2 speakers)
        "diarize": "pyannote_v3.1",  # Latest and most accurate diarization method
        "diarize_ff": True,  # Apply diarization AFTER audio filters for better accuracy
        
        # Transcription Accuracy: Optimize for accuracy in challenging audio conditions
        "temperature": 0.0,  # Deterministic (0.0) for consistent, accurate results
        "beam_size": 8,  # Higher beam size (8) for better accuracy in noisy/low-quality audio
        "patience": 4.0,  # Higher patience (4.0) for better sentence completeness in degraded audio
        
        # Word-level features: Enable for precise timestamps
        "word_timestamps": True,  # Enable word timestamps for better accuracy
        
        # Audio Filters: Aggressive preprocessing for low-quality phone audio
        # Phone calls typically have: background noise, low quality, narrow frequency range
        "ff_speechnorm": True,  # Amplify quiet speech (important for phone audio)
        "ff_loudnorm": True,  # Normalize audio volume to broadcast standard
        "ff_lowhighpass": True,  # Remove frequencies outside 50Hz-7800Hz (focuses on speech, reduces noise)
        "ff_fftdn": 15,  # Moderate denoise (15) - reduces background noise without over-processing
        # Note: 12 is normal strength, 15 is slightly more aggressive for phone calls
        
        # Output: Include multiple formats for flexibility
        "output_formats": ["text", "txt", "srt", "vtt"],  # Multiple formats including SRT/VTT for speaker labeling
        
        # Subtitle formatting: Option 1 settings for better sentence breaks
        # Note: Sentence mode is auto-enabled with diarization, but we set it explicitly for clarity
        "standard": False,  # Disabled - using custom formatting instead
        "max_line_width": 70,  # Increased from 42 for longer sentences
        "max_line_count": 3,  # Increased from 2 to allow more lines per segment
        "max_comma_cent": 90,  # Increased from 70 to reduce comma breaks
        "sentence": True,  # Enable sentence mode (also auto-enabled by diarization)
        
        "batch_recursive": True,
        "check_files": True,
        "print_progress": True,
        "output_dir": "source"
        
        # IMPORTANT: For phone conversations, set speaker count to 2 if known (most phone calls are 2 speakers).
        # Setting the exact speaker count dramatically improves diarization accuracy in noisy conditions.
    },
    "Custom": {
        # Empty dict - user configures everything manually
    }
}

def get_preset(name):
    """Get a preset configuration by name."""
    return PRESETS.get(name, PRESETS["Custom"]).copy()

def get_preset_names():
    """Get list of available preset names."""
    return list(PRESETS.keys())

