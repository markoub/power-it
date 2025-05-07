#!/usr/bin/env python3

import os
import sys
import shutil
from glob import glob
import asyncio
from config import PRESENTATIONS_STORAGE_DIR
import traceback

async def migrate_images():
    """
    Migrate images from the root of presentation directories to the images subdirectory.
    This ensures compatibility with the updated image path structure.
    """
    print(f"Starting image migration from {PRESENTATIONS_STORAGE_DIR}")
    
    # Get all presentation directories
    presentation_dirs = [d for d in os.listdir(PRESENTATIONS_STORAGE_DIR) 
                        if os.path.isdir(os.path.join(PRESENTATIONS_STORAGE_DIR, d))]
    
    # Exclude temp directory which doesn't need migration
    if "temp" in presentation_dirs:
        presentation_dirs.remove("temp")
    
    print(f"Found {len(presentation_dirs)} presentation directories: {presentation_dirs}")
    
    for pres_dir in presentation_dirs:
        try:
            full_pres_dir = os.path.join(PRESENTATIONS_STORAGE_DIR, pres_dir)
            
            # Check if this directory has an images subdirectory
            images_dir = os.path.join(full_pres_dir, "images")
            if not os.path.exists(images_dir):
                os.makedirs(images_dir, exist_ok=True)
                print(f"Created images directory: {images_dir}")
            
            # Find all PNG files in the presentation directory (not in subdirectories)
            png_files = glob(os.path.join(full_pres_dir, "*.png"))
            
            if png_files:
                print(f"Found {len(png_files)} PNG files in {pres_dir}")
                
                for png_file in png_files:
                    filename = os.path.basename(png_file)
                    target_path = os.path.join(images_dir, filename)
                    
                    # If the file doesn't already exist in the images directory
                    if not os.path.exists(target_path):
                        print(f"Moving {png_file} -> {target_path}")
                        shutil.copy2(png_file, target_path)
                        
                        # Optionally, remove the original file:
                        # os.remove(png_file)
            else:
                print(f"No PNG files found in the root of {pres_dir}")
        
        except Exception as e:
            print(f"Error processing directory {pres_dir}: {str(e)}")
            traceback.print_exc()
    
    print("Image migration completed")

if __name__ == "__main__":
    asyncio.run(migrate_images()) 