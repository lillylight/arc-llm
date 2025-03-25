#!/usr/bin/env python3
"""
Arc LLM Web Interface

This script provides a web interface for Arc LLM using Flask.
"""

import os
import tempfile
import uuid
from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify

from arc_llm import ArcLLM

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize Arc LLM
claude_api_key = os.environ.get("CLAUDE_API_KEY")
arc_llm = ArcLLM(claude_api_key=claude_api_key)


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    """Generate layout from text description."""
    text = request.form.get('text')
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        # Generate layout from text
        layout_str = arc_llm.convert_text_to_layout(text)

        # Save layout to file
        layout_id = str(uuid.uuid4())
        layout_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{layout_id}.txt')
        with open(layout_path, 'w') as f:
            f.write(layout_str)

        # Generate visualization
        vis_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{layout_id}.rrd')
        arc_llm.visualize(layout_str, output_file=vis_path)

        return jsonify({
            'layout_id': layout_id,
            'layout': layout_str
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/view/<layout_id>')
def view(layout_id):
    """View the visualization for a layout."""
    layout_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{layout_id}.txt')
    vis_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{layout_id}.rrd')

    if not os.path.exists(layout_path) or not os.path.exists(vis_path):
        return "Layout not found", 404

    with open(layout_path, 'r') as f:
        layout_str = f.read()

    return render_template('view.html', layout_id=layout_id, layout=layout_str)


@app.route('/download/<layout_id>')
def download(layout_id):
    """Download the visualization file."""
    vis_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{layout_id}.rrd')
    if not os.path.exists(vis_path):
        return "Visualization not found", 404
    return send_file(vis_path, as_attachment=True)


@app.route('/examples')
def examples():
    """Get example text descriptions."""
    examples = {
        'simple': open('examples/living_room.txt', 'r').read(),
        'complex': open('examples/complex_house.txt', 'r').read()
    }
    return jsonify(examples)


if __name__ == '__main__':
    # Check if Claude API key is set
    if not claude_api_key:
        print("Warning: CLAUDE_API_KEY environment variable not set.")
        print("Set it with: export CLAUDE_API_KEY='your-api-key'")

    # Create templates directory if it doesn't exist
    os.makedirs(os.path.join(os.path.dirname(__file__), 'templates'), exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), 'static'), exist_ok=True)

    # Start the Flask app
    app.run(debug=True)
