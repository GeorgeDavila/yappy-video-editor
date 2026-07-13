# Automatic Speech2Video video editing pipeline

Processing pipeline for turning input speech into full video. Can't capture every nuance of video editing but we'll try to get a majority of the busy work done.

We'll use singular embedding models here to embed text/images/video into just one embedding model at a time. The first will be a text/image only embedding model like Clip to produce videos with static images, this will be for more casual and demonstrative use - can suffice for many use cases and more devices. The 2nd will use an text/audio/images/video embedding model in order to incorporate video, this will be the Proper albeit more computationally intensive use.

We dont use audio embeddings because this is intended for narration. If I'm narrating a documentary about animals and my dog barks in the background of an audio clip it could erroneously bias that segment towards the dog embeddings even if that particular segment is supposed to be about Zebras.

```mermaid
graph TD;
    %% mermaid chart docs: https://mermaid.js.org/syntax/flowchart.html
    AUDIO_UPLOAD(["Upload Speech"])-->SPEECH_DATA[("User Speech MP3")]
    
    %% doesn't need to be a facecam video, just a common example
    FACECAM_UPLOAD(["Optional: Upload Speech with video/facecam"])-->FACECAM_DATA["Facecam File"]
    FACECAM_DATA-->FACECAM_SPLIT["Split audio from video, keep time aligned"]
    FACECAM_SPLIT--Speech MP3-->SPEECH_DATA
    FACECAM_SPLIT--Visual only MP4-->FACECAM_VISUAL_DATA[("Facecam MP4")]

    SPEECH_DATA-->AUDIO_PREPROCESSING{"Audio Preprocessing: remove long silences, normalize loudness if needed. May run Background noise removal (models fairly light like as low as 8mb) maybe include a bool for this as an option in case gives errors."};
    %% AUDIO_UPLOAD-->EMBED_AUDIO_INIT{"Audio Embeddings Generated."};
    AUDIO_PREPROCESSING-->STT_MODEL{"Speech to Text processing with timestamps"}
    STT_MODEL==Sentence/Timestamp Dictionary==>EMBED_TEXT{"Text Embeddings Generated."};
    
    IMAGE_UPLOAD(["Optional: Upload image assets"])-->VISUAL_FILE_DATA_EXTRACTION["Extract file name and textual metadata"];
    VIDEO_UPLOAD(["Optional: Upload video assets"])-->VISUAL_FILE_DATA_EXTRACTION;
    VISUAL_FILE_DATA_EXTRACTION-->VISUAL_DATA[("Visual Assets Data")];
    VISUAL_DATA-->EMBED_IMAGE_VIDEO{"Image/Video Embeddings Generated. Generate text embeddings from Image/Video file names and file textual metadata."};

    EMBED_TEXT==Sentence/Timestamp/Text Embeds Dictionary==>AUDIO_SIMILARITY["Flag and remove overly similar neighboring sentences. Remove the first sentence as the latter is likely a correction."];
    AUDIO_SIMILARITY-->AUDIO_STOP["Remove STOP words and k sentences before the STOP word for which there is a similar sentence in range STOP_thresh after the STOP word."];

    %% AUDIO_STOP-->AUDIO_AGENT["Now that we have our core audio we can inject prompts into the pipeline to remove unwanted topics or whatever"];
    
    AUDIO_STOP-->AUDIO_CLIPPING["Use the timestamps to create a separate audio clip for each selected sentence"];
    AUDIO_CLIPPING-->EMBED_AUDIO{"Audio Embeddings Generated for each sentence clipping."};
    EMBED_AUDIO==Sentence/Timestamp/Text Embeds/Audio Embeds Dictionary==>AUDIO_ANALYSIS["Analyze audio embeddings for potential audio distortions, static, background noise, etc. Remove intolerable clips."]

    AUDIO_ANALYSIS-->AUDIO_POSTPROCESSING["Recombine audio clips into a single audio file, normalize audio. Recombine these with the initial facecam video, if one was included. After reconstruction is done, transform timestamps to fit their new places."];
    FACECAM_VISUAL_DATA-->AUDIO_POSTPROCESSING
    
    %% can technically do audio embed matching too here if it solves some issues but textual embeds should be focus for reasons mentioned elsewhere
    
    AUDIO_POSTPROCESSING-->MP3[("Post MP3 File")];
    AUDIO_POSTPROCESSING-->MP4[("Post MP4 File")];
    AUDIO_POSTPROCESSING==Sentence/Embed dict with NEW Timestamps==>EMBED_MATCHING["Match sentence embeds to image/video. Maybe have a matching_threhold to encourage video use if the video is close enough. Create rankings according to Control Params & Rules"];

    MP3-.IF NO VISUALS were provided generate a blank image to make an mp4.->DONE;
    MP4-.if only visual is facecam.->DONE;

    MP3-->MOVIE_MAKING;
    MP4--put facecam in corner-->MOVIE_MAKING

    EMBED_IMAGE_VIDEO==Visual filenames/Visual Embeds/Video Length/ File data textual embeds Dictionary==>EMBED_MATCHING;

    EMBED_MATCHING-->MOVIE_MAKING["Combine the audio and visuals according to embed rankings and Control Params & Rules"];

    MOVIE_MAKING-->DONE(("DONE!"));
    
    PARAM1(["Optional: Set custom speech sentence similarity thresholds"])-.->AUDIO_SIMILARITY;
    PARAM2(["Optional: Set STOP words"])-.->AUDIO_STOP;
    PARAM3(["Optional:Set generate_images==True"])-.->MOVIE_MAKING;
    PARAM4(["Optional:Set min_visual_change_time or min_visual_change_num_sentences. Minimum time/numberof sentences any visual has to stay on screen. This prevents the visuals from changing too fast. "])-.->MOVIE_MAKING;

```

Write to some xml standard if we can. If no standard is wide enough just output the vid and clips. 

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