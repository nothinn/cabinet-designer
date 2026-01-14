import json
import sys
import os

# Try to import PIL
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Error: Pillow library not found. Please install it using 'pip install pillow'")
    sys.exit(1)

# Configuration
SCALE = 5.0  # Pixels per cm
MARGIN = 100 # Pixels
THICKNESS = 1.8 # cm (Material thickness)

# Colors
COLOR_BG = (255, 255, 255)       # White background
COLOR_OUTLINE = (60, 60, 60)     # Dark Grey outlines
COLOR_CARCASS = (245, 245, 245)  # Off-white for interiors
COLOR_EDGE = (220, 220, 220)     # Cut edge color
COLOR_DOOR = (222, 184, 135)     # Burlywood / Light Oak
COLOR_HANDLE = (50, 50, 50)      # Dark handles
COLOR_TEXT = (0, 0, 0)

def load_config(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def draw_rect(draw, x_cm, y_cm, w_cm, h_cm, fill, outline=None, canvas_height=0):
    """
    Draws a rectangle in CM coordinates.
    x, y: Bottom-Left corner in CM.
    """
    x1 = MARGIN + x_cm * SCALE
    y1 = canvas_height - MARGIN - (y_cm * SCALE)
    
    x2 = MARGIN + (x_cm + w_cm) * SCALE
    y2 = canvas_height - MARGIN - ((y_cm + h_cm) * SCALE)
    
    draw.rectangle([x1, y2, x2, y1], fill=fill, outline=outline, width=2)

def draw_circle(draw, x_cm, y_cm, r_cm, fill, canvas_height):
    cx = MARGIN + x_cm * SCALE
    cy = canvas_height - MARGIN - (y_cm * SCALE)
    r = r_cm * SCALE
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)

