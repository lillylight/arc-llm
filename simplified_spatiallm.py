"""
Simplified SpatialLM module for Arc LLM

This module provides a simplified version of the SpatialLM Layout class
that doesn't require torchsparse or other point cloud processing dependencies.
"""

import numpy as np
import rerun as rr
import rerun.blueprint as rrb


class Wall:
    """Wall entity for layout."""
    
    def __init__(self, id=0, ax=0, ay=0, az=0, bx=0, by=0, bz=0, height=0, thickness=0):
        self.id = id
        self.ax = ax
        self.ay = ay
        self.az = az
        self.bx = bx
        self.by = by
        self.bz = bz
        self.height = height
        self.thickness = thickness


class Door:
    """Door entity for layout."""
    
    def __init__(self, wall_id=0, position_x=0, position_y=0, position_z=0, width=0, height=0, id=0):
        self.id = id
        self.wall_id = wall_id
        self.position_x = position_x
        self.position_y = position_y
        self.position_z = position_z
        self.width = width
        self.height = height


class Window:
    """Window entity for layout."""
    
    def __init__(self, wall_id=0, position_x=0, position_y=0, position_z=0, width=0, height=0, id=0):
        self.id = id
        self.wall_id = wall_id
        self.position_x = position_x
        self.position_y = position_y
        self.position_z = position_z
        self.width = width
        self.height = height


class Bbox:
    """Bounding box entity for layout."""
    
    def __init__(self, class_name='', position_x=0, position_y=0, position_z=0, angle_z=0, scale_x=0, scale_y=0, scale_z=0, id=0):
        self.id = id
        self.class_name = class_name
        self.position_x = position_x
        self.position_y = position_y
        self.position_z = position_z
        self.angle_z = angle_z
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.scale_z = scale_z


