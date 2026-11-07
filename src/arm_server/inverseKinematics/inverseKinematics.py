# código que recebe uma coordenada cartesiana e retorna um mapa de ângulos.
# braço possui 4 graus de liberdade. Isto deve ser levado em conta.
# classe deve receber as medidas do braço robótico.

# é esperado que as coordenadas recebidas estejam no eixo de referência do braço
# o eixo de referência do braço tem como origem a sua base.
# o eixo y aponta para frente do braço. O eixo x aponta para a direita do eixo y, e o eixo z aponta para cima.
# o angulo da base, portanto, é o ângulo entre o eixo original y com o eixo de conexão com o ponto

import numpy as np


class arm4DOF_kinematics:
    def __init__(self, arm_specs:list):
        self.l1 = arm_specs[0]
        self.l2 = arm_specs[1]
        self.l3 = arm_specs[2]
        
        pass

    def compute_FK(self, angle_coords):
        theta_base = angle_coords[0]
        theta_1    = angle_coords[1]
        theta_2    = angle_coords[2]
        theta_3    = angle_coords[3]

        u = self.l1 * np.cos(theta_1) + self.l2 * np.cos(theta_1 + theta_2) + self.l3 * np.cos(theta_1 + theta_2 + theta_3)
        v = self.l1 * np.sin(theta_1) + self.l2 * np.sin(theta_1 + theta_2) + self.l3 * np.sin(theta_1 + theta_2 + theta_3)

        z = v
        x = u * np.sin(theta_base)
        y = u * np.cos(theta_base)

        return x,y,z

    def compute_IK(
        self,
        cartesian_coords: list,
        initial_angles: list,
        joint_limits=None,
        tolerance=1e-6,
        max_iterations=1000,
    ):
        # braço vai possuir:
        # THETA_BASE: angulo de rotação da base
        # THETA_1: angulo de rotação da primeira junta
        # THETA_2: angulo de rotação da segunda junta
        # THETA_3: angulo de rotação do atuador

        target = np.asarray(cartesian_coords, dtype=float)
        angles = np.asarray(initial_angles, dtype=float).copy()

        x, y, z = target
        angles[0] = np.arctan2(x, y)
        planar_target = np.array([np.hypot(x, y), z])
        planar = angles[1:]

        if joint_limits is None:
            joint_limits = [(-np.pi, np.pi)] * 4
        
        lower = np.asarray([limit[0] for limit in joint_limits], dtype=float)
        upper = np.asarray([limit[1] for limit in joint_limits], dtype=float)
        if np.any(lower >= upper):
            raise ValueError("limite de junta excedido!")
        
        angles = np.clip(angles, lower, upper)
        planar = angles[1:]
        initial_planar = planar.copy()

        for _ in range(max_iterations):
            position = self._planar_position(planar)
            error = planar_target - position
            if np.linalg.norm(error) <= tolerance:
                angles[1:] = planar
                return angles

            jacobian = self._planar_jacobian(planar)
            damping = 1e-4
            inverse = jacobian.T @ np.linalg.inv(
                jacobian @ jacobian.T + damping**2 * np.eye(2)
            )
            posture_error = self._wrapped_difference(initial_planar, planar)
            null_space = np.eye(3) - inverse @ jacobian
            step = inverse @ error + 0.05 * null_space @ posture_error
            planar = np.clip(planar + step, lower[1:], upper[1:])

        raise ValueError("IK não convergiu ):")

    def _planar_position(self, angles):
        theta_1, theta_2, theta_3 = angles
        theta_12 = theta_1 + theta_2
        theta_123 = theta_12 + theta_3
        return np.array([
            self.l1 * np.cos(theta_1)
            + self.l2 * np.cos(theta_12)
            + self.l3 * np.cos(theta_123),
            self.l1 * np.sin(theta_1)
            + self.l2 * np.sin(theta_12)
            + self.l3 * np.sin(theta_123),
        ])

    def _planar_jacobian(self, angles):
        theta_1, theta_2, theta_3 = angles
        theta_12 = theta_1 + theta_2
        theta_123 = theta_12 + theta_3
        return np.array([
            [
                -self.l1 * np.sin(theta_1)
                - self.l2 * np.sin(theta_12)
                - self.l3 * np.sin(theta_123),
                -self.l2 * np.sin(theta_12) - self.l3 * np.sin(theta_123),
                -self.l3 * np.sin(theta_123),
            ],
            [
                self.l1 * np.cos(theta_1)
                + self.l2 * np.cos(theta_12)
                + self.l3 * np.cos(theta_123),
                self.l2 * np.cos(theta_12) + self.l3 * np.cos(theta_123),
                self.l3 * np.cos(theta_123),
            ],
        ])

    @staticmethod
    def _wrapped_difference(target, current):
        difference = target - current
        return np.arctan2(np.sin(difference), np.cos(difference))