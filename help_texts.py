"""
Comprehensive help text and explanations for Faster Whisper GUI options.
Provides tooltips and detailed explanations for all features.
"""

# Quick tooltips for hover help
TOOLTIPS = {
    "task": "Choose 'Transcribe' to keep the original language, or 'Translate' to convert to English.",
    "model": "Larger models are more accurate but slower. 'turbo' is fastest, 'large-v2' is balanced.",
    "language": "Select the language spoken in the audio, or 'Auto-detect' to let the program identify it.",
    "output_formats": "Choose one or more output formats. SRT and VTT are subtitle formats, TXT is plain text, JSON contains all metadata.",
    "vad_enable": "Voice Activity Detection filters out parts of audio without speech, improving accuracy.",
    "vad_method": "Different VAD methods vary in speed and accuracy. Click ? for details.",
    "word_timestamps": "Include precise timestamps for each word (required for karaoke/highlight words).",
    "highlight_words": "Underline each word as it's spoken in subtitle files (karaoke effect).",
    "diarize_enable": "Identify different speakers in the audio. Essential for interviews, meetings, and podcasts.",
    "diarize_method": "Different methods for identifying speakers. Click ? for detailed comparison.",
    "num_speakers": "Set if you know the exact number of speakers (improves accuracy). Leave empty for auto-detection.",
    "min_speakers": "Minimum number of speakers to detect. Leave empty for no minimum.",
    "max_speakers": "Maximum number of speakers to detect. Leave empty for no maximum.",
    "speaker_label": "Prefix used for speaker identification (e.g., 'SPEAKER', 'Person', 'Host').",
    "diarize_device": "Device to use for diarization. GPU/CUDA is much faster than CPU.",
    "diarize_threads": "Number of CPU threads for diarization. Auto uses optimal setting.",
    "diarize_only": "Perform only speaker identification without transcription. Click ? for details.",
    "return_embeddings": "Save speaker embeddings to files. Click ? for details.",
    "diarize_ff": "Control when diarization is applied relative to audio filters. Click ? for details.",
    "diarize_dump": "Save diarization debug output to files. Click ? for details.",
    "ff_speechnorm": "Amplify quiet speech to make it more audible. Click ? for details.",
    "ff_loudnorm": "Normalize audio volume to EBU R128 standard (broadcast quality). Click ? for details.",
    "ff_lowhighpass": "Remove frequencies outside 50Hz-7800Hz range (focuses on speech). Click ? for details.",
    "ff_tempo": "Adjust playback speed. Values below 1.0 slow down, above 1.0 speed up.",
    "ff_fftdn": "Reduce background noise. Higher values = more aggressive noise reduction.",
    "temperature": "Controls randomness in transcription. 0 = deterministic (recommended), higher = more variation.",
    "beam_size": "Number of transcription candidates to consider. Higher = more accurate but slower (default: 5).",
    "patience": "How long to wait before finalizing a segment. Higher = more patient (default: 2.0).",
    "device": "Device for transcription. CUDA/GPU is much faster if available.",
    "compute_type": "Quantization type for model. Controls how numbers are stored and processed. 'auto' is recommended.",
    "standard_preset": "Apply standard subtitle formatting preset. Click ? for details.",
    "max_line_width": "Maximum characters per subtitle line. Disabled when Standard Preset is enabled. Click ? for details.",
    "max_line_count": "Maximum lines per subtitle segment. Disabled when Standard Preset is enabled. Click ? for details.",
    "max_comma_percentage": "Percentage of line width before breaking at commas. Disabled when Standard Preset is enabled. Click ? for details.",
    "sentence_mode": "Split subtitles at sentence boundaries. Auto-enabled with diarization. Click ? for details.",
    "batch_recursive": "Process files recursively in subdirectories. Click ? for details.",
    "check_files": "Verify input files before processing. Click ? for details.",
}

