import os
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
import logging

def generate_key():
    """Generate a random 32-byte key for AES-256 encryption"""
    return get_random_bytes(32)  # 32 bytes = 256 bits

def encrypt_file(input_path, output_path, key):
    """
    Encrypt a file using AES encryption in EAX mode
    
    Args:
        input_path (str): Path to the file to encrypt
        output_path (str): Path to save the encrypted file
        key (bytes): 32-byte encryption key
    """
    try:
        # Read the file content
        with open(input_path, 'rb') as file:
            data = file.read()
        
        # Create cipher object and encrypt
        cipher = AES.new(key, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(data)
        
        # Write the encrypted file with nonce and tag
        with open(output_path, 'wb') as file:
            # Write nonce (16 bytes), tag (16 bytes), and ciphertext
            file.write(cipher.nonce)
            file.write(tag)
            file.write(ciphertext)
        
        logging.debug(f"File encrypted successfully: {input_path} -> {output_path}")
        return True
        
    except Exception as e:
        logging.error(f"Encryption error: {e}")
        raise

def decrypt_file(input_path, key):
    """
    Decrypt a file using AES encryption
    
    Args:
        input_path (str): Path to the encrypted file
        key (bytes): 32-byte encryption key
    
    Returns:
        bytes: The decrypted file content
    """
    try:
        # Read the encrypted file
        with open(input_path, 'rb') as file:
            # Read nonce (16 bytes) and tag (16 bytes)
            nonce = file.read(16)
            tag = file.read(16)
            ciphertext = file.read()
        
        # Create cipher object and decrypt
        cipher = AES.new(key, AES.MODE_EAX, nonce)
        data = cipher.decrypt_and_verify(ciphertext, tag)
        
        logging.debug(f"File decrypted successfully: {input_path}")
        return data
        
    except Exception as e:
        logging.error(f"Decryption error: {e}")
        raise
