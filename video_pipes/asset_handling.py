import os
from PIL import Image
from PIL.ExifTags import TAGS
from mutagen import File as MutagenFile
from pathlib import Path

from moviepy import *
import sqlite3
import shutil

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

    def extract_audio_metadata(self):
        text_tags = {}
        if not os.path.exists(self.file_path):
            return {"error": "File not found"}
        ext = os.path.splitext(self.file_path).lower()
        audio_extensions = {'.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac', '.wma', '.m4b'}
        if ext in audio_extensions:
            try:
                audio_file = MutagenFile(self.file_path)
                if audio_file is not None:
                    # Mutagen extracts tags as a key-value dictionary
                    for tag, value in audio_file.items():
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
                return {"error": f"Could not parse audio metadata: {str(e)}"}
        else:
            return {"error": "File is not a recognized video format"}
        return {
            "file_name": os.path.basename(self.file_path),
            "text_metadata": text_tags,
            "file_type": "audio"
        }    
    
    def get_media_asset_type(self):
        ext = os.path.splitext(self.file_path).lower()
        image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.tiff'}
        video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv', '.webm'}
        audio_extensions = {'.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac', '.wma', '.m4b'}
        if ext in image_extensions:
            return "image"
        elif ext in video_extensions:
            return "video"
        elif ext in audio_extensions:
            return "audio"
        else:
            return None
    
    def get_media_asset_metadata(self):
        if self.get_media_asset_type() == "image":
            data = FileDataProcessor(self.file_path).extract_image_metadata()
            return data
        elif self.get_media_asset_type() == "video":
            data = FileDataProcessor(self.file_path).extract_video_metadata()
            return data
        elif self.get_media_asset_type() == "audio":
            data = FileDataProcessor(self.file_path).extract_audio_metadata()
            return data
        else:
            return None

