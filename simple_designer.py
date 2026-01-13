import sys
import os
import json
import subprocess

try:
    import msvcrt
except ImportError:
    msvcrt = None

class CabinetDesigner:
    def __init__(self):
        self.total_height = 240.0 # cm
        self.bottom_height = 80.0 # cm
        self.plinth_height = 8.0 # cm
        self.thickness = 1.8 # cm (approx 18mm)
        # List of dicts: {'width': 60, 'shelf_heights': [130.0, 180.0]}
        # 'shelf_heights' are absolute heights from the floor.
        self.columns = [] 

    def get_total_width(self):
        return sum(c['width'] for c in self.columns)

    def add_column(self, width):
        if width not in [40, 60, 80]:
            print("Invalid width! Choose 40, 60, or 80 cm.")
            return
        # drawers: list of dicts {'height': 20.0}
        # If list is empty, it has a door.
        # Drawers are placed from top of bottom section downwards.
        new_col = {
            'width': width, 
            'shelf_heights': [], 
            'vertical_dividers': [],
            'has_top': True,
            'merge_right': False,
            'drawers': [] 
        }
        self.columns.append(new_col)
        self._set_evenly_spaced_shelves(len(self.columns)-1, 3)
        print(f"Added {width}cm column.")

    def configure_drawers(self, index, count, height_per_drawer=20.0):
        if 0 <= index < len(self.columns):
            if count == 0:
                self.columns[index]['drawers'] = []
                print(f"Column {index+1} set to door (no drawers).")
                return

            # Validate height
            available_h = self.bottom_height - self.plinth_height
            total_req = count * height_per_drawer
            
            if total_req > available_h:
                print(f"Cannot fit {count} drawers of {height_per_drawer}cm. Max available: {available_h}cm.")
                return
            
            # Create drawers
            new_drawers = [{'height': float(height_per_drawer)} for _ in range(count)]
            self.columns[index]['drawers'] = new_drawers
            print(f"Column {index+1} set to {count} drawers of {height_per_drawer}cm.")
        else:
            print("Invalid column index.")

    def set_plinth_height(self, h):
        if h < 0 or h > 20:
            print("Plinth height must be between 0 and 20 cm.")
            return
        self.plinth_height = float(h)
        print(f"Plinth height set to {self.plinth_height} cm.")

    def toggle_drawers(self, index):
        # Deprecated/Updated wrapper
        if 0 <= index < len(self.columns):
            if self.columns[index]['drawers']:
                self.configure_drawers(index, 0)
            else:
                self.configure_drawers(index, 1, 20.0) # Default 1 drawer of 20cm
        else:
            print("Invalid column index.")

    def toggle_top(self, index):
        if 0 <= index < len(self.columns):
            self.columns[index]['has_top'] = not self.columns[index]['has_top']
            state = "ON" if self.columns[index]['has_top'] else "OFF"
            print(f"Column {index+1} top section is now {state}.")
        else:
            print("Invalid column index.")

    def toggle_merge(self, index):
        if 0 <= index < len(self.columns) - 1:
            self.columns[index]['merge_right'] = not self.columns[index]['merge_right']
            state = "MERGED" if self.columns[index]['merge_right'] else "SEPARATED"
            print(f"Divider between Column {index+1} and {index+2} is now {state}.")
        else:
            print("Invalid column index for merge (cannot merge last column to the right).")

    def remove_column(self, index):
        if 0 <= index < len(self.columns):
            removed = self.columns.pop(index)
            print(f"Removed column {index+1} ({removed['width']}cm).")
        else:
            print("Invalid column index.")

    def set_height(self, height_cm):
        if height_cm < self.bottom_height + 20:
            print("Height too small!")
            return
        self.total_height = float(height_cm)
        # Clean up shelves that are now out of bounds
        for col in self.columns:
            col['shelf_heights'] = [h for h in col['shelf_heights'] if h < self.total_height]
            # Also reset dividers if they might be out of index? 
            # Actually space_id is relative to shelf count.
        print(f"Total height set to {self.total_height}cm.")

    def _set_evenly_spaced_shelves(self, index, spaces_count):
        """Helper to set shelves to even spacing."""
        if spaces_count <= 0:
            self.columns[index]['shelf_heights'] = []
            return
            
        top_h = self.total_height - self.bottom_height
        spacing = top_h / spaces_count
        new_shelves = []
        for i in range(1, spaces_count):
            h = self.bottom_height + (spacing * i)
            new_shelves.append(round(h, 1))
        self.columns[index]['shelf_heights'] = new_shelves
        # Reset dividers when resetting shelf count as space IDs change
        self.columns[index]['vertical_dividers'] = []

    def set_shelves_count(self, index, count):
        """Sets shelves to be evenly spaced with 'count' spaces."""
        if 0 <= index < len(self.columns):
            if count < 1:
                # 0 shelves means 1 space
                self.columns[index]['shelf_heights'] = []
                self.columns[index]['vertical_dividers'] = []
                print(f"Column {index+1} cleared of shelves.")
                return
            
            self._set_evenly_spaced_shelves(index, count)
            print(f"Column {index+1} reset to {count} evenly spaced sections.")
        else:
            print("Invalid column index.")

    def add_shelf_at_height(self, index, height_cm):
        if 0 <= index < len(self.columns):
            if height_cm <= self.bottom_height or height_cm >= self.total_height:
                print(f"Height must be between {self.bottom_height} and {self.total_height}.")
                return
            
            # Add and sort
            col = self.columns[index]
            if height_cm not in col['shelf_heights']:
                col['shelf_heights'].append(height_cm)
                col['shelf_heights'].sort()
                # Vertical dividers might shift meaning, but we keep them
                print(f"Added shelf at {height_cm}cm to Column {index+1}.")
            else:
                print("Shelf already exists at that height.")
        else:
            print("Invalid column index.")

    def remove_shelf_by_index(self, col_index, shelf_index):
        if 0 <= col_index < len(self.columns):
            col = self.columns[col_index]
            if 0 <= shelf_index < len(col['shelf_heights']):
                removed_h = col['shelf_heights'].pop(shelf_index)
                # Clear dividers because space mapping changed
                col['vertical_dividers'] = []
                print(f"Removed shelf at {removed_h:.1f}cm from Column {col_index+1}. (Dividers reset)")
            else:
                print("Invalid shelf index.")
        else:
             print("Invalid column index.")

    def subdivide_compartment(self, col_index, space_id):
        if 0 <= col_index < len(self.columns):
            col = self.columns[col_index]
            shelves = col['shelf_heights']
            
            # space_id 0: space between bottom and first shelf (or top cap if none)
            if 0 <= space_id <= len(shelves):
                if space_id in col['vertical_dividers']:
                    col['vertical_dividers'].remove(space_id)
                    print(f"Removed vertical divider in Column {col_index+1}, Space {space_id}.")
                else:
                    col['vertical_dividers'].append(space_id)
                    print(f"Added vertical divider in Column {col_index+1}, Space {space_id}.")
            else:
                print(f"Invalid compartment ID. Valid IDs for this column are 0 to {len(shelves)}.")
        else:
            print("Invalid column index.")

    def list_shelves(self, index):
        if 0 <= index < len(self.columns):
            col = self.columns[index]
            print(f"Shelves for Column {index+1} ({col['width']}cm):")
            if not col['shelf_heights']:
                print("  (No shelves)")
            else:
                for i, h in enumerate(col['shelf_heights']):
                    print(f"  {i+1}: {h:.1f} cm")
        else:
            print("Invalid column index.")

    def move_shelf(self, col_index, shelf_index, amount_cm, silent=False):
        if 0 <= col_index < len(self.columns):
            col = self.columns[col_index]
            shelves = col['shelf_heights']
            if 0 <= shelf_index < len(shelves):
                current_h = shelves[shelf_index]
                new_h = current_h + amount_cm
                
                # Check bounds
                # 1. Cabinet limits
                if new_h < self.bottom_height + 2: # 2cm buffer
                    if not silent: print(f"Cannot move lower than bottom cabinet ({self.bottom_height}cm).")
                    return
                if new_h > self.total_height - 2:
                    if not silent: print(f"Cannot move higher than top ({self.total_height}cm).")
                    return
                
                # 2. Collision with other shelves (keep 2cm buffer)
                # Check lower neighbor
                if shelf_index > 0:
                    lower_limit = shelves[shelf_index - 1] + 2
                    if new_h < lower_limit:
                         if not silent: print(f"Collision with shelf below (at {shelves[shelf_index-1]}cm).")
                         return

                # Check upper neighbor
                if shelf_index < len(shelves) - 1:
                    upper_limit = shelves[shelf_index + 1] - 2
                    if new_h > upper_limit:
                        if not silent: print(f"Collision with shelf above (at {shelves[shelf_index+1]}cm).")
                        return

                shelves[shelf_index] = new_h
                # Don't sort if we are moving interactively, or identity changes.
                # Actually, if we prevent collision, sorting is redundant but safe.
                # However, if we swap by accident, sorting reorders indices.
                # With strict collision checks, they should never cross.
                shelves.sort() 
                if not silent: print(f"Moved shelf to {new_h:.1f} cm.")
            else:
                if not silent: print("Invalid shelf index.")
        else:
            if not silent: print("Invalid column index.")

    def swap_columns(self, index1, index2):
        if 0 <= index1 < len(self.columns) and 0 <= index2 < len(self.columns):
            self.columns[index1], self.columns[index2] = self.columns[index2], self.columns[index1]
            print(f"Swapped Column {index1+1} and Column {index2+1}.")
        else:
            print("Invalid column indices.")

    def save_config(self, filename):
        data = {
            'total_height': self.total_height,
            'bottom_height': self.bottom_height,
            'plinth_height': self.plinth_height,
            'columns': self.columns
        }
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"Configuration saved to {filename}")
        except Exception as e:
            print(f"Error saving file: {e}")

    def load_config(self, filename):
        if not os.path.exists(filename):
            print("File not found.")
            return
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            self.total_height = data.get('total_height', 240.0)
            self.bottom_height = data.get('bottom_height', 80.0)
            self.plinth_height = data.get('plinth_height', 8.0)
            self.columns = data.get('columns', [])
            
            # Compatibility check: if columns have old format
            for c in self.columns:
                if 'shelf_heights' not in c:
                    # Convert 'shelves' count to list
                    count = c.get('shelves', 3) # Old count was spaces
                    c['shelf_heights'] = []
                    if count > 0:
                        top_h = self.total_height - self.bottom_height
                        spacing = top_h / count
                        for i in range(1, count):
                            c['shelf_heights'].append(self.bottom_height + spacing*i)
                
                if 'vertical_dividers' not in c:
                    c['vertical_dividers'] = []
                
                if 'has_top' not in c:
                    c['has_top'] = True
                
                if 'merge_right' not in c:
                    c['merge_right'] = False
                    
                if 'has_drawers' in c:
                    if c['has_drawers'] is True and 'drawers' not in c:
                        # Migrate old boolean to 3 default drawers
                        # Assuming old behavior was 3 full drawers filling space?
                        # Or just standard 20cm ones? Let's do 3 x 20cm
                        c['drawers'] = [{'height': 20.0}, {'height': 20.0}, {'height': 20.0}]
                    elif c['has_drawers'] is False and 'drawers' not in c:
                         c['drawers'] = []
                    # Remove old key
                    del c['has_drawers']
                
                if 'drawers' not in c:
                    c['drawers'] = []
            
            print(f"Configuration loaded from {filename}")
        except Exception as e:
            print(f"Error loading file: {e}")

    def draw(self):
        """Draws an ASCII representation of the cabinet."""
        if not self.columns:
            print("\n[Empty Cabinet]\n")
            return

        # Dimensions
        top_section_height = self.total_height - self.bottom_height
        total_w = self.get_total_width()
        
        scale = 0.1 # 1 line = 10cm
        
        bot_lines = int(self.bottom_height * scale)
        top_lines = int(top_section_height * scale)
        
        def get_w_chars(cm):
            return int(cm * 0.2)

        print("\n" + "=" * 40)
        print(f" CABINET PREVIEW (H: {self.total_height}cm, W: {total_w}cm)")
        print("=" * 40 + "\n")

        # --- Draw Top Section ---
        # Top Cap
        line_str = "+"
        for col in self.columns:
            w_chars = get_w_chars(col['width'])
            line_str += "-" * w_chars + "+"
        print(line_str)

        for r in range(top_lines):
            current_z = self.total_height - (r / scale)
            row_str = "|"
            
            i = 0
            while i < len(self.columns):
                col = self.columns[i]
                w_chars = get_w_chars(col['width'])
                
                # Check if this column and subsequent are merged
                merged_group = [i]
                temp_idx = i
                while temp_idx < len(self.columns) - 1 and self.columns[temp_idx]['merge_right']:
                    temp_idx += 1
                    merged_group.append(temp_idx)
                
                # Logic for drawing the merged group
                # 1. If the group has NO top, draw spaces
                # 2. If the group HAS top, draw based on the first column's shelves
                master_col = self.columns[i]
                group_has_top = any(self.columns[g]['has_top'] for g in merged_group)
                
                # Total group width
                group_w_chars = sum(get_w_chars(self.columns[g]['width']) for g in merged_group) + (len(merged_group) - 1)
                
                if not group_has_top:
                    row_str += " " * group_w_chars + "|"
                else:
                    # Draw based on master_col shelves
                    shelf_heights = master_col['shelf_heights']
                    dividers = master_col.get('vertical_dividers', [])
                    
                    space_id = 0
                    for h in shelf_heights:
                        if current_z > h:
                            space_id += 1

                    is_shelf = False
                    for h in shelf_heights:
                        if abs(current_z - h) < (1.0/scale)/2: 
                            is_shelf = True
                            break
                    
                    if is_shelf:
                        row_str += "-" * group_w_chars + "|"
                    else:
                        if space_id in dividers:
                            mid = group_w_chars // 2
                            line = list(" " * group_w_chars)
                            line[mid] = "|"
                            row_str += "".join(line) + "|"
                        else:
                            row_str += " " * group_w_chars + "|"
                
                # Skip the rest of the group in the outer loop
                i = temp_idx + 1
            
            print(row_str)

        # Middle Divider (Countertop)
        line_str = "+"
        for col in self.columns:
            w_chars = get_w_chars(col['width'])
            line_str += "=" * w_chars + "+"
        print(line_str)

        # --- Draw Bottom Section ---
        for r in range(bot_lines):
            row_str = "|"
            
            # Check if this row is within the plinth area
            # Plinth is at the very bottom.
            # Physical height of this row: r/scale from top of bottom section??
            # No, 'bot_lines' iterates from top of bottom section DOWN to floor.
            # Wait, previously r went 0..bot_lines.
            # 0 is top of bottom section. bot_lines-1 is floor.
            
            # Distance from floor:
            # floor_z = 0.
            # current_z = self.bottom_height - (r / scale)
            
            current_z = self.bottom_height - (r / scale)
            is_plinth = current_z < self.plinth_height
            
            if is_plinth:
                 # Just fill with plinth marker
                 for col in self.columns:
                     w_chars = get_w_chars(col['width'])
                     row_str += "/" * w_chars + "|"
            else:
                for col in self.columns:
                    w_chars = get_w_chars(col['width'])
                    
                    # Check for drawers
                    drawers = col.get('drawers', [])
                    is_drawer_row = False
                    
                    if drawers:
                        # Determine if current_z falls inside a drawer
                        # Drawers start at self.bottom_height and go down
                        # Drawer 0: [bottom_h, bottom_h - d0_h]
                        # Drawer 1: [bottom_h - d0_h, bottom_h - d0_h - d1_h]
                        d_top = self.bottom_height
                        for d in drawers:
                            d_h = d['height']
                            d_bot = d_top - d_h
                            
                            # current_z is the height of the current ASCII row
                            # Check if current_z is roughly within [d_bot, d_top]
                            # Tolerance for ASCII line
                            if d_bot <= current_z <= d_top:
                                # Check if we are at the border (d_bot)
                                if abs(current_z - d_bot) < (1.0/scale)/2:
                                     row_str += "-" * w_chars + "|"
                                     is_drawer_row = True
                                     break
                                else:
                                     # Inside drawer face
                                     if r % 2 != 0 and (d_top - current_z) < (d_h / 2 + 2) and (d_top - current_z) > (d_h / 2 - 2):
                                         # Middle of drawer
                                         label = "DRW"
                                         padding = (w_chars - len(label)) // 2
                                         row_str += " " * padding + label + " " * (w_chars - padding - len(label)) + "|"
                                     else:
                                         row_str += " " * w_chars + "|"
                                     is_drawer_row = True
                                     break
                            
                            d_top -= d_h
                        
                    if not is_drawer_row:
                        if col['width'] == 80:
                            # Two doors for 80cm
                            mid = w_chars // 2
                            line = list(" " * w_chars)
                            line[mid] = "|" # Door separator
                            
                            if r == bot_lines // 2:
                                # Left Label
                                lbl = "DOOR"
                                avail_l = mid
                                pad_l = (avail_l - len(lbl)) // 2
                                if pad_l >= 0:
                                    for k, c in enumerate(lbl):
                                        line[pad_l + k] = c
                                
                                # Right Label
                                lbl = "DOOR"
                                avail_r = w_chars - 1 - mid
                                pad_r = (avail_r - len(lbl)) // 2
                                start_r = mid + 1
                                if pad_r >= 0:
                                    for k, c in enumerate(lbl):
                                        line[start_r + pad_r + k] = c
                            
                            row_str += "".join(line) + "|"
                        else:
                            # Single door
                            if r == bot_lines // 2:
                                 label = "DOOR"
                                 padding = (w_chars - len(label)) // 2
                                 if padding < 0: label = ".."; padding = 0
                                 row_str += " " * padding + label + " " * (w_chars - padding - len(label)) + "|"
                            else:
                                row_str += " " * w_chars + "|"
            print(row_str)

        # Bottom Floor
        line_str = "+"
        for col in self.columns:
            w_chars = get_w_chars(col['width'])
            line_str += "-" * w_chars + "+"
        print(line_str)
        
        # Width Labels
        lbl_str = " "
        for i, col in enumerate(self.columns):
            w_chars = get_w_chars(col['width'])
            lbl = f"#{i+1} {col['width']}cm"
            pad = (w_chars - len(lbl)) // 2
            if pad < 0: pad = 0
            lbl_str += " " * pad + lbl + " " * (w_chars - pad - len(lbl) + 1)
        print(lbl_str)
        print(f" Total Width: {total_w}cm")
        print("\n")

