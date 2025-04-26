from django.urls import path
from .views import upload_audio

urlpatterns = [
    path('transcribe/', upload_audio, name='audio_transcription'),
]