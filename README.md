# 🚀 NeoByte Downloader

*The #1 free and open-source social media downloader with 4K support. A sleek, futuristic, and cross-platform tool built with Python and Flask.*

[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start/deploy?repository=https://github.com/Aaditya1273/NeoByte)
[![GitHub Stars](https://img.shields.io/github/stars/Aaditya1273/NeoByte?style=social)](https://github.com/Aaditya1273/NeoByte)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ Features at a Glance:

* 📥 **Multi-Platform Support**:
  * ▶️ **YouTube** - Videos, playlists, and shorts in up to 4K quality
  * 📸 **Instagram** - Reels, stories, and posts in HD quality
  * 🐦 **X/Twitter** - Videos and GIFs with no quality loss
* 🎧 **Audio Extraction** - Convert any video to high-quality MP3
* 💻 **Cross-platform** - Works on Windows, macOS, Linux, and Android
* 🗂️ **Smart Download Management** - Organize your downloads efficiently
* 🌙 **Dark/Light Mode** - Beautiful adaptive theme support
* ⚡ **Fast & Efficient** - Ultra-optimized download speeds
* 🔒 **No Ads or Watermarks** - 100% clean and safe downloading
* 🌐 **No Registration Required** - Instant downloads without accounts

---

## ⚙️ Installation:

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Aaditya1273/NeoByte.git
   cd NeoByte
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**
   ```bash
   python app.py
   ```
   Or use the provided batch script:
   ```bash
   ./run_web_downloader.bat   # On Windows
   ```

4. **Access the Web Interface**
   Open your browser and navigate to `http://localhost:5000`
   
## 🚀 Deployment Options

### Deploy to Netlify (Static Front-end Only)

1. Fork this repository
2. Sign up on [Netlify](https://www.netlify.com/)
3. Create a new site from Git
4. Select your forked repository
5. Configure build settings:
   - Build command: `mkdir build && cp -r templates/* build/`
   - Publish directory: `build`

### Deploy as Flask Application (Recommended)

#### Option 1: Render
1. Create an account on [Render](https://render.com/)
2. Create a new Web Service
3. Connect your GitHub repository
4. Set the build command: `pip install -r requirements.txt`
5. Set the start command: `gunicorn app:app`

#### Option 2: PythonAnywhere
1. Create an account on [PythonAnywhere](https://www.pythonanywhere.com/)
2. Create a new web app
3. Select Flask and the appropriate Python version
4. Set up your virtual environment and install requirements
5. Configure your WSGI file to point to app.py

#### Option 3: Standalone Executable
Use PyInstaller to create a standalone executable:
```bash
pip install pyinstaller
pyinstaller --onefile --add-data "templates;templates" --add-data "static;static" app.py
```

---

## 🧪 Tech Stack

* 🐍 **Backend**: Python 3.12 with Flask 2.3.3
* 🎬 **Download Engine**: yt-dlp and pytube for maximum compatibility
* 💡 **Frontend**: Bootstrap 5 for responsive, mobile-friendly UI
* 🌐 **Icons**: Font Awesome 6 for beautiful iconography
* 🎨 **Styling**: Custom CSS with futuristic neon effects
* 💾 **Storage**: Local storage for user preferences and download history
* 🔄 **API**: RESTful architecture for seamless client-server communication

---

## 📝 Usage Guide

1. **Downloading Videos**:
   - Paste the video URL in the input field
   - Select desired quality/format
   - Click download

2. **Audio Extraction**:
   - Select MP3 format
   - Choose quality
   - Download

3. **Batch Downloads**:
   - Add multiple URLs
   - Select format
   - Download all

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 🐛 Known Issues

* Some Instagram stories may require authentication
* Twitter/X downloads might be limited by API restrictions
* YouTube age-restricted videos may require login

---

## 🪪 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Note**: This project is free to use for personal purposes. 🚫 No commercial redistribution allowed.

---

## 📞 Support

If you encounter any issues or have questions, please:

1. Check the [GitHub Issues](https://github.com/Aaditya1273/NeoByte/issues) for existing reports
2. Open a new issue with detailed information if your problem is not already reported
3. For urgent assistance, contact the developer at [your-email@example.com]

## ⭐ Star the Repository

If you find NeoByte Downloader useful, please consider giving it a star on GitHub! It helps others discover this tool and motivates continued development.

## 📸 Screenshots

<details>
  <summary>Click to view screenshots</summary>
  
  ### Main Interface
  ![Main Interface](https://example.com/screenshots/main.jpg)
  
  ### YouTube Downloader
  ![YouTube Downloader](https://example.com/screenshots/youtube.jpg)
  
  ### Instagram Downloader
  ![Instagram Downloader](https://example.com/screenshots/instagram.jpg)
  
  ### X/Twitter Downloader
  ![X/Twitter Downloader](https://example.com/screenshots/twitter.jpg)
</details>

---

<p align="center">Made with ❤️ by <a href="https://github.com/Aaditya1273">Aaditya</a></p>

For support, please open an issue in the GitHub repository or contact us at [support@neobyte.com](mailto:support@neobyte.com)

---

*Made with ❤️ by the NeoByte Team*


