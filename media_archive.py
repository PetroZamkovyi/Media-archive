import os
import json
import mimetypes
from pathlib import Path
from PIL import Image
from moviepy.editor import VideoFileClip


# Define function to get media files and their metadata
def get_media_files_metadata(root_dir):
    metadata = []
    for root, dirs, files in os.walk(root_dir):

        for file in files:
            file_path = os.path.join(root, file)
            mime_type, dirs = mimetypes.guess_type(file_path)

            if mime_type and (mime_type.startswith('image') or mime_type.startswith('video')):
                file_info = {
                    'original_path': file_path,
                    'filename': file,
                    'filetype': mime_type,
                    'modified': os.path.getmtime(file_path),
                    'created': os.path.getctime(file_path),
                    'size': os.path.getsize(file_path)
                }
                metadata.append(file_info)

    return metadata


# Define combined function to create shadow folder structure and process media files
def process_and_create_thumbnails(root_dir, shadow_root, media_files):
    for file_info in media_files:
        original_path = file_info['original_path']
        mime_type = file_info['filetype']

        # Compute the shadow path for the file and create directories if necessary
        shadow_path = original_path.replace(root_dir, shadow_root, 1)
        shadow_dir = os.path.dirname(shadow_path)
        os.makedirs(shadow_dir, exist_ok=True)

        # Generate the thumbnail filename
        filename, ext = os.path.splitext(file_info['filename'])
        thumbnail_path = os.path.join(shadow_dir, filename + '-thumbnail' + ext)

        try:
            if mime_type.startswith('image'):
                # Process image
                with Image.open(original_path) as img:
                    img.thumbnail((320, 320))  # Resize the image to a max of 320x320
                    img.save(thumbnail_path)
            elif mime_type.startswith('video'):
                # Process video
                with VideoFileClip(original_path) as clip:
                    clip_resized = clip.resize(width=320)
                    clip_resized.write_videofile(thumbnail_path, codec='libx264', audio_codec='aac')
        except Exception as e:
            print(f"Failed to process {original_path}: {e}")


# Main script
if __name__ == "__main__":
    root_dir = os.getcwd()  # Start script inside the folder
    shadow_root = os.path.join(root_dir, "Media-archive")

    # Ensure shadow folder is not created inside itself
    if root_dir == shadow_root:
        print("Error: The script is already running in the shadow folder!")
        exit()

    os.makedirs(shadow_root, exist_ok=True)

    # Step 1: Gather metadata
    media_files = get_media_files_metadata(root_dir)
    metadata_file_path = os.path.join(shadow_root, 'metadata.json')

    # Step 2: Save metadata to JSON
    with open(metadata_file_path, 'w') as metadata_file:
        json.dump(media_files, metadata_file, indent=4)

    # Step 3: Create shadow folder structure and process files
    process_and_create_thumbnails(root_dir, shadow_root, media_files)

    print(f"Processing completed. Check the '{shadow_root}' folder for results.")