def interactive_move_loop(designer, col_idx, shelf_idx):
    if not msvcrt:
        print("Interactive move not supported on this platform (missing msvcrt).")
        return
    
    print("\n[Interactive Move Mode]")
    print("Controls: 'u'=Up 5cm, 'd'=Down 5cm, 'U'=Up 1cm, 'D'=Down 1cm")
    print("Press ENTER to confirm and exit.")
    
    while True:
        # We don't redraw continuously to avoid flickering, only on change.
        # But we need to listen for keys.
        
        key = msvcrt.getch()
        step = 0.0
        
        if key == b'u': step = 5.0
        elif key == b'd': step = -5.0
        elif key == b'U': step = 1.0
        elif key == b'D': step = -1.0
        elif key == b'\r': break # Enter key
        
        if step != 0.0:
            designer.move_shelf(col_idx, shelf_idx, step, silent=True)
            # Redraw
            # We can try to clear screen for better effect
            os.system('cls' if os.name == 'nt' else 'clear')
            designer.draw()
            # Reprint instructions
            print("\n[Interactive Move Mode] 'u'/'d' to move. ENTER to finish.")
            # Print current pos
            try:
                cur = designer.columns[col_idx]['shelf_heights'][shelf_idx]
                print(f"Shelf is at: {cur:.1f} cm")
            except:
                pass

