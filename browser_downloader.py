import os
import time
import logging
import re
import subprocess
import json
import requests
from urllib.parse import urlparse, parse_qs
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("browser_downloader")

def get_video_id(url):
    """Extract YouTube video ID from URL"""
    if "youtu.be" in url:
        return url.split("/")[-1].split("?")[0]
    
    parsed_url = urlparse(url)
    if parsed_url.netloc in ['www.youtube.com', 'youtube.com']:
        if parsed_url.path == '/watch':
            return parse_qs(parsed_url.query)['v'][0]
        elif parsed_url.path.startswith('/embed/'):
            return parsed_url.path.split('/')[-1]
        elif parsed_url.path.startswith('/v/'):
            return parsed_url.path.split('/')[-1]
    
    # Handle shortened URLs like youtu.be
    if parsed_url.netloc == 'youtu.be':
        return parsed_url.path[1:]
    
    return None

def get_video_info(url):
    """Get video title and available formats without downloading"""
    video_id = get_video_id(url)
    if not video_id:
        return None
    
    try:
        # Use a headless browser to get the video title
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        try:
            # Visit 9xbuddy which doesn't have bot detection
            driver.get(f"https://9xbuddy.xyz/process?url=https://www.youtube.com/watch?v={video_id}")
            
            # Wait for the title to be loaded
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".media-info-title"))
            )
            
            # Get video title
            title_element = driver.find_element(By.CSS_SELECTOR, ".media-info-title")
            title = title_element.text.strip()
            
            # Wait for the download links to appear
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".download-item"))
            )
            
            # Get all download options
            download_items = driver.find_elements(By.CSS_SELECTOR, ".download-item")
            
            formats = []
            download_links = {}
            
            for item in download_items:
                try:
                    quality = item.find_element(By.CSS_SELECTOR, ".download-quality").text.strip()
                    format_type = item.find_element(By.CSS_SELECTOR, ".download-type").text.strip()
                    size = item.find_element(By.CSS_SELECTOR, ".download-size").text.strip()
                    
                    # Get the download button
                    download_btn = item.find_element(By.CSS_SELECTOR, ".download-btn")
                    download_url = download_btn.get_attribute("href")
                    
                    if download_url and "http" in download_url:
                        format_key = f"{quality}_{format_type}"
                        formats.append({
                            "quality": quality,
                            "format": format_type,
                            "size": size,
                            "key": format_key
                        })
                        download_links[format_key] = download_url
                except:
                    continue
            
            return {
                "title": title,
                "video_id": video_id,
                "formats": formats,
                "download_links": download_links
            }
        finally:
            driver.quit()
    
    except Exception as e:
        logger.error(f"Error getting video info: {str(e)}")
        return None

def download_video(url, format_key, output_dir, output_filename=None):
    """Download a YouTube video using browser automation"""
    video_info = get_video_info(url)
    
    if not video_info or format_key not in video_info["download_links"]:
        return None, "Failed to get video information or format not available"
    
    download_url = video_info["download_links"][format_key]
    
    if not output_filename:
        # Clean title to create a safe filename
        title = re.sub(r'[\\/*?:"<>|]', "", video_info["title"])
        # Determine extension
        format_parts = format_key.split('_')
        ext = "mp4" if format_parts[1] in ["MP4", "mp4"] else "mp3" if format_parts[1] in ["MP3", "mp3"] else "mp4"
        output_filename = f"{title}.{ext}"
    
    output_path = os.path.join(output_dir, output_filename)
    
    try:
        logger.info(f"Downloading from URL: {download_url}")
        
        # Download the file using requests
        response = requests.get(download_url, stream=True)
        response.raise_for_status()
        
        # Get total file size if available
        total_size = int(response.headers.get('content-length', 0))
        
        # Download the file
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        return output_path, None
    
    except Exception as e:
        logger.error(f"Error downloading video: {str(e)}")
        return None, str(e)

def download_with_quality(url, quality, is_audio, output_dir, filename=None):
    """Download video with specified quality or audio"""
    try:
        # Get video info
        video_info = get_video_info(url)
        if not video_info:
            return None, "Failed to get video information"
        
        # Determine the format to download
        formats = video_info["formats"]
        target_format = None
        
        if is_audio:
            # Try to find an MP3 format
            for fmt in formats:
                if "MP3" in fmt["format"] or "mp3" in fmt["format"]:
                    target_format = fmt
                    break
            
            # If no MP3, try to find an audio format
            if not target_format:
                for fmt in formats:
                    if "audio" in fmt["format"].lower():
                        target_format = fmt
                        break
        else:
            # For video, find the closest matching quality
            quality_map = {
                "highest": 1080,  # Default for highest
                "1080p": 1080,
                "720p": 720,
                "480p": 480,
                "360p": 360,
                "lowest": 144    # Default for lowest
            }
            
            target_quality = quality_map.get(quality, 720)  # Default to 720p if not recognized
            
            # Find available video qualities
            quality_options = {}
            for fmt in formats:
                if "MP4" in fmt["format"] or "mp4" in fmt["format"]:
                    # Extract numeric quality if available
                    quality_str = fmt["quality"]
                    if "p" in quality_str:
                        try:
                            q_value = int(quality_str.split("p")[0])
                            quality_options[q_value] = fmt
                        except:
                            pass
            
            # Find the closest matching quality
            if quality == "highest" and quality_options:
                target_quality = max(quality_options.keys())
            elif quality == "lowest" and quality_options:
                target_quality = min(quality_options.keys())
            
            available_qualities = sorted(quality_options.keys())
            
            if available_qualities:
                # Find the closest quality that doesn't exceed the target
                suitable_qualities = [q for q in available_qualities if q <= target_quality]
                if suitable_qualities:
                    closest_quality = max(suitable_qualities)
                else:
                    closest_quality = min(available_qualities)
                
                target_format = quality_options[closest_quality]
        
        # If we found a suitable format, download it
        if target_format:
            return download_video(url, target_format["key"], output_dir, filename)
        else:
            return None, "No suitable format found for the requested quality"
    
    except Exception as e:
        logger.error(f"Error in download_with_quality: {str(e)}")
        return None, str(e)

def download_instagram_content(url, output_dir, filename):
    """Download Instagram content using browser automation"""
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        try:
            driver.get(url)
            time.sleep(3)
            
            # Look for video elements
            video_elements = driver.find_elements(By.TAG_NAME, "video")
            
            if video_elements:
                video_url = video_elements[0].get_attribute("src")
                if video_url:
                    # Download the video
                    response = requests.get(video_url, stream=True)
                    if response.status_code == 200:
                        output_path = os.path.join(output_dir, filename)
                        with open(output_path, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)
                        return output_path, None
            
            return None, "No video content found"
            
        finally:
            driver.quit()
            
    except Exception as e:
        return None, str(e)

def get_instagram_info(url):
    """Get Instagram content information"""
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        try:
            driver.get(url)
            time.sleep(2)
            
            # Try to get title from meta tags
            title_element = driver.find_element(By.TAG_NAME, "title")
            title = title_element.get_attribute("textContent") if title_element else "Instagram Content"
            
            return {"title": title.replace(" • Instagram", "").strip()}
            
        finally:
            driver.quit()
            
    except Exception as e:
        logger.error(f"Error getting Instagram info: {str(e)}")
        return None