class DataManager:
    def __init__(
        self,
        parent_directory = Path(__file__).parent,
        user_assets_directory = "user_assets", 
        image_assets_directory = "image_assets", 
        audio_assets_directory = "audio_assets", 
        video_assets_directory = "video_assets"
        ):
        self.parent_directory = parent_directory
        self.user_assets_directory = parent_directory / user_assets_directory
        self.image_assets_directory = parent_directory / image_assets_directory
        self.audio_assets_directory = parent_directory / audio_assets_directory
        self.video_assets_directory = parent_directory / video_assets_directory
    # this is intended to be used casually by a lay user. 
    # Focus is on keeping assets in standard file system, and not in a database.
    # Use sqlite only in background processes.

    def create_assets_table_in_sqlite(self):
        conn = sqlite3.connect(self.user_assets_directory)
        cursor = conn.cursor()
        # asset_class is one of: user_assets, image_assets, audio_assets, video_assets
        cursor.execute("CREATE TABLE IF NOT EXISTS assets (id INTEGER PRIMARY KEY AUTOINCREMENT, asset_class TEXT, name TEXT, path TEXT, file_name TEXT, file_type TEXT, text_metadata TEXT)")
        conn.commit()
        conn.close()
        return True
    
    def fix_erroneous_paths(self):
        #run this function every so often to fix erroneous paths in the asset directories

        # create directories if they don't exist
        if not os.path.exists(self.image_assets_directory):
            os.makedirs(self.image_assets_directory)
        if not os.path.exists(self.audio_assets_directory):
            os.makedirs(self.audio_assets_directory)
        if not os.path.exists(self.video_assets_directory):
            os.makedirs(self.video_assets_directory)
        if not os.path.exists(self.user_assets_directory):
            os.makedirs(self.user_assets_directory)
        
        # fix erroneous paths
        for image_asset_path in self.image_assets_directory.iterdir():
            asset_file_type = FileDataProcessor(image_asset_path).get_media_asset_type()
            if (asset_file_type == "audio"):
                #move audio to audio_assets directory
                shutil.move(image_asset_path, self.audio_assets_directory / os.path.basename(image_asset_path))
                return self.audio_assets_directory / os.path.basename(image_asset_path)
            if (asset_file_type == "video"):
                #move video to video_assets directory
                shutil.move(image_asset_path, self.video_assets_directory / os.path.basename(image_asset_path))
                return self.video_assets_directory / os.path.basename(image_asset_path)
            else:
                return image_asset_path
        for audio_asset_path in self.audio_assets_directory.iterdir():
            asset_file_type = FileDataProcessor(audio_asset_path).get_media_asset_type()
            if (asset_file_type == "image"):
                #move image to image_assets directory
                shutil.move(audio_asset_path, self.image_assets_directory / os.path.basename(audio_asset_path))
                return self.image_assets_directory / os.path.basename(audio_asset_path)
            if (asset_file_type == "video"):
                #move video to video_assets directory
                shutil.move(audio_asset_path, self.video_assets_directory / os.path.basename(audio_asset_path))
                return self.video_assets_directory / os.path.basename(audio_asset_path)
            else:
                return audio_asset_path
        for video_asset_path in self.video_assets_directory.iterdir():
            asset_file_type = FileDataProcessor(video_asset_path).get_media_asset_type()
            if (asset_file_type == "image"):
                #move image to image_assets directory
                shutil.move(video_asset_path, self.image_assets_directory / os.path.basename(video_asset_path))
                return self.image_assets_directory / os.path.basename(video_asset_path)
            if (asset_file_type == "audio"):
                #move audio to audio_assets directory
                shutil.move(video_asset_path, self.audio_assets_directory / os.path.basename(video_asset_path))
                return self.audio_assets_directory / os.path.basename(video_asset_path)
            else:
                return video_asset_path
        return True

    # Store Paths, Not Files
    def save_asset_to_sqlite(self, asset_path):
        if self.user_assets_directory in asset_path:
            asset_class = "user_assets"
        
        asset_name = os.path.basename(asset_path)
        conn = sqlite3.connect(self.user_assets_directory)
        cursor = conn.cursor()

        asset_metadata = FileDataProcessor(asset_path).get_media_asset_metadata()
        if asset_metadata is None:
            # Log error
            print(f"Could not get media asset metadata: {asset_path}")
            return False
        
        asset_file_name = asset_metadata["file_name"]
        asset_file_type = asset_metadata["file_type"]
        asset_text_metadata = asset_metadata["text_metadata"]

        if asset_file_type is None:
            # Log error
            print(f"Could not get media asset type: {asset_path}")
            return False
        if not os.path.exists(asset_path):
            # Log error
            print(f"File not found: {asset_path}")
            return False

        if is_user_asset:
            asset_class = "user_assets"
        else:
            if asset_file_type == "image":
                asset_class = "image_assets"
            elif asset_file_type == "audio":
                asset_class = "audio_assets"
            elif asset_file_type == "video":
                asset_class = "video_assets"
            else:
                # Log error
                print(f"Could not get media asset type: {asset_path}")
                return False
        if asset_class is None:
            # Log error
            print(f"Asset class is required: {asset_path}")
            return False
        if asset_name is None:
            # Log error
            print(f"Asset name is required: {asset_path}")
            return False
        if asset_path is None:
            # Log error
            print(f"Asset path is required: {asset_path}")
            return False
        if asset_file_name is None:
            # Log error
            print(f"Asset file name is required: {asset_path}")
            return False
        if asset_file_type is None:
            # Log error
            print(f"Asset file type is required: {asset_path}")
            return False
        if asset_text_metadata == "" or asset_text_metadata is None or asset_text_metadata == {}:
            # Null value is allowed
            asset_text_metadata = "{}"
        # Convert asset_text_metadata to string if it is not a string
        if not isinstance(asset_text_metadata, str):
            asset_text_metadata = str(asset_text_metadata)
        cursor.execute(
            "INSERT INTO assets (asset_class, name, path, file_name, file_type, text_metadata) VALUES (?, ?, ?, ?, ?, ?)", 
            (asset_class, asset_name, asset_path, asset_file_name, asset_file_type, asset_text_metadata))
        conn.commit()
        conn.close()
        return asset_metadata
    
    def save_user_asset_to_sqlite(self, asset_path):
        self.save_asset_to_sqlite("user_assets", asset_path, True)
        return True
    
    def save_image_asset_to_sqlite(self, asset_path):
        self.save_asset_to_sqlite("image_assets", asset_path, False)
        return True
    
    def save_audio_asset_to_sqlite(self, asset_path):
        self.save_asset_to_sqlite("audio_assets", asset_path, False)
        return True
    
    def save_video_asset_to_sqlite(self, asset_path):
        self.save_asset_to_sqlite("video_assets", asset_path, False)
        return True
    
    def save_all_assets_to_sqlite(self):
        self.save_user_asset_to_sqlite(self.user_assets_directory)
        self.save_image_asset_to_sqlite(self.image_assets_directory)
        self.save_audio_asset_to_sqlite(self.audio_assets_directory)
        self.save_video_asset_to_sqlite(self.video_assets_directory)
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

