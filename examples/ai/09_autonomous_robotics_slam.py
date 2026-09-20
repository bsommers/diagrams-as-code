"""Example architecture: Autonomous Mobile Robot (AMR) SLAM Engine (AI domain)."""
from __future__ import annotations

import sys
from pathlib import Path

from diagrams_as_code import Diagram, Edge, Group, Shape


def build_diagram(output_dir: Path | str = "output/ai") -> Path:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    svg_file = out / "09_autonomous_robotics_slam.svg"
    png_file = out / "09_autonomous_robotics_slam.png"
    readme_file = out / "09_autonomous_robotics_slam_README.md"

    with Diagram("Autonomous Mobile Robot (AMR) SLAM Engine", theme="nord") as diag:
        with diag.group("Sensor Array") as g_1:
            lidar = diag.add(Shape("lidar", "3D Flash LiDAR", icon="sensor", frequency="20Hz 128-Beam"))
            camera = diag.add(Shape("camera", "Stereo Depth Camera", icon="vision", fov="120 Degree FOV"))
            camera.below(lidar, margin=30)
            imu = diag.add(Shape("imu", "High-Precision IMU", icon="sensor", axes="6-DOF Accelerometer/Gyro"))
            imu.below(camera, margin=30)

        with diag.group("Perception Compute") as g_2:
            ekf = diag.add(Shape("ekf", "Sensor Fusion EKF", icon="chip", algorithm="Extended Kalman Filter"))

        with diag.group("Navigation Core") as g_3:
            slam = diag.add(Shape("slam", "Cartographer 3D SLAM", icon="brain", map="Occupancy Grid Map"))
            planner = diag.add(Shape("planner", "TEB Local Planner", icon="workflow", obstacle_avoidance="Dynamic"))
            planner.below(slam, margin=30)

        with diag.group("Actuation Tier") as g_4:
            motors = diag.add(Shape("motors", "CAN Motor Controller", icon="plc", bus="CANopen 1Mbps"))

        # Position starting group
        g_1.at(60.0, 80.0)

        # Arrange groups in horizontal sequence
        g_2.right_of(g_1, margin=50)
        g_3.right_of(g_2, margin=50)
        g_4.right_of(g_3, margin=50)

        # Establish inter-element connections with protocol annotations
        lidar >> diag.edge("Point Cloud Data", style="solid") >> ekf
        camera >> diag.edge("Depth Frames", style="solid") >> ekf
        imu >> diag.edge("Inertial Odometry", style="solid") >> ekf
        ekf >> diag.edge("Fused State Vector", style="solid") >> slam
        slam >> diag.edge("Robot Pose & Global Map", style="solid") >> planner
        planner >> diag.edge("Velocity Commands (Twist)", style="solid") >> motors

    # Render outputs after diagram context resolves layout constraints
    diag.render_svg(svg_file)
    diag.render_png(png_file)
    diag.generate_readme("09_autonomous_robotics_slam.svg", readme_file)

    return svg_file


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/ai")
    build_diagram(dest)
