from moviepy import *
from pydub import AudioSegment

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
    
    def remove_silence(self, audio_clip, silence_thresh=-40, min_silence_len=500, buffer_ms=200):
        audio_segment = AudioSegment.from_mp3(audio_clip)
        audio_segment = audio_segment.strip_silence(silence_thresh=silence_thresh, min_silence_len=min_silence_len)
        audio_segment.export(self.audio_output_path, format="mp3")
        return audio_segment
    
    def normalize_audio(self, audio_clip):
        audio_segment = AudioSegment.from_mp3(audio_clip)
        audio_segment = audio_segment.normalize()
        audio_segment.export(self.audio_output_path, format="mp3")
        return audio_segment
