import re

path = '/home/deniz/generalrobotcontrol/src/ME462RobotControl/zenpool_draw_letter/scripts/full_cleaning.py'

with open(path, 'r') as f:
    content = f.read()

# 1. Imports
content = content.replace(
"""from moveit_msgs.srv import GetMotionPlan
from moveit_msgs.msg import Constraints, JointConstraint, PositionConstraint, OrientationConstraint, BoundingVolume
from shape_msgs.msg import SolidPrimitive
from geometry_msgs.msg import Pose""",
"""from moveit_msgs.srv import GetCartesianPath, GetMotionPlan
from moveit_msgs.msg import Constraints, JointConstraint
from geometry_msgs.msg import Pose"""
)

# 2. Add cartesian client back
content = content.replace(
"        self.plan_client = self.create_client(GetMotionPlan, '/plan_kinematic_path')",
"        self.cartesian_client = self.create_client(GetCartesianPath, '/compute_cartesian_path')\n        self.plan_client = self.create_client(GetMotionPlan, '/plan_kinematic_path')"
)

# 3. Add scale_trajectory_speed
scale_func = """    def scale_trajectory_speed(self, traj, speed_factor):
        if speed_factor >= 1.0: return traj
        time_multiplier = 1.0 / speed_factor
        for point in traj.points:
            t_sec = point.time_from_start.sec + (point.time_from_start.nanosec * 1e-9)
            t_sec *= time_multiplier
            point.time_from_start.sec = int(t_sec)
            point.time_from_start.nanosec = int((t_sec - int(t_sec)) * 1e9)
            if point.velocities:
                point.velocities = [v * speed_factor for v in point.velocities]
            if point.accelerations:
                point.accelerations = [a * (speed_factor**2) for a in point.accelerations]
        return traj

"""
# insert before execute_joint_trajectory_safe
content = content.replace("    def execute_joint_trajectory_safe(self, target_joints):", scale_func + "    def execute_joint_trajectory_safe(self, target_joints):")

# 4. Fix execute_joint_trajectory_safe
content = content.replace("        traj = result.motion_plan_response.trajectory.joint_trajectory\n        \n        # MoveIt's default planner",
                          "        traj = result.motion_plan_response.trajectory.joint_trajectory\n        traj = self.scale_trajectory_speed(traj, self.joint_speed)\n        \n        # MoveIt's default planner")

# 5. execute_pilz_lin -> execute_cartesian_path
pattern_pilz = re.compile(r'    def execute_pilz_lin\(self, target_pose\):.*?        return self\.execute_trajectory\(traj\)\n', re.DOTALL)
cartesian_func = """    def execute_cartesian_path(self, waypoints):
        if not self.cartesian_client.wait_for_service(timeout_sec=5.0):
            return False
            
        req = GetCartesianPath.Request()
        req.header.frame_id = 'ur5e_base_link'
        req.group_name = 'ur_arm'
        req.waypoints = waypoints
        req.max_step = 0.02  # Increased from 0.01 to 0.02 for smoother kinematics!
        req.avoid_collisions = True
        
        future = self.cartesian_client.call_async(req)
        result = wait_for_future(self, future)
        
        if not result or result.fraction < 0.99:
            self.get_logger().error(f"Failed Cartesian Path! (Fraction: {result.fraction if result else 'None'})")
            return False
            
        traj = result.solution.joint_trajectory
        
        # REMOVED the dangerous 50ms fallback loop!
        # If time_from_start is 0, it means the Time Parameterization (TOTG/Ruckig) crashed!
        if len(traj.points) > 1 and traj.points[-1].time_from_start.sec == 0 and traj.points[-1].time_from_start.nanosec == 0:
            self.get_logger().error("MoveIt Time Parameterization FAILED (time=0). Aborting to prevent velocity spikes!")
            return False
                
        traj = self.scale_trajectory_speed(traj, self.cart_speed)
        return self.execute_trajectory(traj)
"""
content = pattern_pilz.sub(cartesian_func, content)

# 6. execute_absolute_cartesian
content = content.replace("return self.execute_pilz_lin(target)", "return self.execute_cartesian_path([target])")

# 7. execute_reorient
pattern_reorient = re.compile(r'    def execute_reorient\(self, pitch_deg, roll_deg, yaw_deg\):.*?        return self\.execute_pilz_lin\(target\)\n', re.DOTALL)
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
        
        # Slicing the rotation into 10 waypoints to force Cartesian rigidity
        waypoints = []
        steps = 10
        
        # Shortest path math for yaw interpolation
        diff_roll = (target_roll - start_roll + math.pi) % (2 * math.pi) - math.pi
        diff_pitch = (target_pitch - start_pitch + math.pi) % (2 * math.pi) - math.pi
        diff_yaw = (target_yaw - start_yaw + math.pi) % (2 * math.pi) - math.pi
        
        for i in range(1, steps + 1):
            fraction = i / float(steps)
            r = start_roll + diff_roll * fraction
            p = start_pitch + diff_pitch * fraction
            y = start_yaw + diff_yaw * fraction
            
            new_q = quaternion_from_euler(r, p, y)
            
            target = Pose()
            target.position.x = curr.transform.translation.x
            target.position.y = curr.transform.translation.y
            target.position.z = curr.transform.translation.z
            target.orientation.x = new_q[0]
            target.orientation.y = new_q[1]
            target.orientation.z = new_q[2]
            target.orientation.w = new_q[3]
            waypoints.append(target)
        
        return self.execute_cartesian_path(waypoints)
"""
content = pattern_reorient.sub(reorient_func, content)

with open(path, 'w') as f:
    f.write(content)

print("full_cleaning reverted to OMPL successfully!")
