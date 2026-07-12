# peyote-speech2video

Processing pipeline for turning input speech into full video. Can't capture every nuance of video editing but we'll try to get a majority of the busy work done.

We'll use singular embedding models here to embed text/images/video into just one embedding model at a time. The first will be a text/image only embedding model like Clip to produce videos with static images, this will be for more casual and demonstrative use. The 2nd will use an text/images/video embedding model in order to incorporate video, this will be the Proper albeit more computationally intensive use. 

We dont use audio embeddings because this is intended for narration. If I'm narrating a documentary about animals and my dog barks in the background of an audio clip it could erroneously bias that segment towards the dog embeddings even if that particular segment is supposed to be about Zebras.

```mermaid
graph TD;
    A1(["Upload Speech"])-->B0{"Audio Preprocessing: remove long silences, normalize loudness if needed."};
    B0-->B1{"Speech to Text processing with timestamps"}
    B1-->B2{"Text/Image/Video Embeddings generated."};
    B2-->B3{Also generate text embeddings from file names and file textual metadata."}
    A2(["Optional: Upload images"])-->B2;
    A3(["Optional: Upload videos"])-->B2;

    B1-->C1["Flag and remove overly similar neighboring sentences. Remove the first sentence as the latter is likely a correction."]
    C1-->C2["Remove STOP words and k sentences before the STOP word for which there is a similar sentence in range k+10 after the STOP word."]
    B2-->C1;
    
    PARAM1(["Optional: Adjust Speech Sentence Similarity Thresholds"])-->B1;
    PARAM2(["Optional: Set STOP words"])-->B1;
    PARAM3(["Optional:Set generate_images==True"])-->B2;
    PARAM4(["Optional:Set min_visual_change_time or min_visual_change_num_sentences. Minimum time/numberof sentences any visual has to stay on screen. This prevents the visuals from changing too fast. "])-->B2;

```

### STOP words 

Remove STOP words and k sentences before the STOP word for which there is a similar sentence in range k+10 after the STOP word. We can assume that if a similar sentence is retreaded in ~ 1 paragraph after the STOP word then that new sentence is intended to replace the original. 

`kthres= 10` will be the default, adjust as needed. 