# CLIPSemanticImageArithmetics

A demonstration of vector arithmetic for visual and textual semantic search in an image archive.

## Overview

This repository showcases how vector arithmetic can be applied to perform semantic searches through both visual and textual queries in an image database. The system allows users to combine search criteria using arithmetic operations (addition and subtraction) to create complex semantic queries.

## Components

The repository contains three main components:

1. **curlretrieve.py**  
   A utility tool that downloads images from the WikiArt dataset.

2. **insertwikiart.py**  
   A Python script that processes an input list of image files (from stdin), generates their embeddings, and stores them as vectors in Redis.

3. **app.py**  
   The core search application that enables users to:  
   - Input search criteria  
   - Combine criteria using arithmetic operations (+, -)  
   - Perform semantic searches based on these combinations  

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/CLIPSemanticImageArithmetics.git
   cd CLIPSemanticImageArithmetics
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure you have Redis running locally or configure the connection settings.

## Usage

1. **Download images** (optional if you have your own dataset):
   ```bash
   python curlretrieve.py
   ```

2. **Process images and store embeddings**:
   ```bash
   ls /path/to/images/*.jpg | python insertwikiart.py
   ```

3. **Run the search application**:
   ```bash
   python app.py
   ```

## Search Syntax

The search application supports vector arithmetic operations:
- `+` combines concepts (e.g., "sun" + "beach")
- `-` excludes concepts (e.g., "portrait" - "man")
- Combine multiple operations (e.g., "landscape" + "sunset" - "city")

## Examples

- Find images that combine the concepts of water and sky:
  ```
  water + sky
  ```

- Find portrait images excluding male subjects:
  ```
  portrait - man
  ```

- Complex query combining multiple concepts:
  ```
  landscape + sunset - city + mountain
  ```

## Requirements

- Python 3.x
- Redis
- CLIP model (will be automatically downloaded)
- Other dependencies listed in requirements.txt
