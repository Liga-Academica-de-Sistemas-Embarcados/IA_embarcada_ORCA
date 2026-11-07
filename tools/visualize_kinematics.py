"""Interactively solve and visualize the 4-DOF arm in 3D."""
# (acvmg): teste feito por IA

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

IK_DIR = Path(__file__).resolve().parents[1] / "src" / "arm_server" / "inverseKinematics"
sys.path.insert(0, str(IK_DIR))

from inverseKinematics import arm4DOF_kinematics


def joint_positions(arm, angles):
    """Return the base and each joint position for a set of angles."""
    theta_base, theta_1, theta_2, theta_3 = angles
    relative_angles = np.cumsum([theta_1, theta_2, theta_3])
    radial_lengths = np.array([arm.l1, arm.l2, arm.l3]) * np.cos(relative_angles)
    heights = np.array([arm.l1, arm.l2, arm.l3]) * np.sin(relative_angles)
    radial = np.cumsum(radial_lengths)
    z = np.cumsum(heights)

    return np.vstack([
        np.zeros(3),
        np.column_stack([
            radial * np.sin(theta_base),
            radial * np.cos(theta_base),
            z,
        ]),
    ])


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Solve IK and visualize a 1 m, 1 m, 1 m arm."
    )
    parser.add_argument("--x", type=float, help="Target x coordinate in meters")
    parser.add_argument("--y", type=float, help="Target y coordinate in meters")
    parser.add_argument("--z", type=float, help="Target z coordinate in meters")
    parser.add_argument(
        "--initial-angles",
        nargs=4,
        type=float,
        metavar=("BASE", "JOINT1", "JOINT2", "JOINT3"),
        help="Initial joint angles in degrees (default: 0 57 -57 0)",
    )
    parser.add_argument(
        "--initial-only",
        action="store_true",
        help="Display the initial robot configuration without solving IK",
    )
    return parser.parse_args()


def read_target(args):
    if args.x is not None and args.y is not None and args.z is not None:
        return np.array([args.x, args.y, args.z], dtype=float)
    if any(value is not None for value in (args.x, args.y, args.z)):
        raise ValueError("provide all of --x, --y and --z, or none of them")

    return np.array([
        float(input("Target x (m): ")),
        float(input("Target y (m): ")),
        float(input("Target z (m): ")),
    ])


def plot_arm(arm, angles, target=None, title="Robot configuration"):
    points = joint_positions(arm, angles)
    reached = np.asarray(arm.compute_FK(angles))

    figure = plt.figure()
    axis = figure.add_subplot(projection="3d")
    axis.plot(
        points[:, 0], points[:, 1], points[:, 2],
        "o-", linewidth=3, label="arm",
    )
    if target is not None:
        axis.scatter(*target, color="tab:red", s=70, label="target")
        axis.scatter(*reached, color="tab:green", s=50, label="reached")

    extent = arm.l1 + arm.l2 + arm.l3
    axis.set_xlim(-extent, extent)
    axis.set_ylim(-extent, extent)
    axis.set_zlim(-extent, extent)
    axis.set_box_aspect((1, 1, 1))
    axis.set_xlabel("x (m)")
    axis.set_ylabel("y (m)")
    axis.set_zlabel("z (m)")
    axis.set_title(title)
    axis.legend()
    plt.show()


def main():
    args = parse_arguments()
    initial_angles = (
        np.radians([0.0, 57.0, -57.0, 0.0])
        if args.initial_angles is None
        else np.radians(args.initial_angles)
    )
    arm = arm4DOF_kinematics([1.0, 1.0, 1.0])

    if args.initial_only:
        print("Initial joint angles (degrees):", np.degrees(initial_angles))
        print("Initial position (m):          ", arm.compute_FK(initial_angles))
        plot_arm(arm, initial_angles, title="Initial robot configuration")
        return

    target = read_target(args)
    try:
        angles = arm.compute_IK(target, initial_angles=initial_angles)
    except ValueError as error:
        raise SystemExit(f"Could not solve IK: {error}") from error

    reached = np.asarray(arm.compute_FK(angles))
    print("Joint angles (degrees):", np.degrees(angles))
    print("Target position (m):   ", target)
    print("Reached position (m):  ", reached)
    print("Position error (m):    ", np.linalg.norm(reached - target))
    plot_arm(arm, angles, target)


if __name__ == "__main__":
    main()
