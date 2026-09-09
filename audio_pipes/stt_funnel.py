import re
from faster_whisper import WhisperModel
#from sentence_transformers import SentenceTransformer
#import numpy as np
#from sklearn.metrics.pairwise import cosine_similarity
import nltk
from pydub import AudioSegment
from pydub.utils import make_chunks  # Optional for finer control
import json
from embed_funnel import EmbedFunnel #, ModelType, ALLOWED_EMBED_MODELS

nltk.download('punkt', quiet=True)

def transcribe_with_timestamps(audio_path: str, model_size: str = "base", device: str = "cpu") -> tuple[list[dict], float]:
    """Transcribe and return segments with timestamps."""
    model = WhisperModel(model_size, device=device, compute_type="int8" if device == "cpu" else "float16")
    segments, info = model.transcribe(
        audio_path,
        beam_size=5,
        word_timestamps=True,   # Enables word-level (falls back gracefully)
        language=None
    )
    print(f"Detected language: {info.language} (prob: {info.language_probability:.2f})")
    return list(segments), info.duration  # segments have .start, .end, .text, .words

def sentences_with_timestamps(segments: list[dict]) -> list[dict[str, float | str]]:
    """Group into sentences while preserving approximate time ranges."""
    sentences = []
    current_text = []
    current_start = None
    current_end = None
    
    for seg in segments:
        if not current_start:
            current_start = seg.start
        current_end = seg.end
        current_text.append(seg.text.strip())
        
        # Simple sentence boundary detection
        if any(p in seg.text for p in '.!?'):
            full_text = " ".join(current_text).strip()
            if full_text:
                sentences.append({
                    "text": full_text,
                    "start": current_start,
                    "end": current_end,
                    #"segment": seg  # Keep reference if needed
                })
            current_text = []
            current_start = None
    
    # Add any remaining
    if current_text:
        full_text = " ".join(current_text).strip()
        if full_text:
            sentences.append({
                "text": full_text,
                "start": current_start,
                "end": current_end
            })
    return sentences

def transcribed_sentences_to_json(transcribed_sentences: list[dict[str, float | str]]) -> list[dict[str, float | str]]:
    """Convert transcribed sentences to JSON-serializable dicts."""
    return [
        {
            "text": s["text"].strip(),
            "timestamps": [round(s["start"], 2), round(s["end"], 2)],
        }
        for s in transcribed_sentences
    ]

def deduplicate_with_times(
    sentences: list[dict[str, float | str]], 
    threshold: float = 0.88, 
    remove_similar_sentences: bool = False, 
    sentence_embed_model_id: str = None
    ) -> list[dict[str, float | str]]:
    """Remove similar sentences, keep timestamps of retained ones."""
    if sentence_embed_model_id is None:
        print("Sentence embedding model name is not provided")
        return sentences
    
    if not sentences:
        print("No sentences to deduplicate")
        return []

    if remove_similar_sentences == False:
        print("Removing similar sentences is disabled")
        return sentences
    
    if len(sentences) == 0:
        print("No sentences to deduplicate")
        return []
    

    #remove_similar_sentences == True and sentences is not empty case:
    texts = [s["text"] for s in sentences]
    embed_model = EmbedFunnel(sentence_embed_model_id)
    embeddings = embed_model.get_embeddings(texts)
    sim_matrix = embed_model.get_similarity_matrix(embeddings)
    
    to_keep = []
    removed = set()
    
    for i in range(len(sentences)):
        if i in removed:
            continue
        keep = True
        for j in range(i + 1, len(sentences)):
            if sim_matrix[i][j] > threshold:
                removed.add(j)
                keep = False  # Could keep longer one instead
                break
        if keep:
            to_keep.append(sentences[i])
    
    print(f"Kept {len(to_keep)} / {len(sentences)} unique segments")
    return to_keep

def create_cleaned_audio(original_audio_path: str, kept_segments: list[dict[str, float | str]], output_path: str = "cleaned_audio.mp3") -> str:
    """Extract and concatenate kept segments."""
    audio = AudioSegment.from_file(original_audio_path)
    
    cleaned = AudioSegment.empty()
    for seg in kept_segments:
        start_ms = int(seg["start"] * 1000)
        end_ms = int(seg["end"] * 1000)
        chunk = audio[start_ms:end_ms]
        cleaned += chunk  # Simple concat; add crossfade if desired
    
    cleaned.export(output_path, format="mp3")
    print(f"Cleaned audio saved to: {output_path}")
    return output_path

# === Usage ===
if __name__ == "__main__":
    audio_file = "data/feudalism.mp3"
    #audio_file = "data/kennedy-nuclear-test.mp3"
    with open("settings.json", "r", encoding="utf-8") as f:
        settings = json.load(f)
    remove_similar_sentences = settings["stt_settings"]["remove_similar_sentences"]
    sentence_similarity_threshold = settings["stt_settings"]["sentence_similarity_threshold"]
    sentence_embed_model_id = settings["stt_settings"]["sentence_embed_model_id"]
    model_size = settings["stt_settings"]["model_size"]
    device = settings["stt_settings"]["device"]

    segments, duration = transcribe_with_timestamps(audio_file, model_size=model_size, device=device)  # or "cpu"
    sentences = sentences_with_timestamps(segments)
    sentences_json = transcribed_sentences_to_json(sentences)

    print(sentences_json)
    with open("data/sentences.json", "w", encoding="utf-8") as f:
        json.dump(sentences_json, f, ensure_ascii=False, indent=4)

    print(f"Original: {len(sentences)} sentences, ~{duration:.1f}s")

    kept = deduplicate_with_times(
        sentences,
        threshold=sentence_similarity_threshold,
        remove_similar_sentences=remove_similar_sentences,
        sentence_embed_model_id=sentence_embed_model_id,
    )

    create_cleaned_audio(audio_file, kept, "data/cleaned_speech.mp3")

    # Optional: Save cleaned transcript with times
    with open("data/cleaned_transcript.txt", "w", encoding="utf-8") as f:
        for s in kept:
            f.write(f"[{s['start']:.2f}-{s['end']:.2f}s] {s['text']}\n")