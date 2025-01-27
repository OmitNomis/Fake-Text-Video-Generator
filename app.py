import logging
import sys
import uuid
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

from flask import Flask, request, jsonify, send_file, render_template, send_from_directory
from flask_cors import CORS
from moviepy import VideoFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips, CompositeAudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from gtts import gTTS
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import tempfile
import time
import os
from PIL import Image, ImageFilter, ImageDraw
import io
import numpy as np
import requests
from werkzeug.utils import secure_filename

from modules.chat_interface import capture_chat_interface
from modules.audio_generator import generate_audio_eleven_labs, get_voice_ids
from modules.video_generator import generate_video
from modules.file_handlers import upload_profile_picture, get_profile_pictures, get_background_videos
from config import VOICE_SETTINGS, SOUND_EFFECTS, PROFILE_PICTURES_DIR, OUTPUT_DIR

app = Flask(__name__)
CORS(app)

app.config['DEBUG'] = True

# Global list to track temporary files for cleanup
temp_files = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate_endpoint():
    try:
        data = request.json
        print("Received data:", data)
        messages = data['messages']
        
        voice_settings = data.get('voiceSettings', {})
        if not voice_settings.get('apiKey'):
            return jsonify({'error': 'ElevenLabs API key is required'}), 400
        
        if not voice_settings.get('sender') or not voice_settings.get('receiver'):
            return jsonify({'error': 'Voice settings must include sender and receiver voice types'}), 400
        
        print("Processing messages in generate_endpoint:")
        for msg in messages:
            print(f"Message: {msg.get('text', 'NO TEXT')} | "
                  f"Sender: {msg.get('is_sender', 'NO SENDER')} | "
                  f"Sound Effect: {msg.get('soundEffect', 'NONE')}")
        
        header_data = {
            'profileImage': data.get('profileImage', ''),
            'headerName': data.get('headerName', 'John Doe'),
            'voiceSettings': voice_settings,
            'backgroundVideo': data.get('backgroundVideo')
        }
        
        video_filename = generate_video(messages, header_data)
        return jsonify({
            'success': True,
            'video_url': f'/output/{video_filename}'
        })
    except Exception as e:
        print(f"Error in generate endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/output/<filename>')
def serve_video(filename):
    return send_from_directory(OUTPUT_DIR, filename)

@app.route('/api/fetch-voices', methods=['POST'])
def fetch_voices():
    try:
        data = request.json
        api_key = data.get('apiKey')
        
        if not api_key:
            return jsonify({'error': 'API key is required'}), 400
            
        voices = get_voice_ids(api_key)
        return jsonify(voices)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload-profile-picture', methods=['POST'])
def upload_profile_picture_endpoint():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        image_path = upload_profile_picture(file)
        if image_path:
            return jsonify({'image_path': image_path})
        else:
            return jsonify({'error': 'Failed to upload image'}), 500

@app.route('/api/profile-pictures')
def get_profile_pictures_endpoint():
    return jsonify(get_profile_pictures())

@app.route('/api/background-videos')
def get_background_videos_endpoint():
    return jsonify(get_background_videos())

if __name__ == '__main__':
    try:
        logging.info("Starting the Flask application...")
        app.run(debug=True, host='0.0.0.0', port=5001)
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        sys.exit(1)