# Detailed explanations for question mark buttons
DETAILED_HELP = {
    "vad_method": {
        "title": "Voice Activity Detection (VAD) Methods",
        "content": """Voice Activity Detection identifies parts of audio that contain speech, filtering out silence and noise.

Available methods:
• pyannote_v3: Most accurate, best for complex audio with background noise. Slower but produces best results.
• silero_v4_fw / silero_v5_fw: Faster, good for most cases. Recommended default for balanced speed and accuracy.
• silero_v3: Older version, less accurate than v4/v5.
• webrtc: Very fast and lightweight, but less accurate. Good for real-time applications.
• auditok: Alternative method, may work better in some specific scenarios.

Recommendation: Start with silero_v4_fw or silero_v5_fw. Use pyannote_v3 if you need maximum accuracy."""
    },
    
    "diarize_method": {
        "title": "Speaker Diarization Methods - Accuracy Guide",
        "content": """Speaker diarization identifies who is speaking at different times in the audio.

Available methods (ranked by accuracy):
• pyannote_v3.1: ⭐ BEST ACCURACY - Latest version, most accurate speaker identification. Recommended default for maximum accuracy. Best for interviews, meetings, podcasts with multiple speakers. Use this when accuracy is your top priority.

• pyannote_v3.0: ⭐ HIGH ACCURACY - Older but stable version, slightly less accurate than v3.1. Use if v3.1 has compatibility issues or if you need a proven stable option.

• reverb_v2: ⭐ GOOD FOR ECHO - Improved reverb method, excellent for challenging audio environments with echo or reverb (recorded in large rooms, halls, auditoriums). Use when your audio has significant reverb or echo that affects speaker separation.

• reverb_v1: ⚠️ OLDER METHOD - Older reverb method, less accurate than v2. Only use if v2 is not available.

ACCURACY TIPS:
1. Use pyannote_v3.1 for best results (default in Diarize preset)
2. Set exact speaker count if known (dramatically improves accuracy)
3. Use larger models (large-v2, large-v3-turbo) for better diarization
4. Enable audio filters to clean audio first (improves diarization accuracy)
5. Use GPU/CUDA for faster processing (doesn't affect accuracy but makes it practical)

When to use diarization:
• Interviews and conversations
• Meetings with multiple participants
• Podcasts with multiple hosts
• Any audio where identifying who is speaking is important

Performance: Diarization is computationally intensive. Use GPU/CUDA if available for much faster processing."""
    },
    
    "model": {
        "title": "Whisper Models - Complete Guide",
        "content": """Different models offer different balances of accuracy and speed. Choose based on your priorities.

MODELS RANKED BY ACCURACY (Best to Fastest):

⭐ BEST ACCURACY:
• large-v2: ⭐ RECOMMENDED - Excellent accuracy, proven and reliable. Fewer hallucinations than v3 models. Best choice for most use cases, especially when accuracy and reliability are important.

• large-v3-turbo: Latest turbo-optimized model. Good accuracy with better speed than large-v3. May have more hallucinations than large-v2 in some cases.

• large-v3: Latest full Whisper model. May produce worse results than large-v2 due to increased hallucinations, especially in difficult audio conditions. Use with caution.

• large-v1: Older large model. Still accurate but superseded by v2/v3.

BALANCED OPTIONS:
• medium: Good balance of accuracy and speed. Recommended minimum for decent quality transcriptions. Good for general use.

FAST BUT LESS ACCURATE:
• small: Faster processing, acceptable accuracy for simple audio. Good for quick transcriptions.

• base: Base model, faster but less accurate. Use for speed when accuracy is less critical.

• tiny: Smallest, fastest model. Least accurate. Only use for very fast processing when accuracy can be sacrificed.

LEGACY:
• turbo: Legacy turbo model (may be same as large-v3-turbo). Fast with good accuracy.

RECOMMENDATIONS:
• Maximum Accuracy: large-v2 (most reliable, fewer hallucinations) or large-v3-turbo
• Best Balance: large-v2 or large-v3-turbo
• Speed Priority: medium or small
• Quick Processing: base or tiny

Note: large-v3 may produce worse results than large-v2 due to increased hallucinations. large-v2 is recommended for most use cases.

For Diarization: Use large-v2 (recommended) or large-v3-turbo for best speaker identification accuracy.

Note: Larger models require more VRAM/RAM. Ensure your system has sufficient resources."""
    },
    
    "output_formats": {
        "title": "Output Formats",
        "content": """Choose one or more formats for your transcription output.

Available formats:
• SRT: Standard subtitle format, widely compatible with video players and editing software. Includes timestamps and text.
• VTT: Web Video Text Tracks format, similar to SRT, used for web videos. Includes timestamps and text.
• TXT: Plain text file with transcription. Always includes timestamps along with the text content. Timestamps appear at the beginning of each segment.
• JSON: Detailed data format with all metadata, timestamps, word-level data, and speaker information (if diarization enabled). Structured format for programmatic use.

Note: If diarization is enabled, speaker labels will be included in all formats except JSON."""
    },
    
    "presets": {
        "title": "Presets - Quick Start Configurations",
        "content": """Presets provide optimized starting configurations for different use cases. You can modify any settings after selecting a preset.

AVAILABLE PRESETS:

⭐ STANDARD (Recommended for most users)
• Best for: General transcription tasks, interviews, podcasts, meetings
• Model: large-v2 (excellent accuracy, reliable, fewer hallucinations)
• Settings: Optimized for MAXIMUM accuracy in controlled interview environments
• VAD: Enabled with pyannote_v3 (most accurate method)
• Beam Size: 10 (maximum accuracy)
• Patience: 5.0 (maximum completeness)
• Word Timestamps: Enabled
• Audio Filters: Loudness normalization only
• Output: TXT format
• When to use: Most common use case - clean audio, interviews, general transcription needs

⚡ TURBO (Speed optimized)
• Best for: Quick transcriptions when speed is priority
• Model: turbo (fast while maintaining good accuracy)
• Settings: Balanced for speed and accuracy
• VAD: Enabled with silero_v4_fw (faster method)
• Beam Size: 5 (default, balanced)
• Patience: 2.0 (default, faster)
• Word Timestamps: Enabled
• Audio Filters: Light normalization
• Output: TXT format
• When to use: When you need fast results and can accept slightly lower accuracy

🎤 DIARIZE (Speaker identification)
• Best for: Interviews, meetings, podcasts with multiple speakers
• Model: large-v2 (best for speaker identification accuracy)
• Settings: Optimized for MAXIMUM accuracy in controlled interview environments
• Diarization: Enabled with pyannote_v3.1 (latest, most accurate method)
• VAD: Enabled with pyannote_v3 (most accurate)
• Beam Size: 10 (maximum accuracy)
• Patience: 5.0 (maximum completeness)
• Word Timestamps: Enabled
• Audio Filters: Loudness normalization
• Output: TXT, SRT, VTT formats (multiple formats for speaker labeling)
• When to use: When you need to identify who is speaking (interviews, meetings, multi-speaker content)
• ⚠️ IMPORTANT: Set the exact number of speakers if known (dramatically improves accuracy)

📞 PHONE CONVERSATION AUDIO (Low-quality/noisy audio)
• Best for: Phone calls, low-quality recordings, noisy audio
• Model: large-v2 (robust for degraded audio)
• Settings: Optimized for challenging audio conditions
• Diarization: Enabled with pyannote_v3.1
• VAD: Enabled with pyannote_v3 (most accurate for noisy audio)
• Beam Size: 8 (higher for noisy conditions)
• Patience: 4.0 (better for degraded audio)
• Word Timestamps: Enabled
• Audio Filters: Aggressive preprocessing
  - Speech normalization (amplifies quiet speech)
  - Loudness normalization
  - Low/high pass filter (removes non-speech frequencies)
  - Denoise: 15 (moderate noise reduction)
• Output: TXT, SRT, VTT formats
• When to use: Phone calls, recordings with background noise, low-quality audio
• ⚠️ IMPORTANT: For phone calls, set speaker count to 2 if known (most calls are 2 speakers)

🔧 CUSTOM
• Best for: Advanced users who want full control
• Settings: No pre-configured settings - you configure everything manually
• When to use: When you want to set all options yourself from scratch

TIPS:
• You can modify any setting after selecting a preset
• For best diarization accuracy, always set the exact speaker count if known
• Presets are starting points - feel free to customize based on your specific needs"""
    },
    
    "audio_filters": {
        "title": "Audio Filters",
        "content": """Audio filters preprocess your audio to improve transcription quality.

• Speech Normalization (ff_speechnorm): Amplifies quiet speech to make it more audible. Use when speakers are too quiet.
• Loudness Normalization (ff_loudnorm): Normalizes audio volume to EBU R128 broadcast standard. Use for consistent volume levels.
• Low/High Pass Filter (ff_lowhighpass): Removes frequencies outside 50Hz-7800Hz range, focusing on speech frequencies. Use to reduce background noise.
• Tempo Adjustment (ff_tempo): Adjusts playback speed. Values below 1.0 slow down (helpful for fast speech), above 1.0 speed up.
• Denoise (ff_fftdn): Reduces background noise using Fast Fourier Transform. Higher values = more aggressive (0-97, default: 0 = disabled).

Use filters when your audio has quality issues. Start with one filter at a time to see the effect."""
    },
    
    "advanced_options": {
        "title": "Advanced Transcription Options",
        "content": """These options fine-tune the transcription process.

• Temperature: Controls randomness in transcription. 0 = deterministic (recommended for consistent results), higher values = more variation. Default: 0.
• Beam Size: Number of transcription candidates to consider. Higher = more accurate but slower. Range: 1-10, default: 5.
• Patience: How long the model waits before finalizing a segment. Higher = more patient, may improve accuracy. Default: 2.0.
• Best Of: Number of candidates when sampling with non-zero temperature. Default: 5.
• Length Penalty: Token length penalty coefficient. Default: 1.0.
• Repetition Penalty: Penalty for repeating tokens. Values > 1.0 penalize repetition. Default: 1.0.

Most users should leave these at default values unless experiencing specific issues."""
    },
    
    "diarization_settings": {
        "title": "Speaker Count Settings - Accuracy Optimization",
        "content": """Configure how many speakers to identify in your audio. Setting these correctly is CRITICAL for accuracy.

• Number of Speakers: ⭐ MOST IMPORTANT - Set the exact number of speakers if known. This dramatically improves accuracy. The program will look for exactly this many speakers, which prevents false positives and improves separation quality.

• Min Speakers: Set minimum number of speakers to detect. Use when you know there are at least X speakers but not the exact count.

• Max Speakers: Set maximum number of speakers to detect. Use when you know there are at most X speakers but not the exact count.

ACCURACY BEST PRACTICES:
1. ⭐ SET EXACT COUNT: If you know there are exactly 2, 3, 4, etc. speakers, set "Number of Speakers" to that exact number. This is the SINGLE MOST IMPORTANT setting for accuracy.

2. Use Min/Max when you have a range: If you know there are 2-4 speakers but not the exact count, set Min=2, Max=4.

3. Auto-detection (all empty): Only use when you truly don't know the speaker count. Less accurate than setting the exact count.

Examples:
• Interview with 2 people: Set Number of Speakers = 2 ⭐ BEST ACCURACY
• Meeting with 3-5 participants: Set Min = 3, Max = 5
• Podcast with 2 hosts: Set Number of Speakers = 2 ⭐ BEST ACCURACY
• Unknown number: Leave all empty (less accurate)

Remember: Setting the exact speaker count is the #1 way to improve diarization accuracy!"""
    },
    
    "device_selection": {
        "title": "Device Selection (CPU vs GPU)",
        "content": """Choose which device to use for processing.

• Auto: Automatically detects and uses CUDA/GPU if available, otherwise uses CPU.
• CUDA: Use GPU for processing. Much faster than CPU, especially for large models and diarization. Requires NVIDIA GPU with CUDA support.
• CPU: Use CPU only. Slower but works on any computer.

Recommendation: Use Auto or CUDA if you have an NVIDIA GPU. GPU processing can be 5-10x faster than CPU."""
    },
    
    "diarize_device": {
        "title": "Diarization Device Selection",
        "content": """Choose which device to use specifically for speaker diarization processing.

• Auto: Automatically detects and uses CUDA/GPU if available, otherwise uses CPU. Recommended default.

• CUDA: Use GPU for diarization. MUCH faster than CPU (5-10x speedup). Strongly recommended if you have an NVIDIA GPU with CUDA support. Diarization is computationally intensive, so GPU makes a huge difference.

• CPU: Use CPU only for diarization. Works on any computer but significantly slower. Only use if you don't have a compatible GPU.

IMPORTANT FOR ACCURACY:
• Device selection does NOT affect accuracy - GPU and CPU produce the same results
• GPU is much faster, making it practical to use larger models and higher settings
• For best accuracy workflow: Use GPU + larger models (large-v2, large-v3-turbo) + higher beam size

Note: This is separate from the main transcription device setting. You can use GPU for diarization even if using CPU for transcription (though not recommended).

Recommendation: Use Auto or CUDA if available. GPU makes diarization practical for real-world use."""
    },
    
    "task": {
        "title": "Task Selection (Transcribe vs Translate)",
        "content": """Choose what the program should do with your audio.

• Transcribe: Converts speech to text in the original language. The output will be in whatever language is spoken in the audio (e.g., Spanish audio → Spanish text).

• Translate: Converts speech to text and translates it to English. The output will always be in English, regardless of the source language.

When to use each:
• Use Transcribe when you want to preserve the original language or when working with English audio.
• Use Translate when you need English text from non-English audio.

Note: When using Translate, you should still select the source language (the language spoken in the audio) for best accuracy."""
    },
    
    "language": {
        "title": "Language Selection",
        "content": """Select the language spoken in your audio file.

• Auto-detect: Let the program automatically identify the language. Works well for most cases but may be slightly less accurate than manual selection.

• Specific Language: Select the exact language for better accuracy. This is especially important for:
  - Audio with multiple languages
  - Languages that are similar to each other
  - When using the Translate task

Available languages include: English, Spanish, French, German, Japanese, Chinese, and many more.

Tip: If you're unsure, start with Auto-detect. If the results are poor, try selecting the language manually."""
    },
    
    "speaker_label": {
        "title": "Speaker Label",
        "content": """Customize the prefix used to identify speakers in the output.

Default: "SPEAKER"

Examples:
• "SPEAKER" → SPEAKER_00, SPEAKER_01, etc.
• "Person" → Person_00, Person_01, etc.
• "Host" → Host_00, Host_01, etc. (good for podcasts)
• "Interviewer" → Interviewer_00, Interviewee_01, etc.

This label appears in the transcription output to identify which speaker said each line. You can customize it to match your use case or workflow."""
    },
    
    "diarize_threads": {
        "title": "Diarization Threads",
        "content": """Number of CPU threads to use for diarization processing.

• Auto (0): Automatically determines the optimal number of threads based on your CPU. Recommended for most users.

• Manual: Set a specific number of threads (1-32). Use this if:
  - You want to limit CPU usage
  - You're running other intensive programs
  - Auto-detection isn't working well

Note: This only affects CPU processing. If you're using GPU/CUDA, this setting has no effect.

For best accuracy: Use Auto or set to match your CPU core count."""
    },
    
    "diarize_ff": {
        "title": "Diarize After Filters",
        "content": """Control the order of processing: when diarization runs relative to audio filters.

What it does:
This checkbox determines whether diarization is applied BEFORE or AFTER audio filters (like denoise, normalization, etc.).

• CHECKED (Enabled - Recommended): 
  Processing order: Audio Filters → Diarization → Transcription
  - Audio is cleaned/filtered first (noise reduction, normalization, etc.)
  - Then diarization runs on the cleaned audio
  - Better accuracy because diarization works with cleaner, better-quality audio
  - Recommended when using audio filters

• UNCHECKED (Disabled):
  Processing order: Diarization → Audio Filters → Transcription
  - Diarization runs on original, unfiltered audio
  - Then filters are applied to the audio
  - May be slightly faster but potentially less accurate
  - Use only if you're not using audio filters

When to use each:
• CHECKED: Use when you have audio filters enabled (denoise, normalization, etc.) - this is the default and recommended setting
• UNCHECKED: Only use if you're not using any audio filters and want slightly faster processing

Recommendation: Keep this CHECKED (enabled) for best accuracy, especially when using audio filters."""
    },
    
    "diarize_only": {
        "title": "Diarize Only (No Transcription)",
        "content": """Perform speaker identification WITHOUT transcribing the audio.

What it does:
• Identifies and labels different speakers in the audio
• Creates speaker segments with timestamps
• Does NOT create any transcription text
• Outputs only speaker identification data

When to use:
• You only need to know WHO is speaking and WHEN, not WHAT they're saying
• You want to analyze speaker patterns or conversation flow
• You'll do transcription separately or with different settings
• Testing or debugging diarization settings

Output:
• Speaker segments with timestamps
• Speaker labels (SPEAKER_00, SPEAKER_01, etc.)
• No transcription text

Note: This is useful for specialized workflows. Most users will want transcription AND diarization together (leave this unchecked)."""
    },
    
    "return_embeddings": {
        "title": "Return Embeddings",
        "content": """Save speaker embedding vectors to separate files.

What are embeddings?
Speaker embeddings are mathematical representations of each speaker's voice characteristics. They're used internally by the diarization system to identify and distinguish speakers.

What this option does:
• Saves one embedding file per speaker
• Creates separate files for each unique speaker identified
• Files contain the voice "fingerprint" data for each speaker

When to use:
• Advanced analysis of speaker characteristics
• Research or development work
• Building speaker recognition systems
• Debugging diarization issues
• Creating speaker profiles for future matching

File format:
• One file per speaker (e.g., speaker_0.emb, speaker_1.emb)
• Binary or text format depending on implementation
• Contains numerical vectors representing voice characteristics

Note: This is an advanced feature. Most users don't need this unless doing specialized work with speaker recognition."""
    },
    
    "diarize_dump": {
        "title": "Dump Diarization Output",
        "content": """Save detailed diarization debug information to files.

What it does:
• Saves intermediate diarization processing data
• Creates debug files showing how speakers were identified
• Includes timing information, confidence scores, and processing details
• Useful for troubleshooting diarization issues

Output files:
• Diarization timing data
• Speaker segment boundaries
• Confidence scores for speaker identification
• Processing logs and intermediate results

When to use:
• Troubleshooting diarization accuracy issues
• Understanding why speakers were identified incorrectly
• Debugging diarization performance problems
• Research or development work
• Fine-tuning diarization settings

What you'll get:
• Detailed logs of the diarization process
• Information about how the system made decisions
• Data that can help identify why certain speakers were or weren't detected

Note: This creates additional files and increases processing time slightly. Only enable when you need to debug or analyze the diarization process."""
    },
    
    "ff_speechnorm": {
        "title": "Speech Normalization",
        "content": """Amplify quiet speech segments to make them more audible and easier to transcribe.

What it does:
• Automatically detects quiet speech segments
• Amplifies (increases volume of) quiet speech
• Makes soft-spoken words more audible
• Improves transcription accuracy for quiet speakers

When to use:
• Audio with speakers who talk quietly
• Recordings with inconsistent volume levels
• Interviews where one person is much quieter than another
• Audio where speech volume varies significantly
• When transcription misses quiet words or phrases

How it works:
• Analyzes audio to identify speech segments
• Detects segments that are quieter than average
• Amplifies those segments to match normal speech levels
• Preserves loud segments at their original level

Benefits:
• Better transcription of quiet speech
• More consistent volume levels
• Improved accuracy for soft-spoken speakers
• Better handling of volume variations

Note: This filter focuses specifically on speech frequencies. It's different from general loudness normalization which affects the entire audio signal.

Recommendation: Enable if you have issues with quiet speech not being transcribed accurately."""
    },
    
    "ff_loudnorm": {
        "title": "Loudness Normalization (EBU R128)",
        "content": """Normalize audio volume to broadcast industry standard (EBU R128 loudness standard).

What it does:
• Adjusts overall audio volume to meet broadcast standards
• Ensures consistent loudness across the entire audio file
• Applies professional broadcast audio normalization
• Makes audio suitable for professional use

EBU R128 Standard:
• European Broadcasting Union standard for audio loudness
• Used by TV, radio, and streaming services
• Ensures consistent volume across different content
• Prevents audio from being too loud or too quiet

When to use:
• Preparing audio for broadcast or streaming
• Audio with inconsistent volume levels
• Professional transcription projects
• When you need consistent loudness
• Audio that will be used in professional contexts

How it works:
• Measures integrated loudness (overall perceived volume)
• Adjusts gain to target loudness level (-23 LUFS standard)
• Applies true peak limiting to prevent clipping
• Maintains audio quality while normalizing volume

Benefits:
• Professional-grade audio normalization
• Consistent volume levels
• Meets broadcast standards
• Better for professional use cases
• Prevents audio from being too loud or too quiet

Note: This is more comprehensive than speech normalization - it normalizes the entire audio signal, not just speech segments.

Recommendation: Use for professional projects or when you need broadcast-quality audio normalization."""
    },
    
    "ff_lowhighpass": {
        "title": "Low/High Pass Filter",
        "content": """Remove frequencies outside the speech range (50Hz to 7800Hz) to focus on human speech.

What it does:
• Removes very low frequencies (below 50Hz) - rumble, wind noise, etc.
• Removes very high frequencies (above 7800Hz) - hiss, cymbals, etc.
• Keeps frequencies in the human speech range
• Focuses audio processing on speech content

Frequency ranges:
• Low frequencies (removed): Below 50Hz - rumble, wind, traffic noise
• Speech frequencies (kept): 50Hz to 7800Hz - human voice range
• High frequencies (removed): Above 7800Hz - hiss, cymbals, high-pitched noise

When to use:
• Audio with low-frequency rumble or wind noise
• Recordings with high-frequency hiss or static
• Audio with background noise outside speech range
• When you want to focus processing on speech only
• Recordings made in noisy environments

How it works:
• Uses sinc filter for low frequencies (high quality)
• Uses afir filter for high frequencies
• Preserves speech frequencies (50Hz-7800Hz)
• Removes frequencies that don't contain speech

Benefits:
• Reduces non-speech noise
• Improves transcription accuracy
• Cleaner audio for processing
• Better focus on speech content
• Reduces interference from background noise

Examples of what gets removed:
• Low frequencies: Rumble, wind, traffic, machinery
• High frequencies: Hiss, static, cymbals, electronic noise

Note: This is a frequency filter, not a noise reduction filter. It removes entire frequency ranges, which can affect music or other non-speech audio.

Recommendation: Enable when you have low-frequency rumble or high-frequency hiss that interferes with transcription."""
    },
    
    "compute_type": {
        "title": "Compute Type (Quantization)",
        "content": """Control how numbers are stored and processed in the AI model. Affects speed, memory usage, and accuracy.

Available options:
• auto: Automatically selects the best type based on your hardware. Recommended for most users. Best balance of speed and accuracy.

• default: Uses the model's default precision. Good general-purpose option.

• int8: 8-bit integers. Fastest, uses least memory, but slightly less accurate. Good for speed when accuracy is less critical.

• float16: 16-bit floating point. Fast, uses less memory than float32, good accuracy. Good balance for GPU processing.

• float32: 32-bit floating point. Most accurate, uses most memory, slower. Best accuracy but requires more resources.

What is quantization?
Quantization reduces the precision of numbers in the AI model to make it run faster and use less memory. Lower precision = faster but potentially less accurate.

Speed vs Accuracy:
• int8: Fastest ⚡, least accurate
• float16: Fast 🚀, good accuracy
• float32: Slower 🐢, most accurate ⭐
• auto: Balanced (recommended)

When to use each:
• auto: Use for most cases - let the system choose
• int8: When speed is critical and slight accuracy loss is acceptable
• float16: Good for GPU processing, fast with good accuracy
• float32: When maximum accuracy is required and you have sufficient resources

Memory usage:
• int8: Uses least memory (good for limited VRAM)
• float16: Moderate memory usage
• float32: Uses most memory (requires more VRAM/RAM)

Recommendation: Use 'auto' for best results. The system will choose the optimal type based on your hardware and model."""
    },
    
    "standard_preset": {
        "title": "Standard Preset",
        "content": """Apply optimized subtitle formatting settings for standard use cases.

What it does:
Automatically configures multiple subtitle formatting options:
• Max line width: 42 characters per line
• Max line count: 2 lines per subtitle segment
• Max comma percentage: 70% (breaks lines at commas when line is 70% full)
• Sentence mode: Enabled (splits subtitles at sentence boundaries)

Result:
• Subtitles formatted for easy reading
• Two-line maximum per subtitle
• Appropriate line breaks
• Sentence-based segmentation
• Professional subtitle appearance

When to use:
• Creating subtitles for videos
• Standard subtitle formatting needs
• When you want professional-looking subtitles
• General-purpose transcription projects
• Most common use cases

Benefits:
• Consistent subtitle formatting
• Easy to read on screen
• Professional appearance
• Optimized line breaks

Important Notes:
• Word Timestamps Requirement: The faster-whisper-xxl.exe program REQUIRES --word_timestamps=True when using --standard. If you enable Standard Preset, Word Timestamps will be automatically enabled. You cannot use Standard Preset without Word Timestamps due to this program requirement.
• Sentence-based segmentation
• If you want to remove timestamps from the output after processing, use the "Remove Timestamps" feature that appears after transcription completes.
• Incompatible with Custom Subtitle Formatting: If you customize any subtitle formatting options (Max Line Width, Max Line Count, Max Comma Percentage, or Sentence Mode), Standard Preset will be automatically disabled. Standard Preset uses fixed values and cannot be combined with custom formatting.

Recommendation: Enable for most subtitle creation projects. Provides good default formatting."""
    },
    
    "max_line_width": {
        "title": "Max Line Width",
        "content": """Set the maximum number of characters per line in subtitle output.

What it does:
• Controls how many characters appear on each line of a subtitle
• Prevents subtitles from being too long and hard to read
• Automatically breaks lines when the limit is reached

Default values:
• Standard Preset: 42 characters
• Custom: You can set any value from 1 to 200

When to use:
• Creating subtitles for videos
• When you want to control subtitle line length
• For different screen sizes or readability preferences
• When Standard Preset doesn't meet your needs

Examples:
• 42 characters: Standard for most video players (Standard Preset default)
• 30-35 characters: Shorter lines, good for smaller screens
• 50-60 characters: Longer lines, good for larger displays
• 0 or Auto: Let the program decide automatically

Important Notes:
• This option is disabled when Standard Preset is enabled
• If you change this value, Standard Preset will be automatically disabled
• Works with Max Line Count to control subtitle appearance
• Only applies to subtitle formats (SRT, VTT), not plain text

Recommendation: Use 42 characters (Standard Preset default) for most cases, or customize based on your display needs."""
    },
    
    "max_line_count": {
        "title": "Max Line Count",
        "content": """Set the maximum number of lines per subtitle segment.

What it does:
• Controls how many lines each subtitle can have
• Prevents subtitles from taking up too much screen space
• Ensures subtitles are readable and not overwhelming

Default values:
• Standard Preset: 2 lines
• Custom: You can set any value from 1 to 10

When to use:
• Creating subtitles for videos
• When you want to control how many lines appear at once
• For different screen sizes or readability preferences
• When Standard Preset doesn't meet your needs

Examples:
• 2 lines: Standard for most video players (Standard Preset default)
• 1 line: Single-line subtitles, minimal screen space
• 3-4 lines: More text per subtitle, good for slower reading speeds
• Higher values: More text visible, but may cover more of the video

Important Notes:
• This option is disabled when Standard Preset is enabled
• If you change this value, Standard Preset will be automatically disabled
• Works with Max Line Width to control subtitle appearance
• Only applies to subtitle formats (SRT, VTT), not plain text

Recommendation: Use 2 lines (Standard Preset default) for most cases, as it provides a good balance between readability and screen space."""
    },
    
    "max_comma_percentage": {
        "title": "Max Comma Percentage",
        "content": """Set when to break subtitle lines at commas.

What it does:
• Controls line breaking behavior at commas
• When a line reaches this percentage of Max Line Width, the program will prefer to break at commas
• Helps create more natural line breaks in subtitles

Default values:
• Standard Preset: 70%
• Custom: You can choose from 20%, 30%, 40%, 50%, 60%, 70%, 80%, 90%, or 100%

How it works:
• If set to 70%: When a line reaches 70% of Max Line Width, the program will look for commas to break the line
• Lower percentages: Break lines earlier, more aggressive line breaking
• Higher percentages: Break lines later, allow longer lines before breaking
• 100%: Only break at commas when the line is completely full

When to use:
• Creating subtitles for videos
• When you want to control where lines break
• For more natural-looking subtitle formatting
• When Standard Preset doesn't meet your needs

Examples:
• 70%: Standard Preset default - good balance
• 50-60%: More aggressive line breaking, shorter lines
• 80-90%: Less aggressive, longer lines before breaking
• 100%: Only break at commas when absolutely necessary

Important Notes:
• This option is disabled when Standard Preset is enabled
• If you change this value, Standard Preset will be automatically disabled
• Works with Max Line Width and Max Line Count
• Only applies to subtitle formats (SRT, VTT), not plain text

Recommendation: Use 70% (Standard Preset default) for most cases, as it provides natural line breaks."""
    },
    
    "sentence_mode": {
        "title": "Sentence Mode",
        "content": """Enable sentence-based subtitle segmentation.

What it does:
• Splits subtitles at sentence boundaries (periods, exclamation marks, question marks)
• Creates more natural subtitle breaks
• Improves readability by keeping complete sentences together

Default behavior:
• Automatically enabled when Diarization is enabled
• Automatically enabled when Standard Preset is enabled
• Can be manually enabled for custom formatting

When to use:
• Creating subtitles for videos
• When you want sentence-based segmentation
• For more natural subtitle appearance
• When Standard Preset doesn't meet your needs
• When diarization is not enabled but you want sentence breaks

How it works:
• The program identifies sentence boundaries in the transcription
• Subtitles are created to align with these boundaries
• Results in more readable, natural-looking subtitles

Important Notes:
• This option is disabled when Standard Preset is enabled
• This option is automatically enabled (and disabled) when Diarization is enabled
• If you manually enable this when Standard Preset is enabled, Standard Preset will be disabled
• Works with other subtitle formatting options (Max Line Width, Max Line Count, Max Comma Percentage)
• Only applies to subtitle formats (SRT, VTT), not plain text

Recommendation: Enable for most subtitle projects. Provides more natural subtitle breaks and better readability."""
    },
    
    "batch_recursive": {
        "title": "Batch Recursive",
        "content": """Process multiple files and folders recursively (including subdirectories).

What it does:
• Processes all files in the selected folder
• Recursively processes files in all subdirectories
• Handles multiple files in one operation
• Automatically finds all audio/video files in folder structure

How it works:
• You select a folder (or multiple files/folders)
• Program scans the folder and all subfolders
• Finds all supported audio/video files
• Processes each file with the same settings
• Saves outputs in appropriate locations

When to use:
• Processing multiple files at once
• Organizing files in folders and subfolders
• Batch transcription projects
• Processing entire directory structures
• When you have many files to transcribe

Output behavior:
• Output files are saved in the same location as input files (by default)
• Or in the specified output directory
• Maintains folder structure
• Each file gets its own transcription output

Benefits:
• Process many files without manual selection
• Maintains folder organization
• Efficient for large projects
• Consistent settings across all files
• Saves time on multiple files

Example:
If you select a folder with this structure:
  /Recordings/
    /Meeting1/
      audio1.mp3
      audio2.mp3
    /Meeting2/
      audio3.mp3

All three audio files will be processed automatically.

Note: Make sure you have enough disk space and processing time for all files. Large batches can take significant time.

Recommendation: Enable when processing multiple files or entire folder structures."""
    },
    
    "check_files": {
        "title": "Check Files",
        "content": """Verify input files for errors before processing begins.

What it does:
• Checks each input file before processing
• Verifies files are valid and readable
• Detects corrupted or invalid files
• Identifies files that can't be processed
• Prevents processing errors by catching problems early

Checks performed:
• File exists and is accessible
• File format is valid
• File is not corrupted
• File can be opened and read
• File is a supported audio/video format

When to use:
• Processing multiple files (batch processing)
• When you're unsure about file quality
• Processing files from unknown sources
• Large batch operations
• When you want to avoid processing errors

Benefits:
• Catches problems before processing starts
• Saves time by identifying bad files early
• Prevents wasted processing on corrupted files
• Better error reporting
• More reliable batch processing

What happens:
• If a file is valid: Processing continues normally
• If a file has errors: Error is reported, file is skipped, processing continues with other files
• You get a report of which files were checked and any issues found

Error detection:
• Corrupted files
• Unsupported formats
• Files that can't be read
• Invalid file structures
• Permission issues

Note: This adds a small amount of time before processing starts, but can save significant time by catching problems early.

Recommendation: Enable when processing multiple files or when file quality is uncertain. Especially useful with Batch Recursive."""
    },
    
    "vad_enable": {
        "title": "Voice Activity Detection (VAD)",
        "content": """Voice Activity Detection identifies parts of audio that contain speech and filters out silence and background noise.

Benefits:
• Improves transcription accuracy by focusing on speech segments
• Reduces processing time by skipping silent parts
• Better handling of audio with long pauses or background noise

When to disable:
• Very short audio clips (< 30 seconds)
• Audio that is already pre-processed
• When you need to preserve all audio segments (even silence)

Recommendation: Keep enabled for most use cases. It significantly improves accuracy and speed."""
    },
    
    "word_timestamps": {
        "title": "Word Timestamps",
        "content": """Include precise timestamps for each individual word in the transcription.

Benefits:
• Enables word-level timing in subtitle files
• Required for "Highlight Words" (karaoke) feature
• More precise subtitle synchronization
• Better for video editing and synchronization

When to disable:
• You only need sentence-level timestamps
• Processing very long files where word timestamps add significant time
• Plain text output where timestamps aren't needed

Note: Word timestamps are required for the karaoke/highlight words feature. Disabling this will also disable highlight words.

Recommendation: Keep enabled for subtitle formats (SRT, VTT). You can disable for plain text output."""
    },
    
    "highlight_words": {
        "title": "Highlight Words (Karaoke Effect)",
        "content": """Underline each word as it's spoken in subtitle files, creating a karaoke-style effect.

How it works:
• Each word is highlighted/underlined at the exact moment it's spoken
• Creates a visual karaoke effect in video players
• Works with SRT and VTT subtitle formats

Requirements:
• Word Timestamps must be enabled
• Sentence mode cannot be active (but note: diarization automatically enables sentence mode)

Use cases:
• Music videos with lyrics
• Educational videos
• Language learning content
• Any video where you want words highlighted as they're spoken

Note: This feature increases processing time slightly. Disable if you don't need the karaoke effect."""
    },
    
    "ff_tempo": {
        "title": "Tempo Adjustment",
        "content": """Adjust the playback speed of your audio before transcription.

Range: 0.5 to 2.0
• 1.0 = Normal speed (default, disabled)
• Below 1.0 = Slows down audio (e.g., 0.8 = 80% speed)
• Above 1.0 = Speeds up audio (e.g., 1.2 = 120% speed)

When to use:
• Slow down (0.5-0.9): Very fast speech that's hard to transcribe accurately
• Speed up (1.1-2.0): Very slow speech to reduce processing time (not recommended for accuracy)

Important notes:
• Slowing down can improve accuracy for fast speakers
• Speeding up reduces accuracy and is not recommended
• This affects the entire audio file
• Processing time is affected by tempo changes

Recommendation: Use 1.0 (normal) for best results. Only adjust if you have specific issues with speech speed."""
    },
    
    "ff_fftdn": {
        "title": "Denoise Filter",
        "content": """Reduce background noise in your audio using Fast Fourier Transform.

Range: 0 to 97
• 0 = Disabled (default)
• 12 = Normal strength (good starting point)
• 30-50 = Moderate noise reduction
• 70-97 = Aggressive noise reduction

When to use:
• Audio with constant background noise (fans, air conditioning, etc.)
• Recordings with hiss or static
• Audio with low-level background chatter
• Poor quality recordings

How it works:
• Analyzes audio frequencies
• Identifies and reduces noise patterns
• Preserves speech frequencies

Tips:
• Start with 12-20 for mild noise
• Increase gradually if needed
• Too high values (80+) may affect speech quality
• Test on a short clip first

Warning: Very high values may introduce artifacts or affect speech clarity. Use conservatively."""
    },
    
    "temperature": {
        "title": "Temperature",
        "content": """Controls the randomness and creativity of the transcription.

Range: 0.0 to 1.0
• 0.0 = Deterministic, most consistent (recommended)
• 0.2-0.4 = Slight variation
• 0.5-1.0 = More variation, less consistent

How it works:
• Lower values = More predictable, consistent transcriptions
• Higher values = More variation, may handle unusual words better but less consistent

When to adjust:
• Keep at 0.0 for most cases (best consistency)
• Increase slightly (0.2-0.3) if transcription is too conservative
• Higher values may help with unusual accents or words, but reduce consistency

Recommendation: Keep at 0.0 (default) for best accuracy and consistency. Only adjust if you're experiencing specific issues."""
    },
    
    "beam_size": {
        "title": "Beam Size",
        "content": """Number of transcription candidates the model considers before choosing the best one.

Range: 1 to 10
• Default: 5
• Lower (1-3) = Faster, less accurate
• Higher (6-10) = Slower, more accurate

How it works:
• The model generates multiple possible transcriptions
• Beam size determines how many candidates to evaluate
• Higher beam size = more thorough search = better accuracy

When to adjust:
• Increase (6-10) for maximum accuracy (slower processing)
• Decrease (3-4) for faster processing (slight accuracy trade-off)
• Keep at 5 for balanced speed and accuracy

For best accuracy: Use 7-10, especially for:
• Important transcriptions
• Audio with accents or unclear speech
• When accuracy is more important than speed

Recommendation: Keep at 5 for most cases. Increase to 7-10 for maximum accuracy."""
    },
    
    "patience": {
        "title": "Patience",
        "content": """How long the model waits before finalizing a transcription segment.

Range: 0.0 to 10.0
• Default: 2.0
• Lower = Faster decisions, may cut off sentences
• Higher = More patient, waits longer for complete sentences

How it works:
• Controls when the model decides a segment is complete
• Higher patience = model waits longer for sentence endings
• Helps prevent cutting off sentences mid-thought

When to adjust:
• Increase (3.0-5.0) for:
  - Long, complex sentences
  - Speakers who pause frequently
  - Better sentence completeness
• Decrease (1.0-1.5) for:
  - Faster processing
  - Short, simple sentences
  - When speed is priority

For best accuracy: Use 3.0-4.0 for:
• Complex content
• Multiple speakers
• Important transcriptions

Recommendation: Keep at 2.0 for most cases. Increase to 3.0-4.0 for better sentence completeness."""
    },
    
    "diarize_enable": {
        "title": "Speaker Diarization",
        "content": """Identify and label different speakers in your audio.

What it does:
• Automatically detects when different people are speaking
• Labels each speaker (SPEAKER_00, SPEAKER_01, etc.)
• Creates separate transcription lines for each speaker

Perfect for:
• Interviews (interviewer and interviewee)
• Meetings with multiple participants
• Podcasts with multiple hosts
• Conversations and discussions
• Any audio with 2+ speakers

How it works:
• Uses advanced AI models to analyze voice characteristics
• Identifies unique speakers based on voice patterns
• Separates speech segments by speaker

Accuracy tips:
• Use larger models (large-v2, large-v3-turbo) for better results
• Set exact speaker count if known (significantly improves accuracy)
• Use GPU/CUDA for faster processing
• Enable audio filters to clean audio first (improves diarization accuracy)

Note: Diarization automatically enables sentence mode for better speaker separation."""
    }
}

def get_tooltip(key):
    """Get tooltip text for a given option key."""
    return TOOLTIPS.get(key, "")

def get_detailed_help(key):
    """Get detailed help content for a given option key."""
    return DETAILED_HELP.get(key, {"title": "Help", "content": "No help available for this option."})

