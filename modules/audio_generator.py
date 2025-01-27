import requests
import tempfile
from config import VOICE_SETTINGS

def generate_audio_eleven_labs(text, voice_id, api_key):
    """Generate audio using ElevenLabs API"""
    print(f"\nGenerating audio for voice_id: {voice_id}")
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": VOICE_SETTINGS
    }
    
    print("Making API request...")
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        temp_audio = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
        temp_audio.write(response.content)
        temp_audio.close()
        return temp_audio.name
    else:
        print(f"Error response: {response.text}")
        raise Exception(f"ElevenLabs API error: {response.text}")

def get_voice_ids(api_key):
    """Fetch all available voices from ElevenLabs"""
    print("\nFetching voices from ElevenLabs...")
    headers = {"xi-api-key": api_key}
    
    response = requests.get(
        "https://api.elevenlabs.io/v1/voices",
        headers=headers
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch voices: {response.text}")
        
    voices = response.json()["voices"]
    
    if not voices:
        raise ValueError("No voices found in your ElevenLabs account")
    
    return voices
