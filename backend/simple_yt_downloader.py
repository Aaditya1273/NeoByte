import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from threading import Thread
try:
    from pytube import YouTube, Playlist
except ImportError:
    import subprocess
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pytube"])
    from pytube import YouTube, Playlist

class YoutubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple YouTube Downloader")
        self.root.geometry("800x500")
        self.root.minsize(800, 500)
        
        # Set theme colors
        self.bg_color = "#333333"
        self.fg_color = "#FFFFFF"
        self.accent_color = "#FF0000"  # YouTube red
        
        self.root.config(bg=self.bg_color)
        
        self.setup_ui()
    
    def setup_ui(self):
        # URL Frame
        url_frame = tk.Frame(self.root, bg=self.bg_color)
        url_frame.pack(fill="x", padx=20, pady=20)
        
        url_label = tk.Label(url_frame, text="Enter YouTube URL:", bg=self.bg_color, fg=self.fg_color, font=("Arial", 12))
        url_label.pack(anchor="w")
        
        url_input_frame = tk.Frame(url_frame, bg=self.bg_color)
        url_input_frame.pack(fill="x", pady=5)
        
        self.url_var = tk.StringVar()
        self.url_entry = tk.Entry(url_input_frame, textvariable=self.url_var, font=("Arial", 12), bd=0, highlightthickness=1, highlightbackground="#666666")
        self.url_entry.pack(side="left", fill="x", expand=True, ipady=5)
        
        paste_button = tk.Button(url_input_frame, text="Paste", command=self.paste_clipboard, bg="#666666", fg=self.fg_color, bd=0, padx=10, font=("Arial", 10))
        paste_button.pack(side="right", padx=(5, 0), pady=2)
        
        # Options Frame
        options_frame = tk.Frame(self.root, bg=self.bg_color)
        options_frame.pack(fill="x", padx=20, pady=10)
        
        # Download type selection
        type_frame = tk.Frame(options_frame, bg=self.bg_color)
        type_frame.pack(fill="x", pady=5)
        
        type_label = tk.Label(type_frame, text="Download Type:", bg=self.bg_color, fg=self.fg_color, font=("Arial", 12))
        type_label.pack(side="left", padx=(0, 10))
        
        self.download_type = tk.StringVar(value="video")
        video_radio = tk.Radiobutton(type_frame, text="Video", variable=self.download_type, value="video", bg=self.bg_color, fg=self.fg_color, selectcolor=self.bg_color, activebackground=self.bg_color, activeforeground=self.fg_color)
        video_radio.pack(side="left", padx=(0, 10))
        
        audio_radio = tk.Radiobutton(type_frame, text="Audio Only", variable=self.download_type, value="audio", bg=self.bg_color, fg=self.fg_color, selectcolor=self.bg_color, activebackground=self.bg_color, activeforeground=self.fg_color)
        audio_radio.pack(side="left")
        
        # Resolution selection
        res_frame = tk.Frame(options_frame, bg=self.bg_color)
        res_frame.pack(fill="x", pady=5)
        
        res_label = tk.Label(res_frame, text="Video Quality:", bg=self.bg_color, fg=self.fg_color, font=("Arial", 12))
        res_label.pack(side="left", padx=(0, 10))
        
        self.resolution = tk.StringVar(value="highest")
        res_options = ["highest", "720p", "480p", "360p", "lowest"]
        res_dropdown = ttk.Combobox(res_frame, textvariable=self.resolution, values=res_options, state="readonly", width=10)
        res_dropdown.pack(side="left")
        
        # Output directory selection
        dir_frame = tk.Frame(options_frame, bg=self.bg_color)
        dir_frame.pack(fill="x", pady=5)
        
        dir_label = tk.Label(dir_frame, text="Save To:", bg=self.bg_color, fg=self.fg_color, font=("Arial", 12))
        dir_label.pack(side="left", padx=(0, 10))
        
        self.output_dir = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Downloads"))
        dir_entry = tk.Entry(dir_frame, textvariable=self.output_dir, font=("Arial", 12), bd=0, highlightthickness=1, highlightbackground="#666666")
        dir_entry.pack(side="left", fill="x", expand=True, ipady=5)
        
        browse_button = tk.Button(dir_frame, text="Browse", command=self.browse_directory, bg="#666666", fg=self.fg_color, bd=0, padx=10, font=("Arial", 10))
        browse_button.pack(side="right", padx=(5, 0), pady=2)
        
        # Download Button
        download_button = tk.Button(options_frame, text="DOWNLOAD", command=self.start_download, bg=self.accent_color, fg=self.fg_color, font=("Arial", 12, "bold"), bd=0, padx=10, pady=5)
        download_button.pack(fill="x", pady=20)
        
        # Progress Frame
        progress_frame = tk.Frame(self.root, bg=self.bg_color)
        progress_frame.pack(fill="x", padx=20, pady=10)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", mode="determinate", variable=self.progress_var)
        self.progress_bar.pack(fill="x", pady=5)
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = tk.Label(progress_frame, textvariable=self.status_var, bg=self.bg_color, fg=self.fg_color, font=("Arial", 10))
        status_label.pack(anchor="w", pady=5)
        
        # Results Frame
        self.results_frame = tk.Frame(self.root, bg=self.bg_color)
        self.results_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.result_text = tk.Text(self.results_frame, bg="#222222", fg=self.fg_color, font=("Arial", 10), bd=0, highlightthickness=1, highlightbackground="#666666")
        self.result_text.pack(fill="both", expand=True)
        self.result_text.insert("1.0", "* Simple YouTube Downloader ready to use\n* Enter a YouTube URL and click DOWNLOAD\n")
        self.result_text.config(state="disabled")
        
    def paste_clipboard(self):
        clipboard_text = self.root.clipboard_get()
        self.url_var.set(clipboard_text)
    
    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir.set(directory)
    
    def log_message(self, message):
        self.result_text.config(state="normal")
        self.result_text.insert("end", f"{message}\n")
        self.result_text.see("end")
        self.result_text.config(state="disabled")
        
    def progress_callback(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage = (bytes_downloaded / total_size) * 100
        self.progress_var.set(percentage)
        
        # Update status text
        progress_text = f"Downloading: {percentage:.1f}% of {self.format_size(total_size)}"
        self.status_var.set(progress_text)
        
    def format_size(self, size_bytes):
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes/1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes/(1024*1024):.1f} MB"
        else:
            return f"{size_bytes/(1024*1024*1024):.1f} GB"
        
    def download_complete(self, stream, file_path):
        self.status_var.set("Download completed!")
        self.progress_var.set(100)
        self.log_message(f"✓ Download completed: {os.path.basename(file_path)}")
        
    def start_download(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
        
        download_type = self.download_type.get()
        resolution = self.resolution.get()
        output_dir = self.output_dir.get()
        
        # Reset progress
        self.progress_var.set(0)
        self.status_var.set("Starting download...")
        
        # Start download in a separate thread
        download_thread = Thread(target=self.download_video, args=(url, download_type, resolution, output_dir))
        download_thread.daemon = True
        download_thread.start()
    
    def download_video(self, url, download_type, resolution, output_dir):
        try:
            # Check if it's a playlist
            if "playlist" in url or "&list=" in url and not ("&index=" in url):
                self.log_message(f"Detected playlist URL. Starting playlist download...")
                try:
                    playlist = Playlist(url)
                    self.log_message(f"Playlist: {playlist.title}")
                    self.log_message(f"Videos to download: {len(playlist.video_urls)}")
                    
                    for video_url in playlist.video_urls:
                        self.log_message(f"Processing: {video_url}")
                        self.download_single_video(video_url, download_type, resolution, output_dir)
                except Exception as e:
                    self.log_message(f"Error with playlist: {str(e)}")
            else:
                # Single video download
                self.download_single_video(url, download_type, resolution, output_dir)
                
        except Exception as e:
            self.status_var.set("Error during download")
            self.log_message(f"Error: {str(e)}")
            messagebox.showerror("Download Error", str(e))
    
    def download_single_video(self, url, download_type, resolution, output_dir):
        try:
            yt = YouTube(url, on_progress_callback=self.progress_callback, on_complete_callback=self.download_complete)
            self.log_message(f"Title: {yt.title}")
            self.log_message(f"Author: {yt.author}")
            self.log_message(f"Length: {yt.length} seconds")
            
            if download_type == "audio":
                # Download audio
                self.log_message("Downloading audio only...")
                stream = yt.streams.filter(only_audio=True).first()
                file_path = stream.download(output_path=output_dir)
                
                # Convert to MP3
                base, ext = os.path.splitext(file_path)
                new_file = base + '.mp3'
                os.rename(file_path, new_file)
                self.log_message(f"Converted to MP3: {os.path.basename(new_file)}")
            else:
                # Download video
                self.log_message("Downloading video...")
                if resolution == "highest":
                    stream = yt.streams.filter(progressive=True).get_highest_resolution()
                elif resolution == "lowest":
                    stream = yt.streams.filter(progressive=True).get_lowest_resolution()
                else:
                    # Try to get the requested resolution, fall back to highest available
                    stream = yt.streams.filter(progressive=True, resolution=resolution).first()
                    if not stream:
                        self.log_message(f"Resolution {resolution} not available, using highest available...")
                        stream = yt.streams.filter(progressive=True).get_highest_resolution()
                
                self.log_message(f"Selected stream: {stream.resolution}, {stream.mime_type}")
                stream.download(output_path=output_dir)
                
        except Exception as e:
            self.log_message(f"Error downloading {url}: {str(e)}")
            raise

if __name__ == "__main__":
    root = tk.Tk()
    app = YoutubeDownloader(root)
    
    # Set app icon if available
    try:
        root.iconbitmap("icon.ico")
    except:
        pass
        
    # Style configuration for ttk widgets
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TProgressbar", thickness=15, troughcolor="#222222", background="#FF0000")
    
    root.mainloop() 