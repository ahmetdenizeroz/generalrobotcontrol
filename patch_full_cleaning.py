import os

path = '/home/deniz/generalrobotcontrol/src/ME462RobotControl/zenpool_draw_letter/scripts/full_cleaning.py'

with open(path, 'r') as f:
    content = f.read()

# 1. Imports
content = content.replace(
"""from moveit_msgs.srv import GetCartesianPath, GetMotionPlan
from moveit_msgs.msg import Constraints, JointConstraint
from geometry_msgs.msg import Pose""",
"""from moveit_msgs.srv import GetMotionPlan
from moveit_msgs.msg import Constraints, JointConstraint, PositionConstraint, OrientationConstraint, BoundingVolume
from shape_msgs.msg import SolidPrimitive
from geometry_msgs.msg import Pose"""
)

# 2. scale_trajectory_speed removal
import re
pattern_scale = re.compile(r'    def scale_trajectory_speed\(self, traj, speed_factor\):.*?        return traj\n', re.DOTALL)
content = pattern_scale.sub('', content)

# 3. execute_joint_trajectory_safe
content = content.replace("        traj = self.scale_trajectory_speed(traj, self.joint_speed)\n", "")

# 4. execute_cartesian_path -> execute_pilz_lin
pattern_cart = re.compile(r'    def execute_cartesian_path\(self, waypoints\):.*?        return self\.execute_trajectory\(traj\)\n', re.DOTALL)
pilz_func = """    def execute_pilz_lin(self, target_pose):
        if not self.plan_client.wait_for_service(timeout_sec=5.0):
            return False
            
        req = GetMotionPlan.Request()
        req.motion_plan_request.pipeline_id = 'pilz_industrial_motion_planner'
        req.motion_plan_request.planner_id = 'LIN'
        req.motion_plan_request.group_name = 'ur_arm'
        req.motion_plan_request.max_velocity_scaling_factor = self.cart_speed
        req.motion_plan_request.max_acceleration_scaling_factor = self.cart_speed
        
        c = Constraints()
        pc = PositionConstraint()
        pc.link_name = 'ur5e_tool0'
        pc.header.frame_id = 'ur5e_base_link'
        bv = BoundingVolume()
        sp = SolidPrimitive()
        sp.type = SolidPrimitive.SPHERE
        sp.dimensions = [0.001]
        bv.primitives.append(sp)
        bv.primitive_poses.append(target_pose)
        pc.constraint_region = bv
        pc.weight = 1.0
        
        oc = OrientationConstraint()
        oc.link_name = 'ur5e_tool0'
        oc.header.frame_id = 'ur5e_base_link'
        oc.orientation = target_pose.orientation
        oc.absolute_x_axis_tolerance = 0.01
        oc.absolute_y_axis_tolerance = 0.01
        oc.absolute_z_axis_tolerance = 0.01
        oc.weight = 1.0
        
        c.position_constraints.append(pc)
        c.orientation_constraints.append(oc)
        req.motion_plan_request.goal_constraints.append(c)
        
        future = self.plan_client.call_async(req)
        result = wait_for_future(self, future)
        
        if not result or result.motion_plan_response.error_code.val != 1:
            self.get_logger().error(f"Failed Pilz LIN Path! Error code: {result.motion_plan_response.error_code.val if result else 'None'}")
            return False
            
        traj = result.motion_plan_response.trajectory.joint_trajectory
        return self.execute_trajectory(traj)
"""
content = pattern_cart.sub(pilz_func, content)

# 5. execute_absolute_cartesian
content = content.replace("return self.execute_cartesian_path([target])", "return self.execute_pilz_lin(target)")

# 6. execute_reorient
pattern_reorient = re.compile(r'    def execute_reorient\(self, pitch_deg, roll_deg, yaw_deg\):.*?        return self\.execute_cartesian_path\(waypoints\)\n', re.DOTALL)
reorient_func = """    def execute_reorient(self, pitch_deg, roll_deg, yaw_deg):
        self.get_logger().info(f"Rotating to Pitch:{pitch_deg}, Roll:{roll_deg}, Yaw:{yaw_deg} (wrt Z-axis table frame)")
        curr = self.get_current_pose()
        if not curr: return False
        
        start_q = curr.transform.rotation
        start_roll, start_pitch, start_yaw = euler_from_quaternion(start_q.x, start_q.y, start_q.z, start_q.w)
        
        table_offset_deg = 45.0
        target_roll = math.pi + math.radians(pitch_deg)
        target_pitch = 0.0 + math.radians(roll_deg)
        target_yaw = math.radians(yaw_deg + table_offset_deg)
        
        new_q = quaternion_from_euler(target_roll, target_pitch, target_yaw)
        
        target = Pose()
        target.position = curr.transform.translation
        target.orientation.x = new_q[0]
        target.orientation.y = new_q[1]
        target.orientation.z = new_q[2]
        target.orientation.w = new_q[3]
        
        return self.execute_pilz_lin(target)
"""
content = pattern_reorient.sub(reorient_func, content)

with open(path, 'w') as f:
    f.write(content)

print("full_cleaning Pilz patch applied successfully!")
