from moviepy import *

class VideoProcessing:
    def __init__(self, facecam_upload_path, audio_upload_path, facecam_output_path, audio_output_path):
        self.facecam_upload_path = facecam_upload_path
        self.audio_upload_path = audio_upload_path
        self.facecam_output_path = facecam_output_path
        self.audio_output_path = audio_output_path

    def split_video_from_audio(self):
        video = VideoFileClip(self.facecam_upload_path)
        audio, video = video.audio, video.without_audio()
        audio.write_audiofile(self.audio_output_path)
        video.write_videofile(self.facecam_output_path)
        return audio, video
    
    def merge_video_and_audio(self):
        video = VideoFileClip(self.facecam_output_path)
        audio = AudioFileClip(self.audio_output_path)
        video = video.set_audio(audio)
        video.write_videofile(self.facecam_upload_path)
        return video
    
    def merge_video_clips(self, video_clips):
        video = concatenate_videoclips(video_clips)
        video.write_videofile(self.facecam_output_path)
        return video
    
    def merge_audio_clips(self, audio_clips):
        audio = concatenate_audioclips(audio_clips)
        audio.write_audiofile(self.audio_output_path)
        return audio
    