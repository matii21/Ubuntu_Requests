import requests
import os
import hashlib
from urllib.parse import urlparse

def create_image_directory():
    """Create the directory for storing images if it doesn't exist"""
    os.makedirs("Fetched_Images", exist_ok=True)
    print("[OK] Fetched_Images directory ready")

def extract_filename(url, content_type):
    """Extract filename from URL or generate one based on content type"""
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    
    # If no filename in URL, generate one
    if not filename or '.' not in filename:
        # Determine extension from Content-Type header or default to jpg
        extension = "jpg"  # default
        if content_type:
            # Map common content types to extensions
            content_map = {
                "image/jpeg": "jpg",
                "image/jpg": "jpg",
                "image/png": "png",
                "image/gif": "gif",
                "image/webp": "webp",
                "image/svg+xml": "svg"
            }
            extension = content_map.get(content_type, "jpg")
        
        # Create a hash-based filename for uniqueness
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        filename = f"downloaded_image_{url_hash}.{extension}"
    
    return filename

def is_duplicate_image(content, directory="Fetched_Images"):
    """Check if image content already exists in directory to avoid duplicates"""
    # Check if directory exists and has files
    if not os.path.exists(directory) or not os.listdir(directory):
        return False, None
        
    content_hash = hashlib.md5(content).hexdigest()
    
    for existing_file in os.listdir(directory):
        file_path = os.path.join(directory, existing_file)
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'rb') as f:
                    existing_content = f.read()
                    if hashlib.md5(existing_content).hexdigest() == content_hash:
                        return True, existing_file
            except (IOError, OSError):
                continue
    
    return False, None

def download_image(url):
    """Download an image from the provided URL with proper error handling"""
    try:
        # Send request with appropriate headers and timeout
        headers = {
            'User-Agent': 'UbuntuImageFetcher/1.0 (Community Project)'
        }
        
        print(f"Connecting to {urlparse(url).netloc}...")
        response = requests.get(url, headers=headers, timeout=15)
        
        # Check for HTTP errors
        response.raise_for_status()
        
        # Verify we're getting an image
        content_type = response.headers.get('Content-Type', '')
        if not content_type.startswith('image/'):
            print("[WARNING] URL does not point to a standard image type")
            # We'll proceed but note this might not be an image
        
        # Check file size for safety (limit to 10MB)
        content_length = response.headers.get('Content-Length')
        if content_length and int(content_length) > 10 * 1024 * 1024:
            return False, "File size exceeds 10MB limit"
        
        # Check if we already have this image
        is_duplicate, existing_filename = is_duplicate_image(response.content)
        if is_duplicate:
            return True, f"Image already exists as {existing_filename}"
        
        # Get appropriate filename
        filename = extract_filename(url, content_type)
        filepath = os.path.join("Fetched_Images", filename)
        
        # Save the image
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        return True, f"Successfully fetched: {filename}"
        
    except requests.exceptions.RequestException as e:
        return False, f"Connection error: {e}"
    except Exception as e:
        return False, f"An error occurred: {e}"

def get_sample_image_urls():
    """Return some sample direct image URLs for testing"""
    return [
        "https://images.pexels.com/photos/2486168/pexels-photo-2486168.jpeg",
        "https://images.pexels.com/photos/417074/pexels-photo-417074.jpeg",
        "https://images.pexels.com/photos/933964/pexels-photo-933964.jpeg",
        "https://images.pexels.com/photos/206359/pexels-photo-206359.jpeg"
    ]

def main():
    print("=" * 60)
    print("Welcome to the Ubuntu Image Fetcher")
    print("A tool for mindfully collecting images from the web")
    print("=" * 60)
    
    # Create directory for images
    create_image_directory()
    
    print("\nIMPORTANT: Please provide a DIRECT link to an image file")
    print("(not a webpage like pexels.com/search/)")
    print("\nExample direct image URLs:")
    
    sample_urls = get_sample_image_urls()
    for i, url in enumerate(sample_urls[:2], 1):
        print(f"{i}. {url}")
    
    # Get URL from user
    url = input("\nPlease enter the DIRECT image URL (or press Enter for demo): ").strip()
    
    # Provide a default test URL if user just presses Enter
    if not url:
        url = sample_urls[0]
        print(f"\nUsing demo URL: {url}")
    
    # Validate URL format
    parsed_url = urlparse(url)
    if not parsed_url.scheme or not parsed_url.netloc:
        print("[ERROR] Invalid URL format. Please include http:// or https://")
        return
    
    # Check if it looks like a webpage URL rather than direct image
    if any(x in parsed_url.netloc for x in ['search', 'www.']) and not any(url.endswith(x) for x in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
        print("[WARNING] This looks like a webpage, not a direct image link!")
        print("Please find a direct image URL by:")
        print("1. Right-clicking on an image")
        print("2. Selecting 'Copy image address' or 'Open image in new tab'")
        print("3. Using that direct URL instead")
        return
    
    # Download the image
    success, message = download_image(url)
    
    if success:
        print(f"[SUCCESS] {message}")
        print("\nConnection strengthened. Community enriched.")
    else:
        print(f"[ERROR] {message}")
        print("\nWe apologize for the interruption in our connection.")

if __name__ == "__main__":
    main()