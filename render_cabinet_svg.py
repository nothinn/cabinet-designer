"""
SVG Renderer for Cabinet Designer
Pure-Python SVG generation with no external dependencies
"""

# Configuration
SCALE = 5.0  # Pixels per cm
MARGIN = 100  # Pixels
THICKNESS = 1.8  # cm (Material thickness)

# Colors (RGB tuples)
COLOR_BG = (255, 255, 255)       # White background
COLOR_OUTLINE = (60, 60, 60)     # Dark Grey outlines
COLOR_CARCASS = (245, 245, 245)  # Off-white for interiors
COLOR_EDGE = (220, 220, 220)     # Cut edge color
COLOR_DOOR = (222, 184, 135)     # Burlywood / Light Oak
COLOR_HANDLE = (50, 50, 50)      # Dark handles
COLOR_TEXT = (0, 0, 0)

def rgb_to_hex(r, g, b):
    """Convert RGB tuple to hex color string"""
    return f"#{r:02x}{g:02x}{b:02x}"

def svg_rect(x, y, w, h, fill, stroke=None, stroke_width=2):
    """Generate SVG rectangle element"""
    fill_hex = rgb_to_hex(*fill) if fill else "none"
    stroke_attr = f'stroke="{rgb_to_hex(*stroke)}" stroke-width="{stroke_width}"' if stroke else 'stroke="none"'
    return f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{fill_hex}" {stroke_attr}/>'

def svg_circle(cx, cy, r, fill):
    """Generate SVG circle element"""
    fill_hex = rgb_to_hex(*fill)
    return f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{fill_hex}"/>'

def svg_line(x1, y1, x2, y2, stroke, stroke_width=2):
    """Generate SVG line element"""
    stroke_hex = rgb_to_hex(*stroke)
    return f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{stroke_hex}" stroke-width="{stroke_width}"/>'

def svg_text(x, y, text, size, fill, anchor="middle"):
    """Generate SVG text element"""
    fill_hex = rgb_to_hex(*fill)
    return f'<text x="{x:.2f}" y="{y:.2f}" font-family="Arial, sans-serif" font-size="{size}" fill="{fill_hex}" text-anchor="{anchor}" dominant-baseline="middle">{text}</text>'

def draw_rect_cm(x_cm, y_cm, w_cm, h_cm, fill, outline, canvas_height, elements):
    """
    Draw a rectangle in CM coordinates and add to elements list.
    x, y: Bottom-Left corner in CM.
    """
    x1 = MARGIN + x_cm * SCALE
    y1 = canvas_height - MARGIN - (y_cm * SCALE)

    x2 = MARGIN + (x_cm + w_cm) * SCALE
    y2 = canvas_height - MARGIN - ((y_cm + h_cm) * SCALE)

    # SVG uses top-left origin, so y2 is top, y1 is bottom
    width = x2 - x1
    height = y1 - y2

    elements.append(svg_rect(x1, y2, width, height, fill, outline))

def draw_circle_cm(x_cm, y_cm, r_cm, fill, canvas_height, elements):
    """Draw a circle in CM coordinates and add to elements list"""
    cx = MARGIN + x_cm * SCALE
    cy = canvas_height - MARGIN - (y_cm * SCALE)
    r = r_cm * SCALE
    elements.append(svg_circle(cx, cy, r, fill))

def draw_line_cm(x1_cm, y1_cm, x2_cm, y2_cm, stroke, stroke_width, canvas_height, elements):
    """Draw a line in CM coordinates and add to elements list"""
    x1 = MARGIN + x1_cm * SCALE
    y1 = canvas_height - MARGIN - (y1_cm * SCALE)
    x2 = MARGIN + x2_cm * SCALE
    y2 = canvas_height - MARGIN - (y2_cm * SCALE)
    elements.append(svg_line(x1, y1, x2, y2, stroke, stroke_width))

