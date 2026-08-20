# Automatic Speech2Video video editing pipeline

Processing pipeline for turning input speech into full video. Can't capture every nuance of video editing but we'll try to get a majority of the busy work done.

We'll use singular embedding models here to embed text/images/video into just one embedding model at a time. The first will be a text/image only embedding model like Clip to produce videos with static images, this will be for more casual and demonstrative use - can suffice for many use cases and more devices. The 2nd will use an text/audio/images/video embedding model in order to incorporate video, this will be the Proper albeit more computationally intensive use.

We dont use audio embeddings because this is intended for narration. If I'm narrating a documentary about animals and my dog barks in the background of an audio clip it could erroneously bias that segment towards the dog embeddings even if that particular segment is supposed to be about Zebras.

## Architecture Diagram

Animated line = default pathway. Red diamond = ML model inference. Green = possible starting points.


## Saving to XML / json
Write to some xml standard if we can. If no standard is wide enough just output the vid and clips. 

Write to json. E.g. {{'time', 'image', 'effect' .....}, {'time', 'audio', .....}}. From here we can write scripts to change to markdown language for other video editors or easy translation to straightup code for other preogrammatic editors. Keep audio/video/image assets in separate eleements even if they share exact same times - this allows easier portability to other editors and easier editing. 

## Setup 

```
pip install faster-whisper sentence-transformers nltk pydub numpy scikit-learn
# pydub needs FFmpeg installed on your system
```

### Background Noise removal models

https://huggingface.co/mlx-community/DeepFilterNet-mlx

https://build.nvidia.com/nvidia/bnr/modelcard

### Image/Video file metadata embeddings 
We embed textual metadata and filenames too so users can more easily use novel data in this pipeline. E.g. if they're talking about their dog named snowball they can just name the file after the dog so the pipeline can use the dog image when given only a name. 

Might want to weight these heavier if within a certain similarity distance. Or save additional snippets elsewhere if its sufficiently close to the embedding of a competing image. 


### Similarity

Remove similar sentences within a sentence distance `similarity_sentence_distance = 10` and/or time range `similarity_time_range = 20.0` (default number of seconds as a float)

### STOP words 

Remove STOP words and k sentences before the STOP word for which there is a similar sentence in range `STOP_thresh` after the STOP word. We can assume that if a similar sentence is retreaded in ~ 1 paragraph after the STOP word then that new sentence is intended to replace the original. 

`STOP_thresh= 10` will be the default, adjust as needed. 

### Control Params & Rules
`min_relevance` parameter to control how relevant a video/image needs to be before its shown. Only used when user provides and inital video. E.g. if a facecam is provided and we set a min_relevance then we'll only show the face cam unless the relevance threshold is met. 

`matching_threhold` - if a video embed is close enough to a higher ranking image embed use this to give preference to videos. Set to 0 to just have the top embed win even if its an image

`limit_uses_to_once=True` limits the usage of each visual item to 1 appearance

`min_visual_change_num_sentences` minimum number of sentences a visual must remain on screen. If `loop_videos=false` videos should still end if theyre shorter than this time

`min_visual_change_time` minimum time a visual must remain on screen. If `loop_videos=false` videos should still end if theyre shorter than this time

`cut_videos=False` Set to true to cutoff videos if a higher ranking embed starts. `min_visual_change_num_sentences` and `min_visual_change_time` will apply before this. 

`loop_videos=false` set to true to make videos loop to fill out the interval alotted. If false itll just move on to the next visual 


# Resources

## Models

### Embedding Models

* [Qwen3-VL-Embedding-8B](https://huggingface.co/Qwen/Qwen3-VL-Embedding-8B) - multimodal text/image/video embeds. Fairly high on current benchmarks. And qwen series has more community support.
* [Qwen3-VL-Embedding-2B](https://huggingface.co/Qwen/Qwen3-VL-Embedding-2B) - Lighter Qwen model fairly close to 8B on benchmarks. 
* [e5-omni-3B](https://huggingface.co/Haon-Chen/e5-omni-3B) - Multimodal embeds for text, images, audio, and video, adding Audio to pipeline. Built on Qwen2.5-Omni-3B so carries over lots of qwen pipeline. 
* [e5-omni-7B](https://huggingface.co/Haon-Chen/e5-omni-7B) - heavier e5 variant
* [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) - legacy but still good sentence embedding model

Multimodal Embedding Benchmark: https://huggingface.co/spaces/TIGER-Lab/MMEB-Leaderboard

### Speech-to-Text

We use `pip install faster-whisper` for speech transcription

### Restorative Audio Enhancement

We use [nineninesix/diamond-1.0](https://huggingface.co/nineninesix/diamond-1.0) for audio enhancement. The model purports "Diamond turns degraded audio into near-studio 44.1 kHz speech" and does seem to enhance audio from their examples. Although I personally don't have much of an ear for professional grad audio so you might want to split test yours.

This is on by default. Set `"restorative_audio_enhancement": false` in `settings.json` to turn this off.

We'll leave the original audio unadultered and simply append `_diamond_enhanced.mp3` to the audio file name if `"restorative_audio_enhancement": true` 


## Data

In this repo we'll use [feudalism.mp3](https://dn721507.ca.archive.org/0/items/historyofthemiddleages_2507_librivox/historyofthemiddleages_06_munro_128kb.mp3) from [internet archive](https://archive.org/details/historyofthemiddleages_2507_librivox)
## Datasets
* https://github.com/huggingface/dataspeech
* https://huggingface.co/datasets/MLCommons/peoples_speech
* https://github.com/thuhcsi/SpeechCraft
* https://github.com/google-deepmind/librispeech-long
* https://github.com/Yuan-ManX/ai-audio-datasets
* https://huggingface.co/datasets/nvidia/LongAudio

## Easy to use longform speeches
Search engines tend to make mp3's hard to find. Some resources here. 
* https://archive.org/details/audio
* https://www.csun.edu/science/ref/audio/index.html
* https://commons.wikimedia.org/wiki/Category:Audio_files_of_speeches