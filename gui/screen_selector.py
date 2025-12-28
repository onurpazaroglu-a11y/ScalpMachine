# SCREEN SELECTOR MODULE - Defines the area for ScreenCapturing

import json
from PIL import ImageGrab
import tkinter as tk

class ScreenCapture:
    def __init__(self):
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.bbox = None
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the main window
        
        # For drawing the selection rectangle
        self.canvas = None
        self.rect_id = None
        
    def select_area(self):
        """Allow user to select an area by drawing a bounding box"""
        print("Please select an area by dragging your mouse...")
        
        # Create a transparent overlay using a top-level window
        overlay = tk.Toplevel()
        overlay.attributes('-alpha', 0.3)
        overlay.attributes('-fullscreen', True)
        overlay.wm_overrideredirect(True)  # Remove window decorations
        
        # Create a canvas for drawing
        self.canvas = tk.Canvas(overlay, cursor="cross", bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind mouse events to the overlay
        overlay.bind('<Button-1>', self.on_mouse_down)
        overlay.bind('<B1-Motion>', self.on_mouse_drag)
        overlay.bind('<ButtonRelease-1>', self.on_mouse_up)
        
        # Start the event loop
        self.root.mainloop()
        
    def on_mouse_down(self, event):
        """Handle mouse down event"""
        self.start_x = event.x
        self.start_y = event.y
        
    def on_mouse_drag(self, event):
        """Handle mouse drag event"""
        if self.start_x is not None and self.start_y is not None:
            # Update the bounding box coordinates
            self.end_x = event.x
            self.end_y = event.y
            
            # Draw the rectangle as user drags
            if self.rect_id:
                self.canvas.delete(self.rect_id) # type: ignore
            
            # Create a rectangle to show current selection
            self.rect_id = self.canvas.create_rectangle( # type: ignore
                self.start_x, 
                self.start_y, 
                self.end_x, 
                self.end_y,
                outline='red', 
                width=2
            )
            
    def on_mouse_up(self, event):
        """Handle mouse up event"""
        self.end_x = event.x
        self.end_y = event.y
        
        # Calculate the bounding box
        if self.start_x is not None and self.start_y is not None:
            self.bbox = {
                'x': min(self.start_x, self.end_x),
                'y': min(self.start_y, self.end_y),
                'width': abs(self.end_x - self.start_x),
                'height': abs(self.end_y - self.start_y)
            }
            
        # Save the bounding box to JSON file
        self.save_bbox_to_json()
        
        # Close the overlay
        self.root.quit()
        
    def save_bbox_to_json(self):
        """Save the bounding box coordinates to a JSON file"""
        bbox_data = {
            'bbox': self.bbox
        }
        
        with open('data\screen.json', 'w') as f: # type: ignore
            json.dump(bbox_data, f, indent=4)
            json.dump(bbox_data, f, indent=4)
            
        print(f"Bounding box saved to ss.json: {self.bbox}")
        
    def capture_screenshot(self):
        """Capture screenshot of the selected area"""
        if self.bbox is None:
            print("No bounding box selected.")
            return
            
        # Capture the screen
        screenshot = ImageGrab.grab()
        
        # Crop to selected area
        cropped = screenshot.crop(
            (self.bbox['x'], 
            self.bbox['y'], 
            self.bbox['x'] + self.bbox['width'], 
            self.bbox['y'] + self.bbox['height'])
        )
        
        # Save the screenshot
        cropped.save('screenshot.png')
        print("Screenshot saved as screenshot.png")

# Example usage
if __name__ == "__main__":
    selector = ScreenCapture()
    selector.select_area()
    # selector.capture_screenshot()  # Commented out to avoid saving screenshot