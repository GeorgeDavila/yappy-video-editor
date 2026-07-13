from moviepy import *
import sqlite3

facecam_upload_path = "facecam.mp4"
audio_upload_path = "audio.mp3"
facecam_output_path = "facecam_output.mp4"
audio_output_path = "audio_output.mp3"

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