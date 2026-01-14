import os
import time
from flask import Flask, render_template, request, redirect, url_for, send_file
from simple_designer import CabinetDesigner
from render_cabinet import render_cabinet

app = Flask(__name__)

# Initialize Designer
designer = CabinetDesigner()
# Start with some default state
if not designer.columns:
    designer.add_column(60)
    designer.add_column(80)

TEMP_CONFIG = "temp_web_config.json"
SAVES_DIR = "saved_designs"
STATIC_DIR = "static"
RENDER_OUTPUT = os.path.join(STATIC_DIR, "cabinet_preview.png")

# Ensure static and saves dirs exist
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)
if not os.path.exists(SAVES_DIR):
    os.makedirs(SAVES_DIR)

@app.route('/')
def index():
    saved_files = [f for f in os.listdir(SAVES_DIR) if f.endswith('.json')]
    return render_template('index.html', designer=designer, enumerate=enumerate, len=len, time=time, saved_files=saved_files)

@app.route('/image')
def image():
    # Save config
    designer.save_config(TEMP_CONFIG)
    # Render
    render_cabinet(TEMP_CONFIG, RENDER_OUTPUT)
    # Return file with cache busting is handled in frontend by adding query param
    return send_file(RENDER_OUTPUT, mimetype='image/png')

@app.route('/api/save', methods=['POST'])
def save():
    filename = request.form.get('filename')
    if filename:
        if not filename.endswith('.json'):
            filename += '.json'
        filepath = os.path.join(SAVES_DIR, filename)
        designer.save_config(filepath)
    return redirect(url_for('index'))

@app.route('/api/load', methods=['POST'])
def load():
    filename = request.form.get('filename')
    if filename:
        filepath = os.path.join(SAVES_DIR, filename)
        if os.path.exists(filepath):
            designer.load_config(filepath)
    return redirect(url_for('index'))

@app.route('/api/reset', methods=['POST'])
def reset():
    global designer
    designer = CabinetDesigner()
    designer.add_column(60)
    designer.add_column(80)
    return redirect(url_for('index'))

@app.route('/api/set_height', methods=['POST'])
def set_height():
    try:
        h = float(request.form.get('height'))
        designer.set_height(h)
    except ValueError:
        pass
    return redirect(url_for('index'))

@app.route('/api/add_column', methods=['POST'])
def add_column():
    try:
        width = int(request.form.get('width'))
        designer.add_column(width)
    except ValueError:
        pass
    return redirect(url_for('index'))

@app.route('/api/remove_column', methods=['POST'])
def remove_column():
    try:
        idx = int(request.form.get('index'))
        designer.remove_column(idx)
    except ValueError:
        pass
    return redirect(url_for('index'))

@app.route('/api/move_column', methods=['POST'])
def move_column():
    try:
        idx = int(request.form.get('index'))
        direction = request.form.get('direction')
        if direction == 'left' and idx > 0:
            designer.swap_columns(idx, idx-1)
        elif direction == 'right' and idx < len(designer.columns) - 1:
            designer.swap_columns(idx, idx+1)
    except ValueError:
        pass
    return redirect(url_for('index'))

@app.route('/api/toggle_top', methods=['POST'])
def toggle_top():
    try:
        idx = int(request.form.get('index'))
        designer.toggle_top(idx)
    except ValueError:
        pass
    return redirect(url_for('index'))

@app.route('/api/toggle_merge', methods=['POST'])
def toggle_merge():
    try:
        idx = int(request.form.get('index'))
        designer.toggle_merge(idx)
    except ValueError:
        pass
    return redirect(url_for('index'))

@app.route('/api/set_shelves_count', methods=['POST'])
def set_shelves_count():
    try:
        idx = int(request.form.get('index'))
        count = int(request.form.get('count'))
        designer.set_shelves_count(idx, count)
    except ValueError:
        pass
    return redirect(url_for('index'))

@app.route('/api/add_shelf', methods=['POST'])
def add_shelf():
    try:
        idx = int(request.form.get('index'))
        height = float(request.form.get('height'))
        designer.add_shelf_at_height(idx, height)
    except ValueError:
        pass
    return redirect(url_for('index'))

@app.route('/api/configure_drawers', methods=['POST'])
def configure_drawers():
    try:
        idx = int(request.form.get('index'))
        count = int(request.form.get('count'))
        # Optional height param could be added, defaulting to 20
        designer.configure_drawers(idx, count, 20.0)
    except ValueError:
        pass
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Make sure we can import local modules
    import sys
    sys.path.append(os.getcwd())
    app.run(debug=True, port=5000)
