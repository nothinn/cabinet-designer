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

def render_cabinet_to_svg(designer_obj):
    """
    Renders the cabinet configuration to an SVG string.
    """
    # Extract data
    if isinstance(designer_obj, dict):
        data = designer_obj
    else:
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
    
    svg = f'<svg width="{img_w}" height="{img_h}" viewBox="0 0 {img_w} {img_h}" xmlns="http://www.w3.org/2000/svg" style="background:white;">\n'
    
    # Helper for coordinates conversion (Y-flip)
    def to_svg_y(y_cm):
        return img_h - MARGIN - (y_cm * SCALE)

    def svg_rect(x_cm, y_cm, w_cm, h_cm, fill, outline="none"):
        x = MARGIN + x_cm * SCALE
        # y in PIL logic is top-left, but input is bottom-left in CM.
        # SVG Y is top-down. 
        # y_cm is bottom of rect. y_cm + h_cm is top of rect.
        # Top of rect in SVG pixels:
        y_px = to_svg_y(y_cm + h_cm)
        w_px = w_cm * SCALE
        h_px = h_cm * SCALE
        
        stroke = f'stroke="{outline}" stroke-width="2"' if outline != "none" else ""
        return f'<rect x="{x:.1f}" y="{y_px:.1f}" width="{w_px:.1f}" height="{h_px:.1f}" fill="{fill}" {stroke} />'

    def svg_line(x1_px, y1_px, x2_px, y2_px, color, width=2):
        return f'<line x1="{x1_px:.1f}" y1="{y1_px:.1f}" x2="{x2_px:.1f}" y2="{y2_px:.1f}" stroke="{color}" stroke-width="{width}" />'

    def svg_circle(x_cm, y_cm, r_cm, fill):
        cx = MARGIN + x_cm * SCALE
        cy = to_svg_y(y_cm)
        r = r_cm * SCALE
        return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" />'
    
    def svg_text(x_px, y_px, content, size=16, color="black"):
        # y_px in SVG text is baseline. 
        return f'<text x="{x_px:.1f}" y="{y_px:.1f}" font-family="Arial, sans-serif" font-size="{size}" fill="{color}" text-anchor="middle">{content}</text>'

    # Color Map (Hex)
    C_OUTLINE = "#3C3C3C"
    C_CARCASS = "#F5F5F5"
    C_DOOR = "#DEB887"
    C_HANDLE = "#323232"
    C_TEXT = "#000000"
    C_PLINTH = "#323232"

    # Draw Floor
    floor_y = img_h - MARGIN
    svg += svg_line(MARGIN - 50, floor_y, img_w - MARGIN + 50, floor_y, C_OUTLINE, 3) + "\n"
    
    current_x = 0.0
    i = 0
    while i < len(columns):
        col = columns[i]
        
        # Determine merged group
        merged_group_indices = [i]
        temp_idx = i
        while temp_idx < len(columns) - 1 and columns[temp_idx].get('merge_right', False):
            temp_idx += 1
            merged_group_indices.append(temp_idx)
            
        group_w = sum(columns[g]['width'] for g in merged_group_indices)
        group_has_top = any(columns[g].get('has_top', True) for g in merged_group_indices)
        master_col = columns[i]
        
        # --- 1. Bottom Modules ---
        for g_idx in merged_group_indices:
            col_g = columns[g_idx]
            w_g = col_g['width']
            drawers = col_g.get('drawers', [])
            
            x_g = current_x + sum(columns[k]['width'] for k in range(i, g_idx))
            
            # Plinth (2cm recess)
            svg += svg_rect(x_g + 2, 0, w_g - 4, plinth_h, C_PLINTH) + "\n"
            
            base_y = plinth_h
            current_y_top = base_y + (bot_h - plinth_h)
            
            if drawers:
                for d in drawers:
                    d_h = d['height']
                    d_y = current_y_top - d_h
                    svg += svg_rect(x_g, d_y, w_g, d_h, C_DOOR, C_OUTLINE) + "\n"
                    # Handle (10cm wide, 2cm high)
                    handle_y_cm = d_y + d_h - 5
                    handle_x_cm = x_g + w_g/2 - 5
                    svg += svg_rect(handle_x_cm, handle_y_cm, 10, 2, C_HANDLE) + "\n"
                    current_y_top -= d_h
            
            remaining_h = current_y_top - base_y
            if remaining_h > 1.0:
                svg += svg_rect(x_g, base_y, w_g, remaining_h, C_DOOR, C_OUTLINE) + "\n"
                
                if w_g == 80:
                    mid_x = x_g + (w_g / 2)
                    mid_px = MARGIN + mid_x * SCALE
                    top_px = to_svg_y(base_y + remaining_h)
                    bot_px = to_svg_y(base_y)
                    svg += svg_line(mid_px, top_px, mid_px, bot_px, C_OUTLINE, 2) + "\n"
                    
                    svg += svg_circle(x_g + (w_g/2) - 3, base_y + remaining_h - 10, 1, C_HANDLE) + "\n"
                    svg += svg_circle(x_g + (w_g/2) + 3, base_y + remaining_h - 10, 1, C_HANDLE) + "\n"
                else:
                    svg += svg_circle(x_g + w_g - 5, base_y + remaining_h - 10, 1, C_HANDLE) + "\n"
            
            # Label
            label_x = MARGIN + (x_g + w_g/2)*SCALE
            label_y = img_h - MARGIN + 35
            svg += svg_text(label_x, label_y, f"{w_g}cm", 24, C_TEXT) + "\n"

        # --- 2. Top Module ---
        if group_has_top:
            # Sides
            svg += svg_rect(current_x, bot_h, THICKNESS, total_h - bot_h, C_CARCASS, C_OUTLINE) + "\n"
            svg += svg_rect(current_x + group_w - THICKNESS, bot_h, THICKNESS, total_h - bot_h, C_CARCASS, C_OUTLINE) + "\n"
            
            # Top/Counter
            svg += svg_rect(current_x, total_h - THICKNESS, group_w, THICKNESS, C_CARCASS, C_OUTLINE) + "\n"
            svg += svg_rect(current_x, bot_h - THICKNESS, group_w, THICKNESS, C_CARCASS, C_OUTLINE) + "\n"
            
            shelves = master_col.get('shelf_heights', [])
            dividers = master_col.get('vertical_dividers', [])
            sorted_shelves = sorted(shelves)
            all_bounds = [bot_h] + sorted_shelves + [total_h]
            
            for j in range(len(all_bounds) - 1):
                low, high = all_bounds[j], all_bounds[j+1]
                mid_z = (low + high) / 2
                
                # Height Label
                tx = MARGIN + (current_x + 2) * SCALE + 20
                ty = to_svg_y(mid_z) + 6
                svg += svg_text(tx, ty, f"{high-low:.1f}", 18, "#777777") + "\n"
                
                if j in dividers:
                    mid_x = current_x + (group_w / 2)
                    svg += svg_rect(mid_x - THICKNESS/2, low, THICKNESS, high - low, C_CARCASS, C_OUTLINE) + "\n"

            for h in sorted_shelves:
                if bot_h < h < total_h:
                    svg += svg_rect(current_x + THICKNESS, h - THICKNESS, group_w - 2*THICKNESS, THICKNESS, C_CARCASS, C_OUTLINE) + "\n"
        
        current_x += group_w
        i = temp_idx + 1

    # Total Dims
    svg += svg_text(img_w/2, MARGIN/2, f"Total Width: {total_w}cm | Total Height: {total_h}cm", 36, C_TEXT) + "\n"
    
    svg += "</svg>"
    return svg

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python render_cabinet.py <config.json> [output.png]")
    else:
        cfg, out = sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "cabinet_render.png"
        render_cabinet(cfg, out)