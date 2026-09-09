import requests
import os
import json
import base64
from pathlib import Path
from PIL import Image

from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

def encode_image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        try:
            return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            raise ValueError(f"Failed to encode image to base64: {image_path}") from e
        finally:
            image_file.close()

def encode_image_to_data_url(image_path: str) -> str:
    #https://openrouter.ai/docs/guides/overview/multimodal/image-understanding
    image_types_allowed = ["jpg", "jpeg", "png", "gif", "webp"]
    image_extension = image_path.split(".")[-1]
    if image_extension not in image_types_allowed:
        raise ValueError(f"Image type not allowed: {image_extension}")
    
    if image_extension == "jpg":
        image_type = "jpeg"
    else:
        image_type = image_extension

    base64_image = encode_image_to_base64(image_path)
    return f"data:image/{image_type};base64,{base64_image}"

def VL_embed(text: str, image_path: str):
    response = requests.post(
    "https://openrouter.ai/api/v1/embeddings",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    },
    json={
        "model": "qwen/qwen3-embedding-8b",
        "input": [
        {
            "content": [
            {"type": "text", "text": text},
            {"type": "image_url", "image_url": {"url": encode_image_to_data_url(image_path)}}
            ]
        }
        ],
        "encoding_format": "float",
    }
    )
    if response.status_code != 200:
        raise ValueError(f"Failed to get embedding: {response.status_code} {response.text}")

    data = response.json()
    embedding = data["data"][0]["embedding"]
    print(f"Embedding dimension: {len(embedding)}")
    return embedding

def VL_embed_image(image_path: str):
    response = requests.post(
    "https://openrouter.ai/api/v1/embeddings",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    },
    json={
        "model": "qwen/qwen3-embedding-8b",
        "input": [
        {
            "content": [
            {"type": "image_url", "image_url": {"url": encode_image_to_data_url(image_path)}}
            ]
        }
        ],
        "encoding_format": "float",
    }
    )
    if response.status_code != 200:
        raise ValueError(f"Failed to get embedding: {response.status_code} {response.text}")

    data = response.json()
    embedding = data["data"][0]["embedding"]
    print(f"Embedding dimension: {len(embedding)}")
    return embedding

def VL_embed_text(text: str):
    response = requests.post(
    "https://openrouter.ai/api/v1/embeddings",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    },
    json={
        "model": "qwen/qwen3-embedding-8b",
        "input": [
        {
            "content": [
            {"type": "text", "text": text}
            ]
        }
        ],
        "encoding_format": "float",
    }
    )
    if response.status_code != 200:
        raise ValueError(f"Failed to get embedding: {response.status_code} {response.text}")

    data = response.json()
    embedding = data["data"][0]["embedding"]
    print(f"Embedding dimension: {len(embedding)}")
    return embedding