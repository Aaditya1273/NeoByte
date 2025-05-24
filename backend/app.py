from flask import Flask, render_template, request, jsonify, send_from_directory, send_file
import os
import uuid
import logging
import subprocess
import shutil
import browser_downloader  # Import the browser downloader

# Set up logging
logging.basicConfig(
    filename='neobyte.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('neobyte')

# Update paths for frontend/backend separation
frontend_dir = os.path.join(os.path.dirname(os.getcwd()), 'frontend')
app = Flask(__name__, 
    static_folder=os.path.join(frontend_dir, 'static'),
    template_folder=os.path.join(frontend_dir, 'templates'))
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
    
    # Create a temporary download directory that will be cleaned after each download
    # This directory will only temporarily hold files during processing
    temp_dir = os.path.join(os.getcwd(), 'downloads')
    os.makedirs(temp_dir, exist_ok=True)
    
    # Clean any existing files in the directory to prevent accumulation
    for filename in os.listdir(temp_dir):
        file_path = os.path.join(temp_dir, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            logger.error(f"Error cleaning temporary file {file_path}: {e}")
    
    # Generate a unique ID for this download
    download_id = str(uuid.uuid4())
    
    try:
        # First try with browser downloader which bypasses bot detection
        try:
            logger.info(f"Attempting to download with browser downloader: {url}")
            
            is_audio = download_type == 'audio'
            # Modified to use streaming download instead of temp files
            stream, filename, error = browser_downloader.stream_with_quality(
                url, 
                resolution,
                is_audio
            )
            
            if stream and filename:
                # Get original filename from the browser downloader
                video_info = browser_downloader.get_video_info(url)
                if video_info:
                    title = video_info["title"]
                    # Clean filename
                    title = title.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
                    original_filename = f"{title}.{'mp3' if is_audio else 'mp4'}"
                else:
                    original_filename = f"youtube_{download_id}.{'mp3' if is_audio else 'mp4'}"
                
                # Serve the file
                response = send_file(
                    file_path,
                    as_attachment=True,
                    download_name=original_filename,
                    conditional=False
                )
                
                # Clean up temp file immediately after sending
                @response.call_on_close
                def cleanup():
                    try:
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            logger.info(f"Removed temporary file: {file_path}")
                    except Exception as e:
                        logger.error(f"Error removing temporary file: {e}")
                
                logger.info(f"Successfully downloaded with browser downloader: {original_filename}")
                return response
            else:
                logger.error(f"Browser downloader failed: {error}")
                # Fall through to other methods
        except Exception as browser_error:
            logger.error(f"Browser downloader error: {str(browser_error)}")
            # Fall through to other methods
        
        # If browser downloader failed, try with pytube
        try:
            from pytube import YouTube
            import re
            
            # Fix for pytube age-restricted videos
            def bypass_age_gate(url):
                try:
                    url = url.replace("watch?v=", "embed/")
                    return url
                except:
                    return url
                    
            # Try to process with pytube
            logger.info(f"Attempting to download with pytube: {url}")
            
            # Bypass age gate if needed
            embed_url = bypass_age_gate(url)
            
            # Initialize pytube YouTube object
            yt = YouTube(url)
            
            # Get video title for filename
            video_title = yt.title
            # Clean filename
            video_title = re.sub(r'[\\/*?:"<>|]', "", video_title)
            
            # Determine file path
            if download_type == 'audio':
                # Audio download
                output_file = os.path.join(temp_dir, f"{download_id}.mp3")
                stream = yt.streams.filter(only_audio=True).first()
                
                # Download the file
                file_path = stream.download(output_path=temp_dir, filename=f"{download_id}.mp4")
                
                # Convert to mp3 if ffmpeg is available
                if os.path.exists(FFMPEG_PATH):
                    try:
                        subprocess.run([
                            FFMPEG_PATH, '-i', file_path, 
                            '-vn', '-ab', '192k', '-ar', '44100', '-y', 
                            output_file
                        ], check=True, capture_output=True)
                        
                        # Remove the original mp4 file
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            
                        filename = output_file
                        original_filename = f"{video_title}.mp3"
                    except Exception as e:
                        logger.error(f"Error converting to MP3: {str(e)}")
                        # If conversion fails, just use the mp4
                        filename = file_path
                        original_filename = f"{video_title}.mp4"
                else:
                    # No ffmpeg, just rename the file
                    filename = file_path
                    original_filename = f"{video_title}.mp4" 
            else:
                # Video download
                if resolution == "highest":
                    stream = yt.streams.get_highest_resolution()
                elif resolution == "lowest":
                    stream = yt.streams.filter(progressive=True).order_by('resolution').first()
                elif resolution in ["2160p", "1440p", "1080p", "720p", "480p", "360p"]:
                    # Extract the numeric value
                    res_value = resolution[:-1]  # Remove 'p'
                    # Find the closest matching resolution
                    stream = yt.streams.filter(res=resolution, file_extension='mp4').first()
                    if not stream:
                        stream = yt.streams.get_highest_resolution()
                else:
                    stream = yt.streams.get_highest_resolution()
                
                # Download the file
                filename = stream.download(output_path=temp_dir, filename=f"{download_id}.mp4")
                original_filename = f"{video_title}.mp4"
            
            # Replace invalid characters in filename
            original_filename = original_filename.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
            
            # Serve the file
            response = send_file(
                filename,
                as_attachment=True,
                download_name=original_filename,
                conditional=False
            )
            
            # Clean up temp file immediately after sending
            @response.call_on_close
            def cleanup():
                try:
                    if os.path.exists(filename):
                        os.remove(filename)
                        logger.info(f"Removed temporary file: {filename}")
                except Exception as e:
                    logger.error(f"Error removing temporary file: {e}")
            
            logger.info(f"Successfully downloaded with pytube: {original_filename}")
            return response
            
        except Exception as pytube_error:
            logger.error(f"Pytube download failed: {str(pytube_error)}")
            logger.info("Falling back to yt-dlp with alternative options...")
            
            # Fallback to yt-dlp with special options to bypass bot detection
            import yt_dlp
            
            # Configure yt-dlp options with bypass settings
            output_template = os.path.join(temp_dir, f'{download_id}.%(ext)s')
            
            ydl_opts = {
                'outtmpl': output_template,
                'quiet': True,
                'no_warnings': True,
                'ffmpeg_location': FFMPEG_PATH,
                # Try to bypass bot detection
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android', 'web'],
                        'player_skip': ['js', 'configs', 'webpage']
                    }
                },
                # Use a mobile user agent
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Android 12; Mobile; rv:68.0) Gecko/68.0 Firefox/96.0',
                    'Accept-Language': 'en-US,en;q=0.5'
                }
            }
            
            # Add format options
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
                    ydl_opts['format'] = 'bestvideo[height<=2160][ext=mp4]+bestaudio[ext=m4a]/best[height<=2160][ext=mp4]/best'
                elif resolution == "1440p":
                    ydl_opts['format'] = 'bestvideo[height<=1440][ext=mp4]+bestaudio[ext=m4a]/best[height<=1440][ext=mp4]/best'
                elif resolution == "1080p":
                    ydl_opts['format'] = 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best'
                else:
                    ydl_opts['format'] = f'bestvideo[height<={resolution[:-1]}][ext=mp4]+bestaudio[ext=m4a]/best[height<={resolution[:-1]}][ext=mp4]/best'
            
            # Extract and download
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Get information and download the video
                info = ydl.extract_info(url, download=True)
                logger.info(f"Downloaded with yt-dlp to temporary location for immediate delivery to user")
                
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
        # Try browser downloader first (more reliable for Instagram)
        try:
            logger.info(f"Attempting Instagram download with browser method: {url}")
            
            # Use browser downloader for Instagram content
            file_path, error = browser_downloader.download_instagram_content(
                url, 
                temp_dir,
                f"{download_id}.mp4"
            )
            
            if file_path and os.path.exists(file_path):
                # Get content info
                content_info = browser_downloader.get_instagram_info(url)
                if content_info and content_info.get('title'):
                    title = content_info['title']
                    # Clean filename
                    title = title.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
                    original_filename = f"{title}.mp4"
                else:
                    # Generate filename based on URL type
                    if 'reel' in url.lower():
                        original_filename = f"Instagram_Reel_{download_id[:8]}.mp4"
                    elif 'stories' in url.lower():
                        original_filename = f"Instagram_Story_{download_id[:8]}.mp4"
                    else:
                        original_filename = f"Instagram_Post_{download_id[:8]}.mp4"
                
                # Serve the file
                response = send_file(
                    file_path,
                    as_attachment=True,
                    download_name=original_filename,
                    conditional=False
                )
                
                # Clean up temp file after sending
                @response.call_on_close
                def cleanup():
                    try:
                        if os.path.exists(file_path):
                            os.remove(file_path)
                    except:
                        pass
                
                logger.info(f"Successfully downloaded Instagram content: {original_filename}")
                return response
            
        except Exception as browser_error:
            logger.warning(f"Browser downloader failed: {str(browser_error)}")
        
        # Fallback to yt-dlp with enhanced options
        import yt_dlp
        
        # Configure yt-dlp options for Instagram download with authentication support
        output_template = os.path.join(temp_dir, f'{download_id}.%(ext)s')
        
        ydl_opts = {
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
            'ffmpeg_location': FFMPEG_PATH,
            'format': 'best[height<=1080]/best',  # Limit to 1080p to avoid issues
            'extract_flat': False,
            'ignoreerrors': True,
            'no_check_certificate': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'referer': 'https://www.instagram.com/',
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Accept-Encoding': 'gzip,deflate',
                'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
                'Keep-Alive': '300',
                'Connection': 'keep-alive',
            }
        }
        
        # Extract info first to get metadata
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info(f"Downloading Instagram content from: {url}")
            
            try:
                info = ydl.extract_info(url, download=True)
            except yt_dlp.utils.ExtractorError as e:
                if 'login' in str(e).lower() or 'private' in str(e).lower():
                    return jsonify({
                        'error': 'This Instagram content is private or requires login. Please try with a public post/reel.'
                    }), 400
                else:
                    raise e
            
            if not info:
                return jsonify({
                    'error': 'Could not download content. The post may be private, deleted, or not accessible.'
                }), 400
            
            # Determine the output filename
            filename = ydl.prepare_filename(info)
            
            # Ensure the file exists
            if not os.path.exists(filename):
                # Try with different extension if needed
                possible_files = [os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if f.startswith(download_id)]
                if possible_files:
                    filename = possible_files[0]
                else:
                    return jsonify({'error': 'Failed to download file. Content may be protected or unavailable.'}), 500
            
            # Get original filename and content type
            if 'title' in info and info['title']:
                content_title = info['title']
            else:
                # Generate a title based on the type of content
                if 'reel' in url.lower():
                    content_title = f"Instagram_Reel_{download_id[:8]}"
                elif 'stories' in url.lower():
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
            
            # Clean up temp file after sending
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
        
        # Provide more specific error messages
        if 'login' in str(e).lower():
            return jsonify({
                'error': 'This Instagram content requires authentication. Please try with a public post or reel.'
            }), 400
        elif 'private' in str(e).lower():
            return jsonify({
                'error': 'This Instagram account or post is private and cannot be downloaded.'
            }), 400
        elif 'not found' in str(e).lower():
            return jsonify({
                'error': 'Instagram content not found. The post may have been deleted or the URL is incorrect.'
            }), 404
        else:
            return jsonify({
                'error': 'Failed to download Instagram content. Please try again or check if the content is publicly accessible.'
            }), 500

