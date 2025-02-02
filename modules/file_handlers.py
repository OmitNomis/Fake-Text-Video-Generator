import os
from werkzeug.utils import secure_filename
from config import PROFILE_PICTURES_DIR

def upload_profile_picture(file):
    if file and file.filename:
        filename = secure_filename(file.filename)
        filepath = os.path.join(PROFILE_PICTURES_DIR, filename)
        file.save(filepath)
        return f'/static/images/profile_pictures/{filename}'
    return None

def get_profile_pictures():
    return [f for f in os.listdir(PROFILE_PICTURES_DIR) 
            if os.path.isfile(os.path.join(PROFILE_PICTURES_DIR, f)) 
            and f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]

def get_background_videos():
    video_dir = os.path.join('static', 'videos')
    return [f for f in os.listdir(video_dir) if f.lower().endswith(('.mp4', '.mov'))]

def get_background_music():
    music_dir = os.path.join('static', 'music')
    return [f for f in os.listdir(music_dir) if f.endswith(('.mp3', '.wav', '.ogg'))]