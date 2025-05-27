# CLIPSemanticImageArithmetics

A demonstration of vector arithmetic for visual and textual semantic search in an image archive.

Because: _KING - MAN + WOMAN  = QUEEN_

![image](https://github.com/user-attachments/assets/aa8d05f9-fb55-4def-9625-a5551335e5c8)




## Overview

This repository showcases how vector arithmetic can be applied to perform semantic searches through both visual and textual queries in an image database. The system allows users to combine search criteria using arithmetic operations (addition and subtraction) to create complex semantic queries.
I have used the **AI** ​​LLM extensively in producing this documentation and developing the main python frontend parts for this project... and I have to say, "**it works**"!

ref.: https://www.youtube.com/watch?v=r6TJfGUhv6s

## Components

The repository contains three main components:

1. **curlretrieve.py**  
   A utility tool that downloads images from the WikiArt dataset.

2. **insertwikiart.py**  
   A Python script that processes an input list of image files (from stdin), generates their embeddings, and stores them as vectors in Redis.

3. **app.py**  
   The core search application that enables users to:  
   - Input search criteria  text, uploaded image, indexed image
   - Combine criteria using + arithmetic operations (but you can use negative factor in order to make substractions)  
   - Perform semantic searches based on these combinations  

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/vagrillo/CLIPSemanticImageArithmetics.git
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


## Requirements

- Python 3.x
- Redis
- CLIP model (will be automatically downloaded)
- Other dependencies listed in requirements.txt
