import os
import requests
from PIL import Image
from io import BytesIO
import json
from urllib.parse import urlparse
import time

# Configuration
BASE_URL = "https://datasets-server.huggingface.co/rows?dataset=nroggendorff%2Fwikiart&config=default&split=train"

BATCH_SIZE = 100  # Number of items to process in each batch
MAX_FILES_PER_DIR = 2000  # Maximum files per directory before creating a new numbered directory
MAX_DIMENSION = 448  # Maximum dimension (width or height) for resized images
BASE_OUTPUT_DIR = "wikiart_images"  # Base directory for downloaded images
DELAY_BETWEEN_REQUESTS = 5  # Delay in seconds between requests to be polite to the server

# Create main directory if it doesn't exist
os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)

def download_image(url):
    """
    Download an image from the given URL and return it as a PIL Image object.
    
    Args:
        url (str): URL of the image to download
        
    Returns:
        Image: PIL Image object if successful, None otherwise
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for HTTP errors
        return Image.open(BytesIO(response.content))
    except Exception as e:
        print(f"Error downloading image {url}: {e}")
        return None

def resize_image(image):
    """
    Resize an image while maintaining aspect ratio, ensuring neither dimension exceeds MAX_DIMENSION.
    
    Args:
        image (Image): PIL Image object to resize
        
    Returns:
        Image: Resized PIL Image object if successful, None otherwise
    """
    try:
        # Calculate new dimensions while maintaining aspect ratio
        width, height = image.size
        if width > height:
            new_width = MAX_DIMENSION
            new_height = int(height * (MAX_DIMENSION / width))
        else:
            new_height = MAX_DIMENSION
            new_width = int(width * (MAX_DIMENSION / height))

        return image.resize((new_width, new_height), Image.LANCZOS)
    except Exception as e:
        print(f"Error resizing image: {e}")
        return None

def save_image(image, path):
    """
    Save an image to the specified path as JPEG with 85% quality.
    
    Args:
        image (Image): PIL Image object to save
        path (str): Destination path for the image
        
    Returns:
        bool: True if save was successful, False otherwise
    """
    try:
        image.save(path, "JPEG", quality=85)
        return True
    except Exception as e:
        print(f"Error saving image {path}: {e}")
        return False

def get_or_create_subdir(base_dir, subdir_name):
    """
    Get or create a subdirectory, creating numbered versions if directory has too many files.
    
    Args:
        base_dir (str): Parent directory path
        subdir_name (str): Name of subdirectory to create/find
        
    Returns:
        str: Path to the (possibly numbered) subdirectory
    """
    # Create numbered directory if base directory has too many files
    dir_path = os.path.join(base_dir, subdir_name)
    if os.path.exists(dir_path):
        files_count = len([f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))])
        if files_count >= MAX_FILES_PER_DIR:
            # Find first available number
            dir_num = 1
            while os.path.exists(f"{dir_path}_{dir_num}"):
                dir_num += 1
            dir_path = f"{dir_path}_{dir_num}"

    os.makedirs(dir_path, exist_ok=True)
    return dir_path

def process_batch(offset, artist_names, genre_names, style_names):
    """
    Process a batch of images from the dataset starting at the given offset.
    
    Args:
        offset (int): Starting index for the batch
        artist_names (list): List of artist names
        genre_names (list): List of genre names
        style_names (list): List of style names
        
    Returns:
        bool: True if batch was processed successfully, False otherwise
    """
    url = f"{BASE_URL}&offset={offset}&length={BATCH_SIZE}"
    print(f"Fetching batch from {offset} to {offset+BATCH_SIZE}...")

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if "rows" not in data:
            print("No rows found in batch")
            return False

        for row_data in data["rows"]:
            row_idx = row_data["row_idx"]
            row = row_data["row"]

            if "image" not in row or "src" not in row["image"]:
                print(f"Row {row_idx} doesn't contain a valid image")
                continue

            # Get category values
            artist_id = row.get("artist", 0)  # 0 = Unknown Artist
            genre_id = row.get("genre", 10)   # 10 = Unknown Genre
            style_id = row.get("style", -1)  # -1 = Unknown Style

            artist_name = artist_names[artist_id] if artist_id < len(artist_names) else "Unknown Artist"
            genre_name = genre_names[genre_id] if genre_id < len(genre_names) else "Unknown Genre"
            style_name = style_names[style_id] if 0 <= style_id < len(style_names) else "Unknown Style"

            # Create directory structure
            artist_dir = get_or_create_subdir(BASE_OUTPUT_DIR, artist_name)
            genre_dir = get_or_create_subdir(artist_dir, genre_name)
            style_dir = get_or_create_subdir(genre_dir, style_name)

            # File path
            file_path = os.path.join(style_dir, f"{row_idx}.jpg")

            # Skip if file already exists
            if os.path.exists(file_path):
                print(f"File {file_path} already exists, skipping")
                continue

            # Download and process image
            img_url = row["image"]["src"]
            image = download_image(img_url)
            if image is None:
                continue

            resized_image = resize_image(image)
            if resized_image is None:
                continue

            if save_image(resized_image, file_path):
                print(f"Saved {file_path}")
            else:
                continue

        return True

    except Exception as e:
        print(f"Error processing batch {offset}: {e}")
        return False

def get_category_names():
    """
    Fetch category names (artists, genres, styles) from the dataset API.
    
    Returns:
        tuple: (artist_names, genre_names, style_names) lists
    """
    try:
        response = requests.get("https://datasets-server.huggingface.co/first-rows?dataset=nroggendorff%2Fwikiart&config=default&split=train")
        response.raise_for_status()
        data = response.json()

        features = data["features"]
        artist_names = []
        genre_names = []
        style_names = []

        for feature in features:
            if feature["name"] == "artist":
                artist_names = feature["type"]["names"]
            elif feature["name"] == "genre":
                genre_names = feature["type"]["names"]
            elif feature["name"] == "style":
                style_names = feature["type"]["names"]

        return artist_names, genre_names, style_names

    except Exception as e:
        print(f"Error fetching category names: {e}")
        return [], [], []

def main():
    """
    Main function to orchestrate the downloading and processing of images.
    """
    # Get category names
    artist_names, genre_names, style_names = get_category_names()
    if not artist_names or not genre_names or not style_names:
        print("Unable to fetch category names, exiting")
        return

    print("Starting download...")
    offset = 16300
    while True:
        success = process_batch(offset, artist_names, genre_names, style_names)
        if not success:
            break

        offset += BATCH_SIZE
        time.sleep(30)  # Be polite to the server

if __name__ == "__main__":
    main()
