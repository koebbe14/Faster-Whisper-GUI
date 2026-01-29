# Faster Whisper GUI

A comprehensive, user-friendly graphical interface for audio and video transcription with advanced speaker diarization capabilities. Built on top of `faster-whisper-xxl.exe`, this application makes high-quality transcription, translation, and diarization easy and accessable.  Faster-whisper-xxl is a modified version of OpenAi Whisper (see Credits and Acknowledgments below)

## 🎯 Overview

Faster Whisper GUI provides an intuitive interface for transcribing audio and video files with state-of-the-art accuracy. Whether you need to transcribe a single interview or process hundreds of files in batch, this application offers the tools and flexibility to get the job done efficiently.

## Initial Use and Model Downloads

Upon inital launch of the .exe file, a zip file will be automatically extracted to the necessary location.  The .exe does NOT include any predownloaded Models.  Therefore, an internet connection is required the first time a model is used so it can be automatically downloaded.  Once a model is downloaded, no network connection is needed and the program is Standalone.

# A link to download the .exe can be found on the "Releases" page

### Key Highlights

- **Zero Configuration Required**: Download and run - all dependencies included
- **Maximum Accuracy**: Optimized presets for interview-quality transcriptions
- **Speaker Identification**: Advanced diarization to identify who said what
- **Batch Processing**: Handle multiple files with individual settings
- **Audio Quality Analysis**: Get intelligent suggestions for optimal settings
- **Multiple Output Formats**: SRT, VTT, TXT, and JSON formats
- **Post-Processing Tools**: Speaker replacement and timestamp removal utilities

## ✨ Features

### Core Transcription Features

- **Multi-Format Support**: Process audio and video files in virtually any format (MP3, MP4, WAV, M4A, FLAC, etc.)
- **Language Support**: Transcribe in 99+ languages or translate to English
- **Multiple Models**: Choose from tiny to large-v3-turbo models based on your accuracy/speed needs
- **Real-Time Progress**: Watch transcription progress with live output and status updates
- **Drag & Drop**: Simply drag files or folders into the application
- **Batch Processing**: Process multiple files with a queue system and per-file settings

### Speaker Diarization (Speaker Identification)

Identify different speakers in your audio - perfect for interviews, meetings, podcasts, and multi-speaker content.

- **Multiple Diarization Methods**:
  - `pyannote_v3.1` (Recommended) - Latest and most accurate
  - `pyannote_v3.0` - Stable fallback option
  - `reverb_v2` - Best for audio with echo/reverb
  - `reverb_v1` - Legacy method for compatibility

- **Speaker Count Optimization**: Set exact speaker count for dramatically improved accuracy
- **Speaker Replacement Tool**: After transcription, replace generic labels (SPEAKER_00, SPEAKER_01) with actual names
- **GPU Acceleration**: Optional GPU support for 5-10x faster processing
- **Min/Max Speaker Range**: Set speaker count ranges when exact count is unknown

### Audio Processing & Quality

- **Audio Quality Analysis**: Analyze your audio files and receive intelligent suggestions for optimal filter settings
  - Noise level detection (low/medium/high)
  - Volume level assessment
  - Quality score (0-100)
  - Personalized filter recommendations

- **Audio Filters**:
  - **Speech Normalization**: Amplify quiet speech to make it more audible
  - **Loudness Normalization**: Normalize to EBU R128 broadcast standard
  - **Low/High Pass Filter**: Remove frequencies outside speech range (50Hz-7800Hz)
  - **Denoise**: Reduce background noise (adjustable intensity 0-97)
  - **Tempo Adjustment**: Adjust playback speed for fast or slow speech

- **Voice Activity Detection (VAD)**: Automatically filter out non-speech segments

### User Experience Features

- **Preset Configurations**: Five optimized presets for different use cases
  - **Standard**: Maximum accuracy for clean interview recordings
  - **Turbo**: Speed-optimized for quick transcriptions
  - **Diarize**: Optimized for speaker identification with maximum accuracy
  - **Phone Conversation Audio**: Optimized for low-quality/noisy phone recordings
  - **Custom**: Full manual control

- **Comprehensive Help System**:
  - Tooltips on hover for quick explanations
  - Detailed help dialogs (click "?" buttons)
  - Context-sensitive help that adapts to your selections
  - Best Practices guide shown on first run

