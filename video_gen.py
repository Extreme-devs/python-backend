import glob
from moviepy.editor import *
from moviepy.video.fx import all as vfx
from PIL import Image, ImageEnhance
import numpy as np
import os
from moviepy.config import change_settings

# Configure MoviePy to use ImageMagick
# You'll need to adjust this path to where ImageMagick is installed on your system
# IMAGEMAGICK_BINARY = r"C:\Program Files\ImageMagick-7.1.1-Q16\magick.exe"
# change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_BINARY})

def zoom_effect(clip, zoom_ratio=1.3, duration=None):
    """
    Custom zoom effect for MoviePy clips
    """
    if duration is None:
        duration = clip.duration
    
    def zoom_factory(t):
        progress = t / duration
        current_zoom = 1 + (zoom_ratio - 1) * progress
        return current_zoom
    
    return clip.resize(zoom_factory)

class VideoGenerator:
    def __init__(self, output_path="output_video.mp4"):
        self.output_path = output_path
        self.clips = []
        self.duration_per_image = 3
        
    def resize_image(self, img, size):
        """Resize image using updated PIL syntax"""
        return img.resize(size, Image.Resampling.LANCZOS)
    
    def add_image(self, image_path, start_time, duration=None, effects=None):
        """Add an image to the video with specified effects"""
        try:
            # Open and process image with PIL first
            pil_image = Image.open(image_path)
            
            # Convert to RGB if necessary
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Convert PIL image to numpy array
            img_array = np.array(pil_image)
            
            # Create MoviePy clip from numpy array
            clip = ImageClip(img_array)
            
            if duration:
                clip = clip.set_duration(duration)
            else:
                clip = clip.set_duration(self.duration_per_image)
            
            clip = clip.set_start(start_time)
            
            if effects:
                if 'brightness' in effects:
                    clip = clip.fx(vfx.colorx, effects['brightness'])
                
                if 'fade' in effects:
                    clip = clip.crossfadein(1).crossfadeout(1)
                
                if 'zoom' in effects:
                    clip = zoom_effect(clip, zoom_ratio=1.3, duration=clip.duration)
            
            self.clips.append(clip)
            
        except Exception as e:
            print(f"Error processing image {image_path}: {str(e)}")
    
    def create_text_clip(self, text, fontsize=30, color='white'):
        """Create text clip without relying on ImageMagick"""
        # Create a blank numpy array
        w, h = 1920, 100  # Height adjusted for text
        text_array = np.zeros((h, w, 3), dtype=np.uint8)
        text_array.fill(255)  # White background
        
        # Convert to ImageClip
        txt_clip = ImageClip(text_array)
        
        # Add text properties as metadata
        txt_clip.text = text
        txt_clip.fontsize = fontsize
        txt_clip.color = color
        
        return txt_clip
    
    def add_text(self, text, start_time, duration, position='center', fontsize=30, color='white'):
        """Add text overlay using custom text clip"""
        try:
            txt_clip = self.create_text_clip(text, fontsize, color)
            txt_clip = txt_clip.set_position(position).set_duration(duration)
            txt_clip = txt_clip.set_start(start_time)
            self.clips.append(txt_clip)
        except Exception as e:
            print(f"Error adding text '{text}': {str(e)}")
    
    def add_music(self, music_path, volume=1.0):
        """Add background music to the video"""
        try:
            if os.path.exists(music_path):
                self.audio = AudioFileClip(music_path)
                self.audio = self.audio.volumex(volume)
            else:
                print(f"Music file not found: {music_path}")
        except Exception as e:
            print(f"Error adding music from {music_path}: {str(e)}")
    
    def generate(self, size=(1920, 1080)):
        """Generate the final video"""
        try:
            if not self.clips:
                raise ValueError("No clips added to the video")
            
            # Combine all clips
            final = CompositeVideoClip(self.clips, size=size)
            
            # Add music if it exists
            if hasattr(self, 'audio'):
                # Loop the audio if it's shorter than the video
                if self.audio.duration < final.duration:
                    self.audio = afx.audio_loop(self.audio, duration=final.duration)
                else:
                    # Trim audio if it's longer than the video
                    self.audio = self.audio.subclip(0, final.duration)
                
                final = final.set_audio(self.audio)
            
            # Write the final video
            final.write_videofile(self.output_path, fps=24, codec='libx264', 
                                audio_codec='aac', threads=4)
            
        except Exception as e:
            print(f"Error generating video: {str(e)}")

def create_travel_video(image_paths, descriptions, music_path):
    """Create a travel video with the given images, descriptions, and background music"""
    if not image_paths:
        print("No images found!")
        return
    
    video = VideoGenerator("travel_video.mp4")
    
    current_time = 0
    for i, (image_path, description) in enumerate(zip(image_paths, descriptions)):
        if not os.path.exists(image_path):
            print(f"Image not found: {image_path}")
            continue
            
        effects = {
            'brightness': 1.2,
            'fade': True,
            'zoom': True
        }
        video.add_image(image_path, current_time, duration=5, effects=effects)
        
        video.add_text(description, 
                      start_time=current_time + 1,
                      duration=3,
                      position=('center', 'bottom'),
                      fontsize=40)
        
        current_time += 5
    
    if os.path.exists(music_path):
        video.add_music(music_path, volume=0.7)
    else:
        print(f"Music file not found: {music_path}")
    
    video.generate()

# Example usage
if __name__ == "__main__":
    image_paths = glob.glob('images/*')
    descriptions = [
        'Beautiful beach view',
        'City skyline',
        'Mountain landscape'
    ]
    music_path = 'nights.mp3'
    
    # Ensure we have matching descriptions for all images
    descriptions = descriptions[:len(image_paths)]
    
    create_travel_video(image_paths, descriptions, music_path)