import os
import logging
import time
import glob

def validate_file_size(file_obj, max_size):
    """
    Validate that the uploaded file doesn't exceed the maximum size
    
    Args:
        file_obj: Flask file object from request.files
        max_size (int): Maximum file size in bytes
        
    Returns:
        bool: True if file size is valid, False otherwise
    """
    # Get current position to reset after checking
    file_obj.seek(0, os.SEEK_END)
    file_size = file_obj.tell()
    file_obj.seek(0)  # Reset file position
    
    return file_size <= max_size

def cleanup_old_files(encrypted_folder, qr_folder, max_age=86400):
    """
    Remove old encrypted files and QR codes to prevent disk space issues
    
    Args:
        encrypted_folder (str): Path to folder with encrypted files
        qr_folder (str): Path to folder with QR codes
        max_age (int): Maximum age of files in seconds (default: 24 hours)
    """
    try:
        current_time = time.time()
        
        # Clean up encrypted files
        for file_path in glob.glob(f"{encrypted_folder}/*.enc"):
            if os.path.exists(file_path):
                # Get the file's last modification time
                file_mod_time = os.path.getmtime(file_path)
                
                # If the file is older than max_age, delete it
                if current_time - file_mod_time > max_age:
                    os.remove(file_path)
                    logging.debug(f"Removed old encrypted file: {file_path}")
        
        # Clean up QR codes
        for file_path in glob.glob(f"{qr_folder}/*.png"):
            if os.path.exists(file_path):
                # Get the file's last modification time
                file_mod_time = os.path.getmtime(file_path)
                
                # If the file is older than max_age, delete it
                if current_time - file_mod_time > max_age:
                    os.remove(file_path)
                    logging.debug(f"Removed old QR code: {file_path}")
                    
    except Exception as e:
        logging.error(f"Error during file cleanup: {e}")
