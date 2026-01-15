# Cabinet Designer CLI

A simple Python-based tool for designing custom cabinets with shelving, drawers, and modular bases.

## Features
- **Interactive CLI:** Design cabinets in real-time.
- **Modular Base:** Supports 40, 60, and 80cm modules.
- **Customizable:** Adjust height, shelving, plinths, and drawers.
- **Advanced Options:** Vertical subdivision, merged top sections.
- **Rendering:** Generates ASCII previews and high-quality 2D schematic images.

## Usage
1. Run the designer:
   ```bash
   python simple_designer.py
   ```
2. Use commands like `add`, `shelf`, `drawer`, `render`.
   Type `help` for a full list.

## Preview System

This project includes an automatic preview system that deploys branch and PR previews to GitHub Pages:

- **Main Site**: `https://nothinn.github.io/cabinet-designer/`
- **Branch Previews**: `https://nothinn.github.io/cabinet-designer/branch-name/`
- **PR Previews**: `https://nothinn.github.io/cabinet-designer/pr-number-branch-name/`
- **Preview Index**: `https://nothinn.github.io/cabinet-designer/preview-index.html`

The preview index automatically shows all available previews and updates hourly.

## Requirements
- Python 3.x
- Pillow (`pip install pillow`) for image rendering.
- Requests (`pip install requests`) for preview generation.
