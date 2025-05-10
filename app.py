import os
import io
import base64
import redis
import datetime
import numpy as np
from PIL import Image
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from sentence_transformers import SentenceTransformer
import torch
torch.set_num_threads(1)

# Initialize Flask application
app = Flask(__name__)

# Load pre-trained CLIP models for image and text embeddings
# English-only CLIP model
model = SentenceTransformer("clip-ViT-B-32")
# Multilingual CLIP model (supports multiple languages) , i will use it for the query text embeddings
modelml = SentenceTransformer('sentence-transformers/clip-ViT-B-32-multilingual-v1')
# this two models works in the same vector space , the first one it's not multilingual 

# Connect to Redis server for vector similarity search
redis_client = redis.Redis(host='localhost', port=6380, decode_responses=True, encoding='utf-8')

# Configure thread settings for PyTorch
torch.set_num_threads(1)

# Configuration constants
PORT = 9977
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Increase maximum upload size (50MB)
app.config['MAX_FORM_MEMORY_SIZE'] = 50 * 1024 * 1024


def search_similar_vectors(collection: str, query_embedding: np.ndarray, topk: int):
    """
    Search for similar vectors in Redis using the given query embedding.
    
    Args:
        collection: Name of the Redis collection to search in
        query_embedding: The embedding vector to compare against
        topk: Number of top similar items to return
        
    Returns:
        List of similar items with their scores
        using Redis VSIM command that searches for vector similarities using HNSW antirez indexing
    """
    args = ["VSIM", collection, "VALUES", str(len(query_embedding))]
    args.extend(map(str, query_embedding))
    args.append("WITHSCORES")
    args.append("COUNT")
    args.append(topk)
    return redis_client.execute_command(*args)


def process_filename(key):
    """
    Extract relevant information from the filename/path.
    
    Args:
        key: The full path string
        
    Returns:
        Processed portion of the filename
    """
    return(key[18:].split('/')[0])


@app.route('/wikiartparam/', methods=['GET', 'POST'])
def index():
    """
    Main endpoint for handling search requests.
    Supports both GET (initial page load) and POST (search queries).
    """
    search_query = request.args.get('q', '')
    
    if request.method == 'POST':
        search_elements = []
        search_elements = request.form.getlist('search_elements[]')
        elements = []

        # Parse and process each search element (can be text or image)
        for element in search_elements:
            elem_type, *data = element.split('|')
            if elem_type == 'text':
                text, weight = data
                elements.append(('text', text, float(weight)))
            elif elem_type == 'image':
                img_data, weight = data
                elements.append(('image', img_data, float(weight)))

        combined_embedding = None

        # Generate embeddings for each element and combine them
        for elem in elements:
            elem_type, content, weight = elem

            if elem_type == 'text':
                # Use multilingual model for text embeddings
                embedding = modelml.encode(content) * weight
                print(f"## Processing text: {content} with weight {weight}")
            elif elem_type == 'image':
                if content.startswith('data:image'):
                    # Handle base64 encoded image from clipboard
                    img_data = content.split(',')[1]
                    print("Processing image from clipboard")
                    img = Image.open(io.BytesIO(base64.b64decode(img_data)))
                    embedding = model.encode([img])[0] * weight
                else:
                    print(f"Processing image from file: {content}")
                    if content[:17] == "../wikiart_images":
                        # Handle images from wikiart dataset ...  workaround for a wrong indexing  
                        img = Image.open(content[1:])
                    else:
                        # Handle uploaded images
                        img = Image.open(os.path.join(UPLOAD_FOLDER, secure_filename(content)))
                    embedding = model.encode([img])[0] * weight

            # Combine embeddings using weighted sum
            if combined_embedding is None:
                combined_embedding = embedding
            else:
                combined_embedding += embedding

        if combined_embedding is not None:
            # Normalize the combined embedding vector
            combined_embedding = combined_embedding / np.linalg.norm(combined_embedding)

            # Search for similar vectors in Redis
            results = search_similar_vectors("wikiartCLIP", combined_embedding, 30)

            # Format results for JSON response
            formatted_results = []
            for i in range(0, len(results), 2):
                key = results[i]
                score = float(results[i+1])
                filename = os.path.basename(key)
                fileinfo = process_filename(key)
                key = f"../{key}"
                formatted_results.append({
                    'key': key,
                    'filename': filename,
                    'score': score,
                    'epoch_info': fileinfo
                })

            return jsonify({'results': formatted_results})

        return jsonify({'error': 'No valid search elements provided'})

    # Render the template for GET requests
    return render_template('parameterwikiart.html', search_query=search_query)


@app.route('/wikiartparam/upload', methods=['POST'])
def upload():
    """
    Handle file uploads for search images.
    """
    print("Max content length:", app.config['MAX_CONTENT_LENGTH'])
    if 'file' in request.files:
        file = request.files['file']
        if file.filename != '':
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)

            try:
                # Save the uploaded file
                file.save(filepath)

                # Resize image if it's too large
                try:
                    img = Image.open(filepath)
                    if img.size[0] > 1024 or img.size[1] > 1024:
                        img.thumbnail((1024, 1024))
                        img.save(filepath)
                except Exception as e:
                    print(f"Error resizing image: {e}")

                return jsonify({'filename': filename})
            except Exception as e:
                return jsonify({'error': f'Error saving file: {str(e)}'}), 500

    return jsonify({'error': 'No file uploaded'}), 400


if __name__ == '__main__':
    # Start the Flask application
    app.run(host='0.0.0.0', port=PORT, debug=True)
