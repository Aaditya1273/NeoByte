from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import threading
import time
from datetime import timedelta
from pytube import YouTube, Playlist
import uuid
import json

app = Flask(__name__, static_folder='static')
app.config['TITLE'] = 'NeoByte Downloader'

# Store download tasks and their status
downloads = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    download_type = request.form.get('download_type')
    resolution = request.form.get('resolution')
    
    if not url:
        return jsonify({'error': 'Please enter a YouTube URL'}), 400
    
    # Create downloads directory if it doesn't exist
    download_dir = os.path.join(os.getcwd(), 'downloads')
    os.makedirs(download_dir, exist_ok=True)
    
    # Generate a unique ID for this download
    download_id = str(uuid.uuid4())
    
    # Initialize download status
    downloads[download_id] = {
        'status': 'starting',
        'progress': 0,
        'title': '',
        'author': '',
        'duration': '',
        'messages': ['Starting download...'],
        'completed': False,
        'error': None,
        'file_path': None
    }
    
    # Start download in a background thread
    thread = threading.Thread(
        target=process_download,
        args=(download_id, url, download_type, resolution, download_dir)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({'download_id': download_id})

def process_download(download_id, url, download_type, resolution, output_dir):
    try:
        # Check if it's a playlist
        if "playlist" in url or "&list=" in url and not ("&index=" in url):
            add_message(download_id, "Detected playlist URL. Starting playlist download...")
            try:
                playlist = Playlist(url)
                add_message(download_id, f"Playlist: {playlist.title}")
                add_message(download_id, f"Videos to download: {len(playlist.video_urls)}")
                
                for video_url in playlist.video_urls:
                    add_message(download_id, f"Processing: {video_url}")
                    download_single_video(download_id, video_url, download_type, resolution, output_dir)
            except Exception as e:
                add_message(download_id, f"Error with playlist: {str(e)}")
                downloads[download_id]['error'] = str(e)
        else:
            # Single video download
            download_single_video(download_id, url, download_type, resolution, output_dir)
            
    except Exception as e:
        add_message(download_id, f"Error: {str(e)}")
        downloads[download_id]['error'] = str(e)
    finally:
        downloads[download_id]['completed'] = True

def download_single_video(download_id, url, download_type, resolution, output_dir):
    try:
        def progress_callback(stream, chunk, bytes_remaining):
            total_size = stream.filesize
            bytes_downloaded = total_size - bytes_remaining
            percentage = (bytes_downloaded / total_size) * 100
            downloads[download_id]['progress'] = percentage
        
        yt = YouTube(url, on_progress_callback=progress_callback)
        
        # Update video info
        downloads[download_id]['title'] = yt.title
        downloads[download_id]['author'] = yt.author
        
        # Format duration
        duration = str(timedelta(seconds=yt.length))
        if duration.startswith('0:'):
            duration = duration[2:]
        downloads[download_id]['duration'] = duration
        
        add_message(download_id, f"Title: {yt.title}")
        add_message(download_id, f"Author: {yt.author}")
        add_message(download_id, f"Duration: {duration}")
        
        if download_type == "audio":
            # Download audio
            add_message(download_id, "Downloading audio only...")
            stream = yt.streams.filter(only_audio=True).get_audio_only()
            file_path = stream.download(output_path=output_dir)
            
            # Convert to MP3
            base, ext = os.path.splitext(file_path)
            new_file = base + '.mp3'
            os.rename(file_path, new_file)
            file_path = new_file
            add_message(download_id, f"Converted to MP3: {os.path.basename(new_file)}")
        else:
            # Download video
            add_message(download_id, "Downloading video...")
            if resolution == "highest":
                stream = yt.streams.filter(progressive=True).get_highest_resolution()
            elif resolution == "lowest":
                stream = yt.streams.filter(progressive=True).get_lowest_resolution()
            else:
                # Try to get the requested resolution, fall back to highest available
                stream = yt.streams.filter(progressive=True, resolution=resolution).first()
                if not stream:
                    add_message(download_id, f"Resolution {resolution} not available, using highest available...")
                    stream = yt.streams.filter(progressive=True).get_highest_resolution()
            
            add_message(download_id, f"Selected stream: {stream.resolution}, {stream.mime_type}")
            file_path = stream.download(output_path=output_dir)
        
        downloads[download_id]['file_path'] = os.path.basename(file_path)
        add_message(download_id, f"Download completed: {os.path.basename(file_path)}")
        
    except Exception as e:
        add_message(download_id, f"Error downloading {url}: {str(e)}")
        downloads[download_id]['error'] = str(e)

def add_message(download_id, message):
    if download_id in downloads:
        downloads[download_id]['messages'].append(message)

@app.route('/status/<download_id>', methods=['GET'])
def get_status(download_id):
    if download_id not in downloads:
        return jsonify({'error': 'Download not found'}), 404
    
    return jsonify(downloads[download_id])

@app.route('/downloads/<path:filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory('downloads', filename, as_attachment=True)

@app.route('/downloads', methods=['GET'])
def list_downloads():
    completed_downloads = []
    for download_id, download in downloads.items():
        if download['completed'] and download['file_path'] and not download['error']:
            completed_downloads.append({
                'id': download_id,
                'title': download['title'],
                'file_path': download['file_path']
            })
    
    return jsonify(completed_downloads)

if __name__ == '__main__':
    # Ensure downloads directory exists
    os.makedirs('downloads', exist_ok=True)
    app.run(debug=True) 