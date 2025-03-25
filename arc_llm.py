#!/usr/bin/env python3
"""
Arc LLM

This module integrates Claude API with SpatialLM to convert text descriptions
into 2D and 3D visualizations.
"""

import os
import sys
from typing import Optional, Dict, Any, Union

# Add SpatialLM to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "SpatialLM"))

from spatiallm import Layout
from claude_api import ClaudeAPI
from text_to_layout import TextToLayout


class ArcLLM:
    """
    Arc LLM integrates Claude API with SpatialLM to convert text descriptions
    into 2D and 3D visualizations.
    """

    def __init__(self, claude_api_key: Optional[str] = None):
        """
        Initialize Arc LLM.

        Args:
            claude_api_key: Optional API key for Claude API. If not provided,
                           will look for CLAUDE_API_KEY environment variable.
        """
        self.claude_api = ClaudeAPI(api_key=claude_api_key)
        self.text_to_layout = TextToLayout(claude_api_key=claude_api_key)

    def convert_text_to_layout(self, text: str) -> str:
        """
        Convert text description to layout format.

        Args:
            text: Text description of the scene.

        Returns:
            Layout string in SpatialLM format.
        """
        # Generate structured layout description using Claude API
        layout_description = self.claude_api.generate_layout_description(text)
        
        # Convert structured layout description to SpatialLM layout format
        layout_str = self.text_to_layout.generate_layout(layout_description)
        
        return layout_str

    def visualize(self, layout_str: str, output_file: Optional[str] = None) -> None:
        """
        Visualize layout using rerun.

        Args:
            layout_str: Layout string in SpatialLM format.
            output_file: Optional output file path for saving the visualization.
        """
        self.text_to_layout.visualize_layout(layout_str, output_file=output_file)

    def text_to_visualization(self, text: str, output_file: Optional[str] = None) -> str:
        """
        Convert text description to visualization.

        Args:
            text: Text description of the scene.
            output_file: Optional output file path for saving the visualization.

        Returns:
            Layout string in SpatialLM format.
        """
        layout_str = self.convert_text_to_layout(text)
        self.visualize(layout_str, output_file=output_file)
        return layout_str


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Arc LLM")
    parser.add_argument("--text", type=str, help="Text description of the scene")
    parser.add_argument("--text-file", type=str, help="File containing text description")
    parser.add_argument("--output", type=str, help="Output file path for layout")
    parser.add_argument("--vis-output", type=str, help="Output file path for visualization")
    parser.add_argument("--claude-api-key", type=str, help="Claude API key")
    
    args = parser.parse_args()
    
    # Get text input
    if args.text:
        text = args.text
    elif args.text_file:
        with open(args.text_file, "r") as f:
            text = f.read()
    else:
        print("Please provide text input using --text or --text-file")
        return
    
    # Create Arc LLM
    arc_llm = ArcLLM(claude_api_key=args.claude_api_key)
    
    # Convert text to visualization
    layout_str = arc_llm.text_to_visualization(text, output_file=args.vis_output)
    
    # Save layout
    if args.output:
        with open(args.output, "w") as f:
            f.write(layout_str)
    
    print(layout_str)


if __name__ == "__main__":
    main()
