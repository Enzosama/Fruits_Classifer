import requests
from PIL import Image
import io
import os
import tempfile

def download_image(url):
    try:
        response = requests.get(url)
        #In bug trạng thái xấu
        response.raise_for_status()  
        image = Image.open(io.BytesIO(response.content))
        
        # Tạo file temp
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_filename = temp_file.name
            image.save(temp_filename, format="JPEG")
        
        return temp_filename
    #Show lỗi ra terminal để debug
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image: {e}")
        return None
    #Show lỗi ra terminal để debug
    except IOError as e:
        print(f"Error processing image: {e}")
        return None

def cleanup_temp_file(filename):
    try:
        os.remove(filename)
    #Show lỗi ra terminal để debug
    except OSError as e:
        print(f"Error deleting temporary file: {e}")