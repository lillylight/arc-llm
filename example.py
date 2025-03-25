#!/usr/bin/env python3
"""
Arc LLM Example

This script demonstrates how to use Arc LLM to convert text descriptions
into 2D and 3D visualizations.
"""

import os
import argparse
from arc_llm import ArcLLM


def main():
    parser = argparse.ArgumentParser(description="Arc LLM Example")
    parser.add_argument("--api-key", type=str, help="Claude API key")
    parser.add_argument("--text", type=str, help="Text description of the scene")
    parser.add_argument("--output", type=str, default="layout.txt", help="Output file path for layout")
    parser.add_argument("--vis-output", type=str, help="Output file path for visualization")
    
    args = parser.parse_args()
    
    # Get Claude API key
    claude_api_key = args.api_key or os.environ.get("CLAUDE_API_KEY")
    if not claude_api_key:
        claude_api_key = input("Enter your Claude API key: ")
    
    # Get text input
    text = args.text
    if not text:
        text = input("Enter a text description of a scene: ")
    
    # Create Arc LLM
    arc_llm = ArcLLM(claude_api_key=claude_api_key)
    
    # Generate layout from text
    print(f"Generating layout from text: {text}")
    layout_str = arc_llm.convert_text_to_layout(text)
    
    # Save layout
    with open(args.output, "w") as f:
        f.write(layout_str)
    print(f"Layout saved to {args.output}")
    
    # Visualize layout
    print("Visualizing layout...")
    arc_llm.visualize(layout_str, output_file=args.vis_output)
    
    if args.vis_output:
        print(f"Visualization saved to {args.vis_output}")
        print(f"To view the visualization, run: rerun {args.vis_output}")
    else:
        print("Visualization displayed in a new window.")


if __name__ == "__main__":
    main()
