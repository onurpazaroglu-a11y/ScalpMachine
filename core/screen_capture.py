# SCREEN CAPTURE MODULE - Captures png image from saved area

import json
from PIL import ImageGrab
import os

def capture_screenshot():
    # Read the bounding box coordinates from ss.json
    try:
        with open('ss.json', 'r') as f:
            data = json.load(f)
        
        bbox = data['bbox']
        x = bbox['x']
        y = bbox['y']
        width = bbox['width']
        height = bbox['height']
        
        # Calculate the screen coordinates
        left = x
        top = y
        right = x + width
        bottom = y + height
        
        # Capture the screenshot
        screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
        
        # Get filename from user
        print("Enter filename for screenshot (without extension):")
        filename = input().strip()
        
        if not filename:
            print("No filename provided, using default 'screenshot'")
            filename = "screenshot"
        
        # Create capture directory if it doesn't exist
        capture_dir = "capture"
        if not os.path.exists(capture_dir):
            os.makedirs(capture_dir)
        
        # Save the screenshot to capture folder
        filepath = os.path.join(capture_dir, f"{filename}.png")
        
        screenshot.save(filepath)
        print(f"Screenshot saved as {filepath}")
        
    except FileNotFoundError:
        print("Error: ss.json file not found")
        return False
    except KeyError as e:
        print(f"Error: Invalid JSON format - missing key {e}")
        return False
    except Exception as e:
        print(f"Error capturing screenshot: {e}")
        return False
    
    return True

if __name__ == "__main__":
    capture_screenshot()
    
# TODO: Save klasör - isim şekli değişecek. data\screenshots\interval\timestamp.png olması gerekli