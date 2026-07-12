# peyote-speech2video

Processing pipeline for turning input speech into full video

We'll use 2 singular embedding models here to embed text/images/video into just one embedding model at a time. The first will be a text/image only embedding model like Clip to produce videos with static images. The 2nd will use an text/images/video embedding model in order to incorporate video. 

We dont use audio embeddings because this is intended for narration. If I'm narrating a documentary about animals and my dog barks in the background of an audio clip it could erroneously bias that segment towards the dog embeddings even if that particular segment is supposed to be about Zebras.

```mermaid
graph TD;
    A1(["Upload Speech"])-->B1{"Speech to Text processing with timestamps"};
    B1-->B2{"Text/Image/Video Embeddings generated"};
    A2(["Optional: Upload images"])-->B2;
    A3(["Optional: Upload videos"])-->B2;
    
    PARAM1(["Optional: Adjust Speech Sentence Similarity Thresholds"])-->B1;
    PARAM2(["Optional: Set STOP words"])-->B1;
    PARAM3(["Optional:Set generate_images==True"])-->B2;
    PARAM4(["Optional:Set min_visual_change_time or min_visual_change_num_sentences. Minimum time/numberof sentences any visual has to stay on screen. This prevents the visuals from changing too fast. "])-->B2;

```
