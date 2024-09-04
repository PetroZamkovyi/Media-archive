# Media-archive
Mobile optimized Media converter

I want to create a script that converts images and videos from my home media archive to a smaller format that fits my Android phone. 

Recently, I was shown a similar Cloud feature on the Iphone, but I immediately noticed some drawbacks of this approach (especially when there is no internet connection). Anyway, it pushed me to this idea.

You could say it's a Thumbnails generator.

I am sure that many people have already implemented similar software before. Moreover, it can most likely be done with a few commands in a terminal or a simple bash script. But I just want to experiment and make something from scratch.

Implementation:
    Python script (CLI in the future? AWS lambda integration for video processing?)

User interaction, data processing flow:

* Start a script inside a folder with media files (and sub-folders)
* The script creates a Shadow Folder called 'Media-archive' with the same subfolder structure    
* Script analyses the data (read-only) and prepares a JSON file with all the files and their metadata inside the folder
* The script processes every media file in the original folder (read-only) and creates a Thumbnail copy in the Shadow Folder
* The subfolders and processed files should end as original_name + '-thumbnail' + extension.
* At the finish user receives the 'Media-archive' folder with the same folder structure but filled with the reduced-size media.
