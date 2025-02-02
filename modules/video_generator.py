from moviepy import VideoFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips, CompositeAudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from PIL import Image
import numpy as np
import os
from datetime import datetime
import uuid
import time  # Add this import
from .chat_interface import capture_chat_interface
from .audio_generator import generate_audio_eleven_labs
from config import OUTPUT_DIR, SOUND_EFFECTS

def generate_video(messages, header_data):
    try:
        voice_settings = header_data.get('voiceSettings', {})
        api_key = voice_settings.get('apiKey')
        
        if not api_key:
            raise ValueError("ElevenLabs API key is required")
        
        sender_voice_id = voice_settings.get('sender')
        receiver_voice_id = voice_settings.get('receiver')
        
        if not sender_voice_id or not receiver_voice_id:
            raise ValueError("Sender and receiver voice IDs are required")
        
        print(f"Using voice IDs - Sender: {sender_voice_id}, Receiver: {receiver_voice_id}")
        
        selected_bg = header_data.get('backgroundVideo', 'background 3.mp4')
        bg_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'videos', selected_bg)
        
        if not os.path.exists(bg_path):
            raise FileNotFoundError(f"Background video not found: {bg_path}")
        
        background = VideoFileClip(bg_path, audio=False)
        video_clips = []
        audio_clips = []
        current_time = 0
        message_count = 0
        temp_files = []  # Add this to track temporary files

        for i in range(0, len(messages), 5):
            sequence = messages[i:i+5]
            
            for j in range(len(sequence)):
                current_window = sequence[:j+1]
                message_count += 1
                
                # Capture chat interface with retries
                max_retries = 3
                chat_image = None
                
                for attempt in range(max_retries):
                    chat_image = capture_chat_interface(current_window, show_header=(message_count <= 5), header_data=header_data)
                    if chat_image:
                        break
                    print(f"Attempt {attempt + 1} failed, retrying...")
                    time.sleep(1)
                
                if not chat_image:
                    print(f"Failed to capture chat interface for message {message_count} after {max_retries} attempts")
                    continue
                
                msg = sequence[j]
                voice_id = sender_voice_id if msg['is_sender'] else receiver_voice_id
                audio_path = generate_audio_eleven_labs(msg['text'], voice_id, api_key)
                temp_files.append(audio_path)  # Track temporary audio file
                voice_audio = voice_audio = AudioFileClip(audio_path).with_volume_scaled(2.5)
                
                if msg.get('soundEffect') and msg['soundEffect'] in SOUND_EFFECTS:
                    effect_audio = AudioFileClip(SOUND_EFFECTS[msg['soundEffect']])
                    combined_audio = CompositeAudioClip([
                        effect_audio.with_start(0),
                        voice_audio.with_start(0.1)
                    ])
                    audio_duration = max(voice_audio.duration + 0.1, effect_audio.duration)
                else:
                    combined_audio = voice_audio
                    audio_duration = voice_audio.duration
                
                clip_duration = audio_duration + 0.09
                
                show_header = (message_count <= 5)
                current_image = capture_chat_interface(current_window, show_header=show_header, header_data=header_data)
                if current_image is None:
                    print(f"Failed to capture chat interface for message {i + j + 1}")
                    continue

                target_width = int(background.w * 0.85)
                width_scale = target_width / current_image.width
                new_height = int(current_image.height * width_scale)
                current_image = current_image.resize((target_width, new_height), Image.Resampling.LANCZOS)
                current_array = np.array(current_image)

                x_center = background.w // 2 - target_width // 2
                y_top = background.h // 6

                current_clip = (ImageClip(current_array)
                                .with_duration(clip_duration)
                                .with_position((x_center, y_top)))
                
                video_clips.append(current_clip.with_start(current_time))
                audio_clips.append(combined_audio.with_start(current_time))

                current_time += clip_duration

        if not video_clips:
            raise Exception("Failed to generate any valid video clips")
            
        if current_time > background.duration:
            n_loops = int(np.ceil(current_time / background.duration))
            bg_clips = [background] * n_loops
            background_extended = concatenate_videoclips(bg_clips)
            background_extended = background_extended.subclipped(0, current_time)  # Changed from subclip to subclipped
        else:
            background_extended = background.subclipped(0, current_time)  # Changed from subclip to subclipped

        final = CompositeVideoClip(
            [background_extended] + video_clips,
            size=background_extended.size
        )

        if audio_clips:
            final = final.with_audio(CompositeAudioClip(audio_clips))

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        output_filename = f'video_{timestamp}_{unique_id}.mp4'
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        final.write_videofile(output_path, 
                            fps=30, 
                            codec='libx264',
                            audio_codec='aac',
                            bitrate="12000k",  # Increased from 8000k
                            preset='veryslow',  # Changed from 'slower' for better quality
                            threads=4,
                            audio_bitrate="320k",  # Increased from 192k
                            ffmpeg_params=[
                                "-crf", "18",  # Lower CRF value for better quality (default is 23)
                                "-profile:v", "high",
                                "-level", "4.2",
                                "-pix_fmt", "yuv420p"
                            ])
        
        # Clean up temporary files
        for temp_file in temp_files:
            try:
                os.remove(temp_file)
            except:
                pass

        return output_filename
        
    except Exception as e:
        print(f"Error generating video: {str(e)}")
        import traceback
        traceback.print_exc()
        # Clean up temporary files on error
        for temp_file in temp_files:
            try:
                os.remove(temp_file)
            except:
                pass
        raise
