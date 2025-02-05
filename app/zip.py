from zipfile import ZipFile, ZIP_DEFLATED
import os

def create_zip(directory, zip_filename):
    """Create a zip file from the directory"""
    with ZipFile(zip_filename, 'w', ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(directory):
            for file in files:
                print(f"Adding {file} to zip")
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), directory))