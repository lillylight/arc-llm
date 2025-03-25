#!/usr/bin/env python3
"""
Run Example

This script demonstrates how to use Arc LLM with the provided example files.
"""

import os
import argparse
from arc_llm import ArcLLM


def main():
    parser = argparse.ArgumentParser(description="Run Arc LLM Example")
    parser.add_argument("--api-key", type=str, help="Claude API key")
    parser.add_argument("--use-description", action="store_true", help="Use the structured description instead of generating from text")
    parser.add_argument("--complex", action="store_true", help="Use the complex house example instead of the simple living room")
    parser.add_argument("--output", type=str, default="layout.txt", help="Output file path for layout")
    parser.add_argument("--vis-output", type=str, help="Output file path for visualization")
    
    args = parser.parse_args()
    
    # Get Claude API key
    claude_api_key = args.api_key or os.environ.get("CLAUDE_API_KEY")
    if not claude_api_key:
        claude_api_key = input("Enter your Claude API key: ")
    
    # Create Arc LLM
    arc_llm = ArcLLM(claude_api_key=claude_api_key)
    
    # Determine which example to use
    example_prefix = "complex_house" if args.complex else "living_room"
    
    # Load example text
    with open(f"examples/{example_prefix}.txt", "r") as f:
        text = f.read()
    
    print(f"Text description:\n{text}\n")
    
    if args.use_description:
        # Load example structured description
        with open(f"examples/{example_prefix}_description.txt", "r") as f:
            description = f.read()
        
        print(f"Structured description:\n{description}\n")
        
        # Generate layout from structured description
        layout_str = arc_llm.text_to_layout.generate_layout(description)
    else:
        # Generate layout from text
        layout_str = arc_llm.convert_text_to_layout(text)
    
    print(f"Generated layout:\n{layout_str}\n")
    
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
