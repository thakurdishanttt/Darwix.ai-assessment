from django.shortcuts import render
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get HF token from environment
hf_token = os.getenv('HF_TOKEN')

# Initialize HuggingFace token for auth
if hf_token:
    from huggingface_hub import login
    login(hf_token)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .functions import transcribe_audio_with_diarization

@csrf_exempt
def upload_audio(request):
    if request.method == 'POST' and request.FILES.get('audio_file'):
        audio_file = request.FILES['audio_file']
        
        # Save the uploaded file temporarily
        temp_path = default_storage.save(f'tmp/{audio_file.name}', ContentFile(audio_file.read()))
        full_path = default_storage.path(temp_path)
        
        try:
            # Process the audio file
            result = transcribe_audio_with_diarization(full_path)
            
            # Clean up the temporary file
            default_storage.delete(temp_path)
            
            return JsonResponse(result)
        
        except Exception as e:
            # Clean up if error occurs
            if default_storage.exists(temp_path):
                default_storage.delete(temp_path)
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method or no audio file provided'
    }, status=400)