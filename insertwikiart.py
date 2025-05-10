from sentence_transformers import SentenceTransformer
from PIL import Image
import time
import torch
torch.set_num_threads(1)  # Limit PyTorch to use only 1 thread
import redis
import os, sys, re
from io import BytesIO

# Initialize Redis client connection
redis_client = redis.Redis(host='localhost', port=6380, db=0, decode_responses=True, encoding='utf-8')

import os
import requests
from PIL import Image
from io import BytesIO

# Redis collection name for storing CLIP embeddings
collection = "wikiartCLIP"

def add_to_redis(key, embedding):
    """
    Add embedding to Redis using custom VADD command
    
    Args:
        key (str): The identifier for this embedding (typically filename)
        embedding (list): The CLIP embedding vector to store
    """
    args = ["VADD", collection, "VALUES", str(len(embedding))]
    args.extend(map(str, embedding))
    args.append(key)
    redis_client.execute_command(*args)

def is_indexed(filename):
    """
    Check if a file already has an embedding in Redis
    
    Args:
        filename (str): File to check
        
    Returns:
        bool: True if file is already indexed, False otherwise
    """
    args = ["VEMB", collection, filename]
    out = redis_client.execute_command(*args)
    if out == None:
        return False
    return True

def is_valid_jpg_strict(filename):
    """
    Validate that a file is a proper JPEG image
    
    Args:
        filename (str): Path to image file
        
    Returns:
        bool: True if valid JPEG, False otherwise
    """
    if filename is None:
        return False
    try:
        with Image.open(filename) as img:
            return img.format in ('JPEG', 'JPG')
    except (IOError, OSError):
        return False

# Load the CLIP model (ViT-B/32 variant)
model = SentenceTransformer("clip-ViT-B-32")

def generate_CLIP_embedding(filename):
    """
    Generate CLIP embedding for an image file if it's not already indexed
    
    Args:
        filename (str): Path to image file
        
    Returns:
        numpy.ndarray or bool: The CLIP embedding if successful, False if not
    """
    if filename is None:
        return False
    if is_indexed(filename):
        print(f"#{filename} ALREADY INDEXED!")
        return False
    if is_valid_jpg_strict(filename):
        return model.encode(Image.open(filename), use_fast=True)
    else:
        return False

def main():
    """
    Main processing function - reads filenames from stdin and processes them
    """
    items = []
    for line in sys.stdin:
        filename = line.strip()
        emb = generate_CLIP_embedding(filename)
        if (emb is not False):
            print(f"Indexing {filename}")
            add_to_redis(filename, emb)

if __name__ == "__main__":
    main()