- **Settings Validation**: Pre-processing warnings for suboptimal configurations
- **GPU Detection**: Automatic detection and notification when GPU is available
- **Model Management**: Check which models are downloaded and get download information
- **Command Preview**: See the exact command that will be executed before processing

### Post-Processing Tools

- **Speaker Replacement Dialog**: 
  - Review full diarized transcript
  - See all identified speakers in a table
  - Replace generic labels with actual names
  - Preview changes before saving
  - Save updated transcript with custom speaker names

- **Timestamp Removal Tool**: 
  - Remove timestamps from transcriptions
  - Clean up text for easier reading
  - Preserve speaker labels if diarization was used

### Advanced Features

- **Custom Subtitle Formatting**: 
  - Control maximum line width
  - Set maximum lines per segment
  - Configure comma break percentage
  - Enable sentence mode for better segmentation

- **Word-Level Timestamps**: Precise timing for each word
- **Karaoke-Style Subtitles**: Highlight words as they're spoken (VTT format)
- **Processing Queue**: Manage multiple files with individual settings
- **Recursive Folder Processing**: Process entire folder structures
- **File Validation**: Automatic verification of input files before processing

## 📥 Installation

### System Requirements

- **Operating System**: Windows 10 or later
- **Disk Space**: At least 2GB free space (for runtime files and models)
- **RAM**: 4GB minimum, 8GB+ recommended
- **GPU**: Optional but recommended - NVIDIA GPU with CUDA support for 5-10x faster processing

### Installation Steps