def print_help():
    print("Commands:")
    print("  add <40|60|80>        : Add a column of width cm")
    print("  rm <index>            : Remove column at index (1-based)")
    print("  h <cm>                : Set total height (e.g. 240)")
    print("  s <idx> <count>       : Reset column to <count> evenly spaced SECTIONS")
    print("  shelf <idx> <height>  : Add a specific shelf at height cm (from floor)")
    print("  subdivide <idx> <id>  : Divide compartment <id> (0=bottom, 1=above shelf 1...)")
    print("  rm_shelf <idx> <id>   : Remove shelf <id> in column <idx>")
    print("  ls_shelves <idx>      : List shelves in a column with IDs")
    print("  move <col> <id> <cm>  : Move shelf <id> in <col> by <cm>")
    print("  select <col> <id>     : Enter interactive move mode for a shelf")
    print("  swap <idx1> <idx2>    : Swap two columns")
    print("  top <idx>             : Toggle top section for column idx")
    print("  merge <idx>           : Toggle merge with right column")
    print("  plinth <cm>           : Set plinth height (default 8cm)")
    print("  drawer <idx>          : Toggle 1 default drawer for column idx (Legacy)")
    print("  config_drawers <idx> <count> [height] : Set N drawers of H cm (default 20)")
    print("  render [filename]     : Render schematic image (default: cabinet_render.png)")
    print("  save <filename>       : Save configuration to file")
    print("  load <filename>       : Load configuration from file")
    print("  show                  : Redraw the cabinet")
    print("  help                  : Show this help")
    print("  exit                  : Quit")