@app.route('/twitter_download', methods=['POST'])
def twitter_download():
    url = request.form.get('url')
    
    if not url:
        return jsonify({'error': 'Please enter an X (Twitter) URL'}), 400
    
    # Normalize URL (handle both x.com and twitter.com)
    if 'x.com' in url and 'twitter.com' not in url:
        logger.info(f"Converting X URL to Twitter format: {url}")
        url = url.replace('x.com', 'twitter.com')
    
    # Validate URL format
    if not ('twitter.com' in url or 'x.com' in url):
        return jsonify({'error': 'Please enter a valid X or Twitter post URL'}), 400
    
    # Create temp directory if it doesn't exist
    temp_dir = os.path.join(os.getcwd(), 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    
    # Generate a unique ID for this download
    download_id = str(uuid.uuid4())
    
    # Handle cookie file upload if provided
    cookie_file = None
    if 'cookie_file' in request.files and request.files['cookie_file'].filename:
        try:
            cookie_file = os.path.join(temp_dir, f'cookies_{download_id}.txt')
            request.files['cookie_file'].save(cookie_file)
            logger.info(f"Cookie file uploaded for download ID: {download_id}")
        except Exception as e:
            logger.error(f"Error saving cookie file: {str(e)}")
            return jsonify({'error': 'Failed to process cookie file. Please try again.'}), 500
    
    try:
        # Initialize yt-dlp for Twitter download
        import yt_dlp
        
        # Configure yt-dlp options for Twitter download
        output_template = os.path.join(temp_dir, f'{download_id}.%(ext)s')
        
        ydl_opts = {
            'outtmpl': output_template,
            'quiet': False,  # Enable some output for better debugging
            'no_warnings': False,  # Show warnings for better debugging
            'ffmpeg_location': FFMPEG_PATH,
            'format': 'best',  # Get the best quality for Twitter
            'cookiefile': cookie_file,  # Use cookie file if uploaded
            'extract_flat': False,
            'ignoreerrors': True,  # Skip any errors
            'verbose': True  # Enable verbose output for debugging
        }
        
        # Extract info first to get metadata
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info(f"Downloading X content from: {url}")
            info = ydl.extract_info(url, download=True)
            
            if not info:
                # Clean up cookie file
                if cookie_file and os.path.exists(cookie_file):
                    try:
                        os.remove(cookie_file)
                    except:
                        pass
                return jsonify({'error': 'Could not download content. The post may be private, not exist, or contain no media.'}), 400
            
            # Determine the output filename
            filename = ydl.prepare_filename(info)
            
            # Ensure the file exists
            if not os.path.exists(filename):
                # Try with different extension if needed
                possible_files = [os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if f.startswith(download_id) and not f.startswith('cookies_')]
                if possible_files:
                    filename = possible_files[0]
                else:
                    # Clean up cookie file
                    if cookie_file and os.path.exists(cookie_file):
                        try:
                            os.remove(cookie_file)
                        except:
                            pass
                    return jsonify({'error': 'Failed to download file. The post may not contain downloadable media.'}), 500
            
            # Get original filename and content type
            if 'title' in info and info['title']:
                content_title = info['title']
            else:
                # Generate a title based on the account name if available
                if 'uploader' in info and info['uploader']:
                    content_title = f"X_Video_{info['uploader']}_{download_id[:6]}"
                else:
                    content_title = f"X_Video_{download_id[:8]}"
            
            # Get extension
            _, ext = os.path.splitext(filename)
            if not ext:
                ext = '.mp4'  # Default to mp4 if no extension
            
            # Ensure proper extension
            original_filename = f"{content_title}{ext}"
            
            # Replace invalid characters in filename
            original_filename = original_filename.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
            
            # Log file information
            file_size = os.path.getsize(filename)
            logger.info(f"X content downloaded: {original_filename} ({file_size} bytes)")
            
            # Serve the file directly to the user
            response = send_file(
                filename,
                as_attachment=True,
                download_name=original_filename,
                conditional=False
            )
            
            # Clean up temp files after sending (schedule deletion)
            @response.call_on_close
            def cleanup():
                try:
                    # Clean up downloaded file
                    if os.path.exists(filename):
                        os.remove(filename)
                    
                    # Clean up cookie file
                    if cookie_file and os.path.exists(cookie_file):
                        os.remove(cookie_file)
                        
                except Exception as e:
                    logger.error(f"Error cleaning up temporary files: {str(e)}")
            
            logger.info(f"Successfully downloaded X content: {original_filename}")
            return response
            
    except yt_dlp.utils.DownloadError as e:
        error_message = str(e)
        logger.error(f"yt-dlp download error for {url}: {error_message}")
        
        # Clean up cookie file if there was an error
        if cookie_file and os.path.exists(cookie_file):
            try:
                os.remove(cookie_file)
            except:
                pass
        
        # Handle common error cases with more user-friendly messages
        if "Unsupported URL" in error_message:
            return jsonify({'error': 'This URL is not supported or does not contain media content'}), 400
        elif "requires authentication" in error_message:
            return jsonify({'error': 'This content is private and requires authentication. Please try uploading a cookies.txt file from a browser where you are logged in.'}), 403
        elif "not exist" in error_message or "404" in error_message:
            return jsonify({'error': 'The requested content does not exist'}), 404
        else:
            return jsonify({'error': f'Error downloading content: {error_message}'}), 500
    except Exception as e:
        error_message = f"Error downloading X content from {url}: {str(e)}"
        logger.error(error_message)
        
        # Clean up cookie file if there was an error
        if cookie_file and os.path.exists(cookie_file):
            try:
                os.remove(cookie_file)
            except:
                pass
                
        return jsonify({'error': error_message}), 500

@app.route('/cleanup', methods=['GET'])
def cleanup_temp_files():
    """Admin route to clean all temporary files"""
    temp_dir = os.path.join(os.getcwd(), 'temp')
    if os.path.exists(temp_dir):
        cleaned = 0
        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                    cleaned += 1
            except Exception as e:
                logger.error(f"Error cleaning file {file_path}: {e}")
        return jsonify({'message': f'Cleaned {cleaned} temporary files'})
    return jsonify({'message': 'No temporary directory found'})

if __name__ == '__main__':
    # Ensure temp directory exists
    os.makedirs('temp', exist_ok=True)
    
    # Log application start
    logger.info("NeoByte Downloader application started")
    
    # Run the app
    app.run(debug=True)