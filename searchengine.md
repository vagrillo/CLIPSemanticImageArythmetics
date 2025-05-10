
# Semantic Image Search Engine

A Flask-based service that enables semantic search through an image database using multimodal embeddings (text and images) with weighted query combinations.

## Key Features

- **Multimodal Search**: Combine text and image queries in a single search
- **Weighted Elements**: Adjust influence of each query element with weights (-1 to +1)
- **Vector Arithmetic**: Uses vector addition and normalization for combined queries
- **Redis Backend**: Efficient similarity search using Redis as a vector database
- **Multilingual Support**: Works with text inputs in multiple languages

## How It Works

The system uses CLIP (Contrastive Language-Image Pretraining) models to create embeddings for:
- Text inputs (using multilingual CLIP model)
- Image inputs (using standard CLIP model)

Query elements are combined using vector arithmetic:
1. Each element (text/image) is converted to an embedding vector
2. Vectors are multiplied by their respective weights (-1 to +1)
3. All vectors are summed together
4. The combined vector is normalized
5. Redis performs similarity search to find closest matches

Negative weights allow for "negative prompts" (e.g., "find images unlike this one").

## Installation

1. Clone the repository:
   ```bash
   git clone [your-repository-url]
   cd [repository-name]
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure Redis server is running on port 6380

## Requirements

- Python 3.7+
- Redis server with RedisSearch module
- Key Python packages:
  - Flask
  - sentence-transformers
  - Pillow
  - numpy
  - redis-py

## API Endpoints

### Main Search Endpoint
`GET/POST /wikiartparam/`

**Parameters:**
- `q` (GET): Initial search query (optional)
- Form data (POST): Array of search elements in format `type|content|weight`

**Search element formats:**
- Text: `text|your query text|0.8`
- Image (file): `image|filename.jpg|0.5`
- Image (base64): `image|data:image/...|-0.3`

### File Upload Endpoint
`POST /wikiartparam/upload`

Accepts image files for use in searches. Returns the stored filename.

## Usage Examples

### Simple text search
```python
import requests

response = requests.post('http://localhost:9935/wikiartparam/', 
                         data={'search_elements[]': 'text|a sunny landscape|1.0'})
```

### Combined image and text search
```python
# Positive weight for similar images, negative weight for text to exclude
elements = [
    'image|sunset.jpg|0.7',
    'text|cloudy weather|-0.5'
]

response = requests.post('http://localhost:9935/wikiartparam/',
                         data={'search_elements[]': elements})
```

### Using base64 image
```javascript
// In a web application
const canvas = document.getElementById('myCanvas');
const imageData = canvas.toDataURL('image/jpeg');
fetch('http://localhost:9935/wikiartparam/', {
  method: 'POST',
  body: JSON.stringify({
    search_elements: [`image|${imageData}|0.9`]
  })
});
```

## Configuration

Edit these variables in the code:
- `PORT`: Service port (default: 9935)
- `UPLOAD_FOLDER`: Where to store uploaded images
- Redis connection settings

## Response Format

Successful searches return JSON with results sorted by similarity score:
```json
{
  "results": [
    {
      "key": "../path/to/image1.jpg",
      "filename": "image1.jpg",
      "score": 0.872,
      "epoch_info": "additional_data"
    },
    ...
  ]
}
```

## License

[Specify your license here]

## Acknowledgments

- Uses CLIP models from Sentence-Transformers
- Redis for vector similarity search
- Flask for web service framework
```

This README includes:
1. Clear description of the system's purpose and capabilities
2. Technical overview of how it works
3. Installation and setup instructions
4. API documentation with examples
5. Configuration options
6. Response format documentation
7. License placeholder
8. Acknowledgments

You may want to add:
- Screenshots of the interface if you have a frontend
- More detailed deployment instructions
- Information about the Redis data structure/schema
- Performance characteristics or benchmarks
- Any limitations of the system

