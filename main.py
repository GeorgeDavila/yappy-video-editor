from audio_pipes.speech_enhance import enhance_audio
from audio_pipes.audioprocessing import AudioProcessing
from audio_pipes.stt_funnel import *
import json

settings = json.load(open("settings.json"))
remove_similar_sentences = 
sentence_similarity_threshold = 
sentence_embed_model_id = 

#use audio
audio_path = "data/feudalism.mp3"

# ========================audio preprocessing========================
audio_processing = AudioProcessing(audio_path)
#remove silences
audio_processing.remove_silence(audio_path)
#normalize audio
audio_processing.normalize_audio(audio_path)

flag_audio_as_changed: bool = False

# ========================split audio into sentences========================
segments, duration = transcribe_with_timestamps(
    audio_path, 
    model_size=settings["stt_settings"]["model_size"], 
    device=settings["stt_settings"]["device"]
    )
sentences = sentences_with_timestamps(segments)
sentences_json = transcribed_sentences_to_json(sentences)

write_transcribed_sentences_to_json(sentences_json, "data/sentences.json")

if settings["stt_settings"]["remove_similar_sentences"]:
    sentences = deduplicate_with_times(
            sentences,
            threshold=settings["stt_settings"]["sentence_similarity_threshold"],
            remove_similar_sentences=settings["stt_settings"]["remove_similar_sentences"],
            sentence_embed_model_id=settings["stt_settings"]["sentence_embed_model_id"],
        )
    flag_audio_as_changed = True
    #update audio path
    audio_path = create_cleaned_audio(audio_path, sentences, "data/cleaned_speech.mp3")



# ========================enhance after sentence-level editing (optional)========================
if settings["restorative_audio_enhancement"]:
    enhance_audio(audio_path, audio_path)
    flag_audio_as_changed = True
else:
    print("No enhancement needed")

if flag_audio_as_changed:
    # RE - PROCESSING
    #good practice to renormalize after enhancement or cutting out some sentences
    #remove silences
    audio_processing.remove_silence(audio_path)
    #normalize audio
    audio_processing.normalize_audio(audio_path)