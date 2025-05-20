from flask import Flask, render_template, request, jsonify, send_from_directory, send_file
import os
import uuid
import logging
import subprocess
import shutil

# Set up logging
logging.basicConfig(
    filename='neobyte.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('neobyte')

app = Flask(__name__, static_folder='static')
app.config['TITLE'] = 'NeoByte Downloader'

# Path to ffmpeg from the YoutubeDownloaderApp folder
FFMPEG_PATH = os.path.join(os.getcwd(), 'YoutubeDownloaderApp', 'ffmpeg.exe')
if not os.path.exists(FFMPEG_PATH):
    FFMPEG_PATH = 'ffmpeg'  # Use system ffmpeg if not found

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/youtube')
def youtube():
    logger.info("YouTube download page accessed")
    return render_template('youtube.html')

@app.route('/instagram')
def instagram():
    logger.info("Instagram download page accessed")
    return render_template('instagram.html')

@app.route('/twitter')
def twitter():
    logger.info("X download page accessed")
    return render_template('twitter.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    download_type = request.form.get('download_type')
    resolution = request.form.get('resolution')
    
    if not url:
        return jsonify({'error': 'Please enter a YouTube URL'}), 400
    
    # Create temp directory if it doesn't exist
    temp_dir = os.path.join(os.getcwd(), 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    
    # Generate a unique ID for this download
    download_id = str(uuid.uuid4())
    
    try:
        # Initialize yt-dlp for direct download
        import yt_dlp
        
        # Configure yt-dlp options for direct download
        output_template = os.path.join(temp_dir, f'{download_id}.%(ext)s')
        
        ydl_opts = {
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
            'ffmpeg_location': FFMPEG_PATH,
        }
        
        # Different format options based on download type and resolution
        if download_type == 'audio':
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        else:
            # Video download with resolution selection
            if resolution == "highest":
                ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
            elif resolution == "lowest":
                ydl_opts['format'] = 'worstvideo[ext=mp4]+worstaudio[ext=m4a]/worst[ext=mp4]/worst'
            elif resolution == "2160p":
                # Specific format for 4K resolution (2160p)
                ydl_opts['format'] = 'bestvideo[height<=2160][ext=mp4]+bestaudio[ext=m4a]/best[height<=2160][ext=mp4]/best'
            elif resolution == "1440p":
                # Specific format for 2K resolution (1440p)
                ydl_opts['format'] = 'bestvideo[height<=1440][ext=mp4]+bestaudio[ext=m4a]/best[height<=1440][ext=mp4]/best'
            elif resolution == "1080p":
                # Specific format for Full HD resolution (1080p)
                ydl_opts['format'] = 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best'
            else:
                # Try to match the requested resolution
                ydl_opts['format'] = f'bestvideo[height<={resolution[:-1]}][ext=mp4]+bestaudio[ext=m4a]/best[height<={resolution[:-1]}][ext=mp4]/best'
        
        # Extract info first to get metadata
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # Determine the output filename
            if download_type == 'audio':
                filename = os.path.join(temp_dir, f"{download_id}.mp3")
            else:
                filename = ydl.prepare_filename(info)
            
            # Ensure the file exists
            if not os.path.exists(filename):
                # Try with different extension if needed
                possible_files = [os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if f.startswith(download_id)]
                if possible_files:
                    filename = possible_files[0]
                else:
                    return jsonify({'error': 'Failed to download file'}), 500
            
            # Get original filename
            original_filename = f"{info.get('title', 'video')}"
            if download_type == 'audio':
                original_filename = f"{original_filename}.mp3"
            else:
                original_filename = f"{original_filename}.mp4"
            
            # Replace invalid characters in filename
            original_filename = original_filename.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
            
            # Serve the file directly to the user
            response = send_file(
                filename,
                as_attachment=True,
                download_name=original_filename,
                conditional=False
            )
            
            # Clean up temp file after sending (schedule deletion)
            @response.call_on_close
            def cleanup():
                try:
                    if os.path.exists(filename):
                        os.remove(filename)
                except:
                    pass
            
            return response
        
    except Exception as e:
        error_message = f"Error downloading {url}: {str(e)}"
        logger.error(error_message)
        return jsonify({'error': error_message}), 500

@app.route('/instagram_download', methods=['POST'])
def instagram_download():
    url = request.form.get('url')
    
    if not url:
        return jsonify({'error': 'Please enter an Instagram URL'}), 400
    
    # Check if the URL is from Instagram
    if not ('instagram.com' in url or 'instagr.am' in url):
        return jsonify({'error': 'Please enter a valid Instagram URL'}), 400
    
    # Create temp directory if it doesn't exist
    temp_dir = os.path.join(os.getcwd(), 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    
    # Generate a unique ID for this download
    download_id = str(uuid.uuid4())
    
    try:
        # Initialize yt-dlp for Instagram download
        import yt_dlp
        
        # Configure yt-dlp options for Instagram download
        output_template = os.path.join(temp_dir, f'{download_id}.%(ext)s')
        
        ydl_opts = {
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
            'ffmpeg_location': FFMPEG_PATH,
            'format': 'best',  # Get the best quality for Instagram
            'cookiefile': None,  # No cookies needed for public content
            'extract_flat': False,
            'ignoreerrors': True  # Skip any errors
        }
        
        # Extract info first to get metadata
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info(f"Downloading Instagram content from: {url}")
            info = ydl.extract_info(url, download=True)
            
            if not info:
                return jsonify({'error': 'Could not download content. The post may be private or not exist.'}), 400
            
            # Determine the output filename
            filename = ydl.prepare_filename(info)
            
            # Ensure the file exists
            if not os.path.exists(filename):
                # Try with different extension if needed
                possible_files = [os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if f.startswith(download_id)]
                if possible_files:
                    filename = possible_files[0]
                else:
                    return jsonify({'error': 'Failed to download file'}), 500
            
            # Get original filename and content type
            if 'title' in info and info['title']:
                content_title = info['title']
            else:
                # Generate a title based on the type of content
                if 'reel' in url:
                    content_title = f"Instagram_Reel_{download_id[:8]}"
                elif 'stories' in url:
                    content_title = f"Instagram_Story_{download_id[:8]}"
                else:
                    content_title = f"Instagram_Post_{download_id[:8]}"
            
            # Get extension
            _, ext = os.path.splitext(filename)
            if not ext:
                ext = '.mp4'  # Default to mp4 if no extension
            
            # Ensure proper extension
            original_filename = f"{content_title}{ext}"
            
            # Replace invalid characters in filename
            original_filename = original_filename.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
            
            # Serve the file directly to the user
            response = send_file(
                filename,
                as_attachment=True,
                download_name=original_filename,
                conditional=False
            )
            
            # Clean up temp file after sending (schedule deletion)
            @response.call_on_close
            def cleanup():
                try:
                    if os.path.exists(filename):
                        os.remove(filename)
                except:
                    pass
            
            logger.info(f"Successfully downloaded Instagram content: {original_filename}")
            return response
            
    except Exception as e:
        error_message = f"Error downloading Instagram content from {url}: {str(e)}"
        logger.error(error_message)
        return jsonify({'error': error_message}), 500

if __name__ == '__main__':
    # Ensure temp directory exists
    os.makedirs('temp', exist_ok=True)
    
    # Log application start
    logger.info("NeoByte Downloader application started")
    
    # Run the app
    app.run(debug=True) 