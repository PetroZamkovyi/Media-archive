import os
import json
import mimetypes
from PIL import Image
from moviepy.editor import VideoFileClip


# Function to get media files and their metadata
def get_media_files_metadata(root_dir):
    metadata = {}
    for root, dirs, files in os.walk(root_dir):

        for file in files:
            file_path = os.path.join(root, file)
            mime_type, _ = mimetypes.guess_type(file_path)

            if mime_type and (mime_type.startswith('image') or mime_type.startswith('video')):
                # Calculate the relative path
                relative_path = os.path.relpath(file_path, root_dir)

                # Skip files in 'Media-archive' folder
                if relative_path.startswith('Media-archive'):
                    print(f"Skipping file in shadow folder: {relative_path}")
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
    try:
        '''
        Process image. Image made on my phone Xiaomi Mi Note 10 usually have 6016x4512 px
        Phone width is only 1440x1080
        '''
        with Image.open(original_path) as img:
            max_width, max_height = 1440, 1440
            img.thumbnail((max_width, max_height))
            img.save(thumbnail_path)
    except Exception as e:
        print(f"Failed to process image {original_path}: {e}")


def process_video(original_path, thumbnail_path):
    try:
        # Resize and save the video
        with VideoFileClip(original_path) as clip:
            clip_resized = clip.resize(width=320)
            clip_resized.write_videofile(thumbnail_path, codec='libx264', audio_codec='aac')
    except Exception as e:
        print(f"Failed to process video {original_path}: {e}")


# Function to process media files (calls process_image or process_video)
def process_media(file_info, relative_path, shadow_root):
    original_path = file_info['original_path']
    mime_type = file_info['filetype']

    # Compute the shadow path for the file and create directories if necessary
    shadow_path = os.path.join(shadow_root, relative_path)
    shadow_dir = os.path.dirname(shadow_path)
    os.makedirs(shadow_dir, exist_ok=True)

    # Generate the thumbnail filename
    filename, ext = os.path.splitext(file_info['filename'])
    thumbnail_path = os.path.join(shadow_dir, filename + '-thumbnail' + ext)

    # Call appropriate processing function based on the file type
    if mime_type.startswith('image'):
        process_image(original_path, thumbnail_path)
    elif mime_type.startswith('video'):
        process_video(original_path, thumbnail_path)


def main():
    root_dir = os.getcwd()  # Start script inside the folder
    shadow_root = os.path.join(root_dir, "Media-archive")

    # Ensure shadow folder is not created inside itself
    if root_dir.endswith("Media-archive"):
        print("Error: The script is already running in the shadow folder!")
        exit()

    os.makedirs(shadow_root, exist_ok=True)

    # Step 1: Gather metadata
    media_files = get_media_files_metadata(root_dir)
    metadata_file_path = os.path.join(shadow_root, 'metadata.json')

    # Step 2: Save metadata to JSON
    with open(metadata_file_path, 'w', encoding='utf-8') as metadata_file:
        json.dump(media_files, metadata_file, indent=4, ensure_ascii=False)

    # Step 3: Process each media file
    for relative_path, file_info in media_files.items():
        process_media(file_info, relative_path, shadow_root)

    print(f"Processing completed. Check the '{shadow_root}' folder for results.")


if __name__ == "__main__":
    main()
