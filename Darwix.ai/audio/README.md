# Audio Transcription and Speaker Diarization

This module provides functionality to transcribe audio files and identify different speakers in the recording.

## Requirements

1. Install the required packages:

   ```
   pip install -r requirements.txt
   ```

2. Get a Hugging Face API token:
   - Go to [Hugging Face](https://huggingface.co/) and create an account
   - Go to your profile → Settings → Access Tokens
   - Create a new token with read permissions
   - Create a `.env` file in your project root and add: `HF_TOKEN=your_token_here`

## Usage

```python
from audio.functions import transcribe_audio_with_diarization

# Process an audio file
result = transcribe_audio_with_diarization("path/to/your/audio_file.mp3")

# Print the diarized transcript
for segment in result['diarized_transcript']:
    print(segment)
```

## Features

- **Automatic Speech Recognition**: Uses OpenAI's Whisper model for accurate transcription
- **Speaker Diarization**: Identifies different speakers in the audio
- **Fallback Mode**: If HF_TOKEN is not available, falls back to a simpler heuristic-based approach

## Testing

Run the test script to verify functionality:

```
python audio/test_diarization.py
```

## Important Notes

1. The pyannote/speaker-diarization model requires authentication with a Hugging Face token
2. For proper diarization, you need to accept the model's license agreement on Hugging Face
3. Audio files should be in a format supported by the libraries (WAV, FLAC, MP3, etc.)