class Layout:
    """Layout class for SpatialLM."""
    
    def __init__(self, layout_str=None):
        """Initialize Layout."""
        self.walls = []
        self.doors = []
        self.windows = []
        self.bboxes = []
        
        if layout_str:
            self._parse_layout_str(layout_str)
    
    def _parse_layout_str(self, layout_str):
        """Parse layout string."""
        lines = layout_str.strip().split('\n')
        
        for line in lines:
            if not line or line.startswith('#'):
                continue
                
            if '=' not in line:
                continue
                
            entity_id, entity_str = line.split('=', 1)
            entity_id = entity_id.strip()
            entity_type = entity_id.split('_')[0]
            
            if entity_type == 'wall':
                # Parse wall
                # Example: Wall(0.0,0.0,0.0,5.0,0.0,0.0,2.8,0.2)
                params = entity_str.strip('Wall()').split(',')
                if len(params) >= 8:
                    wall = Wall(
                        id=int(entity_id.split('_')[1]),
                        ax=float(params[0]),
                        ay=float(params[1]),
                        az=float(params[2]),
                        bx=float(params[3]),
                        by=float(params[4]),
                        bz=float(params[5]),
                        height=float(params[6]),
                        thickness=float(params[7]),
                    )
                    self.walls.append(wall)
            
            elif entity_type == 'door':
                # Parse door
                # Example: Door(wall_0,2.5,0.0,0.0,1.0,2.0)
                params = entity_str.strip('Door()').split(',')
                if len(params) >= 6:
                    wall_id = int(params[0].split('_')[1])
                    door = Door(
                        id=int(entity_id.split('_')[1]),
                        wall_id=wall_id,
                        position_x=float(params[1]),
                        position_y=float(params[2]),
                        position_z=float(params[3]),
                        width=float(params[4]),
                        height=float(params[5]),
                    )
                    self.doors.append(door)
            
            elif entity_type == 'window':
                # Parse window
                # Example: Window(wall_1,2.5,0.0,1.0,1.5,1.0)
                params = entity_str.strip('Window()').split(',')
                if len(params) >= 6:
                    wall_id = int(params[0].split('_')[1])
                    window = Window(
                        id=int(entity_id.split('_')[1]),
                        wall_id=wall_id,
                        position_x=float(params[1]),
                        position_y=float(params[2]),
                        position_z=float(params[3]),
                        width=float(params[4]),
                        height=float(params[5]),
                    )
                    self.windows.append(window)
            
            elif entity_type == 'bbox':
                # Parse bbox
                # Example: Bbox(sofa,2.5,0.5,0.0,0.0,2.0,0.8,0.8)
                params = entity_str.strip('Bbox()').split(',')
                if len(params) >= 8:
                    bbox = Bbox(
                        id=int(entity_id.split('_')[1]),
                        class_name=params[0],
                        position_x=float(params[1]),
                        position_y=float(params[2]),
                        position_z=float(params[3]),
                        angle_z=float(params[4]),
                        scale_x=float(params[5]),
                        scale_y=float(params[6]),
                        scale_z=float(params[7]),
                    )
                    self.bboxes.append(bbox)
    
    def to_language_string(self):
        """Convert layout to language string."""
        lines = []
        
        # Add walls
        for wall in self.walls:
            lines.append(f"wall_{wall.id}=Wall({wall.ax},{wall.ay},{wall.az},{wall.bx},{wall.by},{wall.bz},{wall.height},{wall.thickness})")
        
        # Add doors
        for door in self.doors:
            lines.append(f"door_{door.id}=Door(wall_{door.wall_id},{door.position_x},{door.position_y},{door.position_z},{door.width},{door.height})")
        
        # Add windows
        for window in self.windows:
            lines.append(f"window_{window.id}=Window(wall_{window.wall_id},{window.position_x},{window.position_y},{window.position_z},{window.width},{window.height})")
        
        # Add bboxes
        for bbox in self.bboxes:
            lines.append(f"bbox_{bbox.id}=Bbox({bbox.class_name},{bbox.position_x},{bbox.position_y},{bbox.position_z},{bbox.angle_z},{bbox.scale_x},{bbox.scale_y},{bbox.scale_z})")
        
        return '\n'.join(lines)
    
    def to_boxes(self):
        """Convert layout to boxes for visualization."""
        boxes = []
        
        # Add walls
        for wall in self.walls:
            # Calculate center and scale
            center_x = (wall.ax + wall.bx) / 2
            center_y = (wall.ay + wall.by) / 2
            center_z = (wall.az + wall.bz) / 2 + wall.height / 2
            
            # Calculate length (distance between start and end)
            length = np.sqrt((wall.bx - wall.ax)**2 + (wall.by - wall.ay)**2)
            
            # Calculate rotation
            angle = np.arctan2(wall.by - wall.ay, wall.bx - wall.ax)
            rotation = np.array([
                [np.cos(angle), -np.sin(angle), 0],
                [np.sin(angle), np.cos(angle), 0],
                [0, 0, 1]
            ])
            
            boxes.append({
                'id': f'wall_{wall.id}',
                'class': 'wall',
                'label': 'wall',
                'center': [center_x, center_y, center_z],
                'scale': [length, wall.thickness, wall.height],
                'rotation': rotation.tolist(),
            })
        
        # Add doors
        for door in self.doors:
            # Find the corresponding wall
            wall = next((w for w in self.walls if w.id == door.wall_id), None)
            if wall is None:
                continue
            
            # Calculate center
            center_x = door.position_x
            center_y = door.position_y
            center_z = door.position_z + door.height / 2
            
            # Calculate rotation (same as wall)
            angle = np.arctan2(wall.by - wall.ay, wall.bx - wall.ax)
            rotation = np.array([
                [np.cos(angle), -np.sin(angle), 0],
                [np.sin(angle), np.cos(angle), 0],
                [0, 0, 1]
            ])
            
            boxes.append({
                'id': f'door_{door.id}',
                'class': 'door',
                'label': 'door',
                'center': [center_x, center_y, center_z],
                'scale': [door.width, wall.thickness, door.height],
                'rotation': rotation.tolist(),
            })
        
        # Add windows
        for window in self.windows:
            # Find the corresponding wall
            wall = next((w for w in self.walls if w.id == window.wall_id), None)
            if wall is None:
                continue
            
            # Calculate center
            center_x = window.position_x
            center_y = window.position_y
            center_z = window.position_z + window.height / 2
            
            # Calculate rotation (same as wall)
            angle = np.arctan2(wall.by - wall.ay, wall.bx - wall.ax)
            rotation = np.array([
                [np.cos(angle), -np.sin(angle), 0],
                [np.sin(angle), np.cos(angle), 0],
                [0, 0, 1]
            ])
            
            boxes.append({
                'id': f'window_{window.id}',
                'class': 'window',
                'label': 'window',
                'center': [center_x, center_y, center_z],
                'scale': [window.width, wall.thickness, window.height],
                'rotation': rotation.tolist(),
            })
        
        # Add bboxes
        for bbox in self.bboxes:
            # Calculate rotation
            rotation = np.array([
                [np.cos(bbox.angle_z), -np.sin(bbox.angle_z), 0],
                [np.sin(bbox.angle_z), np.cos(bbox.angle_z), 0],
                [0, 0, 1]
            ])
            
            boxes.append({
                'id': f'bbox_{bbox.id}',
                'class': bbox.class_name,
                'label': bbox.class_name,
                'center': [bbox.position_x, bbox.position_y, bbox.position_z],
                'scale': [bbox.scale_x, bbox.scale_y, bbox.scale_z],
                'rotation': rotation.tolist(),
            })
        
        return boxes


def visualize_layout(layout_str, output_file=None):
    """Visualize layout using rerun."""
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
                    half_sizes=0.5 * np.array(box["scale"]),
                    labels=label,
                ),
                rr.InstancePoses3D(mat3x3=box["rotation"]),
                static=False,
            )
    
    if not output_file:
        rr.script_main()
