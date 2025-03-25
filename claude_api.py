#!/usr/bin/env python3
"""
Claude API Integration for Arc LLM

This module provides integration with the Claude API for generating structured
layout descriptions from text input.
"""

import os
import json
import requests
from typing import Dict, List, Optional, Union, Any


class ClaudeAPI:
    """
    Client for interacting with the Claude API.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Claude API client.

        Args:
            api_key: Claude API key. If not provided, will look for CLAUDE_API_KEY
                    environment variable.
        """
        self.api_key = api_key or os.environ.get("CLAUDE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Claude API key not provided. Please provide an API key or "
                "set the CLAUDE_API_KEY environment variable."
            )
        
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: str = "claude-3-opus-20240229",
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> str:
        """
        Generate a response from Claude.

        Args:
            prompt: The user prompt to send to Claude.
            system_prompt: Optional system prompt to provide context.
            model: Claude model to use.
            max_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature.

        Returns:
            Generated text response.
        """
        if system_prompt is None:
            system_prompt = (
                "You are a helpful assistant that generates structured layout descriptions "
                "for 3D scenes. Your task is to convert the user's text description into "
                "a structured format that can be used to create a 3D visualization."
            )

        data = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        }

        response = requests.post(
            self.api_url,
            headers=self.headers,
            json=data,
        )

        if response.status_code != 200:
            raise Exception(f"API request failed: {response.text}")

        result = response.json()
        return result["content"][0]["text"]

    def generate_layout_description(self, text: str) -> str:
        """
        Generate a structured layout description from text.

        Args:
            text: Text description of the scene.

        Returns:
            Structured layout description.
        """
        system_prompt = """
        You are a specialized assistant that converts natural language descriptions of buildings, houses, and spaces into structured layout descriptions. Your task is to analyze the user's description and generate a structured representation that follows these specific formats:

        # Basic Elements
        1. Walls: "wall from (x1,y1,z1) to (x2,y2,z2) with height h and thickness t"
        2. Doors: "door on wall N at position (x,y,z) with width w and height h"
        3. Windows: "window on wall N at position (x,y,z) with width w and height h"
        4. Objects: "a [object_name] at position (x,y,z) with angle a and scale (sx,sy,sz)"

        # Multi-Floor Support
        5. Floors: "floor N at height h with dimensions (width, length)"
        6. Staircases: "staircase from floor N to floor M at position (x,y,z) with width w and direction d"

        # Room Relationships
        7. Rooms: "room [room_name] on floor N with dimensions (width, length) connected to [other_room] via [connection_type]"
        8. Open Areas: "open area between [room1] and [room2] with dimensions (width, length)"

        # Advanced Object Types
        9. Architectural Features: "a [feature_type] at position (x,y,z) with dimensions (w,l,h) and style [style]"
        10. Built-ins: "a built-in [type] along wall N from position (x1,y1,z1) to (x2,y2,z2) with height h"
        11. Fixtures: "a [fixture_type] at position (x,y,z) facing direction d with dimensions (w,l,h)"

        # Measurement and Proportion
        12. Dimensions: "set [room/object] dimensions to (w,l,h) in [units]"
        13. Proportions: "make [room1] [X] times larger than [room2]"
        14. Constraints: "ensure minimum distance of [distance] between [object1] and [object2]"

        # Style and Material
        15. Materials: "set [element] material to [material_type] with color [color]"
        16. Style: "apply [style_name] style to [room/entire_house]"

        Where:
        - Coordinates are in meters unless otherwise specified
        - Wall N refers to the Nth wall defined (starting from 0)
        - Floor N refers to the Nth floor (0 = ground floor, 1 = first floor, etc.)
        - Angles are in radians
        - Scale values are in meters
        - Connection types include: "door", "opening", "archway"
        - Direction values include: "north", "south", "east", "west" or degrees in radians

        Your response should ONLY contain these structured descriptions, one per line, with no additional text or explanations. Use reasonable default values for any dimensions not specified in the description.

        For complex descriptions like multi-floor buildings or houses with multiple rooms, organize your response by floor and then by room, using comments (lines starting with #) to indicate sections:

        # Example output for a two-story house:
        # Ground Floor
        floor 0 at height 0 with dimensions (10, 15)
        room living_room on floor 0 with dimensions (5, 7) connected to kitchen via opening
        wall from (0,0,0) to (5,0,0) with height 2.8 and thickness 0.2
        wall from (5,0,0) to (5,7,0) with height 2.8 and thickness 0.2
        wall from (5,7,0) to (0,7,0) with height 2.8 and thickness 0.2
        wall from (0,7,0) to (0,0,0) with height 2.8 and thickness 0.2
        window on wall 0 at position (2.5,0,1.0) with width 1.5 and height 1.0
        a sofa at position (2.5,6,0) with angle 3.14 and scale (2.0,0.8,0.8)
        a coffee_table at position (2.5,4,0) with angle 0 and scale (1.2,1.2,0.5)
        
        room kitchen on floor 0 with dimensions (5, 5) connected to living_room via opening
        wall from (5,0,0) to (10,0,0) with height 2.8 and thickness 0.2
        wall from (10,0,0) to (10,5,0) with height 2.8 and thickness 0.2
        wall from (10,5,0) to (5,5,0) with height 2.8 and thickness 0.2
        a built-in cabinet along wall 0 from position (6,0,0) to (9,0,0) with height 2.0
        
        # First Floor
        floor 1 at height 3.0 with dimensions (10, 15)
        staircase from floor 0 to floor 1 at position (8,10,0) with width 1.0 and direction west
        
        room bedroom on floor 1 with dimensions (5, 5) connected to hallway via door
        wall from (0,0,3.0) to (5,0,3.0) with height 2.8 and thickness 0.2
        wall from (5,0,3.0) to (5,5,3.0) with height 2.8 and thickness 0.2
        wall from (5,5,3.0) to (0,5,3.0) with height 2.8 and thickness 0.2
        wall from (0,5,3.0) to (0,0,3.0) with height 2.8 and thickness 0.2
        door on wall 2 at position (2.5,5,3.0) with width 1.0 and height 2.0
        a bed at position (2.5,2.5,3.0) with angle 0 and scale (2.0,1.6,0.5)
        """

        prompt = f"""
        Please convert the following description into a structured layout format:

        {text}

        Remember to follow the specified format exactly, with one structure per line.
        """

        return self.generate(prompt, system_prompt=system_prompt)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test Claude API integration")
    parser.add_argument("--api-key", type=str, help="Claude API key")
    parser.add_argument("--text", type=str, help="Text description of the scene")
    parser.add_argument("--text-file", type=str, help="File containing text description")
    
    args = parser.parse_args()
    
    # Get text input
    if args.text:
        text = args.text
    elif args.text_file:
        with open(args.text_file, "r") as f:
            text = f.read()
    else:
        text = "A living room with a sofa against the north wall, a coffee table in the center, and a TV on the south wall. There's a window on the east wall and a door on the west wall."
    
    # Create Claude API client
    claude_api = ClaudeAPI(api_key=args.api_key)
    
    # Generate layout description
    layout_description = claude_api.generate_layout_description(text)
    
    print(layout_description)
