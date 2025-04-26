from transformers import pipeline
import os
import torch
from dotenv import load_dotenv
import re
import warnings
from pyannote.audio import Pipeline
import tempfile
import soundfile as sf
from pydub import AudioSegment

# Load environment variables
load_dotenv()

# Get HF token from environment
hf_token = os.getenv('HF_TOKEN')

def transcribe_audio_with_diarization(audio_path):
    """
    Transcribe audio and perform speaker diarization
    
    Args:
        audio_path: Path to the audio file
        
    Returns:
        Dictionary containing transcription and speaker segments
    """
    try:
        # Check if HF_TOKEN is available
        if not hf_token:
            raise ValueError("HF_TOKEN not found in environment. Please set HF_TOKEN in .env file.")
            
        # Initialize the ASR pipeline with a smaller model for faster processing
        transcriber = pipeline("automatic-speech-recognition", 
                             model="openai/whisper-small")
        
        # Perform transcription with timestamps
        print("Performing transcription...")
        result = transcriber(audio_path, return_timestamps=True)
        
        # Extract text and chunks
        text = result['text'] if isinstance(result, dict) and 'text' in result else ""
        chunks = result.get('chunks', [])
        
        # Initialize speaker diarization pipeline
        print("Initializing speaker diarization...")
        diarization_pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization@2.1",
            use_auth_token=hf_token
        )
        
        # Perform diarization
        print("Performing diarization...")
        diarization = diarization_pipeline(audio_path)
        
        # Process and combine transcription with speaker information
        print("Processing diarization results...")
        transcript_with_speakers = process_diarization(diarization, chunks)
        
        return {
            'status': 'success',
            'transcription': text,
            'diarized_transcript': transcript_with_speakers,
            'segments': chunks
        }
        
    except ValueError as ve:
        # Special handling for missing token
        if "HF_TOKEN not found" in str(ve):
            print(f"WARNING: {str(ve)}")
            print("Falling back to simple speaker separation...")
            return fallback_diarization(audio_path)
        else:
            raise ve
    except Exception as e:
        raise Exception(f"Error in transcription and diarization: {str(e)}")

def fallback_diarization(audio_path):
    """
    Fallback method when proper diarization can't be performed
    """
    try:
        # Initialize the ASR pipeline
        transcriber = pipeline("automatic-speech-recognition", 
                             model="openai/whisper-small")
        
        # Perform transcription
        result = transcriber(audio_path, return_timestamps=True)
        
        # Extract text and chunks
        text = result['text'] if isinstance(result, dict) and 'text' in result else ""
        chunks = result.get('chunks', [])
        
        # Use a more sophisticated heuristic for speaker separation
        transcript_with_speakers = enhanced_speaker_separation(chunks, text)
        
        return {
            'status': 'success',
            'transcription': text,
            'diarized_transcript': transcript_with_speakers,
            'segments': chunks
        }
    except Exception as e:
        raise Exception(f"Error in fallback diarization: {str(e)}")

def process_diarization(diarization, transcript_chunks):
    """
    Process diarization output and align with transcript chunks
    
    Args:
        diarization: Diarization result from pyannote
        transcript_chunks: Transcript chunks with timestamps
        
    Returns:
        List of speaker-labeled transcript segments
    """
    # Create a dictionary to map speakers to their segments
    speaker_segments = {}
    
    # Process diarization output
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        if speaker not in speaker_segments:
            speaker_segments[speaker] = []
        
        speaker_segments[speaker].append({
            'start': turn.start,
            'end': turn.end
        })
    
    # Combine transcription chunks with speaker information
    speaker_transcript = []
    
    # Track the previous speaker to detect changes
    prev_speaker = None
    
    for i, chunk in enumerate(transcript_chunks):
        if not isinstance(chunk, dict) or 'timestamp' not in chunk or 'text' not in chunk:
            continue
            
        start_time, end_time = chunk['timestamp']
        text = chunk['text']
        
        # Find which speaker was talking during this segment
        speaker_overlaps = {}
        
        for speaker, segments in speaker_segments.items():
            total_overlap = 0
            for segment in segments:
                overlap_start = max(segment['start'], start_time)
                overlap_end = min(segment['end'], end_time)
                
                if overlap_end > overlap_start:
                    overlap_duration = overlap_end - overlap_start
                    total_overlap += overlap_duration
            
            # Store total overlap for this speaker
            if total_overlap > 0:
                speaker_overlaps[speaker] = total_overlap
        
        # Determine the most likely speaker
        assigned_speaker = None
        max_overlap = 0
        
        for speaker, overlap in speaker_overlaps.items():
            if overlap > max_overlap:
                max_overlap = overlap
                assigned_speaker = speaker
        
        # Enhanced detection for short utterances and conversational transitions
        if assigned_speaker is None or (end_time - start_time < 2.0 and text.strip().startswith("OK")):
            # Short response like "OK" is likely a different speaker responding
            if prev_speaker is not None and i > 0:
                # Choose a different speaker than the previous one
                available_speakers = list(speaker_segments.keys())
                if len(available_speakers) > 1 and prev_speaker in available_speakers:
                    available_speakers.remove(prev_speaker)
                    assigned_speaker = available_speakers[0]
        
        # Format as "Speaker X: text"
        if assigned_speaker:
            speaker_name = f"Speaker {assigned_speaker.split('_')[-1]}"
            prev_speaker = assigned_speaker
        else:
            speaker_name = "Unknown Speaker"
            
        speaker_transcript.append(f"{speaker_name}: {text}")
    
    return speaker_transcript

