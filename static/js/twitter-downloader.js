document.addEventListener('DOMContentLoaded', function() {
    const urlInput = document.getElementById('url');
    const cookieFileInput = document.getElementById('cookie-file');
    const cookieFileNameDisplay = document.getElementById('cookie-file-name');
    const downloadForm = document.getElementById('twitter-download-form');
    const downloadButton = document.getElementById('download-button');
    const statusMessage = document.getElementById('status-message');
    
    // Handle URL input validation
    urlInput.addEventListener('input', function() {
        validateUrl();
    });
    
    urlInput.addEventListener('paste', function() {
        setTimeout(() => {
            validateUrl();
        }, 100);
    });
    
    // Handle cookie file selection
    if (cookieFileInput) {
        cookieFileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                const fileName = this.files[0].name;
                cookieFileNameDisplay.textContent = fileName;
                cookieFileNameDisplay.style.display = 'block';
            } else {
                cookieFileNameDisplay.textContent = '';
                cookieFileNameDisplay.style.display = 'none';
            }
        });
    }
    
    // URL validation function
    function validateUrl() {
        const url = urlInput.value.trim();
        
        if (url.length > 0) {
            // Basic check for Twitter/X URL format
            if (url.match(/https?:\/\/(www\.)?(twitter|x)\.com\/[^\/]+\/status\/\d+/i)) {
                urlInput.classList.remove('is-invalid');
                urlInput.classList.add('is-valid');
                downloadButton.disabled = false;
                return true;
            } else {
                urlInput.classList.remove('is-valid');
                urlInput.classList.add('is-invalid');
                downloadButton.disabled = true;
                return false;
            }
        } else {
            urlInput.classList.remove('is-valid');
            urlInput.classList.remove('is-invalid');
            downloadButton.disabled = true;
            return false;
        }
    }
    
    // Handle form submission for direct download
    if (downloadForm) {
        downloadForm.addEventListener('submit', function(e) {
            if (!validateUrl()) {
                e.preventDefault();
                showStatusMessage('Please enter a valid X or Twitter URL', 'danger');
                return false;
            }
            
            // Show loading indicator
            downloadButton.innerHTML = '<span class="spinner-border spinner-border-sm spinner-border-x" role="status" aria-hidden="true"></span> Processing...';
            downloadButton.disabled = true;
            
            // Form will handle the actual submission and download
            return true;
        });
    }
    
    // Helper function to display status messages
    function showStatusMessage(message, type) {
        statusMessage.innerHTML = `<div class="alert alert-${type}" role="alert">${message}</div>`;
        setTimeout(() => {
            statusMessage.innerHTML = '';
        }, 5000); // Clear after 5 seconds
    }
}); 