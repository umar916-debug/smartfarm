import os
import zipfile
import time
import shutil
import threading
import streamlit as st
import traceback

# Path for the zip file
ZIP_PATH = 'smart_farming_app.zip'

# Get the last modified time of all files
def get_last_modified_time():
    max_time = 0
    for root, _, files in os.walk('.'):
        # Skip hidden directories and __pycache__
        if '/.' in root or '__pycache__' in root:
            continue
        for file in files:
            # Skip the zip file itself and hidden files
            if file == os.path.basename(ZIP_PATH) or file.startswith('.'):
                continue
            full_path = os.path.join(root, file)
            try:
                mod_time = os.path.getmtime(full_path)
                max_time = max(max_time, mod_time)
            except Exception:
                pass
    return max_time

# Create a zip file with all code
def create_zip_file():
    """Create a zip file with all the source code files."""
    # Direct approach without temporary directory
    try:
        # Remove existing zip file if it exists
        if os.path.exists(ZIP_PATH):
            os.remove(ZIP_PATH)
            
        # Create a new zip file directly
        with zipfile.ZipFile(ZIP_PATH, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Walk through all directories
            for root, _, files in os.walk('.'):
                # Skip hidden directories, __pycache__, and any existing zip files
                if '/.' in root or '__pycache__' in root or '.git' in root:
                    continue
                
                # Add each file to the zip
                for file in files:
                    # Skip hidden files, zip files, and temporary files
                    if (file.startswith('.') or file.endswith('.zip') or 
                        file.endswith('.pyc') or file == os.path.basename(ZIP_PATH)):
                        continue
                    
                    file_path = os.path.join(root, file)
                    # Use relative path in the zip file
                    arcname = os.path.relpath(file_path, '.')
                    try:
                        zipf.write(file_path, arcname)
                    except Exception as e:
                        print(f"Error adding {file_path} to zip: {str(e)}")
        
        print(f"Successfully created zip file: {ZIP_PATH}")
        return True
    
    except Exception as e:
        print(f"Error creating zip file: {str(e)}")
        print(traceback.format_exc())
        return False

# Check if the zip file needs to be updated
def update_zip_if_needed():
    try:
        # If zip doesn't exist, create it
        if not os.path.exists(ZIP_PATH):
            return create_zip_file()
            
        # Check if any files have been modified since the zip was created
        zip_mod_time = os.path.getmtime(ZIP_PATH)
        last_mod_time = get_last_modified_time()
        
        # If any file is newer than the zip, update the zip
        if last_mod_time > zip_mod_time:
            return create_zip_file()
            
        return True
    except Exception as e:
        print(f"Error checking zip file: {str(e)}")
        return False

# Background thread to periodically update the zip file
def zip_update_thread():
    while True:
        update_zip_if_needed()
        time.sleep(30)  # Check every 30 seconds

# Start the background thread when the module is imported
thread = threading.Thread(target=zip_update_thread, daemon=True)
thread.start()

# Function for the Streamlit interface to download the zip
def download_code_zip():
    # Ensure the zip is up to date
    update_zip_if_needed()
    
    # Read the zip file
    if os.path.exists(ZIP_PATH):
        with open(ZIP_PATH, 'rb') as f:
            zip_data = f.read()
        
        # Add a download button to the app
        st.download_button(
            label="Download Complete Source Code",
            data=zip_data,
            file_name="smart_farming_app.zip",
            mime="application/zip",
            help="Download a zip file containing all source code for this application"
        )
    else:
        st.error("Zip file not available. Please try again later.")