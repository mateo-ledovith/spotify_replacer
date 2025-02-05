from zipfile import ZipFile, ZIP_DEFLATED
import os

def create_zip(directory, zip_filename):
    """
    Create a zip file from the specified directory.

    Args:
        directory (str): Path to the directory to be zipped.
        zip_filename (str): Name (or path) of the resulting zip file.
        
    This function will:
        - Walk through the directory and its subdirectories.
        - Add all files found to the zip archive.
        - Store the files in the zip with paths relative to the specified directory.
    """
    # Open the zip file in write mode with compression
    with ZipFile(zip_filename, 'w', ZIP_DEFLATED) as zipf:
        # Walk through the directory and its subdirectories
        for root, _, files in os.walk(directory):
            for file in files:
                # Construct the full file path
                full_file_path = os.path.join(root, file)
                
                # Calculate the relative path to store in the zip file
                arcname = os.path.relpath(full_file_path, directory)
                
                # Add the file to the zip archive
                zipf.write(full_file_path, arcname)