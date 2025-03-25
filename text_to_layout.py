#!/usr/bin/env python3
"""
Text to Layout Converter for SpatialLM

This script takes a text description of a scene and converts it into a layout format
that can be visualized by SpatialLM.
"""

import argparse
import os
import re
import sys
import json
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import rerun as rr
import rerun.blueprint as rrb

# Add SpatialLM to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "SpatialLM"))

from spatiallm import Layout
from spatiallm.layout.entity import Wall, Door, Window, Bbox


class TextToLayout:
    """
    Converts text descriptions to SpatialLM layout format.
    """

    def __init__(self, claude_api_key: Optional[str] = None):
        """
        Initialize the TextToLayout converter.

        Args:
            claude_api_key: Optional API key for Claude API. If not provided,
                            the converter will use rule-based parsing.
        """
        self.claude_api_key = claude_api_key
        self.entity_id_counter = {
            "wall": 0,
            "door": 0,
            "window": 0,
            "bbox": 0,
        }

    def _get_next_id(self, entity_type: str) -> int:
        """Get the next available ID for an entity type."""
        entity_id = self.entity_id_counter[entity_type]
        self.entity_id_counter[entity_type] += 1
        return entity_id

    def _parse_wall(self, description: str, floor_height: float = 0.0) -> List[Wall]:
        """
        Parse wall descriptions from text.
        
        Example: "wall from (0,0,0) to (5,0,0) with height 3 and thickness 0.2"
        
        Args:
            description: Text description to parse
            floor_height: Height offset for the floor (default: 0.0)
        """
        walls = []
        # Simple regex pattern to match wall descriptions
        pattern = r"wall\s+from\s+\(([^)]+)\)\s+to\s+\(([^)]+)\)(?:\s+with\s+height\s+(\d+(?:\.\d+)?))?(?:\s+and\s+thickness\s+(\d+(?:\.\d+)?)?)?"
        matches = re.finditer(pattern, description, re.IGNORECASE)
        
        for match in matches:
            start_point = match.group(1).split(",")
            end_point = match.group(2).split(",")
            height = float(match.group(3) or 2.8)  # Default height
            thickness = float(match.group(4) or 0.2)  # Default thickness
            
            # Apply floor height offset if z coordinate is not explicitly specified
            start_z = float(start_point[2]) if len(start_point) > 2 else floor_height
            end_z = float(end_point[2]) if len(end_point) > 2 else floor_height
            
            wall = Wall(
                id=self._get_next_id("wall"),
                ax=float(start_point[0]),
                ay=float(start_point[1]),
                az=start_z,
                bx=float(end_point[0]),
                by=float(end_point[1]),
                bz=end_z,
                height=height,
                thickness=thickness,
            )
            walls.append(wall)
        
        return walls

    def _parse_door(self, description: str, walls: List[Wall]) -> List[Door]:
        """
        Parse door descriptions from text.
        
        Example: "door on wall 0 at position (2.5,0,0) with width 1 and height 2"
        """
        doors = []
        # Simple regex pattern to match door descriptions
        pattern = r"door\s+on\s+wall\s+(\d+)\s+at\s+position\s+\(([^)]+)\)(?:\s+with\s+width\s+(\d+(?:\.\d+)?))?(?:\s+and\s+height\s+(\d+(?:\.\d+)?)?)?"
        matches = re.finditer(pattern, description, re.IGNORECASE)
        
        for match in matches:
            wall_id = int(match.group(1))
            if wall_id >= len(walls):
                continue  # Skip if wall_id is invalid
                
            position = match.group(2).split(",")
            width = float(match.group(3) or 1.0)  # Default width
            height = float(match.group(4) or 2.0)  # Default height
            
            door = Door(
                id=self._get_next_id("door"),
                wall_id=walls[wall_id].id,
                position_x=float(position[0]),
                position_y=float(position[1]),
                position_z=float(position[2]) if len(position) > 2 else 0.0,
                width=width,
                height=height,
            )
            doors.append(door)
        
        return doors

    def _parse_window(self, description: str, walls: List[Wall]) -> List[Window]:
        """
        Parse window descriptions from text.
        
        Example: "window on wall 1 at position (3,2,1) with width 1.5 and height 1"
        """
        windows = []
        # Simple regex pattern to match window descriptions
        pattern = r"window\s+on\s+wall\s+(\d+)\s+at\s+position\s+\(([^)]+)\)(?:\s+with\s+width\s+(\d+(?:\.\d+)?))?(?:\s+and\s+height\s+(\d+(?:\.\d+)?)?)?"
        matches = re.finditer(pattern, description, re.IGNORECASE)
        
        for match in matches:
            wall_id = int(match.group(1))
            if wall_id >= len(walls):
                continue  # Skip if wall_id is invalid
                
            position = match.group(2).split(",")
            width = float(match.group(3) or 1.5)  # Default width
            height = float(match.group(4) or 1.0)  # Default height
            
            window = Window(
                id=self._get_next_id("window"),
                wall_id=walls[wall_id].id,
                position_x=float(position[0]),
                position_y=float(position[1]),
                position_z=float(position[2]) if len(position) > 2 else 0.0,
                width=width,
                height=height,
            )
            windows.append(window)
        
        return windows

    def _parse_bbox(self, description: str) -> List[Bbox]:
        """
        Parse bounding box descriptions from text.
        
        Example: "a sofa at position (2,4,0) with angle 3.14 and scale (2,0.8,0.8)"
        """
        bboxes = []
        # Simple regex pattern to match bounding box descriptions
        pattern = r"(?:a|an)\s+(\w+)\s+at\s+position\s+\(([^)]+)\)(?:\s+with\s+angle\s+(\d+(?:\.\d+)?))?(?:\s+and\s+scale\s+\(([^)]+)\))?"
        matches = re.finditer(pattern, description, re.IGNORECASE)
        
        for match in matches:
            class_name = match.group(1)
            position = match.group(2).split(",")
            angle = float(match.group(3) or 0.0)  # Default angle
            
            scale = [1.0, 1.0, 1.0]  # Default scale
            if match.group(4):
                scale_parts = match.group(4).split(",")
                scale[0] = float(scale_parts[0])
                if len(scale_parts) > 1:
                    scale[1] = float(scale_parts[1])
                if len(scale_parts) > 2:
                    scale[2] = float(scale_parts[2])
            
            bbox = Bbox(
                id=self._get_next_id("bbox"),
                class_name=class_name,
                position_x=float(position[0]),
                position_y=float(position[1]),
                position_z=float(position[2]) if len(position) > 2 else 0.0,
                angle_z=angle,
                scale_x=scale[0],
                scale_y=scale[1],
                scale_z=scale[2],
            )
            bboxes.append(bbox)
        
        return bboxes
    
    def _parse_fixtures(self, description: str) -> List[Bbox]:
        """
        Parse fixture descriptions from text.
        
        Example: "a sink at position (2,4,0) facing direction north with dimensions (0.6,0.5,0.3)"
        """
        fixtures = []
        # Regex pattern to match fixture descriptions
        pattern = r"a\s+(\w+)\s+at\s+position\s+\(([^)]+)\)\s+facing\s+direction\s+(\w+|\d+(?:\.\d+)?)\s+with\s+dimensions\s+\(([^)]+)\)"
        matches = re.finditer(pattern, description, re.IGNORECASE)
        
        for match in matches:
            fixture_type = match.group(1)
            position = match.group(2).split(",")
            direction = match.group(3)
            dimensions = match.group(4).split(",")
            
            # Convert direction to angle in radians
            angle = 0.0
            if direction.lower() == "north":
                angle = 0.0
            elif direction.lower() == "east":
                angle = 1.5708  # π/2
            elif direction.lower() == "south":
                angle = 3.14159  # π
            elif direction.lower() == "west":
                angle = 4.71239  # 3π/2
            else:
                try:
                    angle = float(direction)
                except ValueError:
                    angle = 0.0
            
            fixture = Bbox(
                id=self._get_next_id("bbox"),
                class_name=fixture_type,
                position_x=float(position[0]),
                position_y=float(position[1]),
                position_z=float(position[2]) if len(position) > 2 else 0.0,
                angle_z=angle,
                scale_x=float(dimensions[0]),
                scale_y=float(dimensions[1]),
                scale_z=float(dimensions[2]) if len(dimensions) > 2 else 0.5,
            )
            fixtures.append(fixture)
        
        return fixtures
    
    def _parse_built_ins(self, description: str, walls: List[Wall]) -> List[Bbox]:
        """
        Parse built-in furniture descriptions from text.
        
        Example: "a built-in cabinet along wall 0 from position (1,0,0) to (3,0,0) with height 2.0"
        """
        built_ins = []
        # Regex pattern to match built-in descriptions
        pattern = r"a\s+built-in\s+(\w+)\s+along\s+wall\s+(\d+)\s+from\s+position\s+\(([^)]+)\)\s+to\s+\(([^)]+)\)(?:\s+with\s+height\s+(\d+(?:\.\d+)?)?)?"
        matches = re.finditer(pattern, description, re.IGNORECASE)
        
        for match in matches:
            built_in_type = match.group(1)
            wall_id = int(match.group(2))
            if wall_id >= len(walls):
                continue  # Skip if wall_id is invalid
                
            start_pos = match.group(3).split(",")
            end_pos = match.group(4).split(",")
            height = float(match.group(5) or 2.0)  # Default height
            
            # Calculate center position and scale
            center_x = (float(start_pos[0]) + float(end_pos[0])) / 2
            center_y = (float(start_pos[1]) + float(end_pos[1])) / 2
            center_z = (float(start_pos[2]) if len(start_pos) > 2 else 0.0 + 
                        float(end_pos[2]) if len(end_pos) > 2 else 0.0) / 2
            
            # Calculate length (distance between start and end)
            length = np.sqrt((float(end_pos[0]) - float(start_pos[0]))**2 + 
                             (float(end_pos[1]) - float(start_pos[1]))**2)
            
            # Get wall direction to determine orientation
            wall = walls[wall_id]
            wall_direction = np.arctan2(wall.by - wall.ay, wall.bx - wall.ax)
            
            built_in = Bbox(
                id=self._get_next_id("bbox"),
                class_name=built_in_type,
                position_x=center_x,
                position_y=center_y,
                position_z=center_z,
                angle_z=wall_direction,
                scale_x=length,
                scale_y=0.6,  # Default depth
                scale_z=height,
            )
            built_ins.append(built_in)
        
        return built_ins
    
    def _parse_architectural_features(self, description: str) -> List[Bbox]:
        """
        Parse architectural feature descriptions from text.
        
        Example: "a column at position (2,4,0) with dimensions (0.5,0.5,3.0) and style doric"
        """
        features = []
        # Regex pattern to match architectural feature descriptions
        pattern = r"a\s+(\w+)\s+at\s+position\s+\(([^)]+)\)\s+with\s+dimensions\s+\(([^)]+)\)(?:\s+and\s+style\s+(\w+))?"
        matches = re.finditer(pattern, description, re.IGNORECASE)
        
        for match in matches:
            feature_type = match.group(1)
            position = match.group(2).split(",")
            dimensions = match.group(3).split(",")
            style = match.group(4) or "default"  # Default style
            
            # Combine feature type and style for the class name
            class_name = f"{feature_type}_{style}"
            
            feature = Bbox(
                id=self._get_next_id("bbox"),
                class_name=class_name,
                position_x=float(position[0]),
                position_y=float(position[1]),
                position_z=float(position[2]) if len(position) > 2 else 0.0,
                angle_z=0.0,  # Default angle
                scale_x=float(dimensions[0]),
                scale_y=float(dimensions[1]),
                scale_z=float(dimensions[2]) if len(dimensions) > 2 else 3.0,
            )
            features.append(feature)
        
        return features

    def _generate_layout_with_claude(self, text: str) -> str:
        """
        Generate layout using Claude API.
        
        Args:
            text: Text description of the scene.
            
        Returns:
            Layout string in SpatialLM format.
        """
        # This is a placeholder for Claude API integration
        # In a real implementation, this would call the Claude API
        # and parse the response to generate a layout
        
        # For now, we'll use a simple rule-based approach
        return self._generate_layout_rule_based(text)

    def _parse_floors_and_rooms(self, description: str) -> Dict[int, Dict]:
        """
        Parse floor and room descriptions from text.
        
        Example: 
        "floor 0 at height 0 with dimensions (10, 15)"
        "room living_room on floor 0 with dimensions (5, 7) connected to kitchen via opening"
        
        Returns:
            Dictionary mapping floor numbers to floor information
        """
        floors = {}
        
        # Parse floors
        floor_pattern = r"floor\s+(\d+)\s+at\s+height\s+(\d+(?:\.\d+)?)\s+with\s+dimensions\s+\(([^)]+)\)"
        floor_matches = re.finditer(floor_pattern, description, re.IGNORECASE)
        
        for match in floor_matches:
            floor_num = int(match.group(1))
            height = float(match.group(2))
            dimensions = match.group(3).split(",")
            width = float(dimensions[0])
            length = float(dimensions[1]) if len(dimensions) > 1 else width
            
            floors[floor_num] = {
                "height": height,
                "width": width,
                "length": length,
                "rooms": {}
            }
        
        # If no floors defined, create a default ground floor
        if not floors:
            floors[0] = {
                "height": 0.0,
                "width": 10.0,
                "length": 10.0,
                "rooms": {}
            }
        
        # Parse rooms
        room_pattern = r"room\s+(\w+)\s+on\s+floor\s+(\d+)\s+with\s+dimensions\s+\(([^)]+)\)(?:\s+connected\s+to\s+(\w+)\s+via\s+(\w+))?"
        room_matches = re.finditer(room_pattern, description, re.IGNORECASE)
        
        for match in room_matches:
            room_name = match.group(1)
            floor_num = int(match.group(2))
            dimensions = match.group(3).split(",")
            connected_to = match.group(4)
            connection_type = match.group(5)
            
            width = float(dimensions[0])
            length = float(dimensions[1]) if len(dimensions) > 1 else width
            
            if floor_num not in floors:
                # If floor not defined, create it
                floors[floor_num] = {
                    "height": floor_num * 3.0,  # Assume 3m per floor
                    "width": max(10.0, width),
                    "length": max(10.0, length),
                    "rooms": {}
                }
            
            floors[floor_num]["rooms"][room_name] = {
                "width": width,
                "length": length,
                "connected_to": connected_to,
                "connection_type": connection_type
            }
        
        return floors
    
    def _generate_layout_rule_based(self, text: str) -> str:
        """
        Generate layout using rule-based parsing.
        
        Args:
            text: Text description of the scene.
            
        Returns:
            Layout string in SpatialLM format.
        """
        # Reset entity ID counters
        self.entity_id_counter = {
            "wall": 0,
            "door": 0,
            "window": 0,
            "bbox": 0,
        }
        
        # Parse floors and rooms
        floors = self._parse_floors_and_rooms(text)
        
        # Create layout
        layout = Layout()
        layout.walls = []
        layout.doors = []
        layout.windows = []
        layout.bboxes = []
        
        # Process each floor
        for floor_num, floor_info in floors.items():
            floor_height = floor_info["height"]
            
            # Parse entities for this floor
            walls = self._parse_wall(text, floor_height)
            layout.walls.extend(walls)
            
            doors = self._parse_door(text, walls)
            layout.doors.extend(doors)
            
            windows = self._parse_window(text, walls)
            layout.windows.extend(windows)
            
            # Parse furniture and objects
            bboxes = self._parse_bbox(text)
            layout.bboxes.extend(bboxes)
            
            # Parse fixtures (sinks, toilets, etc.)
            fixtures = self._parse_fixtures(text)
            layout.bboxes.extend(fixtures)
            
            # Parse built-in furniture
            built_ins = self._parse_built_ins(text, walls)
            layout.bboxes.extend(built_ins)
            
            # Parse architectural features
            features = self._parse_architectural_features(text)
            layout.bboxes.extend(features)
        
        return layout.to_language_string()

    def generate_layout(self, text: str) -> str:
        """
        Generate layout from text description.
        
        Args:
            text: Text description of the scene.
            
        Returns:
            Layout string in SpatialLM format.
        """
        if self.claude_api_key:
            return self._generate_layout_with_claude(text)
        else:
            return self._generate_layout_rule_based(text)

    def visualize_layout(self, layout_str: str, output_file: Optional[str] = None) -> None:
        """
        Visualize layout using rerun.
        
        Args:
            layout_str: Layout string in SpatialLM format.
            output_file: Optional output file path for saving the visualization.
        """
        # Parse layout
        layout = Layout(layout_str)
        floor_plan = layout.to_boxes()
        
        # ReRun visualization
        blueprint = rrb.Blueprint(
            rrb.Spatial3DView(name="3D", origin="/world", background=[255, 255, 255]),
            collapse_panels=True,
        )
        
        if output_file:
            rr.init("rerun_arcllm", save_to_file=output_file)
        else:
            rr.init("rerun_arcllm", default_blueprint=blueprint)
        
        rr.log("world", rr.ViewCoordinates.RIGHT_HAND_Z_UP, static=True)
        
        num_entities = len(floor_plan)
        seconds = 0.5
        for ti in range(num_entities + 1):
            sub_floor_plan = floor_plan[:ti]
            
            rr.set_time_seconds("time_sec", ti * seconds)
            for box in sub_floor_plan:
                uid = box["id"]
                group = box["class"]
                label = box["label"]
                
                rr.log(
                    f"world/pred/{group}/{uid}",
                    rr.Boxes3D(
                        centers=box["center"],
                        half_sizes=0.5 * box["scale"],
                        labels=label,
                    ),
                    rr.InstancePoses3D(mat3x3=box["rotation"]),
                    static=False,
                )
        
        if not output_file:
            rr.script_main()


def main():
    parser = argparse.ArgumentParser(description="Convert text to SpatialLM layout")
    parser.add_argument("--text", type=str, help="Text description of the scene")
    parser.add_argument("--text-file", type=str, help="File containing text description")
    parser.add_argument("--output", type=str, help="Output file path for layout")
    parser.add_argument("--visualize", action="store_true", help="Visualize the layout")
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
    
    # Create converter
    converter = TextToLayout(claude_api_key=args.claude_api_key)
    
    # Generate layout
    layout_str = converter.generate_layout(text)
    
    # Save layout
    if args.output:
        with open(args.output, "w") as f:
            f.write(layout_str)
    
    # Visualize layout
    if args.visualize:
        converter.visualize_layout(layout_str, output_file=args.vis_output)
    
    print(layout_str)


if __name__ == "__main__":
    main()
