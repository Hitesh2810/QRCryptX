document.addEventListener('DOMContentLoaded', function() {
    // Copy buttons functionality
    const copyButtons = document.querySelectorAll('.copy-btn');
    copyButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const target = this.getAttribute('data-target');
            let targetInput;
            
            if (target === 'filename') {
                targetInput = this.closest('.input-group').querySelector('input');
            } else if (target === 'file-id') {
                targetInput = this.closest('.input-group').querySelector('input');
            } else if (target === 'key') {
                targetInput = document.querySelector('.key-field');
            }
            
            if (targetInput) {
                targetInput.select();
                document.execCommand('copy');
                
                // Change button text temporarily
                const originalHTML = this.innerHTML;
                this.innerHTML = '<i class="fas fa-check"></i> Copied!';
                setTimeout(() => {
                    this.innerHTML = originalHTML;
                }, 2000);
            }
        });
    });
    
    // QR Scanner functionality for decrypt page
    const startScannerBtn = document.getElementById('start-scanner');
    const stopScannerBtn = document.getElementById('stop-scanner');
    const videoContainer = document.getElementById('video-container');
    
    if (startScannerBtn && stopScannerBtn) {
        let html5QrCode;
        
        startScannerBtn.addEventListener('click', function() {
            startScannerBtn.classList.add('d-none');
            stopScannerBtn.classList.remove('d-none');
            
            // Initialize scanner
            html5QrCode = new Html5Qrcode("video-container");
            const config = { fps: 10, qrbox: { width: 250, height: 250 } };
            
            html5QrCode.start(
                { facingMode: "environment" }, 
                config,
                onScanSuccess
            ).catch(error => {
                console.error("Error starting scanner:", error);
                alert("Could not start camera: " + error);
                startScannerBtn.classList.remove('d-none');
                stopScannerBtn.classList.add('d-none');
            });
        });
        
        stopScannerBtn.addEventListener('click', function() {
            if (html5QrCode) {
                html5QrCode.stop().then(() => {
                    startScannerBtn.classList.remove('d-none');
                    stopScannerBtn.classList.add('d-none');
                });
            }
        });
        
        // Function to handle successful QR code scan
        function onScanSuccess(decodedText) {
            try {
                // Stop scanner
                html5QrCode.stop();
                startScannerBtn.classList.remove('d-none');
                stopScannerBtn.classList.add('d-none');
                
                // Send QR data to server for processing
                fetch('/scan-qr', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ qr_data: decodedText }),
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Populate form fields with QR data
                        document.getElementById('file_id').value = data.file_id;
                        document.getElementById('filename').value = data.filename;
                        
                        // Focus on the key field for the user to enter
                        document.getElementById('key').focus();
                    } else {
                        alert("Error processing QR code: " + data.error);
                    }
                })
                .catch(error => {
                    console.error('Error processing QR code:', error);
                    alert("Failed to process QR code: " + error);
                });
            } catch (error) {
                console.error('QR scan processing error:', error);
                alert("Error processing QR code: " + error);
            }
        }
    }
    
    // File size validation
    const fileInput = document.getElementById('file');
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            // 100MB in bytes
            const maxSize = 100 * 1024 * 1024;
            
            if (this.files[0] && this.files[0].size > maxSize) {
                alert('Error: File size exceeds the 100MB limit!');
                this.value = ''; // Clear the input
            }
        });
    }
});
