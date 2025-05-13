import os
import logging
import uuid
import base64
import json
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from werkzeug.utils import secure_filename
from utils.encryption import encrypt_file, decrypt_file, generate_key
from utils.qrcode_generator import generate_qr_code
from utils.file_handling import validate_file_size, cleanup_old_files
import io

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Create upload folders if they don't exist
UPLOAD_FOLDER = 'uploads'
QR_FOLDER = 'static/qrcodes'
ENCRYPTED_FOLDER = 'encrypted'

for folder in [UPLOAD_FOLDER, QR_FOLDER, ENCRYPTED_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# Maximum file size (100MB)
MAX_FILE_SIZE = 100 * 1024 * 1024

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if a file was uploaded
    if 'file' not in request.files:
        flash('No file selected', 'danger')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    # Check if a file was selected
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('index'))
    
    # Validate file size
    if not validate_file_size(file, MAX_FILE_SIZE):
        flash('File size exceeds the 100MB limit', 'danger')
        return redirect(url_for('index'))
    
    try:
        # Secure the filename
        filename = secure_filename(file.filename)
        file_id = str(uuid.uuid4())
        
        # Save the original file temporarily
        temp_path = os.path.join(UPLOAD_FOLDER, f"{file_id}_{filename}")
        file.save(temp_path)
        
        # Generate encryption key
        key = generate_key()
        key_b64 = base64.b64encode(key).decode('utf-8')
        
        # Encrypt the file
        encrypted_path = os.path.join(ENCRYPTED_FOLDER, f"{file_id}.enc")
        encrypt_file(temp_path, encrypted_path, key)
        
        # Generate QR code with file_id
        qr_data = {
            'file_id': file_id,
            'filename': filename,
        }
        qr_path = os.path.join(QR_FOLDER, f"{file_id}.png")
        generate_qr_code(json.dumps(qr_data), qr_path)
        
        # Store information in session
        session['file_id'] = file_id
        session['filename'] = filename
        session['key'] = key_b64
        session['qr_path'] = f"qrcodes/{file_id}.png"
        
        # Remove the temporary file
        os.remove(temp_path)
        
        # Schedule cleanup of old files
        cleanup_old_files(ENCRYPTED_FOLDER, QR_FOLDER)
        
        flash('File encrypted successfully!', 'success')
        return redirect(url_for('index'))
    
    except Exception as e:
        logging.error(f"Error during file upload: {e}")
        flash(f'Error processing file: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/decrypt', methods=['GET'])
def decrypt_page():
    return render_template('decrypt.html')

@app.route('/decrypt', methods=['POST'])
def decrypt_file_route():
    try:
        # Get file_id and key from form
        file_id = request.form.get('file_id')
        key_b64 = request.form.get('key')
        filename = request.form.get('filename')
        
        if not file_id or not key_b64 or not filename:
            flash('Missing required information', 'danger')
            return redirect(url_for('decrypt_page'))
        
        # Decode the key
        try:
            key = base64.b64decode(key_b64)
        except:
            flash('Invalid decryption key format', 'danger')
            return redirect(url_for('decrypt_page'))
        
        # Check if encrypted file exists
        encrypted_path = os.path.join(ENCRYPTED_FOLDER, f"{file_id}.enc")
        if not os.path.exists(encrypted_path):
            flash('File not found or has expired', 'danger')
            return redirect(url_for('decrypt_page'))
        
        # Decrypt the file to memory
        decrypted_data = decrypt_file(encrypted_path, key)
        
        # Create an in-memory file
        file_stream = io.BytesIO(decrypted_data)
        
        # Send the file to the user
        return send_file(
            file_stream,
            as_attachment=True,
            download_name=filename,
            mimetype='application/octet-stream'
        )
        
    except Exception as e:
        logging.error(f"Error during file decryption: {e}")
        flash(f'Error decrypting file: {str(e)}', 'danger')
        return redirect(url_for('decrypt_page'))

@app.route('/scan-qr', methods=['POST'])
def scan_qr():
    # Handle QR scan data
    data = request.json
    if 'qr_data' in data:
        try:
            qr_data = json.loads(data['qr_data'])
            return jsonify({
                'success': True,
                'file_id': qr_data.get('file_id'),
                'filename': qr_data.get('filename')
            })
        except Exception as e:
            logging.error(f"Error parsing QR data: {e}")
            return jsonify({'success': False, 'error': 'Invalid QR code data'})
    return jsonify({'success': False, 'error': 'No QR data provided'})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
