# acvmg: teste feito por IA

import sys
from pathlib import Path

import numpy as np
import pytest

IK_DIR = Path(__file__).resolve().parents[2] / "src" / "arm_server" / "inverseKinematics"
sys.path.insert(0, str(IK_DIR))

from inverseKinematics import arm4DOF_kinematics


@pytest.fixture
def arm():
    return arm4DOF_kinematics([1.0, 0.8, 0.5])


@pytest.mark.parametrize(
    "angles, expected",
    [
        (
            [0.0, 0.0, 0.0, 0.0],
            [0.0, 2.3, 0.0],
        ),
        (
            [np.pi / 2, 0.0, 0.0, 0.0],
            [2.3, 0.0, 0.0],
        ),
    ],
)
def test_forward_kinematics_for_straight_configurations(arm, angles, expected):
    np.testing.assert_allclose(arm.compute_FK(angles), expected, atol=1e-12)


def test_forward_kinematics_supports_arbitrary_angles(arm):
    angles = np.array([0.4, 0.3, -0.2, 0.5])

    position = np.asarray(arm.compute_FK(angles))
    radial = (
        arm.l1 * np.cos(angles[1])
        + arm.l2 * np.cos(angles[1] + angles[2])
        + arm.l3 * np.cos(angles[1] + angles[2] + angles[3])
    )
    expected = np.array([
        radial * np.sin(angles[0]),
        radial * np.cos(angles[0]),
        arm.l1 * np.sin(angles[1])
        + arm.l2 * np.sin(angles[1] + angles[2])
        + arm.l3 * np.sin(angles[1] + angles[2] + angles[3]),
    ])

    np.testing.assert_allclose(position, expected, atol=1e-12)


@pytest.mark.parametrize("theta_base", [-np.pi / 2, 0.0, np.pi / 4, np.pi / 2])
def test_base_angle_is_recovered_using_documented_axes(arm, theta_base):
    position = np.asarray(arm.compute_FK([theta_base, 0.3, -0.2, 0.5]))

    recovered_base = np.arctan2(position[0], position[1])

    np.testing.assert_allclose(recovered_base, theta_base, atol=1e-12)


def test_inverse_kinematics_returns_four_angles(arm):
    target_angles = np.array([0.4, 0.3, -0.2, 0.5])
    target_position = arm.compute_FK(target_angles)

    solved_angles = arm.compute_IK(target_position, initial_angles=target_angles)

    assert solved_angles is not None
    assert np.asarray(solved_angles).shape == (4,)


def test_inverse_kinematics_reconstructs_target_position(arm):
    target_angles = np.array([0.4, 0.3, -0.2, 0.5])
    target_position = np.asarray(arm.compute_FK(target_angles))

    solved_angles = arm.compute_IK(target_position, initial_angles=target_angles)
    assert solved_angles is not None
    reconstructed_position = np.asarray(arm.compute_FK(solved_angles))

    np.testing.assert_allclose(reconstructed_position, target_position, atol=1e-6)


def test_inverse_kinematics_accepts_cartesian_coordinates(arm):
    target = [0.4, 1.8, 0.6]

    result = arm.compute_IK(target, initial_angles=[0.0, 0.0, 0.0, 0.0])

    assert result is not None
