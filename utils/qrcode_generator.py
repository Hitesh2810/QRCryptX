import qrcode
import logging
import json

def generate_qr_code(data, output_path):
    """
    Generate a QR code with the given data and save it to the specified path
    
    Args:
        data (str): Data to encode in the QR code
        output_path (str): Path to save the QR code image
    """
    try:
        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        
        # Add data to the QR code
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create an image from the QR code
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save the image to the specified path
        img.save(output_path)
        
        logging.debug(f"QR code generated successfully: {output_path}")
        return True
        
    except Exception as e:
        logging.error(f"QR code generation error: {e}")
        raise
