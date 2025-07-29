import cv2
import numpy as np
import pyautogui
import time
import threading
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageGrab
import os
import keyboard  # For F1 hotkey detection

# Configure PyAutoGUI for better performance and reliability
pyautogui.FAILSAFE = False  # Disable fail-safe (moving mouse to corner won't stop)
pyautogui.PAUSE = 0.0       # NO PAUSE - instant actions for 240Hz gaming

class RobloxDigScript:
    def __init__(self):
        # Initialize main window
        self.root = tk.Tk()
        self.root.title("🎯 Roblox Dig Script - F1 Toggle Auto Clicker")
        self.root.geometry("500x700")
        self.root.configure(bg='#2b2b2b')
        self.root.resizable(True, True)
        self.root.minsize(400, 500)  # Minimum size to keep UI usable
        
        # Detection variables
        self.bar_region = None
        self.detecting = False
        self.auto_clicking = False
        self.preview_mode = False
        self.setting_region = False
        
        # Movement detection
        self.prev_frame = None
        self.movement_threshold = 200  # Lower threshold for more sensitive detection
        self.click_cooldown = 0.0  # NO DELAY - instant clicking
        self.last_click_time = 0
        self.last_slider_x = None
        
        # Statistics
        self.stats = {
            'frames_processed': 0,
            'clicks_made': 0,
            'movement_detected': 0,
            'start_time': time.time()
        }
        
        # Create UI
        self.create_interface()
        
        # Detection thread
        self.detection_thread = None
        
        # Setup F1 hotkey
        self.setup_hotkey()
        
        print("============================================================")
        print("🎯 ROBLOX DIG SCRIPT - F1 TOGGLE AUTO-CLICKER")
        print("============================================================")
        print("✅ Smart auto-clicker ready!")
        print("📋 Instructions:")
        print("   1. Make sure the Roblox digging minigame is visible")  
        print("   2. Click 'SELECT BAR AREA' and drag around the entire bar")
        print("   3. Press F1 to toggle auto-clicking ON/OFF")
        print("   4. The script will move mouse and click at perfect moments!")
        print("   5. Press F1 again to stop")
        
    def setup_hotkey(self):
        """Setup F1 hotkey for toggling"""
        try:
            keyboard.add_hotkey('f1', self.toggle_with_f1)
            print("🔥 F1 hotkey registered! Press F1 to toggle auto-clicking")
        except Exception as e:
            print(f"❌ Failed to setup F1 hotkey: {e}")
            
    def toggle_with_f1(self):
        """Toggle auto-clicking with F1 key"""
        if not self.bar_region:
            print("⚠️ Please select bar area first!")
            return
            
        if not self.auto_clicking:
            # Start auto-clicking
            self.preview_mode = False
            self.detecting = True
            self.auto_clicking = True
            self.stats['start_time'] = time.time()
            
            print("🟢 F1 PRESSED - AUTO-CLICKER STARTED!")
            print("🎯 Now aiming mouse and clicking automatically...")
            
            self.root.after(0, lambda: [
                self.start_button.config(text="🔥 F1 AUTO-CLICKER ACTIVE", bg='#ff4444'),
                self.detection_status.config(text="🔥 F1 Auto-clicking active", fg='#4CAF50'),
                self.status_label.config(text="🔥 F1 ACTIVE - Moving mouse and clicking automatically!", fg='#4CAF50')
            ])
            
            self.detection_thread = threading.Thread(target=self.detection_loop, daemon=True)
            self.detection_thread.start()
        else:
            # Stop auto-clicking
            self.detecting = False
            self.auto_clicking = False
            self.preview_mode = True
            
            print("🔴 F1 PRESSED - AUTO-CLICKER STOPPED!")
            print("👀 Back to preview mode...")
            
            self.root.after(0, lambda: [
                self.start_button.config(text="🚀 PRESS F1 TO START", bg='#4CAF50'),
                self.detection_status.config(text="🟡 Preview mode - Press F1 to start", fg='#FFC107'),
                self.status_label.config(text="🟡 PREVIEW MODE - Press F1 to start auto-clicking", fg='#FFC107')
            ])
            
            self.detection_thread = threading.Thread(target=self.preview_loop, daemon=True)
            self.detection_thread.start()
    
    def create_interface(self):
        """Create the user interface"""
        # Title
        title_frame = tk.Frame(self.root, bg='#2b2b2b')
        title_frame.pack(fill='x', padx=10, pady=10)
        
        title_label = tk.Label(title_frame, text="🎯 ROBLOX DIG SCRIPT", 
                              font=('Arial', 20, 'bold'), fg='#4CAF50', bg='#2b2b2b')
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="F1 Toggle Auto-Clicker", 
                                 font=('Arial', 12), fg='#FFC107', bg='#2b2b2b')
        subtitle_label.pack()
        
        # Setup section
        setup_frame = tk.LabelFrame(self.root, text="🔧 SETUP", font=('Arial', 12, 'bold'),
                                   fg='#4CAF50', bg='#2b2b2b', bd=2)
        setup_frame.pack(fill='x', padx=10, pady=5)
        
        # Region selection
        self.region_button = tk.Button(setup_frame, text="📍 SELECT BAR AREA", 
                                      command=self.select_bar_region,
                                      font=('Arial', 12, 'bold'), bg='#2196F3', fg='white',
                                      relief='raised', bd=3, padx=20, pady=10)
        self.region_button.pack(pady=10)
        
        self.region_status = tk.Label(setup_frame, text="❌ No bar area selected", 
                                     font=('Arial', 10), fg='#f44336', bg='#2b2b2b')
        self.region_status.pack(pady=5)
        
        # Control section
        control_frame = tk.LabelFrame(self.root, text="🎮 CONTROLS", font=('Arial', 12, 'bold'),
                                     fg='#4CAF50', bg='#2b2b2b', bd=2)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        # F1 instruction
        f1_label = tk.Label(control_frame, text="🔥 Press F1 to toggle auto-clicking ON/OFF", 
                           font=('Arial', 14, 'bold'), fg='#FF5722', bg='#2b2b2b')
        f1_label.pack(pady=10)
        
        # Start button (for visual feedback only)
        self.start_button = tk.Button(control_frame, text="🚀 PRESS F1 TO START", 
                                     font=('Arial', 12, 'bold'), bg='#4CAF50', fg='white',
                                     relief='raised', bd=3, padx=20, pady=10, state='disabled')
        self.start_button.pack(pady=10)
        
        # Status section
        status_frame = tk.LabelFrame(self.root, text="📊 STATUS", font=('Arial', 12, 'bold'),
                                    fg='#4CAF50', bg='#2b2b2b', bd=2)
        status_frame.pack(fill='x', padx=10, pady=5)
        
        self.detection_status = tk.Label(status_frame, text="⚪ Waiting for setup", 
                                        font=('Arial', 11, 'bold'), fg='#9E9E9E', bg='#2b2b2b')
        self.detection_status.pack(pady=5)
        
        self.status_label = tk.Label(status_frame, text="🔧 Select bar area first, then press F1", 
                                    font=('Arial', 10), fg='#9E9E9E', bg='#2b2b2b')
        self.status_label.pack(pady=5)
        
        # Detection preview
        preview_frame = tk.LabelFrame(self.root, text="🔍 DETECTION PREVIEW", font=('Arial', 12, 'bold'),
                                     fg='#4CAF50', bg='#2b2b2b', bd=2)
        preview_frame.pack(fill='x', padx=10, pady=5)
        
        self.canvas = tk.Canvas(preview_frame, width=430, height=280, bg='black', highlightthickness=0)
        self.canvas.pack(pady=10)
        
        # Statistics
        stats_frame = tk.LabelFrame(self.root, text="📈 STATISTICS", font=('Arial', 12, 'bold'),
                                   fg='#4CAF50', bg='#2b2b2b', bd=2)
        stats_frame.pack(fill='x', padx=10, pady=5)
        
        self.stats_label = tk.Label(stats_frame, text="📊 Ready to start", 
                                   font=('Arial', 10), fg='#9E9E9E', bg='#2b2b2b')
        self.stats_label.pack(pady=5)
        
    def select_bar_region(self):
        """Simple area selection tool - click and drag to select the bar region"""
        if self.setting_region:
            return
            
        self.setting_region = True
        self.root.withdraw()  # Hide main window temporarily
        
        # Take screenshot
        screenshot = ImageGrab.grab()
        screenshot_np = np.array(screenshot)
        
        # Create simple overlay window (not fullscreen)
        overlay = tk.Toplevel()
        overlay.title("Select Bar Area")
        overlay.geometry(f"{screenshot.width}x{screenshot.height}+0+0")
        overlay.attributes('-topmost', True)
        overlay.configure(cursor='crosshair')
        overlay.focus_force()
        
        # Convert screenshot to tkinter format
        screenshot_pil = Image.fromarray(screenshot_np)
        screenshot_tk = ImageTk.PhotoImage(screenshot_pil)
        
        # Create canvas showing your actual screen
        canvas = tk.Canvas(overlay, highlightthickness=0, cursor='crosshair')
        canvas.pack(fill='both', expand=True)
        canvas.create_image(0, 0, anchor='nw', image=screenshot_tk)
        
        # Add simple instruction text
        canvas.create_text(screenshot.width//2, 30, 
                          text="Click and drag to select the minigame bar area", 
                          fill='red', font=('Arial', 14, 'bold'))
        canvas.create_text(screenshot.width//2, 55, 
                          text="Press ESC to cancel", 
                          fill='white', font=('Arial', 12))
        
        # Selection variables
        start_x = start_y = 0
        rect_id = None
        text_ids = []
        
        def on_click(event):
            nonlocal start_x, start_y, rect_id, text_ids
            start_x, start_y = event.x, event.y
            
            # Clear instruction text
            for text_id in text_ids:
                canvas.delete(text_id)
            text_ids.clear()
            
            if rect_id:
                canvas.delete(rect_id)
            rect_id = canvas.create_rectangle(start_x, start_y, start_x, start_y, 
                                            outline='red', width=3)
        
        def on_drag(event):
            nonlocal rect_id
            if rect_id:
                # Update rectangle coordinates
                canvas.coords(rect_id, start_x, start_y, event.x, event.y)
                
                # Show dimensions
                w = abs(event.x - start_x)
                h = abs(event.y - start_y)
                mid_x = (start_x + event.x) // 2
                mid_y = (start_y + event.y) // 2
                
                # Clear previous dimension text
                for item in canvas.find_all():
                    if canvas.type(item) == 'text':
                        canvas.delete(item)
                
                # Add new dimension text
                text_id = canvas.create_text(mid_x, mid_y - 15, 
                                           text=f"{w} x {h}", 
                                           fill='red', font=('Arial', 12, 'bold'))
                text_ids.append(text_id)
        
        def on_release(event):
            nonlocal start_x, start_y
            end_x, end_y = event.x, event.y
            
            # Calculate selection area
            x = min(start_x, end_x)
            y = min(start_y, end_y)
            w = abs(end_x - start_x)
            h = abs(end_y - start_y)
            
            # Ensure minimum size
            if w < 50 or h < 20:
                messagebox.showerror("Selection Too Small", 
                                   f"Selection too small!\n\n" +
                                   f"Current: {w} x {h} pixels\n" +
                                   f"Minimum: 50 x 20 pixels\n\n" +
                                   "Please select a larger area around the bar.")
                overlay.destroy()
                self.root.deiconify()
                self.setting_region = False
                return
            
            # Save the bar region
            self.bar_region = (x, y, w, h)
            
            overlay.destroy()
            self.root.deiconify()
            self.setting_region = False
            
            # Update UI and start preview
            self.region_status.config(text=f"✅ Bar selected: {w}x{h} at ({x},{y})", fg='#4CAF50')
            self.start_button.config(state='normal')
            self.detection_status.config(text="🟡 Preview mode - Press F1 to start", fg='#FFC107')
            self.status_label.config(text="🟡 PREVIEW MODE - Press F1 to start auto-clicking", fg='#FFC107')
            
            # Start preview mode immediately
            self.preview_mode = True
            self.detecting = False
            self.auto_clicking = False
            self.detection_thread = threading.Thread(target=self.preview_loop, daemon=True)
            self.detection_thread.start()
            
            messagebox.showinfo("Area Selected!", 
                              f"✅ Bar area selected successfully!\n\n" +
                              f"📏 Size: {w} x {h} pixels\n" +
                              f"📍 Position: ({x}, {y})\n\n" +
                              f"🎯 Press F1 to start auto-clicking!")
        
        def on_escape(event):
            overlay.destroy()
            self.root.deiconify()
            self.setting_region = False
        
        # Bind events
        canvas.bind('<Button-1>', on_click)
        canvas.bind('<B1-Motion>', on_drag)
        canvas.bind('<ButtonRelease-1>', on_release)
        overlay.bind('<Escape>', on_escape)
        
        overlay.mainloop()
    
    def preview_loop(self):
        """Preview loop for showing detection without clicking"""
        while self.preview_mode and not self.auto_clicking:
            try:
                self.detect_slider_movement(preview_only=True)
                time.sleep(0.004)  # 250 FPS for 240Hz+ monitors
            except Exception as e:
                print(f"Preview error: {e}")
                break
    
    def detection_loop(self):
        """Main detection loop with auto-clicking"""
        while self.detecting and self.auto_clicking:
            try:
                self.detect_slider_movement(preview_only=False)
                time.sleep(0.004)  # 250 FPS - ultra fast for 240Hz
            except Exception as e:
                print(f"Detection error: {e}")
                break
        
    def detect_slider_movement(self, preview_only=False):
        """Detect slider movement and click when slider overlaps with different colored target area"""
        if not self.bar_region:
            return
            
        # Capture only the bar region
        x, y, w, h = self.bar_region
        img = ImageGrab.grab(bbox=(x, y, x+w, y+h))
        img_np = np.array(img)
        
        self.stats['frames_processed'] += 1
        
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
        
        movement_detected = False
        movement_amount = 0
        slider_position = None
        target_area = None
        should_click = False
        click_reason = "Waiting for movement"
        
        # Find the target area (different colored region)
        target_area = self.find_target_area(gray, img_np)
        
        if self.prev_frame is not None:
            # Calculate frame difference to detect movement
            diff = cv2.absdiff(gray, self.prev_frame)
            movement_amount = np.sum(diff > 30)
            movement_detected = movement_amount > self.movement_threshold
            
            if movement_detected:
                self.stats['movement_detected'] += 1
                
                # Find the center of movement (slider position)
                _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                if contours:
                    # Get the largest movement area (likely the slider)
                    largest_contour = max(contours, key=cv2.contourArea)
                    M = cv2.moments(largest_contour)
                    
                    if M["m00"] != 0:
                        slider_x = int(M["m10"] / M["m00"])
                        slider_y = int(M["m01"] / M["m00"])
                        slider_position = (slider_x, slider_y)
                        
                        # Check if slider overlaps with target area
                        if target_area:
                            should_click, distance = self.is_slider_in_target(slider_position, target_area)
                            if should_click:
                                if distance < 5:
                                    click_reason = "🎯 PERFECT TARGET HIT!"
                                else:
                                    click_reason = f"✅ Target overlap! ({distance:.1f}px from center)"
                            else:
                                click_reason = f"Slider {distance:.1f}px from target area"
                        else:
                            # AGGRESSIVE fallback to center detection if no target area found
                            center_x = w // 2
                            distance_from_center = abs(slider_x - center_x)
                            
                            # MUCH MORE GENEROUS center clicking
                            if distance_from_center < 60:  # Doubled the range
                                should_click = True
                                click_reason = f"Center fallback ({distance_from_center}px)"
                            else:
                                click_reason = f"No target detected, slider at {distance_from_center}px from center"
        
        # Store current frame for next comparison
        self.prev_frame = gray.copy()
        
        # Auto-click if conditions are met (only if not in preview mode)
        if should_click and self.auto_clicking and not preview_only:
            # NO COOLDOWN - CLICK IMMEDIATELY EVERY TIME
            try:
                # Calculate absolute screen coordinates for mouse click
                click_x = click_y = None
                
                if slider_position and target_area:
                    # Click at the CENTER of the target area, not slider position
                    bar_x, bar_y, bar_w, bar_h = self.bar_region
                    target_center_x = target_area['center_x']
                    target_center_y = target_area['center_y']
                    click_x = bar_x + target_center_x
                    click_y = bar_y + target_center_y
                elif slider_position:
                    # Fallback to slider position if no target area
                    bar_x, bar_y, bar_w, bar_h = self.bar_region
                    click_x = bar_x + slider_position[0]
                    click_y = bar_y + slider_position[1]
                
                # Perform the click if we have valid coordinates
                if click_x is not None and click_y is not None:
                    # INSTANT mouse movement and click - NO DELAYS
                    pyautogui.moveTo(click_x, click_y, duration=0.0)  # Instant movement
                    pyautogui.click(click_x, click_y)
                    
                    self.last_click_time = time.time()
                    self.stats['clicks_made'] += 1
                    
                    print(f"🎯 INSTANT CLICK! {click_reason} at ({click_x}, {click_y}) (Total: {self.stats['clicks_made']})")
                    
                    # Also update the UI to show the click happened
                    self.root.after(0, lambda: self.status_label.config(
                        text=f"🎯 INSTANT CLICK! {click_reason} (Total: {self.stats['clicks_made']})", 
                        fg='#00FF00'
                    ))
                    
            except Exception as e:
                print(f"❌ Click failed: {e}")
                self.root.after(0, lambda: self.status_label.config(
                    text=f"❌ Click failed: {e}", 
                    fg='#FF0000'
                ))
        elif should_click and not self.auto_clicking:
            print(f"🔍 WOULD CLICK (Preview mode): {click_reason}")
        elif should_click and preview_only:
            print(f"👀 WOULD CLICK (Preview only): {click_reason}")
        elif not should_click and self.auto_clicking:
            print(f"⏸️ Not clicking: {click_reason}")
        
        # Update display
        self.update_display(img_np, movement_detected, movement_amount, slider_position, target_area, should_click, click_reason, preview_only)
    
    def find_target_area(self, gray, img_np):
        """Find the target area by detecting smaller distinct regions within the bar"""
        h, w = gray.shape
        
        # Use a more focused approach - look for smaller distinct areas
        # that are clearly different from their immediate surroundings
        
        # Method 1: Local contrast analysis
        # Look for areas that stand out from their immediate neighborhood
        target_candidates = []
        
        # Create a blurred version to compare against
        blurred = cv2.GaussianBlur(gray, (15, 15), 0)
        
        # Find areas with high local contrast
        contrast = cv2.absdiff(gray, blurred)
        
        # Threshold to find significant contrast areas
        _, contrast_mask = cv2.threshold(contrast, 20, 255, cv2.THRESH_BINARY)
        
        # Clean up the mask
        kernel = np.ones((5, 5), np.uint8)
        contrast_mask = cv2.morphologyEx(contrast_mask, cv2.MORPH_OPEN, kernel)
        contrast_mask = cv2.morphologyEx(contrast_mask, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(contrast_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            # Look for smaller, more specific areas (not the whole bar)
            if 100 < area < w * h * 0.3:  # Smaller max size
                x, y, w_area, h_area = cv2.boundingRect(contour)
                
                # Check aspect ratio - target areas are usually not too extreme
                aspect_ratio = w_area / max(h_area, 1)
                if 0.3 <= aspect_ratio <= 3.0:
                    
                    # Calculate local contrast score
                    region = gray[y:y+h_area, x:x+w_area]
                    region_blur = blurred[y:y+h_area, x:x+w_area]
                    local_contrast = np.mean(cv2.absdiff(region, region_blur))
                    
                    target_candidates.append({
                        'type': 'local_contrast',
                        'x': x,
                        'y': y,
                        'w': w_area,
                        'h': h_area,
                        'center_x': x + w_area // 2,
                        'center_y': y + h_area // 2,
                        'area': area,
                        'difference_score': local_contrast,
                        'region_brightness': np.mean(region)
                    })
        
        # Method 2: Edge density analysis for distinct patterns
        edges = cv2.Canny(gray, 50, 150)
        
        # Use smaller kernels to find more localized features
        kernel_small = np.ones((3, 3), np.uint8)
        edges_dilated = cv2.dilate(edges, kernel_small, iterations=1)
        
        edge_contours, _ = cv2.findContours(edges_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in edge_contours:
            area = cv2.contourArea(contour)
            if 80 < area < w * h * 0.25:  # Even smaller for edge detection
                x, y, w_area, h_area = cv2.boundingRect(contour)
                aspect_ratio = w_area / max(h_area, 1)
                
                if 0.3 <= aspect_ratio <= 3.0:
                    # Calculate edge density
                    region_edges = edges[y:y+h_area, x:x+w_area]
                    edge_density = np.sum(region_edges > 0) / (w_area * h_area)
                    
                    if edge_density > 0.1:  # Higher threshold for more distinct features
                        target_candidates.append({
                            'type': 'edge_pattern',
                            'x': x,
                            'y': y,
                            'w': w_area,
                            'h': h_area,
                            'center_x': x + w_area // 2,
                            'center_y': y + h_area // 2,
                            'area': area,
                            'difference_score': edge_density * 200,  # Boost edge scores
                            'region_brightness': np.mean(gray[y:y+h_area, x:x+w_area])
                        })
        
        # Method 3: Color segment analysis
        hsv = cv2.cvtColor(img_np, cv2.COLOR_BGR2HSV)
        
        # Use K-means to find distinct color segments
        data = hsv.reshape((-1, 3))
        data = np.float32(data)
        
        # Use fewer clusters to find main color groups
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        k = min(4, len(np.unique(data.reshape(-1))))  # Max 4 clusters
        
        if k > 1:
            _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            # Reshape labels back to image shape
            labels = labels.reshape(hsv.shape[:2])
            
            # Find the least common cluster (likely the target)
            unique_labels, counts = np.unique(labels, return_counts=True)
            
            # Sort by count (ascending) to find minority segments
            sorted_indices = np.argsort(counts)
            
            for i in range(min(2, len(sorted_indices))):  # Check top 2 minority segments
                label = unique_labels[sorted_indices[i]]
                count = counts[sorted_indices[i]]
                
                # Only consider segments that are not too small or too large
                if w * h * 0.05 < count < w * h * 0.4:
                    # Create mask for this segment
                    segment_mask = (labels == label).astype(np.uint8)
                    
                    # Find contours of this segment
                    seg_contours, _ = cv2.findContours(segment_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    
                    for contour in seg_contours:
                        area = cv2.contourArea(contour)
                        if 100 < area < w * h * 0.3:
                            x, y, w_area, h_area = cv2.boundingRect(contour)
                            aspect_ratio = w_area / max(h_area, 1)
                            
                            if 0.3 <= aspect_ratio <= 3.0:
                                # Score based on how much this segment stands out
                                rarity_score = (1.0 - count / (w * h)) * 100
                                
                                target_candidates.append({
                                    'type': 'color_segment',
                                    'x': x,
                                    'y': y,
                                    'w': w_area,
                                    'h': h_area,
                                    'center_x': x + w_area // 2,
                                    'center_y': y + h_area // 2,
                                    'area': area,
                                    'difference_score': rarity_score,
                                    'region_brightness': np.mean(gray[y:y+h_area, x:x+w_area])
                                })
        
        # Select the best candidate with improved logic
        if target_candidates:
            # Remove overlapping candidates
            unique_candidates = []
            for candidate in sorted(target_candidates, key=lambda x: x['difference_score'], reverse=True):
                is_overlap = False
                for existing in unique_candidates:
                    # Check overlap
                    distance = np.sqrt((candidate['center_x'] - existing['center_x'])**2 + 
                                     (candidate['center_y'] - existing['center_y'])**2)
                    if distance < 25:
                        is_overlap = True
                        break
                
                if not is_overlap:
                    unique_candidates.append(candidate)
            
            if unique_candidates:
                # Prefer smaller, more distinct areas
                best_candidate = unique_candidates[0]
                
                # Additional filtering - reject if too large or positioned poorly
                if best_candidate['area'] < w * h * 0.4:  # Not too large
                    
                    # Add brightness classification
                    mean_brightness = np.mean(gray)
                    std_brightness = np.std(gray)
                    
                    if best_candidate['region_brightness'] > mean_brightness + std_brightness * 0.1:
                        best_candidate['brightness_type'] = 'brighter'
                    elif best_candidate['region_brightness'] < mean_brightness - std_brightness * 0.1:
                        best_candidate['brightness_type'] = 'darker'
                    else:
                        best_candidate['brightness_type'] = 'similar'
                    
                    return best_candidate
        
        return None
    
    def is_slider_in_target(self, slider_position, target_area):
        """Check if slider overlaps with the target area - ULTRA AGGRESSIVE CLICKING"""
        if not slider_position or not target_area:
            return False, float('inf')
        
        slider_x, slider_y = slider_position
        
        # Get target bounds
        target_left = target_area['x']
        target_right = target_area['x'] + target_area['w']
        target_top = target_area['y']
        target_bottom = target_area['y'] + target_area['h']
        target_center_x = target_area['center_x']
        target_center_y = target_area['center_y']
        
        # MUCH MORE GENEROUS overlap detection - click more often!
        tolerance_x = max(25, target_area['w'] * 0.5)  # 50% of target width or 25px minimum
        tolerance_y = max(15, target_area['h'] * 0.5)   # 50% of target height or 15px minimum
        
        # Check if slider is within VERY expanded target bounds
        if (target_left - tolerance_x <= slider_x <= target_right + tolerance_x and
            target_top - tolerance_y <= slider_y <= target_bottom + tolerance_y):
            
            # Calculate distance from target center
            distance = np.sqrt((slider_x - target_center_x)**2 + (slider_y - target_center_y)**2)
            
            return True, distance
        else:
            # Calculate distance to target center
            distance = np.sqrt((slider_x - target_center_x)**2 + (slider_y - target_center_y)**2)
            return False, distance
    
    def update_display(self, img_np, movement_detected, movement_amount, slider_position, target_area, should_click, click_reason, preview_only=False):
        """Update the visual display"""
        # Resize image for display
        display_img = cv2.resize(img_np, (430, 280))
        scale_x = 430 / img_np.shape[1]
        scale_y = 280 / img_np.shape[0]
        
        # Draw target area if detected
        if target_area:
            tx = int(target_area['x'] * scale_x)
            ty = int(target_area['y'] * scale_y)
            tw = int(target_area['w'] * scale_x)
            th = int(target_area['h'] * scale_y)
            
            # Color based on target type and brightness
            if target_area['type'] == 'local_contrast':
                if target_area.get('brightness_type') == 'brighter':
                    color = (0, 255, 255)  # Yellow for brighter areas
                elif target_area.get('brightness_type') == 'darker':
                    color = (255, 0, 255)  # Magenta for darker areas
                else:
                    color = (0, 255, 0)    # Green for similar brightness but different
            elif target_area['type'] == 'color_segment':
                color = (255, 165, 0)      # Orange for color segments
            elif target_area['type'] == 'edge_pattern':
                color = (0, 128, 255)      # Light blue for edge patterns
            else:
                color = (255, 255, 255)    # White for unknown
            
            # Draw target area rectangle
            cv2.rectangle(display_img, (tx, ty), (tx + tw, ty + th), color, 2)
            
            # Create descriptive label
            if target_area['type'] == 'brightness_diff':
                label = f"TARGET ({target_area.get('brightness_type', 'diff')})"
            else:
                label = f"TARGET ({target_area['type']})"
            
            cv2.putText(display_img, label, 
                       (tx, ty - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
            
            # Draw center point WHERE MOUSE WILL CLICK
            center_x = int(target_area['center_x'] * scale_x)
            center_y = int(target_area['center_y'] * scale_y)
            cv2.circle(display_img, (center_x, center_y), 6, (0, 0, 255), -1)  # Red circle for click point
            cv2.circle(display_img, (center_x, center_y), 8, (255, 255, 255), 2)  # White outline
            cv2.putText(display_img, "CLICK HERE", (center_x - 35, center_y - 15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
            
            # Show difference score for debugging
            score_text = f"Score: {target_area['difference_score']:.1f}"
            cv2.putText(display_img, score_text, 
                       (tx, ty + th + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 1)
        else:
            # Draw fallback center line if no target detected
            center_x = display_img.shape[1] // 2
            cv2.line(display_img, (center_x, 0), (center_x, display_img.shape[0]), (128, 128, 128), 1)
            cv2.putText(display_img, "NO TARGET DETECTED", (center_x - 70, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128, 128, 128), 1)
        
        # Draw slider position if detected
        if slider_position:
            sx = int(slider_position[0] * scale_x)
            sy = int(slider_position[1] * scale_y)
            color = (0, 255, 0) if should_click else (0, 0, 255)
            cv2.circle(display_img, (sx, sy), 8, color, -1)
            cv2.putText(display_img, "SLIDER", (sx - 25, sy - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        
        # Add mode indicator
        if preview_only:
            cv2.putText(display_img, "PREVIEW MODE", 
                       (10, display_img.shape[0] - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        # Add status indicators
        if should_click:
            cv2.rectangle(display_img, (0, 0), (display_img.shape[1]-1, display_img.shape[0]-1), 
                         (0, 255, 0), 4)
            status_text = "WOULD CLICK!" if preview_only else "CLICKING NOW!"
            cv2.putText(display_img, status_text, 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        elif movement_detected:
            cv2.rectangle(display_img, (0, 0), (display_img.shape[1]-1, display_img.shape[0]-1), 
                         (0, 165, 255), 2)
            cv2.putText(display_img, f"Movement: {movement_amount:.0f}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
        else:
            cv2.putText(display_img, f"Watching... ({movement_amount:.0f})", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (128, 128, 128), 2)
        
        # Add click reason
        cv2.putText(display_img, click_reason, 
                   (10, display_img.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        # Convert to tkinter format
        display_rgb = cv2.cvtColor(display_img, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(display_rgb)
        tk_image = ImageTk.PhotoImage(pil_image)
        
        # Update canvas
        self.canvas.delete("all")
        self.canvas.create_image(215, 140, image=tk_image) # Center image
        self.canvas.image = tk_image
        
        # Update statistics
        self.update_statistics(movement_amount, should_click, preview_only)
    
    def update_statistics(self, current_movement, should_click=False, preview_only=False):
        """Update statistics display"""
        elapsed_time = time.time() - self.stats['start_time']
        fps = self.stats['frames_processed'] / max(1, elapsed_time)
        
        mode_text = "PREVIEW MODE" if preview_only else "AUTO-CLICKER MODE"
        
        stats_text = f"""
🎯 ROBLOX DIG SCRIPT STATS
==========================
Mode: {mode_text}
Runtime: {elapsed_time:.1f}s
Frames Processed: {self.stats['frames_processed']:,}
Current FPS: {fps:.1f}

🎮 DETECTION RESULTS
==========================
Movement Events: {self.stats['movement_detected']:,}
Total Clicks: {self.stats['clicks_made']:,}
Current Movement: {current_movement:.0f}
Sensitivity: {self.movement_threshold}

⚙️ SYSTEM STATUS
==========================
Bar Area: {'✅ Selected' if self.bar_region else '❌ Not Set'}
Detection: {'🟢 Active' if (self.detecting or self.preview_mode) else '🔴 Stopped'}
Auto-Click: {'🎯 Ready!' if should_click and not preview_only else '🟡 Preview/Waiting'}

📊 PERFORMANCE
==========================
"""
        
        if self.stats['movement_detected'] > 0:
            detection_rate = (self.stats['movement_detected'] / self.stats['frames_processed']) * 100
            stats_text += f"Movement Detection Rate: {detection_rate:.1f}%\n"
            
        if self.stats['clicks_made'] > 0:
            clicks_per_minute = (self.stats['clicks_made'] / elapsed_time) * 60
            stats_text += f"Clicks per Minute: {clicks_per_minute:.1f}\n"
        
        self.stats_label.config(text=stats_text)
    
    def run(self):
        """Start the application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Clean up on exit"""
        self.detecting = False
        self.preview_mode = False
        self.auto_clicking = False
        if self.detection_thread:
            self.detection_thread.join(timeout=1)
        self.root.destroy()

def main():
    app = RobloxDigScript()
    app.run()

if __name__ == "__main__":
    main() 