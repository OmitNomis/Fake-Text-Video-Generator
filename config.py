import os

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

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)
