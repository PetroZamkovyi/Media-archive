import os
import json
import mimetypes
from pathlib import Path
from PIL import Image
from moviepy.editor import VideoFileClip


# Define function to get media files and their metadata
def get_media_files_metadata(root_dir, shadow_root):
    media_files = []
    for root, _, files in os.walk(root_dir):
        # Skip the shadow folder itself
        if root.startswith(shadow_root):
            continue

        for file in files:
            file_path = os.path.join(root, file)
            mime_type, _ = mimetypes.guess_type(file_path)

            if mime_type and (mime_type.startswith('image') or mime_type.startswith('video')):
                file_info = {
                    'original_path': file_path,
                    'filename': file,
                    'filetype': mime_type,
                    'size': os.path.getsize(file_path)
                }
                media_files.append(file_info)

    return media_files


# Define function to create a shadow folder with the same subfolder structure
def create_shadow_folder(root_dir, shadow_root):
    for root, dirs, _ in os.walk(root_dir):
        # Skip the shadow folder itself
        if root.startswith(shadow_root):
            continue

        for dir_name in dirs:
            src_dir_path = os.path.join(root, dir_name)
            shadow_dir_path = src_dir_path.replace(root_dir, shadow_root, 1)
            os.makedirs(shadow_dir_path, exist_ok=True)


# Define function to process and create thumbnails for media files
def create_thumbnails(media_files, shadow_root):
    for file_info in media_files:
        original_path = file_info['original_path']
        mime_type = file_info['filetype']
        shadow_path = original_path.replace(root_dir, shadow_root, 1)
        filename, ext = os.path.splitext(file_info['filename'])
        thumbnail_path = os.path.join(os.path.dirname(shadow_path), filename + '-thumbnail' + ext)

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
    media_files = get_media_files_metadata(root_dir, shadow_root)
    metadata_file_path = os.path.join(shadow_root, 'metadata.json')

    # Save metadata to JSON
    with open(metadata_file_path, 'w') as metadata_file:
        json.dump(media_files, metadata_file, indent=4)

    # Step 2: Create shadow folder structure
    create_shadow_folder(root_dir, shadow_root)

    # Step 3: Process media files and create thumbnails
    create_thumbnails(media_files, shadow_root)

    print(f"Processing completed. Check the '{shadow_root}' folder for results.")
