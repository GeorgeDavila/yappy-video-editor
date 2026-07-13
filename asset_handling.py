import os
from PIL import Image
from PIL.ExifTags import TAGS
from mutagen import File as MutagenFile

from moviepy import *
import sqlite3

facecam_upload_path = "facecam.mp4"
audio_upload_path = "audio.mp3"
facecam_output_path = "facecam_output.mp4"
audio_output_path = "audio_output.mp3"

class FileDataProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
    
    def extract_image_metadata(self):
        if not os.path.exists(self.file_path):
            return {"error": "File not found"}
            
        ext = os.path.splitext(self.file_path).lower()
        image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.tiff'}
        
        text_tags = {}

        # --- IMAGE TEXT METADATA ---
        if ext in image_extensions:
            with Image.open(self.file_path) as img:
                # 1. Standard EXIF Text Tags (Camera, Copyright, Author)
                exif_data = img.getexif()
                if exif_data:
                    for tag_id, value in exif_data.items():
                        tag_name = TAGS.get(tag_id, tag_id)
                        # Look specifically for common text/string fields
                        text_fields = {'ImageDescription', 'Copyright', 'Artist', 'Software', 'DateTime', 'UserComment'}
                        if tag_name in text_fields and isinstance(value, (str, bytes)):
                            if isinstance(value, bytes):
                                value = value.decode(errors='replace').strip()
                            text_tags[tag_name] = value
                
                # 2. Format-specific PNG/WebP Text chunks
                if hasattr(img, "info"):
                    for key, value in img.info.items():
                        # Skip binary chunks, keep strings
                        if isinstance(value, str) and key not in ['exif', 'icc_profile']:
                            text_tags[f"info_{key}"] = value
        else:
            return {"error": "File is not a recognized image format"}
        return {
            "file_name": os.path.basename(self.file_path),
            "text_metadata": text_tags,
            "file_type": "image"
        }

    def extract_video_metadata(self):
        text_tags = {}
        if not os.path.exists(self.file_path):
            return {"error": "File not found"}
        ext = os.path.splitext(self.file_path).lower()
        video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv', '.webm'}
        if ext in video_extensions:
            try:
                video_file = MutagenFile(self.file_path)
                if video_file is not None:
                    # Mutagen extracts tags as a key-value dictionary
                    for tag, value in video_file.items():
                        # Standardize value presentation (remove list wrappers if single element)
                        clean_value = value[0] if isinstance(value, list) and len(value) == 1 else value
                        
                        # Ignore purely binary objects (like embedded cover art)
                        if isinstance(clean_value, (str, int, float)):
                            text_tags[tag] = clean_value
                        elif isinstance(clean_value, bytes):
                            try:
                                text_tags[tag] = clean_value.decode('utf-8', errors='ignore').strip()
                            except Exception:
                                pass # Skip non-textual binary chunks
            except Exception as e:
                return {"error": f"Could not parse video metadata: {str(e)}"}
        else:
            return {"error": "File is not a recognized video format"}
        return {
            "file_name": os.path.basename(self.file_path),
            "text_metadata": text_tags,
            "file_type": "video"
        }
        # --- EXAMPLE USAGE ---
        # video_meta = extract_video_metadata("my_movie.mp4")
        # image_meta = extract_image_metadata("holiday_photo.jpg")
        # print(video_meta)
        # print(image_meta)
        
class DataManager:
    def __init__(self, user_assets_directory, image_assets_directory, audio_assets_directory, video_assets_directory):
        self.user_assets_directory = user_assets_directory
        self.image_assets_directory = image_assets_directory
        self.audio_assets_directory = audio_assets_directory
        self.video_assets_directory = video_assets_directory

    # this is intended to be used casually by a lay user. 
    # Focus is on keeping assets in standard file system, and not in a database.
    # Use sqlite only in background processes.

    # Store Paths, Not Files
    def save_all_assets_to_sqlite(self):
        conn = sqlite3.connect(self.user_assets_directory)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS assets (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, path TEXT)")
        cursor.execute("INSERT INTO assets (name, path) VALUES (?, ?)", ("user_assets", self.user_assets_directory))
        cursor.execute("INSERT INTO assets (name, path) VALUES (?, ?)", ("image_assets", self.image_assets_directory))
        cursor.execute("INSERT INTO assets (name, path) VALUES (?, ?)", ("audio_assets", self.audio_assets_directory))
        cursor.execute("INSERT INTO assets (name, path) VALUES (?, ?)", ("video_assets", self.video_assets_directory))
        conn.commit()
        conn.close()
        return True

    def load_asset_from_sqlite(self, asset_name):
        conn = sqlite3.connect(self.user_assets_directory)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM assets WHERE name = ?", (asset_name,))
        asset = cursor.fetchone()
        conn.close()
        return asset
    
    def load_user_assets_from_sqlite(self):
        conn = sqlite3.connect(self.user_assets_directory)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM assets WHERE name = ?", ("user_assets",))
        user_assets = cursor.fetchall()
        conn.close()
        return user_assets

    def load_image_assets_from_sqlite(self):
        conn = sqlite3.connect(self.user_assets_directory)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM assets WHERE name = ?", ("image_assets",))
        image_assets = cursor.fetchall()
        conn.close()
        return image_assets
    
    def load_audio_assets_from_sqlite(self):
        conn = sqlite3.connect(self.user_assets_directory)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM assets WHERE name = ?", ("audio_assets",))
        audio_assets = cursor.fetchall()
        conn.close()
        return audio_assets
    
    def load_video_assets_from_sqlite(self):
        conn = sqlite3.connect(self.user_assets_directory)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM assets WHERE name = ?", ("video_assets",))
        video_assets = cursor.fetchall()
        conn.close()
        return video_assets
    
    def delete_all_assets_from_sqlite(self):
        conn = sqlite3.connect(self.user_assets_directory)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM assets WHERE name = ?", ("user_assets",))
        cursor.execute("DELETE FROM assets WHERE name = ?", ("image_assets",))
        cursor.execute("DELETE FROM assets WHERE name = ?", ("audio_assets",))
        cursor.execute("DELETE FROM assets WHERE name = ?", ("video_assets",))
        conn.commit()
        conn.close()
        return True

    def delete_asset_from_sqlite(self, asset_name):
        conn = sqlite3.connect(self.user_assets_directory)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM assets WHERE name = ?", (asset_name,))
        conn.commit()
        conn.close()
        return True

class FacecamPreprocessing:
    def __init__(self, facecam_upload_path, audio_upload_path, facecam_output_path, audio_output_path):
        self.facecam_upload_path = facecam_upload_path
        self.audio_upload_path = audio_upload_path
        self.facecam_output_path = facecam_output_path
        self.audio_output_path = audio_output_path

    def split_video_from_audio(self):
        video = VideoFileClip(self.video_upload_path)
        audio, video = video.audio, video.without_audio()
        audio.write_audiofile(self.audio_output_path)
        video.write_videofile(self.video_output_path)
        return audio, video