import rclpy
from rclpy.node import Node
from moveit_msgs.srv import GetMotionPlan
from moveit_msgs.msg import Constraints, PositionConstraint, OrientationConstraint, BoundingVolume
from geometry_msgs.msg import Pose, Point
from shape_msgs.msg import SolidPrimitive
import sys

rclpy.init()
node = Node('pilz_tester')
client = node.create_client(GetMotionPlan, '/plan_kinematic_path')
if not client.wait_for_service(timeout_sec=2.0):
    print('Service not available')
    sys.exit(1)

req = GetMotionPlan.Request()
req.motion_plan_request.pipeline_id = 'pilz_industrial_motion_planner'
req.motion_plan_request.planner_id = 'LIN'
req.motion_plan_request.group_name = 'ur_arm'
req.motion_plan_request.max_velocity_scaling_factor = 0.1
req.motion_plan_request.max_acceleration_scaling_factor = 0.1

c = Constraints()
pc = PositionConstraint()
pc.link_name = 'ur5e_tool0'
pc.header.frame_id = 'ur5e_base_link'
bv = BoundingVolume()
sp = SolidPrimitive()
sp.type = SolidPrimitive.SPHERE
sp.dimensions = [0.001]
bv.primitives.append(sp)
bv.primitive_poses.append(Pose()) # Dummy target pose
pc.constraint_region = bv
pc.weight = 1.0

oc = OrientationConstraint()
oc.link_name = 'ur5e_tool0'
oc.header.frame_id = 'ur5e_base_link'
oc.orientation.w = 1.0
oc.absolute_x_axis_tolerance = 0.01
oc.absolute_y_axis_tolerance = 0.01
oc.absolute_z_axis_tolerance = 0.01
oc.weight = 1.0

c.position_constraints.append(pc)
c.orientation_constraints.append(oc)
req.motion_plan_request.goal_constraints.append(c)

future = client.call_async(req)
rclpy.spin_until_future_complete(node, future)
result = future.result()
print('Pilz Error Code:', result.motion_plan_response.error_code.val)
