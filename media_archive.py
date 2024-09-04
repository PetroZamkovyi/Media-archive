import os
import json
import mimetypes
import logging
from PIL import Image
import moviepy.editor as mpy


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_media_files_metadata(root_dir):
    """Gather metadata for all media files in the given directory."""
    metadata = {}
    for root, _, files in os.walk(root_dir):
        for file in files:
            file_path = os.path.join(root, file)
            mime_type, _ = mimetypes.guess_type(file_path)

            if mime_type and (mime_type.startswith('image') or mime_type.startswith('video')):
                relative_path = os.path.relpath(file_path, root_dir)

                if relative_path.startswith('Media-archive'):
                    logging.info(f"Skipping file in shadow folder: {relative_path}")
                    continue

                file_info = {
                    'original_path': file_path,
                    'filename': file,
                    'filetype': mime_type,
                    'modified': os.path.getmtime(file_path),
                    'created': os.path.getctime(file_path),
                    'size': os.path.getsize(file_path)
                }
                metadata[relative_path] = file_info

    return metadata


def process_image(original_path, thumbnail_path):
    """Resize and save the image."""
    try:
        with Image.open(original_path) as img:
            max_width, max_height = 1440, 1440
            img.thumbnail((max_width, max_height))
            img.save(thumbnail_path)
        logging.info(f"Processed image: {original_path}")
    except Exception as e:
        logging.error(f"Failed to process image {original_path}: {e}")


def process_video(original_path, thumbnail_path):
    """Resize and save the video."""
    try:
        with mpy.VideoFileClip(original_path) as clip:
            clip_resized = clip.resize(width=320)
            clip_resized.write_videofile(thumbnail_path, codec='libx264', audio_codec='aac')
        logging.info(f"Processed video: {original_path}")
    except Exception as e:
        logging.error(f"Failed to process video {original_path}: {e}")


def process_media(file_info, relative_path, shadow_root):
    """Process the media file based on its type."""
    original_path = file_info['original_path']
    mime_type = file_info['filetype']

    shadow_path = os.path.join(shadow_root, relative_path)
    shadow_dir = os.path.dirname(shadow_path)
    os.makedirs(shadow_dir, exist_ok=True)

    filename, ext = os.path.splitext(file_info['filename'])
    thumbnail_path = os.path.join(shadow_dir, filename + '-thumbnail' + ext)

    if mime_type.startswith('image'):
        process_image(original_path, thumbnail_path)
    elif mime_type.startswith('video'):
        process_video(original_path, thumbnail_path)


def main():
    root_dir = os.getcwd()  # Start script inside the folder
    shadow_root = os.path.join(root_dir, "Media-archive")

    if root_dir.endswith("Media-archive"):
        logging.error("The script is already running in the shadow folder!")
        exit()

    os.makedirs(shadow_root, exist_ok=True)

    # Gather metadata
    media_files = get_media_files_metadata(root_dir)
    metadata_file_path = os.path.join(shadow_root, 'metadata.json')

    # Save metadata to JSON
    with open(metadata_file_path, 'w', encoding='utf-8') as metadata_file:
        json.dump(media_files, metadata_file, indent=4, ensure_ascii=False)

    # Process each media file
    for relative_path, file_info in media_files.items():
        process_media(file_info, relative_path, shadow_root)

    logging.info(f"Processing completed. Check the '{shadow_root}' folder for results.")


if __name__ == "__main__":
    main()
