# CLIPSemanticImageArithmetics

A demonstration of vector arithmetic for visual and textual semantic search in an image archive.

KING - MAN + WOMAN  = QUEEN

![image](https://github.com/user-attachments/assets/e772013d-77a8-4648-9c96-dd54ef8d8cee)




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
   - Input search criteria  text, uploaded image, indexed image
   - Combine criteria using + arithmetic operations (but you can use negative factor in order to make substractions)  
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


## Requirements

- Python 3.x
- Redis
- CLIP model (will be automatically downloaded)
- Other dependencies listed in requirements.txt
