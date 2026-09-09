from audio_pipes.speech_enhance import enhance_audio
import json

settings = json.load(open("settings.json"))
#use audio
audio_path = "data/feudalism.mp3"



#enhance at the sentence level
if settings["restorative_audio_enhancement"]:
    enhance_audio(audio_path, audio_path)
else:
    print("No enhancement needed")