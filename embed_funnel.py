import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from enum import Enum

class ModelType(Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"

ALLOWED_MODELS = {
    "all-MiniLM-L6-v2": [ModelType.TEXT],
    "Qwen3-VL-Embedding-2B": [ModelType.TEXT, ModelType.IMAGE, ModelType.VIDEO],
    "Qwen3-VL-Embedding-8B": [ModelType.TEXT, ModelType.IMAGE, ModelType.VIDEO],
    "e5-omni-3B": [ModelType.TEXT, ModelType.AUDIO, ModelType.IMAGE, ModelType.VIDEO],
    "e5-omni-7B": [ModelType.TEXT, ModelType.AUDIO, ModelType.IMAGE, ModelType.VIDEO],
}

class EmbedFunnel:
    def __init__(self, embed_model_id: str):
        self.embed_model_id = embed_model_id
        self.model = SentenceTransformer(self.embed_model_id)
        self.model_types: list[ModelType] = []
        self.batch_size = 32
        self.show_progress_bar = True
        self.print_embeddings_shape = True
        if self.embed_model_id is not None:
            self.validate_model() # Validate model is allowed

    def validate_model(self) -> None:
        if self.embed_model_id not in ALLOWED_MODELS:
            raise ValueError(
                f"Model {self.embed_model_id} is not allowed. "
                f"Allowed models: {list(ALLOWED_MODELS)}"
            )
        self.model_types = ALLOWED_MODELS[self.embed_model_id] #this is a list of ModelType enums
        print(f"Model {self.embed_model_id} supports the following data types: {self.model_types}")
        if len(self.model_types) == 0:
            raise ValueError(
                f"Model {self.embed_model_id} does not support any data types. "
                f"Allowed models: {list(ALLOWED_MODELS)}"
            )

    def get_embeddings(self, data2embed: list[str | dict] | str | dict) -> np.ndarray:
        if not isinstance(data2embed, list):
            #if it's a solo object thats not a list, convert it to a list
            data2embed = [data2embed]
        return self.model.encode(data2embed, batch_size=self.batch_size, show_progress_bar=self.show_progress_bar)

    def get_similarity(self, embeddings1: np.ndarray, embeddings2: np.ndarray) -> np.ndarray:
        return cosine_similarity(embeddings1, embeddings2)

    def get_similarity_matrix(self, list_of_embeddings: list[np.ndarray]) -> np.ndarray:
        return cosine_similarity(list_of_embeddings)

    def sim_matrix_query_doc(self, queries: list[str], documents: list[str]) -> np.ndarray:
        # Encode queries and documents
        query_embeddings = self.get_embeddings(queries)
        doc_embeddings = self.get_embeddings(documents)
        if self.print_embeddings_shape:
            print(query_embeddings.shape, doc_embeddings.shape)

        return cosine_similarity(query_embeddings, doc_embeddings) #self.model.similarity(query_embeddings, doc_embeddings)
    
    def remove_similar_data(self, data2trim: list[str | dict], threshold: float = 0.88) -> list[str | dict]:
        embeddings = self.get_embeddings(data2trim)
        sim_matrix = self.get_similarity_matrix(embeddings)
        to_keep = []
        removed = set()
        for i in range(len(embeddings)):
            if i in removed:
                continue
            keep = True
            for j in range(i + 1, len(embeddings)):
                if sim_matrix[i][j] > threshold:
                    removed.add(j)
                    keep = False
                    break
            if keep:
                to_keep.append(data2trim[i])
        print(f"Kept {len(to_keep)} / {len(data2trim)} unique data")
        return to_keep
    
    def remove_bad_audio_data(
        self, 
        audio_data: list[str],
        bad_audio_similarity_threshold: float = 0.97
    ) -> list[str]:
        if self.model_types != [ModelType.AUDIO]:
            raise ValueError(
                f"Model {self.embed_model_id} does not support audio data. "
                #f"Audio models supported: {ALLOWED_MODELS.values()[ModelType.AUDIO.value]}"
            )
        
        queries = ["static audio", "bad audio", "white noise", "silence"]
        similarities = self.sim_matrix_query_doc(queries, audio_data)
        print(similarities)
        print(f"Max similarity: {similarities.max()}")
        print(f"bad_audio_similarity_threshold: {bad_audio_similarity_threshold}")
        if np.any(similarities > bad_audio_similarity_threshold):
            #checks if any value in the matrix is greater than the threshold - if none are, then all audio data is good
            print(f"All audio data is good")
            return audio_data
        else:
            to_keep = []
            for i in range(len(audio_data)):
                if similarities[:, i].max() < bad_audio_similarity_threshold:
                    to_keep.append(audio_data[i])
            print(f"Kept {len(to_keep)} / {len(audio_data)} good audio data out of {len(audio_data)} total audio data")
            return to_keep

if __name__ == "__main__":
    model = EmbedFunnel("Qwen3-VL-Embedding-2B")
    queries = ["A woman playing with her dog on a beach at sunset.", "Pet owner training dog outdoors near water.", "Woman surfing on waves during a sunny day.", "City skyline view from a high-rise building at night."]
    documents = ["A woman shares a joyful moment with her golden retriever on a sun-drenched beach at sunset, as the dog offers its paw in a heartwarming display of companionship and trust.", "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-VL/assets/demo.jpeg", {"text": "A woman shares a joyful moment with her golden retriever on a sun-drenched beach at sunset, as the dog offers its paw in a heartwarming display of companionship and trust.", "image": "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen-VL/assets/demo.jpeg"}]
    similarities = model.sim_matrix_query_doc(queries, documents)
    print(similarities)