def render_cabinet(config_file, output_file):
    if not os.path.exists(config_file):
        print(f"File {config_file} not found.")
        return

    data = load_config(config_file)
    
    total_h = data.get('total_height', 240.0)
    bot_h = data.get('bottom_height', 80.0)
    plinth_h = data.get('plinth_height', 8.0)
    columns = data.get('columns', [])
    
    total_w = sum(c['width'] for c in columns)
    
    # Image Dimensions
    img_w = int((total_w * SCALE) + (MARGIN * 2))
    img_h = int((total_h * SCALE) + (MARGIN * 2))
    
    im = Image.new('RGB', (img_w, img_h), COLOR_BG)
    draw = ImageDraw.Draw(im)
    
    # Try to load a font
    try:
        font = ImageFont.truetype("arial.ttf", 20)
        title_font = ImageFont.truetype("arial.ttf", 30)
        small_font = ImageFont.truetype("arial.ttf", 10)
    except IOError:
        font = None
        title_font = None
        small_font = None

    # Draw Floor Line
    floor_y = img_h - MARGIN
    draw.line([MARGIN - 50, floor_y, img_w - MARGIN + 50, floor_y], fill=COLOR_OUTLINE, width=3)
    
    current_x = 0.0
    
    i = 0
    while i < len(columns):
        col = columns[i]
        w = col['width']
        
        # Determine merged group
        merged_group_indices = [i]
        temp_idx = i
        while temp_idx < len(columns) - 1 and columns[temp_idx].get('merge_right', False):
            temp_idx += 1
            merged_group_indices.append(temp_idx)
            
        group_w = sum(columns[g]['width'] for g in merged_group_indices)
        group_has_top = any(columns[g].get('has_top', True) for g in merged_group_indices)
        master_col = columns[i]
        
        # --- 1. Bottom Modules (Always individual) ---
        for g_idx in merged_group_indices:
            col_g = columns[g_idx]
            w_g = col_g['width']
            drawers = col_g.get('drawers', [])
            
            # Calculate x for this specific base
            x_g = current_x + sum(columns[k]['width'] for k in range(i, g_idx))
            
            # Draw Plinth (Recessed)
            draw_rect(draw, x_g + 2, 0, w_g - 4, plinth_h, (50, 50, 50), None, img_h)
            
            # Draw Main Box (above plinth)
            box_h = bot_h - plinth_h
            base_y = plinth_h
            
            # Start drawing content from top of base section (base_y + box_h) downwards
            # Or simpler: base_y is bottom. top is base_y + box_h.
            # Drawers start at top.
            
            current_y_top = base_y + box_h
            
            if drawers:
                for d in drawers:
                    d_h = d['height']
                    # Draw drawer
                    # Y pos: current_y_top - d_h
                    d_y = current_y_top - d_h
                    draw_rect(draw, x_g, d_y, w_g, d_h, COLOR_DOOR, COLOR_OUTLINE, img_h)
                    # Handle
                    draw_rect(draw, x_g + w_g/2 - 5, d_y + d_h - 5, 10, 2, COLOR_HANDLE, None, img_h)
                    
                    current_y_top -= d_h
            
            # Remaining space? Draw door
            remaining_h = current_y_top - base_y
            if remaining_h > 1.0: # If notable space remains
                draw_rect(draw, x_g, base_y, w_g, remaining_h, COLOR_DOOR, COLOR_OUTLINE, img_h)
                
                if w_g == 80:
                    mid_x = x_g + (w_g / 2)
                    x_px = MARGIN + mid_x * SCALE
                    draw.line([x_px, img_h - MARGIN - (base_y*SCALE), x_px, img_h - MARGIN - ((base_y+remaining_h) * SCALE)], fill=COLOR_OUTLINE, width=2)
                    draw_circle(draw, x_g + (w_g/2) - 3, base_y + remaining_h - 10, 1, COLOR_HANDLE, img_h)
                    draw_circle(draw, x_g + (w_g/2) + 3, base_y + remaining_h - 10, 1, COLOR_HANDLE, img_h)
                else:
                    draw_circle(draw, x_g + w_g - 5, base_y + remaining_h - 10, 1, COLOR_HANDLE, img_h)
            
            # Width label (individual for each base)
            text = f"{w_g}cm"
            bbox = draw.textbbox((0, 0), text, font=font)
            tw = bbox[2] - bbox[0]
            draw.text((MARGIN + (x_g + w_g/2)*SCALE - tw/2, img_h - MARGIN + 10), text, fill=COLOR_TEXT, font=font)

        # --- 2. Top Module (Merged group) ---
        if group_has_top:
            # Side Panels (Outer)
            draw_rect(draw, current_x, bot_h, THICKNESS, total_h - bot_h, COLOR_CARCASS, COLOR_OUTLINE, img_h)
            draw_rect(draw, current_x + group_w - THICKNESS, bot_h, THICKNESS, total_h - bot_h, COLOR_CARCASS, COLOR_OUTLINE, img_h)
            
            # Top Cap and Countertop (Full group width)
            draw_rect(draw, current_x, total_h - THICKNESS, group_w, THICKNESS, COLOR_CARCASS, COLOR_OUTLINE, img_h)
            draw_rect(draw, current_x, bot_h - THICKNESS, group_w, THICKNESS, COLOR_CARCASS, COLOR_OUTLINE, img_h)
            
            shelves = master_col.get('shelf_heights', [])
            dividers = master_col.get('vertical_dividers', [])
            sorted_shelves = sorted(shelves)
            all_bounds = [bot_h] + sorted_shelves + [total_h]
            
            for j in range(len(all_bounds) - 1):
                low, high = all_bounds[j], all_bounds[j+1]
                diff = high - low
                
                # Height Label
                mid_z = (low + high) / 2
                h_text = f"{diff:.1f}"
                tx = MARGIN + (current_x + 2) * SCALE
                ty = img_h - MARGIN - (mid_z * SCALE) - 5
                draw.text((tx, ty), h_text, fill=(150, 150, 150), font=small_font)
                
                # Vertical Divider (Centered in merged group)
                if j in dividers:
                    mid_x = current_x + (group_w / 2)
                    draw_rect(draw, mid_x - THICKNESS/2, low, THICKNESS, high - low, COLOR_CARCASS, COLOR_OUTLINE, img_h)

            # Shelves (Span full group)
            for h in sorted_shelves:
                if bot_h < h < total_h:
                    draw_rect(draw, current_x + THICKNESS, h - THICKNESS, group_w - 2*THICKNESS, THICKNESS, COLOR_CARCASS, COLOR_OUTLINE, img_h)
        
        current_x += group_w
        i = temp_idx + 1

    # Total Dimensions
    info_text = f"Total Width: {total_w}cm | Total Height: {total_h}cm"
    draw.text((MARGIN, MARGIN/2), info_text, fill=COLOR_TEXT, font=title_font)

    im.save(output_file)
    print(f"Render saved to {output_file}")

