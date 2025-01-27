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

app = Flask(__name__)
CORS(app)

# Add this line to enable Flask debug mode
app.config['DEBUG'] = True

# Global list to track temporary files for cleanup
temp_files = []


VOICE_SETTINGS = {
    "stability": 0.75,
    "similarity_boost": 0.45,
    "style": 0.40,
}
SOUND_EFFECTS = {
    'vineboom': os.path.join('static', 'sfx', 'vineboom.mp3'),
    'notification': os.path.join('static', 'sfx', 'notification.mp3'),
    'rizz': os.path.join('static', 'sfx', 'rizz.mp3'),
    'send': os.path.join('static', 'sfx', 'send.mp3'),
    'receive': os.path.join('static', 'sfx', 'receive.mp3'),
    'bleh': os.path.join('static', 'sfx', 'bleh.mp3'),
}

PROFILE_PICTURES_DIR = os.path.join('static', 'images', 'profile_pictures')
os.makedirs(PROFILE_PICTURES_DIR, exist_ok=True)

# Add this near the top with other constants
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

def capture_chat_interface(messages, show_header=True, header_data=None):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--hide-scrollbars')
    chrome_options.add_argument('--force-device-scale-factor=1')
    chrome_options.add_argument('--window-size=414,900')
    
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get('http://127.0.0.1:5001')
        
        # Wait for elements
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "dynamic-container"))
        )
        
        # Apply header data if provided
        if header_data:
            driver.execute_script("""
                const profileImage = arguments[0];
                const headerName = arguments[1];
                
                if (profileImage) {
                    document.getElementById('profileImage').src = profileImage;
                }
                if (headerName) {
                    document.getElementById('headerName').textContent = headerName;
                }
            """, header_data['profileImage'], header_data['headerName'])
        
        # Set transparent background
        driver.execute_script("""
            document.body.style.background = 'transparent';
            document.documentElement.style.background = 'transparent';
        """)
        
        # Modified JavaScript to properly handle sound effects
        driver.execute_script("""
            const messages = arguments[0];
            const showHeader = arguments[1];
            
            // Remove input area
            const inputArea = document.querySelector('.input-area');
            if (inputArea) inputArea.remove();
            
            const container = document.querySelector('.container');
            const messageContainer = document.getElementById('messageContainer');
            const header = document.querySelector('.header');
            const dynamicContainer = messageContainer.querySelector('.dynamic-container');
            
            // Show/hide header
            if (header) {
                header.style.display = showHeader ? 'flex' : 'none';
            }
            
            // Reset container styles
            container.style.minHeight = 'unset';
            container.style.height = 'auto';
            messageContainer.style.height = 'auto';
            messageContainer.style.maxHeight = 'none';
            messageContainer.style.minHeight = 'unset';
            
            // Clear existing messages
            dynamicContainer.innerHTML = '';
            
            // Debug log messages
            console.log('Processing messages with sound effects:', messages);

            messages.forEach(msg => {
                if (msg && msg.text && msg.text.trim()) {
                    const messageDiv = document.createElement('div');
                    messageDiv.className = `message ${msg.is_sender ? 'sender' : 'receiver'}`;
                    messageDiv.textContent = msg.text.trim();
                    messageDiv.setAttribute('data-id', msg.id);
                    
                    // Add sound effect if present
                    if (msg.soundEffect) {
                        messageDiv.setAttribute('data-sound-effect', msg.soundEffect);
                        console.log(`Setting sound effect ${msg.soundEffect} for message: ${msg.text}`);
                    }
                    
                    dynamicContainer.appendChild(messageDiv);
                }
            });

            // Force layout recalculation
            container.offsetHeight;
        """, messages, show_header)
        
        # Wait for messages to render
        time.sleep(1.5)
        
        # Take screenshot
        container = driver.find_element(By.CLASS_NAME, "container")
        screenshot = container.screenshot_as_png
        image = Image.open(io.BytesIO(screenshot))
        
        # Convert to RGBA to handle transparency
        image = image.convert('RGBA')
        
        # Create a mask for rounded corners
        mask = Image.new('L', image.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle([(0, 0), (image.size[0]-1, image.size[1]-1)], 20, fill=255)
        
        # Apply the mask
        output = Image.new('RGBA', image.size, (0, 0, 0, 0))
        output.paste(image, mask=mask)
        
        # Crop to content
        bbox = output.getbbox()
        if bbox:
            output = output.crop(bbox)
        
        return output
        
    except Exception as e:
        print(f"Error capturing chat interface: {e}")
        import traceback
        traceback.print_exc()
        return None
        
    finally:
        driver.quit()

def generate_audio_eleven_labs(text, voice_id, api_key):
    """Generate audio using ElevenLabs API"""
    print(f"\nGenerating audio for voice_id: {voice_id}")
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"  # Changed to v1
    
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
        temp_files.append(temp_audio.name)
        temp_audio.write(response.content)
        temp_audio.close()
        return temp_audio.name
    else:
        print(f"Error response: {response.text}")
        raise Exception(f"ElevenLabs API error: {response.text}")

# Update get_voice_ids function
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
    
    return voices  # Return the raw voices array

# Update generate_video function to use voice IDs directly
def generate_video(messages, header_data):
    try:
        voice_settings = header_data.get('voiceSettings', {})
        api_key = voice_settings.get('apiKey')
        
        if not api_key:
            raise ValueError("ElevenLabs API key is required")
        
        # Get sender and receiver voice IDs directly from the request
        sender_voice_id = voice_settings.get('sender')
        receiver_voice_id = voice_settings.get('receiver')
        
        if not sender_voice_id or not receiver_voice_id:
            raise ValueError("Sender and receiver voice IDs are required")
        
        print(f"Using voice IDs - Sender: {sender_voice_id}, Receiver: {receiver_voice_id}")
        
        # Rest of the function remains the same
        # Get the selected background video
        selected_bg = header_data.get('backgroundVideo', 'background 3.mp4')
        print(f"Using background video: {selected_bg}")  # Debug log
        
        # Use the selected background video
        bg_path = os.path.join(os.path.dirname(__file__), 'static', 'videos', selected_bg)
        print(f"Background video path: {bg_path}")  # Debug log
        
        if not os.path.exists(bg_path):
            raise FileNotFoundError(f"Background video not found: {bg_path}")
        
        background = VideoFileClip(bg_path, audio=False)
        video_clips = []
        audio_clips = []
        current_time = 0
        message_count = 0

        # Process messages in sequences of 5
        for i in range(0, len(messages), 5):
            sequence = messages[i:i+5]
            
            for j in range(len(sequence)):
                current_window = sequence[:j+1]
                message_count += 1
                
                msg = sequence[j]
                voice_id = sender_voice_id if msg['is_sender'] else receiver_voice_id
                audio_path = generate_audio_eleven_labs(msg['text'], voice_id, api_key)
                voice_audio = AudioFileClip(audio_path)
                
                # Add sound effect if specified
                if msg.get('soundEffect') and msg['soundEffect'] in SOUND_EFFECTS:
                    print(f"Adding sound effect: {msg['soundEffect']}")  # Debug log
                    effect_audio = AudioFileClip(SOUND_EFFECTS[msg['soundEffect']])
                    # Combine voice and effect (effect plays slightly before voice)
                    combined_audio = CompositeAudioClip([
                        effect_audio.with_start(0),
                        voice_audio.with_start(0.1)  # Slight delay for voice
                    ])
                    audio_duration = max(voice_audio.duration + 0.1, effect_audio.duration)
                else:
                    combined_audio = voice_audio
                    audio_duration = voice_audio.duration
                
                # Use combined audio duration for clip timing
                clip_duration = audio_duration + 0.09  # Reduced pause between messages
                
                # Show header only for the first five messages
                show_header = (message_count <= 5)
                current_image = capture_chat_interface(current_window, show_header=show_header, header_data=header_data)
                if current_image is None:
                    print(f"Failed to capture chat interface for message {i + j + 1}")
                    continue

                # Resize image to fit the background
                target_width = int(background.w * 0.85)
                width_scale = target_width / current_image.width
                new_height = int(current_image.height * width_scale)
                current_image = current_image.resize((target_width, new_height), Image.LANCZOS)
                current_array = np.array(current_image)

                # Calculate position to center
                x_center = background.w // 2 - target_width // 2
                y_top = background.h // 6  # Keep vertical position the same

                # Create clip for current message state
                current_clip = (ImageClip(current_array)
                                .with_duration(clip_duration)
                                .with_position((x_center, y_top)))
                
                video_clips.append(current_clip.with_start(current_time))
                audio_clips.append(combined_audio.with_start(current_time))

                current_time += clip_duration

        if not video_clips:
            raise Exception("No valid messages to generate video.")

        if current_time > background.duration:
            n_loops = int(np.ceil(current_time / background.duration))
            bg_clips = [background] * n_loops
            background_extended = concatenate_videoclips(bg_clips)
            background_extended = background_extended.subclipped(0, current_time)
        else:
            background_extended = background.subclipped(0, current_time)

        final = CompositeVideoClip(
            [background_extended] + video_clips,
            size=background_extended.size
        )

        if audio_clips:
            final = final.with_audio(CompositeAudioClip(audio_clips))

        # Generate unique filename with timestamp and UUID
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        output_filename = f'video_{timestamp}_{unique_id}.mp4'
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        final.write_videofile(output_path, 
                            fps=30, 
                            codec='libx264',
                            audio_codec='aac',
                            bitrate="8000k",
                            preset='slower',
                            threads=4,
                            audio_bitrate="192k")
        
        return output_filename
        
    except Exception as e:
        print(f"Error generating video: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

@app.route('/api/generate', methods=['POST'])
def generate_endpoint():
    try:
        data = request.json
        print("Received data:", data)  # Debug log
        messages = data['messages']
        
        # Validate voice settings
        voice_settings = data.get('voiceSettings', {})
        if not voice_settings.get('apiKey'):
            return jsonify({
                'error': 'ElevenLabs API key is required'
            }), 400
        
        if not voice_settings.get('sender') or not voice_settings.get('receiver'):
            return jsonify({
                'error': 'Voice settings must include sender and receiver voice types'
            }), 400
        
        # Debug log for messages and sound effects
        print("Processing messages in generate_endpoint:")
        for msg in messages:
            print(f"Message: {msg.get('text', 'NO TEXT')} | "
                  f"Sender: {msg.get('is_sender', 'NO SENDER')} | "
                  f"Sound Effect: {msg.get('soundEffect', 'NONE')}")
        
        header_data = {
            'profileImage': data.get('profileImage', ''),
            'headerName': data.get('headerName', 'John Doe'),
            'voiceSettings': voice_settings,  # Pass the validated voice settings
            'backgroundVideo': data.get('backgroundVideo')  # Make sure this is passed from the frontend
        }
        
        video_filename = generate_video(messages, header_data)
        return jsonify({
            'success': True,
            'video_url': f'/output/{video_filename}'
        })
    except Exception as e:
        print(f"Error in generate endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Add new route to serve video files
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
        return jsonify(voices)  # Return the complete voice data
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload-profile-picture', methods=['POST'])
def upload_profile_picture():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(PROFILE_PICTURES_DIR, filename)
        file.save(filepath)
        return jsonify({
            'image_path': f'/static/images/profile_pictures/{filename}'
        })

@app.route('/api/profile-pictures')
def get_profile_pictures():
    files = [f for f in os.listdir(PROFILE_PICTURES_DIR) 
             if os.path.isfile(os.path.join(PROFILE_PICTURES_DIR, f)) 
             and f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]
    return jsonify(files)

@app.route('/api/background-videos')
def get_background_videos():
    video_dir = os.path.join('static', 'videos')
    videos = [f for f in os.listdir(video_dir) if f.lower().endswith(('.mp4', '.mov'))]
    return jsonify(videos)

if __name__ == '__main__':
    try:
        logging.info("Starting the Flask application...")
        # Change the port to 5000 (Flask's default) in case 5001 is occupied
        app.run(debug=True, host='0.0.0.0', port=5001)
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        sys.exit(1)