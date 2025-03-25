# Arc LLM

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/lillylight/arc-llm/blob/main/colab_runner.ipynb)

Arc LLM is a project that integrates Claude API with [SpatialLM](https://github.com/manycore-research/SpatialLM) to convert text descriptions into 2D and 3D spatial representations. While SpatialLM processes 3D point cloud data from videos to generate structured 3D scene understanding outputs, Arc LLM takes text descriptions from Claude API and converts them directly into the structured layout format that SpatialLM uses for visualization.

## Overview

SpatialLM is designed to process 3D point cloud data and generate structured 3D scene understanding outputs, including architectural elements like walls, doors, windows, and oriented object bounding boxes with their semantic categories. Arc LLM extends this by:

1. Accepting text descriptions from Claude API as input
2. Converting these text descriptions directly into the structured layout format that SpatialLM uses for visualization
3. Using SpatialLM's visualization components to generate 2D and 3D visualizations from this structured layout

## Architecture

Arc LLM consists of the following components:

1. **Claude API Integration**: Communicates with Claude API to generate structured layout descriptions from text
2. **Text-to-Layout Converter**: Converts structured layout descriptions into SpatialLM's layout format
3. **Visualization**: Uses SpatialLM's visualization components to generate 2D and 3D visualizations

## Installation

### Local Installation

```bash
# Clone the repository
git clone https://github.com/lillylight/arc-llm.git
cd arc-llm

# Clone SpatialLM repository
git clone https://github.com/manycore-research/SpatialLM.git

# Create a conda environment
conda create -n arcllm python=3.11
conda activate arcllm
conda install -y nvidia/label/cuda-12.4.0::cuda-toolkit conda-forge::sparsehash

# Install dependencies
pip install torch numpy scipy einops rerun-sdk requests torchsparse
```

### Google Colab

You can run Arc LLM directly in Google Colab without installing anything on your local machine:

1. Click the "Open in Colab" badge at the top of this README
2. The notebook will open in Google Colab
3. Run the cells in order to set up the environment and use Arc LLM

The Colab notebook provides all the functionality of Arc LLM, including:
- Text-to-3D conversion
- Visualization
- Example selection (simple room or complex house)
- Web interface (optional)

For more details on setting up and using Arc LLM with GitHub and Google Colab, see the [GitHub Setup Guide](GITHUB_SETUP.md).

## How It Works

Arc LLM converts text descriptions into 3D visualizations through a multi-step process:

1. **Text Input**: The system takes a natural language description of a scene (e.g., a living room, a house, etc.)

2. **Claude API Processing**: The text is sent to Claude API with a specialized system prompt that instructs it to convert the text into a structured layout description. This structured description follows a specific format for walls, doors, windows, furniture, and other objects.

3. **Layout Generation**: The structured description is parsed and converted into SpatialLM's layout format, which consists of walls, doors, windows, and bounding boxes with specific coordinates, dimensions, and orientations.

4. **Visualization**: The layout is passed to SpatialLM's visualization components, which generate 2D and 3D visualizations using the Rerun library.

### System Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Text Input  │───▶│  Claude API  │───▶│  Layout     │───▶│  SpatialLM  │
│  Description │    │  Processing  │    │  Generation │    │  Visualizer │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## Usage

### Command Line

```bash
# Set Claude API key
export CLAUDE_API_KEY="your-api-key"

# Simple example
python run_example.py

# Complex house example
python run_example.py --complex

# Use pre-generated structured description
python run_example.py --complex --use-description
```

### Python API

```python
from arc_llm import ArcLLM

# Initialize Arc LLM
arc_llm = ArcLLM(claude_api_key="your-api-key")

# Generate layout from text
text = "A living room with a sofa against the north wall, a coffee table in the center, and a TV on the south wall. There's a window on the east wall and a door on the west wall."
layout_str = arc_llm.convert_text_to_layout(text)

# Visualize layout
arc_llm.visualize(layout_str)
```

### Web Interface

Arc LLM includes a web interface for easier interaction:

```bash
# Set Claude API key
export CLAUDE_API_KEY="your-api-key"

# Start the web interface
python web_interface.py
```

Then open your browser and navigate to `http://localhost:5000` to access the web interface.

The web interface allows you to:
- Enter text descriptions or use provided examples
- Generate layouts from text descriptions
- View the generated layout text
- Download the visualization file
- View instructions for visualizing the 3D scene

## Enhanced Capabilities

Arc LLM supports a wide range of architectural features and complex structures:

### Multi-Floor Support
- Multiple floors with different heights
- Staircases connecting floors
- Z-coordinate mapping for 3D positioning

### Room Relationships
- Room definitions with dimensions and connections
- Different connection types (doors, openings, archways)
- Spatial relationships between rooms

### Advanced Object Types
- Architectural features (columns, arches, etc.)
- Built-in furniture (cabinets, shelves, etc.)
- Fixtures (sinks, toilets, showers, etc.)

### Material and Style Specifications
- Material definitions for walls, floors, etc.
- Color specifications
- Style templates (modern, traditional, etc.)

## Input Format

Arc LLM accepts natural language descriptions of scenes, from simple rooms to complex multi-story buildings. The Claude API is used to convert these descriptions into a structured format that can be processed by the text-to-layout converter.

### Simple Example
```
A living room with a sofa against the north wall, a coffee table in the center, and a TV on the south wall. There's a window on the east wall and a door on the west wall.
```

### Complex Example
```
A modern two-story house with 3 bedrooms, 3 bathrooms, a spacious living room, kitchen, and dining area.

The house has the following layout:

Ground Floor:
- A large open-concept living area (8m x 6m) that includes the living room and dining area
- A kitchen (5m x 4m) connected to the dining area via an open archway
- A guest bathroom (2.5m x 2m) with a toilet, sink, and shower
- A home office (3m x 3m)
- A staircase leading to the second floor

First Floor:
- Master bedroom (5m x 5m) with an ensuite bathroom (3m x 2.5m)
- Two additional bedrooms (4m x 4m each)
- A shared bathroom (3m x 2.5m)
- A hallway connecting all rooms
```

## Output Format

Arc LLM generates a structured layout in SpatialLM's format. For complex structures, the output is organized by floor and room.

### Simple Output Example
```
wall_0=Wall(0.0,0.0,0.0,5.0,0.0,0.0,2.8,0.2)
wall_1=Wall(5.0,0.0,0.0,5.0,5.0,0.0,2.8,0.2)
wall_2=Wall(5.0,5.0,0.0,0.0,5.0,0.0,2.8,0.2)
wall_3=Wall(0.0,5.0,0.0,0.0,0.0,0.0,2.8,0.2)
door_0=Door(wall_3,0.0,2.5,0.0,1.0,2.0)
window_0=Window(wall_1,5.0,2.5,1.0,1.5,1.0)
bbox_0=Bbox(sofa,2.5,0.5,0.0,0.0,2.0,0.8,0.8)
bbox_1=Bbox(coffee_table,2.5,2.5,0.0,0.0,1.2,1.2,0.5)
bbox_2=Bbox(tv,2.5,4.5,0.0,3.14,1.5,0.2,0.8)
```

### Complex Output Example
The complex output includes floor definitions, room relationships, and more detailed object specifications. See `examples/complex_house_description.txt` for a complete example.

## License

This project is licensed under the same license as SpatialLM.