def render_cabinet_to_bytes(designer_obj):
    """
    Renders the cabinet configuration to a PNG byte stream.
    Accepts a CabinetDesigner instance or a dict.
    """
    import io
    
    # Extract data
    if isinstance(designer_obj, dict):
        data = designer_obj
    else:
        # Assuming it's the CabinetDesigner class
        data = {
            'total_height': designer_obj.total_height,
            'bottom_height': designer_obj.bottom_height,
            'plinth_height': designer_obj.plinth_height,
            'columns': designer_obj.columns
        }
    
    total_h = data.get('total_height', 240.0)
    bot_h = data.get('bottom_height', 80.0)
    plinth_h = data.get('plinth_height', 8.0)
    columns = data.get('columns', [])
    
    total_w = sum(c['width'] for c in columns)
    
    # Image Dimensions
    img_w = int((total_w * SCALE) + (MARGIN * 2))
    img_h = int((total_h * SCALE) + (MARGIN * 2))
    
    im = Image.new('RGB', (img_w, img_h), COLOR_BG)
    draw = ImageDraw.Draw(im)
    
    # Try to load a font
    try:
        # In PyScript environment, arial.ttf might not exist.
        # Fallback to default if load fails
        font = ImageFont.truetype("arial.ttf", 20)
        title_font = ImageFont.truetype("arial.ttf", 30)
        small_font = ImageFont.truetype("arial.ttf", 10)
    except IOError:
        font = ImageFont.load_default()
        title_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # Draw Floor Line
    floor_y = img_h - MARGIN
    draw.line([MARGIN - 50, floor_y, img_w - MARGIN + 50, floor_y], fill=COLOR_OUTLINE, width=3)
    
    current_x = 0.0
    
    i = 0
    while i < len(columns):
        col = columns[i]
        w = col['width']
        
        # Determine merged group
        merged_group_indices = [i]
        temp_idx = i
        while temp_idx < len(columns) - 1 and columns[temp_idx].get('merge_right', False):
            temp_idx += 1
            merged_group_indices.append(temp_idx)
            
        group_w = sum(columns[g]['width'] for g in merged_group_indices)
        group_has_top = any(columns[g].get('has_top', True) for g in merged_group_indices)
        master_col = columns[i]
        
        # --- 1. Bottom Modules (Always individual) ---
        for g_idx in merged_group_indices:
            col_g = columns[g_idx]
            w_g = col_g['width']
            drawers = col_g.get('drawers', [])
            
            # Calculate x for this specific base
            x_g = current_x + sum(columns[k]['width'] for k in range(i, g_idx))
            
            # Draw Plinth (Recessed)
            draw_rect(draw, x_g + 2, 0, w_g - 4, plinth_h, (50, 50, 50), None, img_h)
            
            # Draw Main Box (above plinth)
            box_h = bot_h - plinth_h
            base_y = plinth_h
            
            # Start drawing content from top of base section (base_y + box_h) downwards
            # Or simpler: base_y is bottom. top is base_y + box_h.
            # Drawers start at top.
            
            current_y_top = base_y + box_h
            
            if drawers:
                for d in drawers:
                    d_h = d['height']
                    # Draw drawer
                    # Y pos: current_y_top - d_h
                    d_y = current_y_top - d_h
                    draw_rect(draw, x_g, d_y, w_g, d_h, COLOR_DOOR, COLOR_OUTLINE, img_h)
                    # Handle
                    draw_rect(draw, x_g + w_g/2 - 5, d_y + d_h - 5, 10, 2, COLOR_HANDLE, None, img_h)
                    
                    current_y_top -= d_h
            
            # Remaining space? Draw door
            remaining_h = current_y_top - base_y
            if remaining_h > 1.0: # If notable space remains
                draw_rect(draw, x_g, base_y, w_g, remaining_h, COLOR_DOOR, COLOR_OUTLINE, img_h)
                
                if w_g == 80:
                    mid_x = x_g + (w_g / 2)
                    x_px = MARGIN + mid_x * SCALE
                    draw.line([x_px, img_h - MARGIN - (base_y*SCALE), x_px, img_h - MARGIN - ((base_y+remaining_h) * SCALE)], fill=COLOR_OUTLINE, width=2)
                    draw_circle(draw, x_g + (w_g/2) - 3, base_y + remaining_h - 10, 1, COLOR_HANDLE, img_h)
                    draw_circle(draw, x_g + (w_g/2) + 3, base_y + remaining_h - 10, 1, COLOR_HANDLE, img_h)
                else:
                    draw_circle(draw, x_g + w_g - 5, base_y + remaining_h - 10, 1, COLOR_HANDLE, img_h)
            
            # Width label (individual for each base)
            text = f"{w_g}cm"
            if font:
                bbox = draw.textbbox((0, 0), text, font=font)
                tw = bbox[2] - bbox[0]
                draw.text((MARGIN + (x_g + w_g/2)*SCALE - tw/2, img_h - MARGIN + 10), text, fill=COLOR_TEXT, font=font)
            else:
                # Fallback text drawing if font weird
                pass

        # --- 2. Top Module (Merged group) ---
        if group_has_top:
            # Side Panels (Outer)
            draw_rect(draw, current_x, bot_h, THICKNESS, total_h - bot_h, COLOR_CARCASS, COLOR_OUTLINE, img_h)
            draw_rect(draw, current_x + group_w - THICKNESS, bot_h, THICKNESS, total_h - bot_h, COLOR_CARCASS, COLOR_OUTLINE, img_h)
            
            # Top Cap and Countertop (Full group width)
            draw_rect(draw, current_x, total_h - THICKNESS, group_w, THICKNESS, COLOR_CARCASS, COLOR_OUTLINE, img_h)
            draw_rect(draw, current_x, bot_h - THICKNESS, group_w, THICKNESS, COLOR_CARCASS, COLOR_OUTLINE, img_h)
            
            shelves = master_col.get('shelf_heights', [])
            dividers = master_col.get('vertical_dividers', [])
            sorted_shelves = sorted(shelves)
            all_bounds = [bot_h] + sorted_shelves + [total_h]
            
            for j in range(len(all_bounds) - 1):
                low, high = all_bounds[j], all_bounds[j+1]
                diff = high - low
                
                # Height Label
                mid_z = (low + high) / 2
                h_text = f"{diff:.1f}"
                tx = MARGIN + (current_x + 2) * SCALE
                ty = img_h - MARGIN - (mid_z * SCALE) - 5
                if small_font:
                    draw.text((tx, ty), h_text, fill=(150, 150, 150), font=small_font)
                
                # Vertical Divider (Centered in merged group)
                if j in dividers:
                    mid_x = current_x + (group_w / 2)
                    draw_rect(draw, mid_x - THICKNESS/2, low, THICKNESS, high - low, COLOR_CARCASS, COLOR_OUTLINE, img_h)

            # Shelves (Span full group)
            for h in sorted_shelves:
                if bot_h < h < total_h:
                    draw_rect(draw, current_x + THICKNESS, h - THICKNESS, group_w - 2*THICKNESS, THICKNESS, COLOR_CARCASS, COLOR_OUTLINE, img_h)
        
        current_x += group_w
        i = temp_idx + 1

    # Total Dimensions
    info_text = f"Total Width: {total_w}cm | Total Height: {total_h}cm"
    if title_font:
        draw.text((MARGIN, MARGIN/2), info_text, fill=COLOR_TEXT, font=title_font)

    # Output to bytes
    img_byte_arr = io.BytesIO()
    im.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python render_cabinet.py <config.json> [output.png]")
    else:
        cfg, out = sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "cabinet_render.png"
        render_cabinet(cfg, out)