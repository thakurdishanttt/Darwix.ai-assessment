# Darwix.ai API - Postman Guide

This guide provides instructions for using the Darwix.ai API with Postman, including request examples and parameter descriptions.

## Setting Up Postman

1. Download and install [Postman](https://www.postman.com/downloads/)
2. Create a new Workspace or use an existing one
3. Create a new Collection named "Darwix.ai API"

## Environment Setup

Create a new Environment in Postman with the following variables:

- `base_url`: The base URL of your API (e.g., `http://localhost:8000` for local development)

### API Environment Variables

Before using the API, ensure you have set up your environment variables:

1. Copy the `.env.sample` file to create your `.env` file:
   ```bash
   cp .env.sample .env
   ```

2. Update the following variables in your `.env` file:
   - `SECRET_KEY`: Your Django secret key
   - `HF_TOKEN`: Your Hugging Face API token (get from https://huggingface.co/settings/tokens)
   - `GEMINI_API_KEY`: Your Google Gemini API key (get from https://makersuite.google.com/app/apikey)
   - `DEBUG`: Set to True for development, False for production
   - `ALLOWED_HOSTS`: Comma-separated list of allowed hosts

## API Endpoints

### 1. Audio Transcription API

#### Request Details

- **Method**: POST
- **URL**: `{{base_url}}/api/audio/transcribe/`
- **Headers**: None required (multipart form data will be set automatically)

#### Request Body

- Select the **form-data** option
- Add a key named `audio_file` and set its type to **File**
- Select an audio file from your computer (.mp3, .wav, .flac, etc.)

#### Example Request

```
POST {{base_url}}/api/audio/transcribe/
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="audio_file"; filename="example.mp3"
Content-Type: audio/mpeg

(file binary data)
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

#### Example Response

```json
{
  "status": "success",
  "transcription": "This is the full transcription of the audio file.",
  "diarized_transcript": [
    "Speaker 1: Hello, how are you doing today?",
    "Speaker 2: I'm doing well, thank you for asking.",
    "Speaker 1: That's great to hear!"
  ],
  "segments": [
    {
      "text": "Hello, how are you doing today?",
      "timestamp": [0.0, 2.5]
    },
    {
      "text": "I'm doing well, thank you for asking.",
      "timestamp": [2.7, 5.1]
    },
    {
      "text": "That's great to hear!",
      "timestamp": [5.3, 6.8]
    }
  ]
}
```

#### Notes

- Maximum file size: Dependent on your Django settings
- Supported file formats: .mp3, .wav, .flac, .ogg, .aac
- Processing time varies based on audio length

### 2. Blog Title Generation API

#### Request Details

- **Method**: GET
- **URL**: `{{base_url}}/api/blog/bloges/:title/`
- **Path Variable**:
  - `title`: The blog content for which to generate titles (URL-encoded)

#### Example Request

```
GET {{base_url}}/api/blog/bloges/Artificial%20intelligence%20is%20transforming%20the%20way%20businesses%20operate%20today.%20From%20customer%20service%20to%20data%20analysis%2C%20AI%20tools%20are%20making%20processes%20more%20efficient./
```

#### Example Response

```json
{
  "success": true,
  "result": [
    "How AI is Revolutionizing Business Operations in 2023",
    "The AI Transformation: Boosting Efficiency in Modern Business",
    "From Customer Service to Data Analysis: AI's Business Impact"
  ]
}
```

#### Notes

- URL encoding is required for the content parameter
- For longer content, consider breaking it into multiple requests
- The API typically returns 3 title suggestions by default

## Troubleshooting

### Common Issues

1. **404 Not Found**: Verify the base URL and endpoint paths
2. **413 Request Entity Too Large**: Audio file may exceed size limits, try a smaller file
3. **500 Internal Server Error**: Check server logs for details

### Authentication Errors

This API currently doesn't require authentication. If you're getting permission errors, check your server configuration.

## Importing the Collection

You can also import this entire collection by downloading the Postman Collection JSON file from our repository and importing it into Postman:

1. In Postman, click "Import" in the top left
2. Select the downloaded JSON file
3. All requests will be imported with the correct settings

---

For additional help, please refer to the [README.md](README.md) file or open an issue in our GitHub repository.
