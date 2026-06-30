import struct
import math

def get_bounds(file_path, scale=0.001):
    try:
        with open(file_path, 'rb') as f:
            f.read(80)
            num_triangles = struct.unpack('<I', f.read(4))[0]
            
            min_x = min_y = min_z = float('inf')
            max_x = max_y = max_z = float('-inf')
            
            for i in range(num_triangles):
                f.read(12)
                v1 = struct.unpack('<fff', f.read(12))
                v2 = struct.unpack('<fff', f.read(12))
                v3 = struct.unpack('<fff', f.read(12))
                f.read(2)
                
                for v in [v1, v2, v3]:
                    x, y, z = v[0]*scale, v[1]*scale, v[2]*scale
                    min_x = min(min_x, x)
                    max_x = max(max_x, x)
                    min_y = min(min_y, y)
                    max_y = max(max_y, y)
                    min_z = min(min_z, z)
                    max_z = max(max_z, z)
                    
            print(f"{file_path.split('/')[-1]}:")
            print(f"  X: {min_x:.4f} to {max_x:.4f} (Size: {max_x-min_x:.4f} m)")
            print(f"  Y: {min_y:.4f} to {max_y:.4f} (Size: {max_y-min_y:.4f} m)")
            print(f"  Z: {min_z:.4f} to {max_z:.4f} (Size: {max_z-min_z:.4f} m)")
    except Exception as e:
        print(f"Failed: {e}")

base = "/home/deniz/generalrobotcontrol/src/ME462RobotControl/my_robot_cell/my_robot_cell_description/meshes/end_effectors/"
get_bounds(base + "tutan-khamun.stl", 0.001)
get_bounds(base + "CleanerTool.stl", 0.001)
get_bounds(base + "PenTool.stl", 0.001)
