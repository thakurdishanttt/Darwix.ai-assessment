# Darwix.ai - Audio Transcription & Blog Generation API

A Django-based API that provides two main services:

1. **Audio Transcription with Speaker Diarization**: Upload audio files and get accurate transcripts with speaker identification
2. **AI-Powered Blog Title Generation**: Generate SEO-friendly blog titles based on content

## Features

### Audio Transcription

- Automatic Speech Recognition (ASR) using OpenAI's Whisper model
- Speaker Diarization to identify different speakers in the audio
- Fallback mode for simpler processing when authentication is limited

### Blog Title Generation

- AI-powered title suggestions using Google's Gemini Pro AI model
- SEO-optimized blog title generation from content snippets
- Configurable number of title suggestions

## Requirements

- Python 3.8+
- Django 5.0+
- Hugging Face account and API token
- Google Gemini API key

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/thakurdishanttt/Darwix.ai-assessment.git
   cd Darwix.ai-assessment
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Copy `.env.sample` to create your `.env` file and fill in your credentials:
   ```bash
   cp .env.sample .env
   ```
   Then edit the `.env` file and replace the placeholder values with your actual credentials:
   - `SECRET_KEY`: Your Django secret key
   - `HF_TOKEN`: Your Hugging Face API token from https://huggingface.co/settings/tokens
   - `GEMINI_API_KEY`: Your Google Gemini API key from https://makersuite.google.com/app/apikey

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Start the development server:
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Audio Transcription

- **URL**: `/api/audio/transcribe/`
- **Method**: POST
- **Body**: Form-data with key 'audio_file' and value being the audio file
- **Response**: JSON with transcription and speaker diarization

### Blog Title Generation

- **URL**: `/api/blog/bloges/<title>/`
- **Method**: GET
- **URL Params**: `title` - Content for which to generate blog titles
- **Response**: JSON with suggested blog titles

## License

[MIT License](LICENSE)

## Credits

Built with:

- [Django](https://www.djangoproject.com/)
- [Hugging Face Transformers](https://huggingface.co/transformers/)
- [PyAnnote Audio](https://github.com/pyannote/pyannote-audio)
- [Google Generative AI](https://ai.google.dev/)
