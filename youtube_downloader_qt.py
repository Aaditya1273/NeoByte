import os
import sys
import threading
from datetime import timedelta

# Auto-install required packages if not present
required_packages = ['PyQt5', 'pytube']
for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        import subprocess
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QComboBox, QPushButton, QRadioButton, 
                             QProgressBar, QFileDialog, QTextEdit, QButtonGroup, QFrame,
                             QMessageBox, QGroupBox, QSplitter)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QUrl, QSize, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QIcon, QFont, QDesktopServices, QPixmap, QColor, QPalette, QLinearGradient, QBrush, QRadialGradient
from pytube import YouTube, Playlist

class VideoDownloaderThread(QThread):
    progress_update = pyqtSignal(float, str)
    status_update = pyqtSignal(str)
    download_finished = pyqtSignal(str)
    download_error = pyqtSignal(str)
    
    def __init__(self, url, download_type, resolution, output_dir):
        super().__init__()
        self.url = url
        self.download_type = download_type
        self.resolution = resolution
        self.output_dir = output_dir
        
    def run(self):
        try:
            # Check if it's a playlist
            if "playlist" in self.url or "&list=" in self.url and not ("&index=" in self.url):
                self.status_update.emit("Detected playlist URL. Starting playlist download...")
                try:
                    playlist = Playlist(self.url)
                    self.status_update.emit(f"Playlist: {playlist.title}")
                    self.status_update.emit(f"Videos to download: {len(playlist.video_urls)}")
                    
                    for video_url in playlist.video_urls:
                        self.status_update.emit(f"Processing: {video_url}")
                        self.download_single_video(video_url)
                except Exception as e:
                    self.status_update.emit(f"Error with playlist: {str(e)}")
                    self.download_error.emit(str(e))
            else:
                # Single video download
                self.download_single_video(self.url)
                
        except Exception as e:
            self.status_update.emit(f"Error: {str(e)}")
            self.download_error.emit(str(e))
    
    def download_single_video(self, url):
        try:
            def progress_callback(stream, chunk, bytes_remaining):
                total_size = stream.filesize
                bytes_downloaded = total_size - bytes_remaining
                percentage = (bytes_downloaded / total_size) * 100
                self.progress_update.emit(percentage, self.format_size(total_size))
                
            def on_complete(stream, file_path):
                self.download_finished.emit(os.path.basename(file_path))
                
            yt = YouTube(url, on_progress_callback=progress_callback, on_complete_callback=on_complete)
            
            self.status_update.emit(f"Title: {yt.title}")
            self.status_update.emit(f"Author: {yt.author}")
            
            # Format duration
            duration = str(timedelta(seconds=yt.length))
            if duration.startswith('0:'):
                duration = duration[2:]
            self.status_update.emit(f"Duration: {duration}")
            
            if self.download_type == "audio":
                # Download audio
                self.status_update.emit("Downloading audio only...")
                stream = yt.streams.filter(only_audio=True).get_audio_only()
                file_path = stream.download(output_path=self.output_dir)
                
                # Convert to MP3
                base, ext = os.path.splitext(file_path)
                new_file = base + '.mp3'
                os.rename(file_path, new_file)
                self.status_update.emit(f"Converted to MP3: {os.path.basename(new_file)}")
            else:
                # Download video
                self.status_update.emit("Downloading video...")
                if self.resolution == "highest":
                    stream = yt.streams.filter(progressive=True).get_highest_resolution()
                elif self.resolution == "lowest":
                    stream = yt.streams.filter(progressive=True).get_lowest_resolution()
                else:
                    # Try to get the requested resolution, fall back to highest available
                    stream = yt.streams.filter(progressive=True, resolution=self.resolution).first()
                    if not stream:
                        self.status_update.emit(f"Resolution {self.resolution} not available, using highest available...")
                        stream = yt.streams.filter(progressive=True).get_highest_resolution()
                
                self.status_update.emit(f"Selected stream: {stream.resolution}, {stream.mime_type}")
                stream.download(output_path=self.output_dir)
                
        except Exception as e:
            self.status_update.emit(f"Error downloading {url}: {str(e)}")
            self.download_error.emit(str(e))
    
    def format_size(self, size_bytes):
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes/1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes/(1024*1024):.1f} MB"
        else:
            return f"{size_bytes/(1024*1024*1024):.1f} GB"

class AnimatedButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._animation = QPropertyAnimation(self, b"geometry")
        self._animation.setDuration(150)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)
        
    def enterEvent(self, event):
        self._animation.stop()
        geo = self.geometry()
        self._animation.setStartValue(geo)
        self._animation.setEndValue(geo.adjusted(-2, -2, 2, 2))
        self._animation.start()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self._animation.stop()
        geo = self.geometry()
        self._animation.setStartValue(geo)
        self._animation.setEndValue(geo.adjusted(2, 2, -2, -2))
        self._animation.start()
        super().leaveEvent(event)

class YoutubeDownloaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube Downloader Pro")
        self.setMinimumSize(950, 700)
        
        # Set background gradient
        self.setAutoFillBackground(True)
        palette = self.palette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor(28, 27, 34))
        gradient.setColorAt(1.0, QColor(19, 18, 23))
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)
        
        # Set stylesheet for the entire application
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1C1B22;
            }
            QWidget {
                background-color: transparent;
                color: #FFFFFF;
                font-family: 'Segoe UI', 'Roboto', sans-serif;
            }
            QLabel {
                color: #FFFFFF;
            }
            QLineEdit {
                background-color: rgba(40, 40, 50, 0.8);
                border: 1px solid #3D3E56;
                border-radius: 8px;
                padding: 10px 15px;
                color: #FFFFFF;
                font-size: 14px;
                selection-background-color: #6E56CF;
            }
            QLineEdit:focus {
                border: 1px solid #6E56CF;
                background-color: rgba(50, 50, 65, 0.9);
            }
            QTextEdit {
                background-color: rgba(30, 30, 40, 0.7);
                border: 1px solid #3D3E56;
                border-radius: 8px;
                padding: 8px;
                color: #FFFFFF;
                font-size: 13px;
                selection-background-color: #6E56CF;
            }
            QPushButton {
                background-color: #6E56CF;
                color: white;
                border-radius: 8px;
                padding: 10px 15px;
                font-weight: bold;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #8A70E8;
            }
            QPushButton:pressed {
                background-color: #5A44B3;
            }
            QPushButton:disabled {
                background-color: #3D3D4D;
                color: #8E8E9A;
            }
            QProgressBar {
                border: none;
                border-radius: 8px;
                background-color: rgba(50, 50, 65, 0.5);
                text-align: center;
                color: white;
                font-weight: bold;
                padding: 0px;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, 
                                      stop:0 #6E56CF, stop:1 #9E6CF3);
                border-radius: 8px;
            }
            QRadioButton, QCheckBox {
                spacing: 8px;
                color: #FFFFFF;
                font-size: 14px;
            }
            QRadioButton::indicator, QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QRadioButton::indicator::checked {
                background-color: #6E56CF;
                border: 2px solid #FFFFFF;
                border-radius: 9px;
            }
            QRadioButton::indicator::unchecked {
                background-color: rgba(40, 40, 50, 0.8);
                border: 2px solid #5D5D6B;
                border-radius: 9px;
            }
            QComboBox {
                background-color: rgba(40, 40, 50, 0.8);
                border: 1px solid #3D3E56;
                border-radius: 8px;
                padding: 8px 15px;
                color: white;
                min-width: 150px;
                font-size: 14px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left-width: 0px;
            }
            QComboBox:on {
                border: 1px solid #6E56CF;
            }
            QComboBox QAbstractItemView {
                background-color: #2A2A38;
                color: white;
                selection-background-color: #6E56CF;
                border-radius: 0px;
                border: 1px solid #3D3E56;
            }
            QGroupBox {
                border: 1px solid #3D3E56;
                border-radius: 10px;
                margin-top: 20px;
                font-weight: bold;
                font-size: 15px;
                padding: 15px;
                background-color: rgba(40, 40, 50, 0.3);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 10px;
                color: #ABA6FF;
            }
            QScrollBar:vertical {
                border: none;
                background: rgba(50, 50, 65, 0.5);
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #6E56CF;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        self.init_ui()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # App logo and title
        header_layout = QHBoxLayout()
        
        # Create YouTube-like logo
        logo_label = QLabel()
        logo_size = 40
        # You'd need to create an actual logo file - this is a placeholder
        # logo_pixmap = QPixmap("youtube_downloader_logo.png")
        # logo_label.setPixmap(logo_pixmap.scaled(logo_size, logo_size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        # Using text as placeholder
        logo_label.setText("▶")
        logo_label.setStyleSheet("""
            font-size: 28px;
            color: #FF0000;
            background-color: #FFFFFF;
            border-radius: 12px;
            padding: 8px;
            min-width: 40px;
            min-height: 40px;
            qproperty-alignment: AlignCenter;
        """)
        logo_label.setFixedSize(logo_size, logo_size)
        
        title_label = QLabel("YouTube Downloader Pro")
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #FFFFFF;
            margin-left: 15px;
        """)
        
        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
        
        # URL input with gradient border
        url_container = QGroupBox()
        url_container.setStyleSheet("""
            QGroupBox {
                border: 2px solid;
                border-radius: 12px;
                border-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6E56CF, stop:1 #9E6CF3);
                padding: 15px;
                background-color: rgba(30, 30, 40, 0.7);
                margin-top: 0px;
            }
        """)
        url_layout = QVBoxLayout(url_container)
        
        url_label = QLabel("Enter YouTube URL or Search Query:")
        url_label.setStyleSheet("font-size: 16px; color: #ABA6FF;")
        
        url_input_layout = QHBoxLayout()
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://www.youtube.com/watch?v=... or search terms")
        self.url_input.setMinimumHeight(50)
        self.url_input.setStyleSheet("""
            QLineEdit {
                font-size: 16px;
                border-radius: 10px;
                padding: 12px 20px;
                background-color: rgba(40, 40, 50, 0.9);
            }
        """)
        
        paste_button = AnimatedButton("Paste")
        paste_button.setIcon(QIcon.fromTheme("edit-paste"))
        paste_button.clicked.connect(self.paste_url)
        paste_button.setFixedWidth(100)
        paste_button.setMinimumHeight(50)
        
        url_input_layout.addWidget(self.url_input)
        url_input_layout.addWidget(paste_button)
        
        url_layout.addWidget(url_label)
        url_layout.addLayout(url_input_layout)
        
        main_layout.addWidget(url_container)
        
        # Split the rest of the UI into two columns
        content_layout = QHBoxLayout()
        
        # Left column - Options
        left_column = QVBoxLayout()
        
        # Options section
        options_group = QGroupBox("Download Options")
        options_layout = QVBoxLayout(options_group)
        options_layout.setSpacing(15)
        
        # Download type selection
        type_layout = QHBoxLayout()
        type_label = QLabel("Download Type:")
        type_label.setStyleSheet("font-size: 15px;")
        type_label.setFixedWidth(130)
        
        self.type_group = QButtonGroup(self)
        self.video_radio = QRadioButton("Video")
        self.audio_radio = QRadioButton("Audio Only")
        
        self.video_radio.setChecked(True)
        
        self.type_group.addButton(self.video_radio)
        self.type_group.addButton(self.audio_radio)
        
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.video_radio)
        type_layout.addWidget(self.audio_radio)
        type_layout.addStretch()
        
        options_layout.addLayout(type_layout)
        
        # Resolution selection
        res_layout = QHBoxLayout()
        res_label = QLabel("Video Quality:")
        res_label.setStyleSheet("font-size: 15px;")
        res_label.setFixedWidth(130)
        
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["highest", "1080p", "720p", "480p", "360p", "lowest"])
        
        res_layout.addWidget(res_label)
        res_layout.addWidget(self.resolution_combo)
        res_layout.addStretch()
        
        options_layout.addLayout(res_layout)
        
        # Output directory selection
        dir_layout = QHBoxLayout()
        dir_label = QLabel("Save To:")
        dir_label.setStyleSheet("font-size: 15px;")
        dir_label.setFixedWidth(130)
        
        self.output_dir = QLineEdit()
        self.output_dir.setText(os.path.join(os.path.expanduser("~"), "Downloads"))
        
        browse_button = AnimatedButton("Browse")
        browse_button.setIcon(QIcon.fromTheme("folder-open"))
        browse_button.clicked.connect(self.browse_directory)
        browse_button.setFixedWidth(100)
        
        dir_layout.addWidget(dir_label)
        dir_layout.addWidget(self.output_dir)
        dir_layout.addWidget(browse_button)
        
        options_layout.addLayout(dir_layout)
        
        left_column.addWidget(options_group)
        
        # Download button with glow effect
        self.download_button = AnimatedButton("DOWNLOAD NOW")
        self.download_button.setMinimumHeight(60)
        self.download_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, 
                               stop:0 #6E56CF, stop:1 #9E6CF3);
                font-size: 18px;
                font-weight: bold;
                border-radius: 10px;
                padding: 15px;
            }
            QPushButton:hover {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, 
                               stop:0 #8A70E8, stop:1 #B285FF);
            }
            QPushButton:pressed {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, 
                               stop:0 #5A44B3, stop:1 #7E56C8);
            }
        """)
        self.download_button.clicked.connect(self.start_download)
        
        left_column.addWidget(self.download_button)
        
        # Progress section
        progress_group = QGroupBox("Download Progress")
        progress_layout = QVBoxLayout(progress_group)
        progress_layout.setSpacing(15)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(25)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p% - %v MB / %m MB")
        
        self.status_label = QLabel("Ready to download")
        self.status_label.setStyleSheet("color: #ABA6FF; font-size: 14px;")
        
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.status_label)
        
        left_column.addWidget(progress_group)
        left_column.addStretch()
        
        # Right column - Log
        right_column = QVBoxLayout()
        
        # Log section
        log_group = QGroupBox("Download Log")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                padding: 15px;
                font-family: 'Consolas', 'Monaco', monospace;
                line-height: 1.5;
            }
        """)
        
        log_layout.addWidget(self.log_text)
        
        right_column.addWidget(log_group)
        
        # Add a button to open the downloads folder
        open_folder_button = AnimatedButton("Open Downloads Folder")
        open_folder_button.setIcon(QIcon.fromTheme("folder-open"))
        open_folder_button.clicked.connect(self.open_downloads_folder)
        open_folder_button.setFixedHeight(40)
        open_folder_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(90, 90, 110, 0.7);
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgba(110, 110, 130, 0.8);
            }
        """)
        
        right_column.addWidget(open_folder_button)
        
        # Set column sizes
        content_layout.addLayout(left_column, 45)
        content_layout.addLayout(right_column, 55)
        
        main_layout.addLayout(content_layout)
        
        # App information footer
        footer_layout = QHBoxLayout()
        
        info_label = QLabel("A modern YouTube downloader with no political messages or unnecessary content.")
        info_label.setStyleSheet("color: #8E8E9A; font-size: 12px;")
        
        footer_layout.addWidget(info_label)
        footer_layout.addStretch()
        
        main_layout.addLayout(footer_layout)
        
        # Initialize with a welcome message
        self.log_message("YouTube Downloader Pro is ready")
        self.log_message("Enter a YouTube URL or search query above and click DOWNLOAD NOW")
        self.log_message("✨ New futuristic UI with enhanced visuals")
    
    def paste_url(self):
        clipboard = QApplication.clipboard()
        self.url_input.setText(clipboard.text())
    
    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Save Location", 
                                                   self.output_dir.text(),
                                                   QFileDialog.ShowDirsOnly)
        if directory:
            self.output_dir.setText(directory)
    
    def open_downloads_folder(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.output_dir.text()))
    
    def log_message(self, message):
        timestamp = QApplication.instance().property("current_time").toString("hh:mm:ss")
        formatted_message = f"<span style='color:#ABA6FF;'>[{timestamp}]</span> <span style='color:#FFFFFF;'>{message}</span>"
        self.log_text.append(formatted_message)
    
    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a YouTube URL or search query")
            return
        
        download_type = "audio" if self.audio_radio.isChecked() else "video"
        resolution = self.resolution_combo.currentText()
        output_dir = self.output_dir.text()
        
        # Check if output directory exists
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not create output directory: {str(e)}")
                return
        
        # Disable download button and reset progress
        self.download_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting download...")
        
        # Start download in a separate thread
        self.download_thread = VideoDownloaderThread(url, download_type, resolution, output_dir)
        self.download_thread.progress_update.connect(self.update_progress)
        self.download_thread.status_update.connect(self.update_status)
        self.download_thread.download_finished.connect(self.download_complete)
        self.download_thread.download_error.connect(self.download_error)
        self.download_thread.start()
    
    def update_progress(self, percentage, total_size):
        self.progress_bar.setValue(int(percentage))
        self.status_label.setText(f"Downloading: {percentage:.1f}% of {total_size}")
        
        # Update progress bar format with actual size
        self.progress_bar.setFormat(f"{percentage:.1f}% - {total_size}")
    
    def update_status(self, message):
        self.log_message(message)
    
    def download_complete(self, filename):
        self.status_label.setText(f"Download completed: {filename}")
        self.progress_bar.setValue(100)
        self.download_button.setEnabled(True)
        
        # Success message box with custom styling
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Download Complete")
        msg_box.setText(f"<h3>Download Successful!</h3><p>File: {filename}</p>")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStandardButtons(QMessageBox.Ok)
        
        # Apply custom style to the message box
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #1C1B22;
                color: #FFFFFF;
            }
            QLabel {
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #6E56CF;
                color: white;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #8A70E8;
            }
        """)
        
        msg_box.exec_()
    
    def download_error(self, error_message):
        self.status_label.setText("Error occurred during download")
        self.download_button.setEnabled(True)
        
        # Error message box
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Download Error")
        msg_box.setText("<h3>An error occurred during download:</h3>")
        msg_box.setInformativeText(error_message)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setStandardButtons(QMessageBox.Ok)
        
        # Apply custom style to the message box
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #1C1B22;
                color: #FFFFFF;
            }
            QLabel {
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #6E56CF;
                color: white;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: #8A70E8;
            }
        """)
        
        msg_box.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application icon if available
    try:
        app.setWindowIcon(QIcon("icon.ico"))
    except:
        pass
    
    # Set time property for log timestamps
    from PyQt5.QtCore import QTime
    app.setProperty("current_time", QTime.currentTime())
    
    # Apply fusion style as base
    app.setStyle("Fusion")
    
    window = YoutubeDownloaderApp()
    window.show()
    
    sys.exit(app.exec_()) 