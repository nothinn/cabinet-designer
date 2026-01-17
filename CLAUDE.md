# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Cabinet Designer is a modular cabinet design tool with an interactive CLI, Flask web interface, and PyScript-powered browser application. It generates ASCII previews and high-quality 2D schematic PNG images of cabinet designs.

## Common Commands

```bash
# Run interactive CLI designer
python simple_designer.py

# Run Flask web server
python web_designer.py

# Render a cabinet config to PNG
python render_cabinet.py <config.json> <output.png>

# Generate preview metadata for GitHub Pages
python generate-previews-json.py [--repo owner/repo] [--output file] [--token github_token]
```

## Architecture

### Core Modules

- **simple_designer.py** (~850 lines): Main design logic with `CabinetDesigner` class handling column management, drawer/shelf configuration, vertical subdivisions, merging, and JSON config save/load
- **render_cabinet.py** (~500 lines): Converts cabinet JSON configs to 2D schematic PNGs using Pillow (5 pixels per cm scale)
- **web_designer.py** (~180 lines): Flask wrapper providing REST API endpoints for the web interface

### Frontend

- **index.html**: PyScript-powered web interface that runs Python directly in browser
- **preview-index.html**: Dynamic preview navigation fetching branches/PRs from GitHub API
- **preview.html**: Dynamic preview loader using `?branch=` or `?pr=` query parameters

### Configuration

- **pyscript.json**: Defines PyScript packages (Pillow) and file mappings
- **templates/*.json**: Pre-configured cabinet designs with rendered PNG previews
- **previews.json**: Generated metadata for available branch/PR previews

### Cabinet Data Structure

```python
{
    'total_height': 240.0,      # cm
    'bottom_height': 80.0,      # cm
    'plinth_height': 8.0,       # cm
    'thickness': 1.8,           # cm (18mm)
    'columns': [{
        'width': 60,            # 40, 60, or 80 cm
        'shelf_heights': [],    # absolute heights in cm
        'vertical_dividers': [],
        'has_top': True,
        'merge_right': False,
        'drawers': [{'height': 20.0}]
    }]
}
```

## GitHub Actions Workflows

- **preview-deploy.yml**: Deploys branch/PR previews on push
- **update-preview-index.yml**: Regenerates previews.json hourly
- **cleanup-previews.yml**: Weekly cleanup of closed PR/deleted branch previews

## Preview System

The dynamic preview system loads content from `raw.githubusercontent.com` to work around GitHub CSP limitations:
- Main site: `https://nothinn.github.io/cabinet-designer/`
- Branch previews: `preview.html?branch=branch-name`
- PR previews: `preview.html?pr=pr-number`
- Preview index: `preview-index.html`

## Dependencies

- Python 3.x
- Pillow (image rendering)
- Requests (GitHub API)
- Flask (web server)
- PyScript 2024.1.1 (browser Python, loaded from CDN)