1. **Download**: Download `FasterWhisperGUI.exe` from the [Releases](https://github.com/yourusername/faster-whisper-gui/releases) page

2. **Extract** (if downloaded as ZIP): Extract to your desired location

3. **Run**: Double-click `FasterWhisperGUI.exe` to launch the application

4. **First Run Setup**: 
   - On first launch, the application will automatically extract necessary runtime files to `%LOCALAPPDATA%\FasterWhisperGUI\`
   - A progress dialog will show the extraction status (this may take a few moments)
   - Models will be automatically downloaded when needed to `%LOCALAPPDATA%\FasterWhisperGUI\_models\`
   - No user intervention required - everything happens automatically

**That's it!** The executable is completely self-contained. No Python installation, no dependencies to install, no configuration needed.

## 📖 Usage Guide

### Quick Start

1. **Launch**: Double-click `FasterWhisperGUI.exe`

2. **Select Files**: 
   - Click "Select Files/Folder..." button, or
   - Drag and drop files/folders into the application

3. **Choose a Preset** (optional but recommended):
   - Select from the dropdown: Standard, Turbo, Diarize, Phone Conversation Audio, or Custom
   - Presets configure optimal settings for different use cases

4. **Configure Settings** (if needed):
   - Modify any settings after selecting a preset
   - Use "?" buttons for detailed help on any option

5. **Start Processing**: Click "Start Processing" button

6. **Post-Processing** (if diarization enabled):
   - Speaker Replacement dialog opens automatically
   - Replace speaker labels with actual names
   - Save the updated transcript

### Detailed Workflow

#### For Single File Transcription

1. **Select File**: Click "Select Files/Folder..." and choose your audio/video file
2. **Choose Preset**: Select appropriate preset (Standard for most cases)
3. **Optional - Analyze Audio**: Click "Analyze Audio Quality" for filter suggestions
4. **Configure Language**: Select the language (don't use Auto-detect for best accuracy)
5. **Choose Output Format**: Select SRT, VTT, TXT, and/or JSON
6. **Start Processing**: Click "Start Processing"
7. **Review Output**: Check the output area for progress and results
8. **Open Output**: Click "Open Output Folder" when complete

#### For Speaker Diarization (Interviews, Meetings)

1. **Select File(s)**: Choose your audio/video file(s)
2. **Choose Preset**: Select "Diarize" preset
3. **Set Speaker Count**: ⭐ **CRITICAL** - Set the exact number of speakers if known (dramatically improves accuracy)
4. **Configure Language**: Specify the language explicitly
5. **Choose Output Formats**: Select TXT, SRT, and/or VTT (speaker labels included)
6. **Start Processing**: Click "Start Processing"
7. **Speaker Replacement**: 
   - Dialog opens automatically after processing
   - Review all identified speakers in the table
   - Replace generic labels (SPEAKER_00, SPEAKER_01) with actual names
   - Preview changes
   - Save updated transcript

#### For Batch Processing (Multiple Files)

1. **Select Multiple Files or Folder**: Choose multiple files or a folder containing files
2. **Configure Settings**: Set your preferred settings
3. **Start Processing**: Click "Start Processing"
4. **Queue Settings Dialog**:
   - Choose "Apply same settings to all files" or
   - Choose "Configure different settings for each file"
5. **Edit Individual Settings** (if needed): Click "Edit Settings" for any file
6. **Monitor Progress**: Processing Queue window shows progress for all files
7. **Review Results**: Each file gets its own output files

### Presets Explained

#### ⭐ Standard Preset (Recommended for Most Users)

- **Best For**: General transcription, clean interview recordings, podcasts, meetings
- **Model**: `large-v2` (excellent accuracy, reliable, fewer hallucinations than v3)
- **Optimization**: Maximum accuracy settings for controlled interview environments
- **Settings**:
  - Beam Size: 10 (maximum accuracy)
  - Patience: 5.0 (maximum completeness)
  - Temperature: 0.0 (deterministic, consistent results)
  - VAD: Enabled with `pyannote_v3` (most accurate method)
  - Audio Filters: Loudness normalization only (minimal processing for clean audio)
- **When to Use**: Most common use case - clean audio, interviews, general transcription needs

#### ⚡ Turbo Preset

- **Best For**: Quick transcriptions when speed is priority
- **Model**: `turbo` (fast while maintaining good accuracy)
- **Settings**: Balanced for speed and accuracy
  - Beam Size: 5 (default, balanced)
  - Patience: 2.0 (default, faster)
  - VAD: Enabled with `silero_v4_fw` (faster method)
- **When to Use**: When you need fast results and can accept slightly lower accuracy

#### 🎤 Diarize Preset

- **Best For**: Interviews, meetings, podcasts with multiple speakers
- **Model**: `large-v2` (best for speaker identification accuracy)
- **Optimization**: Maximum accuracy for speaker identification
- **Settings**:
  - Diarization: Enabled with `pyannote_v3.1` (latest, most accurate method)
  - Beam Size: 10 (maximum accuracy)
  - Patience: 5.0 (maximum completeness)
  - Audio Filters: Loudness normalization only
- **Output**: TXT, SRT, VTT formats (multiple formats for speaker labeling)
- **⚠️ IMPORTANT**: Set the exact number of speakers if known (dramatically improves accuracy)
- **When to Use**: When you need to identify who is speaking

#### 📞 Phone Conversation Audio Preset

- **Best For**: Phone calls, low-quality recordings, noisy audio
- **Model**: `large-v2` (robust for degraded audio)
- **Settings**: Optimized for challenging audio conditions
  - Beam Size: 8 (higher for noisy conditions)
  - Patience: 4.0 (better for degraded audio)
  - Audio Filters: Aggressive preprocessing
    - Speech normalization (amplifies quiet speech)
    - Loudness normalization
    - Low/high pass filter (removes non-speech frequencies)
    - Denoise: 15 (moderate noise reduction)
- **⚠️ IMPORTANT**: For phone calls, set speaker count to 2 if known
- **When to Use**: Phone calls, recordings with background noise, low-quality audio

#### 🔧 Custom Preset

- **Best For**: Advanced users who want full control
- **Settings**: No pre-configured settings - configure everything manually
- **When to Use**: When you want to set all options yourself from scratch

### Audio Quality Analysis

The Audio Quality Analysis feature helps you determine the best settings for your specific audio file.

1. **Select File**: Choose your audio file
2. **Click "Analyze Audio Quality"**: Button in the File Selection section
3. **Review Results**:
   - Quality Score (0-100)
   - Noise Level (Low/Medium/High)
   - Volume Level (Low/Normal/High)
   - Suggested filter settings
4. **Apply Suggestions**: Manually enable suggested filters or use a preset

**Example Suggestions**:
- "Clean audio detected - using minimal filters for best accuracy"
- "Low volume detected - consider enabling Speech Normalization"
- "Some noise detected - consider enabling Denoise filter if quality is poor"

### Output Formats

#### SRT (SubRip Subtitle)
- Standard subtitle format, widely compatible with video players
- Format: Sequential subtitle blocks with timestamps
- Includes speaker labels when diarization is enabled
- Best for: Video editing software, YouTube, general video players

#### VTT (WebVTT)
- Web Video Text Tracks format
- Similar to SRT but web-optimized
- Supports word-level highlighting (karaoke effect)
- Includes speaker labels when diarization is enabled
- Best for: Web videos, HTML5 video players

#### TXT (Plain Text with Timestamps)
- Plain text format with timestamps
- Format: `[HH:MM:SS.mmm --> HH:MM:SS.mmm] Text`
- Includes speaker labels when diarization is enabled
- Example: `[00:38.120 --> 00:41.240] [SPEAKER_01]: We came over to your house earlier this`
- Best for: Reading, editing, general text processing

#### JSON (Detailed Metadata)
- Comprehensive data format with all information
- Includes: timestamps, word-level data, speaker information (separate from text)
- Best for: Programmatic processing, detailed analysis
- Note: Speaker labels are in metadata, not inline with text

## 🎯 Tips for Maximum Accuracy

### General Transcription Accuracy

1. **Specify Language**: Don't use "Auto-detect" - specify the language explicitly for best results
2. **Use Larger Models**: `large-v2` or `large-v3-turbo` provide better accuracy than smaller models
3. **Enable GPU**: If you have an NVIDIA GPU, enable CUDA for faster processing (allows using larger models)
4. **Use Appropriate Preset**: Choose the preset that matches your use case
5. **Audio Quality**: Use "Analyze Audio Quality" to get suggestions for your specific audio

### Speaker Diarization Accuracy

1. **⭐ Set Exact Speaker Count**: The SINGLE MOST IMPORTANT setting - if you know there are exactly 2, 3, 4, etc. speakers, set "Number of Speakers" to that exact number. This dramatically improves accuracy.

2. **Specify Language**: Don't use "Auto-detect" - specify the language explicitly

3. **Use Large Model**: `large-v2` model provides best accuracy for diarization

4. **Use Latest Method**: `pyannote_v3.1` is the most accurate diarization method

5. **Enable GPU**: Diarization is computationally intensive - GPU provides 5-10x speedup

6. **Clean Audio**: For clean recordings (iPhone, quiet rooms), use minimal audio filters

### Audio Filter Strategy

- **Clean Audio** (iPhone recordings, quiet rooms): Use minimal filters (loudness normalization only)
- **Noisy Audio** (phone calls, background noise): Use aggressive filters (denoise, frequency filtering)
- **Low Volume**: Enable speech normalization
- **Inconsistent Volume**: Enable loudness normalization

### Model Selection Guide

- **Maximum Accuracy**: `large-v2` or `large-v3-turbo`
- **Balanced**: `large-v2` (recommended for most users)
- **Speed Priority**: `turbo`
- **Resource Constrained**: `small` or `tiny` (lower accuracy)

## ⌨️ Keyboard Shortcuts

- `Ctrl+O`: Open files
- `Ctrl+S`: Start processing
- `Ctrl+C`: Cancel processing
- `F1`: Show help menu
- `Esc`: Close dialogs

## 🐛 Troubleshooting

### Application Won't Start

- **Insufficient Disk Space**: Ensure at least 2GB free space
- **Antivirus Blocking**: Check if Windows Defender or antivirus is blocking the executable
- **Permission Errors**: Try running as Administrator
- **First Run Delay**: First launch takes longer as files are extracted - wait for extraction dialog to complete

### No Output Generated

- **Check Output Area**: Look for error messages in the output text area
- **Invalid Files**: Verify your input files are valid audio/video formats
- **Disk Space**: Ensure sufficient disk space for output files
- **File Permissions**: Check that you have write permissions to the output folder

### Slow Processing

- **Enable GPU**: If you have NVIDIA GPU, enable CUDA in device settings
- **Use Smaller Model**: Try `turbo` instead of `large-v2` for faster processing
- **Reduce Beam Size**: Lower beam size in Advanced Options (trades accuracy for speed)
- **Disable Audio Filters**: If not needed, disable filters to speed up preprocessing

### Poor Transcription Quality

- **Use Larger Model**: Try `large-v2` or `large-v3-turbo` for better accuracy
- **Specify Language**: Don't use "Auto-detect" - specify language explicitly
- **Enable Audio Filters**: Use Audio Quality Analysis for suggestions
- **Check Audio Quality**: Poor source audio will result in poor transcriptions
- **For Diarization**: Set exact speaker count - this is critical for accuracy

### GPU Not Detected

- **Check Drivers**: Ensure NVIDIA drivers are installed and up to date
- **Verify CUDA**: Run `nvidia-smi` in command prompt to verify CUDA is available
- **Auto Mode**: Application will automatically use CPU if GPU is not available
- **Device Selection**: Ensure "Device" is set to "Auto" or "CUDA" in Advanced Options

### Models Not Downloading

- **Internet Connection**: Check your internet connection
- **Disk Space**: Ensure sufficient space in `%LOCALAPPDATA%\FasterWhisperGUI\_models\`
- **Firewall**: Check if firewall is blocking the download
- **Automatic Download**: Models download automatically when first used - be patient

### "faster-whisper-xxl.exe not found" Error

- **First Run**: Wait for first-run extraction to complete
- **Corrupted Files**: Delete `%LOCALAPPDATA%\FasterWhisperGUI\` and restart (files will re-extract)
- **Permissions**: Ensure you have read/write permissions to AppData folder

### Post-Processing Dialogs Not Appearing

- **Check Output Files**: If output files were generated, dialogs should appear
- **Non-Zero Exit Code**: Dialogs appear even if process returns warnings (as long as outputs are generated)
- **Manual Access**: Use "Identify & Replace Speakers" or "Remove Timestamps" buttons if dialogs don't auto-open

## 📁 File Locations

### Runtime Files (Extracted on First Run)
- **Location**: `C:\Users\[YourUsername]\AppData\Local\FasterWhisperGUI\`
- **Contents**: 
  - `faster-whisper-xxl.exe` - Core transcription engine
  - `ffmpeg.exe` - Audio/video processing
  - `ffprobe.exe` - Media file analysis
  - `_xxl_data\` - Runtime dependencies

### Downloaded Models
- **Location**: `C:\Users\[YourUsername]\AppData\Local\FasterWhisperGUI\_models\`
- **Contents**: Whisper models (downloaded automatically when needed)
- **Size**: Models can be several GB each
- **Models Available**:
  - `tiny`, `small`, `medium`, `large-v1`, `large-v2`, `large-v3`, `large-v3-turbo`

### Configuration
- **Location**: `C:\Users\[YourUsername]\.faster_whisper_gui_config.json`
- **Contents**: User preferences (show best practices dialog, etc.)

## 🔧 Advanced Configuration

### Custom Subtitle Formatting

When "Standard Preset" is disabled, you can customize subtitle formatting:

- **Max Line Width**: Maximum characters per subtitle line (default: 70)
- **Max Line Count**: Maximum lines per subtitle segment (default: 3)
- **Max Comma Percentage**: Percentage of line width before breaking at commas (default: 90%)
- **Sentence Mode**: Split subtitles at sentence boundaries (auto-enabled with diarization)

### Advanced Transcription Options

- **Temperature**: Controls randomness (0.0 = deterministic, recommended)
- **Beam Size**: Number of candidates to consider (1-10, higher = more accurate but slower)
- **Patience**: How long to wait before finalizing segments (higher = more patient)
- **Best Of**: Number of candidates when sampling (default: 5)
- **Length Penalty**: Token length penalty coefficient (default: 1.0)
- **Repetition Penalty**: Penalty for repeating tokens (default: 1.0)

Most users should leave these at default values unless experiencing specific issues.

## 🙏 Credits & Acknowledgments

This application is built on top of excellent open-source projects:

- **faster-whisper-xxl.exe** by [Purfview](https://github.com/Purfview/whisper-standalone-win) - The core transcription engine that powers this application. Special thanks to Purfview for creating and maintaining the standalone Windows executable.

- **Faster Whisper** by [Guillaume Klein](https://github.com/guillaumekln/faster-whisper) - The optimized Whisper implementation that provides fast and accurate transcription.

- **OpenAI Whisper** by [OpenAI](https://github.com/openai/whisper) - The state-of-the-art speech recognition model that makes accurate transcription possible.

- **PyQt6** - The GUI framework that provides the user interface.

- **FFmpeg** - Audio and video processing capabilities.

## 📝 License

This GUI application is provided as-is for use with `faster-whisper-xxl.exe`.

**Note**: This project uses `faster-whisper-xxl.exe` by [Purfview](https://github.com/Purfview/whisper-standalone-win). Please refer to their repository for licensing information regarding the Faster Whisper engine.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## 📧 Support

For issues, questions, or feature requests, please open an issue on GitHub.

