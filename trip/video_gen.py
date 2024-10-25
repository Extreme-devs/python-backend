import uuid
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont
from PIL import Image as PilImage
import numpy as np
import os
import platform
import requests
from io import BytesIO
import tempfile
import urllib.parse


class VideoGenerator:
    def __init__(self, output_path):
        """Initialize the VideoGenerator with default settings and font paths."""
        self.output_path = output_path
        self.default_size = (1280, 720)
        self.resampling_filter = PilImage.Resampling.LANCZOS
        self.default_font = self.get_default_font()
        self.temp_dir = (
            tempfile.mkdtemp()
        )  # Create temporary directory for downloaded images

    def __del__(self):
        """Cleanup temporary files on object destruction."""
        try:
            import shutil

            shutil.rmtree(self.temp_dir)
        except:
            pass

    def download_image(self, image_url):
        """Download image from URL and return a path to the temporary file."""
        try:
            # Create a safe filename from the URL
            filename = urllib.parse.quote(image_url, safe="") + ".jpg"
            temp_path = os.path.join(self.temp_dir, filename)

            # If already downloaded, return cached path
            if os.path.exists(temp_path):
                return temp_path

            # Download the image
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()  # Raise exception for bad status codes

            # Save to temporary file
            img = Image.open(BytesIO(response.content))
            img.save(temp_path)

            return temp_path
        except Exception as e:
            raise ValueError(f"Error downloading image from {image_url}: {str(e)}")

    def get_default_font(self):
        """Get the system's default font path based on the operating system."""
        system = platform.system()
        try:
            if system == "Windows":
                font_paths = [
                    "C:\\Windows\\Fonts\\arial.ttf",
                    "C:\\Windows\\Fonts\\segoeui.ttf",
                    "C:\\Windows\\Fonts\\calibri.ttf",
                ]
            elif system == "Darwin":  # macOS
                font_paths = [
                    "/System/Library/Fonts/Helvetica.ttc",
                    "/Library/Fonts/Arial.ttf",
                ]
            else:  # Linux and others
                font_paths = [
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                    "/usr/share/fonts/TTF/Arial.ttf",
                    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                ]

            for font_path in font_paths:
                if os.path.exists(font_path):
                    return font_path

            default_font = ImageFont.load_default()
            return default_font

        except Exception as e:
            print(f"Warning: Error loading system fonts: {str(e)}")
            return ImageFont.load_default()

    def create_background(self, background_data):
        """Create a background clip from either an image URL or color."""
        try:
            # Changed to match the script format where url is inside background_data
            if background_data.get("type") == "image" and background_data.get("url"):
                # Download and process background image using the correct URL key
                temp_path = self.download_image(background_data["url"])
                bg_img = Image.open(temp_path)
                bg_img = bg_img.resize(self.default_size, self.resampling_filter)
                return ImageClip(np.array(bg_img))
            else:
                # Default to color background if no image is specified
                color = background_data.get("color", (0, 0, 0))
                return ColorClip(self.default_size, color=color)
        except Exception as e:
            raise ValueError(f"Error creating background: {str(e)}")

    def create_text_clip(self, text, font_info, position, size=None):
        """Create a text clip with transparent background."""
        if size is None:
            size = self.default_size

        try:
            # Create empty RGBA image with transparent background
            img = Image.new("RGBA", size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            try:
                if "font_path" in font_info and os.path.exists(font_info["font_path"]):
                    font = ImageFont.truetype(font_info["font_path"], font_info["size"])
                else:
                    if isinstance(self.default_font, str):
                        font = ImageFont.truetype(self.default_font, font_info["size"])
                    else:
                        font = self.default_font
                        print("Warning: Using PIL's default font as fallback")
            except Exception as e:
                print(f"Warning: Font loading error: {str(e)}")
                font = ImageFont.load_default()

            color = font_info["color"]
            if isinstance(color, str):
                if color.startswith("#"):
                    color = tuple(int(color[i : i + 2], 16) for i in (1, 3, 5)) + (255,)
                else:
                    color_map = {
                        "white": (255, 255, 255, 255),
                        "black": (0, 0, 0, 255),
                        "red": (255, 0, 0, 255),
                        "green": (0, 255, 0, 255),
                        "blue": (0, 0, 255, 255),
                        "yellow": (255, 255, 0, 255),
                    }
                    color = color_map.get(color.lower(), (255, 255, 255, 255))
            elif len(color) == 3:
                color = tuple(color) + (255,)

            # Draw text
            draw.text((position["x"], position["y"]), text, font=font, fill=color)

            # Convert RGBA to array while preserving transparency
            return ImageClip(np.array(img), ismask=False, transparent=True)
        except Exception as e:
            raise ValueError(f"Error creating text clip: {str(e)}")

    def create_slide(self, slide_data, duration):
        """Create a slide with support for background images and proper error handling."""
        try:
            background = self.create_background(slide_data["background"])
            background = background.set_duration(duration)
            elements = [background]

            for child in slide_data.get("children", []):
                if child["type"] == "text":
                    text_clip = (
                        self.create_text_clip(
                            child["content"], child["font"], child["position"]
                        )
                        .set_duration(duration)
                        .set_position((child["position"]["x"], child["position"]["y"]))
                    )
                    elements.append(text_clip)

                elif child["type"] == "image":
                    # Download and process image from URL
                    temp_path = self.download_image(child["image_url"])
                    img = Image.open(temp_path)
                    img = img.resize(
                        (child["size"]["width"], child["size"]["height"]),
                        self.resampling_filter,
                    )
                    image_clip = (
                        ImageClip(np.array(img))
                        .set_duration(duration)
                        .set_position((child["position"]["x"], child["position"]["y"]))
                    )
                    elements.append(image_clip)

            return CompositeVideoClip(elements)

        except Exception as e:
            raise ValueError(f"Error creating slide: {str(e)}")

    def generate_video(self, script):
        """Generate the final video with proper error handling."""
        try:
            if not script.get("slides"):
                raise ValueError("No slides found in script")

            clips = []
            for slide in script["slides"]:
                if "duration" not in slide:
                    raise ValueError("Duration not specified for slide")
                slide_clip = self.create_slide(slide, slide["duration"])
                clips.append(slide_clip)

            final_clip = concatenate_videoclips(clips)

            if "background_music" in script and os.path.exists(
                script["background_music"]
            ):
                audio_clip = AudioFileClip(script["background_music"])

                if audio_clip.duration < final_clip.duration:
                    audio_clip = audio_clip.loop(duration=final_clip.duration)
                else:
                    audio_clip = audio_clip.subclip(0, final_clip.duration)

                final_clip = final_clip.set_audio(audio_clip)

            output_path = script.get("output", self.output_path)
            final_clip.write_videofile(
                output_path, fps=24, codec="libx264", audio_codec="aac", threads=4
            )

            final_clip.close()
            if "audio_clip" in locals():
                audio_clip.close()

        except Exception as e:
            raise ValueError(f"Error generating video: {str(e)}")


def generate_video(video_script):
    # video_script = {
    #     "slides": [
    #         {
    #             "background": {
    #                 "type": "image",
    #                 "url": "https://cghemaaztqssvxbmmzwq.supabase.co/storage/v1/object/public/files/0.9467362248042711.jpg",
    #             },
    #             "children": [
    #                 {
    #                     "type": "text",
    #                     "content": "Late Night Conversations",
    #                     "font": {"color": "white", "size": 50, "style": "bold"},
    #                     "position": {"x": 50, "y": 50},
    #                 }
    #             ],
    #             "duration": 5,
    #         },
    #         {
    #             "background": {
    #                 "type": "image",
    #                 "url": "https://cghemaaztqssvxbmmzwq.supabase.co/storage/v1/object/public/files/0.29896717775346804.jpg",
    #             },
    #             "children": [
    #                 {
    #                     "type": "text",
    #                     "content": "Exploring New Ideas",
    #                     "font": {"color": "yellow", "size": 50, "style": "italic"},
    #                     "position": {"x": 50, "y": 50},
    #                 }
    #             ],
    #             "duration": 5,
    #         },
    #         {
    #             "background": {
    #                 "type": "image",
    #                 "url": "https://cghemaaztqssvxbmmzwq.supabase.co/storage/v1/object/public/files/0.4398063834249133.jpg",
    #             },
    #             "children": [
    #                 {
    #                     "type": "text",
    #                     "content": "A Classroom Full of Dreams",
    #                     "font": {"color": "white", "size": 50, "style": "bold"},
    #                     "position": {"x": 50, "y": 50},
    #                 }
    #             ],
    #             "duration": 5,
    #         },
    #         {
    #             "background": {"type": "color", "color": (0, 0, 0)},  # Black background
    #             "children": [
    #                 {
    #                     "type": "text",
    #                     "content": "Memories Made, Lessons Learned!",
    #                     "font": {"color": "white", "size": 50, "style": "bold"},
    #                     "position": {"x": 50, "y": 100},
    #                 }
    #             ],
    #             "duration": 5,
    #         },
    #     ],
    #     "output": "output_video.mp4",
    #     "background_music": "nights.mp3",
    # }
    filename = uuid.uuid4().hex + ".mp4"
    video_script["output"] = filename
    generator = VideoGenerator(output_path=filename)    
    generator.generate_video(video_script)
    return filename