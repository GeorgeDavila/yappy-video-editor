from moviepy import *

class AudioProcessing:
    def __init__(self, audio_upload_path, audio_output_path):
        self.audio_upload_path = audio_upload_path
        self.audio_output_path = audio_output_path

    def merge_audio_clips(self, audio_clips):
        audio = concatenate_audioclips(audio_clips)
        audio.write_audiofile(self.audio_output_path)
        return audio
    
    def split_audio_into_clips(self, audio_clip, clip_duration):
        audio_clips = []
        for i in range(0, audio_clip.duration, clip_duration):
            audio_clips.append(AudioFileClip(audio_clip.subclip(i, i + clip_duration)))
        return audio_clips
    
    def split_audio_into_clips_by_exact_timestamps(self, audio_clip, timestamps):
        audio_clips = []
        for i in range(0, len(timestamps) - 1):
            audio_clips.append(
                [
                    i, 
                    audio_clip.subclip(timestamps[i], timestamps[i + 1]),
                    (timestamps[i], timestamps[i + 1])
                    ]
            )
        dict_audio_clips = {clip[0]: {"audio_clip": clip[1], "timestamps": clip[2]} for clip in audio_clips}
        return dict_audio_clips
    