def enhanced_speaker_separation(transcript_chunks, full_text=""):
    """
    Enhanced heuristic for speaker separation when proper diarization is unavailable
    
    Args:
        transcript_chunks: Transcript chunks with timestamps
        full_text: Full text if chunks are not available
        
    Returns:
        List of speaker-labeled transcript segments
    """
    # If no chunks with timestamps, try to split by sentence endings
    if not transcript_chunks and full_text:
        sentences = re.split(r'(?<=[.!?])\s+', full_text)
        speaker_transcript = []
        current_speaker = 1
        
        for sentence in sentences:
            if sentence.strip():
                speaker_transcript.append(f"Speaker {current_speaker}: {sentence.strip()}")
                # Alternate speakers for each sentence
                current_speaker = 2 if current_speaker == 1 else 1
                
        return speaker_transcript
    
    # Group chunks into potential speaker turns
    speaker_transcript = []
    
    # 1. Group words into sentences or utterances
    sentences = []
    current_sentence = {"text": "", "start": 0, "end": 0}
    
    for chunk in transcript_chunks:
        if not isinstance(chunk, dict) or 'timestamp' not in chunk or 'text' not in chunk:
            continue
            
        start_time, end_time = chunk['timestamp']
        text = chunk['text']
        
        # Start a new sentence if:
        # - Current sentence is empty
        # - Text ends with punctuation
        # - There's a significant pause (>0.75 seconds)
        if not current_sentence["text"]:
            current_sentence = {"text": text, "start": start_time, "end": end_time}
        elif text.rstrip()[-1] in ".!?" or start_time - current_sentence["end"] > 0.75:
            # Complete current sentence
            sentences.append(current_sentence)
            current_sentence = {"text": text, "start": start_time, "end": end_time}
        else:
            # Append to current sentence
            current_sentence["text"] += " " + text
            current_sentence["end"] = end_time
    
    # Add the last sentence if not empty
    if current_sentence["text"]:
        sentences.append(current_sentence)
    
    # 2. Identify potential speaker changes using prosodic features
    current_speaker = 1
    for i, sentence in enumerate(sentences):
        # Switch speakers if:
        # - There's a significant pause between sentences (>1.2s)
        # - This is a short response after a question
        # - Every other sentence (if other heuristics don't apply)
        switch_speaker = False
        
        if i > 0:
            prev_sentence = sentences[i-1]
            pause_duration = sentence["start"] - prev_sentence["end"]
            
            # Check for significant pause
            if pause_duration > 1.2:
                switch_speaker = True
            # Check for question-answer pattern
            elif prev_sentence["text"].rstrip()[-1] == "?" and len(sentence["text"].split()) < 8:
                switch_speaker = True
            # Fallback: switch every other sentence
            elif i % 2 == 0:
                switch_speaker = True
                
        if switch_speaker:
            current_speaker = 2 if current_speaker == 1 else 1
                
        speaker_transcript.append(f"Speaker {current_speaker}: {sentence['text'].strip()}")
    
    # Ensure we have at least one entry from each speaker
    if all(entry.startswith("Speaker 1:") for entry in speaker_transcript):
        # Force at least one entry to be Speaker 2
        if len(speaker_transcript) > 1:
            speaker_transcript[len(speaker_transcript)//2] = "Speaker 2: " + speaker_transcript[len(speaker_transcript)//2][10:]
    
    return speaker_transcript