def render_cabinet_to_svg(designer_obj):
    """
    Renders the cabinet configuration to an SVG string.
    Accepts a CabinetDesigner instance or a dict.
    Returns: SVG string
    """
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

    # Canvas Dimensions
    canvas_w = int((total_w * SCALE) + (MARGIN * 2))
    canvas_h = int((total_h * SCALE) + (MARGIN * 2))

    # SVG elements list
    elements = []

    # Draw Floor Line
    floor_y = canvas_h - MARGIN
    elements.append(svg_line(MARGIN - 50, floor_y, canvas_w - MARGIN + 50, floor_y, COLOR_OUTLINE, 3))

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
            draw_rect_cm(x_g + 2, 0, w_g - 4, plinth_h, (50, 50, 50), None, canvas_h, elements)

            # Draw Main Box (above plinth)
            box_h = bot_h - plinth_h
            base_y = plinth_h

            current_y_top = base_y + box_h

            if drawers:
                for d in drawers:
                    d_h = d['height']
                    # Draw drawer
                    d_y = current_y_top - d_h
                    draw_rect_cm(x_g, d_y, w_g, d_h, COLOR_DOOR, COLOR_OUTLINE, canvas_h, elements)
                    # Handle
                    draw_rect_cm(x_g + w_g/2 - 5, d_y + d_h - 5, 10, 2, COLOR_HANDLE, None, canvas_h, elements)

                    current_y_top -= d_h

            # Remaining space? Draw door
            remaining_h = current_y_top - base_y
            if remaining_h > 1.0:  # If notable space remains
                draw_rect_cm(x_g, base_y, w_g, remaining_h, COLOR_DOOR, COLOR_OUTLINE, canvas_h, elements)

                if w_g == 80:
                    # Draw vertical split line for 80cm doors
                    mid_x = x_g + (w_g / 2)
                    draw_line_cm(mid_x, base_y, mid_x, base_y + remaining_h, COLOR_OUTLINE, 2, canvas_h, elements)
                    # Two handles
                    draw_circle_cm(x_g + (w_g/2) - 3, base_y + remaining_h - 10, 1, COLOR_HANDLE, canvas_h, elements)
                    draw_circle_cm(x_g + (w_g/2) + 3, base_y + remaining_h - 10, 1, COLOR_HANDLE, canvas_h, elements)
                else:
                    # Single handle
                    draw_circle_cm(x_g + w_g - 5, base_y + remaining_h - 10, 1, COLOR_HANDLE, canvas_h, elements)

            # Width label (individual for each base)
            text = f"{w_g}cm"
            text_x = MARGIN + (x_g + w_g/2) * SCALE
            text_y = canvas_h - MARGIN + 25
            elements.append(svg_text(text_x, text_y, text, 20, COLOR_TEXT))

        # --- 2. Top Module (Merged group) ---
        if group_has_top:
            # Side Panels (Outer)
            draw_rect_cm(current_x, bot_h, THICKNESS, total_h - bot_h, COLOR_CARCASS, COLOR_OUTLINE, canvas_h, elements)
            draw_rect_cm(current_x + group_w - THICKNESS, bot_h, THICKNESS, total_h - bot_h, COLOR_CARCASS, COLOR_OUTLINE, canvas_h, elements)

            # Top Cap and Countertop (Full group width)
            draw_rect_cm(current_x, total_h - THICKNESS, group_w, THICKNESS, COLOR_CARCASS, COLOR_OUTLINE, canvas_h, elements)
            draw_rect_cm(current_x, bot_h - THICKNESS, group_w, THICKNESS, COLOR_CARCASS, COLOR_OUTLINE, canvas_h, elements)

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
                ty = canvas_h - MARGIN - (mid_z * SCALE)
                elements.append(svg_text(tx, ty, h_text, 10, (150, 150, 150), "start"))

                # Vertical Divider (Centered in merged group)
                if j in dividers:
                    mid_x = current_x + (group_w / 2)
                    draw_rect_cm(mid_x - THICKNESS/2, low, THICKNESS, high - low, COLOR_CARCASS, COLOR_OUTLINE, canvas_h, elements)

            # Shelves (Span full group)
            for h in sorted_shelves:
                if bot_h < h < total_h:
                    draw_rect_cm(current_x + THICKNESS, h - THICKNESS, group_w - 2*THICKNESS, THICKNESS, COLOR_CARCASS, COLOR_OUTLINE, canvas_h, elements)

        current_x += group_w
        i = temp_idx + 1

    # Total Dimensions
    info_text = f"Total Width: {total_w}cm | Total Height: {total_h}cm"
    elements.append(svg_text(MARGIN, MARGIN/2, info_text, 30, COLOR_TEXT, "start"))

    # Build complete SVG
    svg_header = f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" viewBox="0 0 {canvas_w} {canvas_h}">'
    svg_bg = svg_rect(0, 0, canvas_w, canvas_h, COLOR_BG)
    svg_footer = '</svg>'

    return svg_header + '\n' + svg_bg + '\n' + '\n'.join(elements) + '\n' + svg_footer