def interactive_mode():
    designer = CabinetDesigner()
    print("Welcome to the Interactive Cabinet Designer!")
    designer.add_column(60) # Default start
    designer.add_column(80)
    
    while True:
        designer.draw()
        try:
            cmd_line = input("CMD> ").strip().split()
        except EOFError:
            break
            
        if not cmd_line:
            continue
            
        cmd = cmd_line[0].lower()
        
        if cmd == 'exit':
            break
        elif cmd == 'help':
            print_help()
        elif cmd == 'add':
            if len(cmd_line) > 1:
                try:
                    w = int(cmd_line[1])
                    designer.add_column(w)
                except ValueError:
                    print("Invalid number")
            else:
                print("Usage: add <40|60|80>")
        elif cmd == 'rm':
            if len(cmd_line) > 1:
                try:
                    idx = int(cmd_line[1]) - 1
                    designer.remove_column(idx)
                except ValueError:
                    print("Invalid index")
        elif cmd == 'h':
            if len(cmd_line) > 1:
                try:
                    h = float(cmd_line[1])
                    designer.set_height(h)
                except ValueError:
                    print("Invalid height")
        elif cmd == 's':
            if len(cmd_line) > 2:
                try:
                    idx = int(cmd_line[1]) - 1
                    count = int(cmd_line[2])
                    designer.set_shelves_count(idx, count)
                except ValueError:
                    print("Invalid input")
        elif cmd == 'shelf':
            if len(cmd_line) > 2:
                try:
                    idx = int(cmd_line[1]) - 1
                    h = float(cmd_line[2])
                    designer.add_shelf_at_height(idx, h)
                except ValueError:
                    print("Invalid input")
        elif cmd == 'subdivide':
            if len(cmd_line) > 2:
                try:
                    idx = int(cmd_line[1]) - 1
                    space_id = int(cmd_line[2])
                    designer.subdivide_compartment(idx, space_id)
                except ValueError:
                    print("Invalid input")
        elif cmd == 'rm_shelf':
             if len(cmd_line) > 2:
                try:
                    col_idx = int(cmd_line[1]) - 1
                    shelf_idx = int(cmd_line[2]) - 1
                    designer.remove_shelf_by_index(col_idx, shelf_idx)
                except ValueError:
                    print("Invalid input")
        elif cmd == 'ls_shelves':
            if len(cmd_line) > 1:
                try:
                    idx = int(cmd_line[1]) - 1
                    designer.list_shelves(idx)
                    input("(Press Enter to continue)")
                except ValueError:
                    print("Invalid index")
        elif cmd == 'move':
            if len(cmd_line) > 3:
                try:
                    col_idx = int(cmd_line[1]) - 1
                    shelf_idx = int(cmd_line[2]) - 1
                    amount = float(cmd_line[3])
                    designer.move_shelf(col_idx, shelf_idx, amount)
                except ValueError:
                    print("Invalid input")
        elif cmd == 'select':
            if len(cmd_line) > 2:
                try:
                    col_idx = int(cmd_line[1]) - 1
                    shelf_idx = int(cmd_line[2]) - 1
                    # Basic validation before entering loop
                    if 0 <= col_idx < len(designer.columns):
                        if 0 <= shelf_idx < len(designer.columns[col_idx]['shelf_heights']):
                             interactive_move_loop(designer, col_idx, shelf_idx)
                        else:
                            print("Invalid shelf index.")
                    else:
                        print("Invalid column index.")
                except ValueError:
                    print("Invalid index")
        elif cmd == 'swap':
            if len(cmd_line) > 2:
                try:
                    idx1 = int(cmd_line[1]) - 1
                    idx2 = int(cmd_line[2]) - 1
                    designer.swap_columns(idx1, idx2)
                except ValueError:
                    print("Invalid index")
        elif cmd == 'top':
            if len(cmd_line) > 1:
                try:
                    idx = int(cmd_line[1]) - 1
                    designer.toggle_top(idx)
                except ValueError:
                    print("Invalid index")
        elif cmd == 'merge':
            if len(cmd_line) > 1:
                try:
                    idx = int(cmd_line[1]) - 1
                    designer.toggle_merge(idx)
                except ValueError:
                    print("Invalid index")
        elif cmd == 'plinth':
            if len(cmd_line) > 1:
                try:
                    h = float(cmd_line[1])
                    designer.set_plinth_height(h)
                except ValueError:
                    print("Invalid height")
        elif cmd == 'drawer':
            if len(cmd_line) > 1:
                try:
                    idx = int(cmd_line[1]) - 1
                    designer.toggle_drawers(idx)
                except ValueError:
                    print("Invalid index")
        elif cmd == 'config_drawers':
            if len(cmd_line) > 2:
                try:
                    idx = int(cmd_line[1]) - 1
                    count = int(cmd_line[2])
                    h = float(cmd_line[3]) if len(cmd_line) > 3 else 20.0
                    designer.configure_drawers(idx, count, h)
                except ValueError:
                    print("Invalid input")
        elif cmd == 'render':
            out_file = "cabinet_render.png"
            if len(cmd_line) > 1:
                out_file = cmd_line[1]
            
            # Save temp config
            temp_json = ".temp_render_config.json"
            designer.save_config(temp_json)
            
            # Run render script using subprocess.run for better quoting handling
            try:
                result = subprocess.run(
                    [sys.executable, "render_cabinet.py", temp_json, out_file],
                    check=True,
                    capture_output=True,
                    text=True
                )
                print(f"Image rendered to {out_file}")
            except subprocess.CalledProcessError as e:
                print("Rendering failed.")
                print(f"Error: {e.stderr}")
            except Exception as e:
                print(f"An error occurred: {e}")
            
            # Clean up
            if os.path.exists(temp_json):
                os.remove(temp_json)
        elif cmd == 'save':
            if len(cmd_line) > 1:
                designer.save_config(cmd_line[1])
            else:
                print("Usage: save <filename>")
        elif cmd == 'load':
            if len(cmd_line) > 1:
                designer.load_config(cmd_line[1])
            else:
                print("Usage: load <filename>")
        elif cmd == 'show':
            pass 
        else:
            print("Unknown command. Type 'help'.")

if __name__ == "__main__":
    interactive_mode()
