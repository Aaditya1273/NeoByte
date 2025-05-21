# NeoByte Downloader

A sleek, modern multi-platform social media downloader with a futuristic cyber/neon aesthetic interface.

## Features

- Futuristic cyber/neon themed interface with professional design
- Light/Dark theme toggle for user preference
- Download videos from multiple platforms:
  - YouTube videos and playlists in multiple quality options
  - Instagram reels and stories
  - X/Twitter videos and GIFs
- Extract audio from videos as MP3 files
- Real-time progress tracking with visual feedback
- Cross-platform compatibility (Windows, macOS, Linux, Android)
- Responsive design that works on all devices
- Organized management of completed downloads

## Screenshots

![Dark Theme](screenshots/dark-theme.png)
![Light Theme](screenshots/light-theme.png)

## Installation

1. Clone this repository or download the source code
2. Install the required dependencies:

```
pip install -r requirements.txt
```

## How to Run

Start the web application with:

```
python app.py
```

Or use the included batch file (Windows):

```
run_web_downloader.bat
```

Then open your web browser and navigate to:

```
http://localhost:5000
```

## Usage Instructions

### YouTube Downloads
1. Navigate to the YouTube tab
2. Paste a YouTube URL in the input field
3. Select download type (video or audio)
4. Choose your preferred video quality
5. Click the DOWNLOAD button
6. Monitor the download progress in real-time

### Instagram Downloads
1. Navigate to the Instagram tab
2. Paste an Instagram reel or story URL
3. Click the DOWNLOAD button
4. Wait for the download to complete

### X/Twitter Downloads
1. Navigate to the X tab
2. Paste a tweet URL containing video or GIF
3. Click the DOWNLOAD button
4. Choose your preferred quality if prompted

## Features in Detail

- **Theme Toggle**: Switch between dark and light themes with the toggle in the upper right corner
- **Responsive Design**: Fully responsive layout that adapts to desktop, tablet, and mobile screens
- **Platform Support**: Works across all major operating systems and browsers
- **Real-time Feedback**: Visual progress indicators and status messages
- **Modern UI**: Sleek animations, transitions, and visual effects

## Requirements

- Python 3.6 or higher
- Required packages (listed in requirements.txt):
  - Flask
  - pytube
  - instaloader
  - tweepy
  - beautifulsoup4
  - requests

## Technology

Built with modern web technologies and a focus on user experience:
- Python backend with Flask
- Responsive frontend with Bootstrap 5
- Font Awesome icons
- Local storage for user preferences
- CSS animations and transitions
- Adaptive theming system

## License

This project is free to use for personal purposes.

## Acknowledgements

- Font Awesome for the icon library
- Bootstrap for the responsive framework 