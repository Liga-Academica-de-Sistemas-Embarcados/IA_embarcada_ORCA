# código que recebe uma coordenada cartesiana e retorna um mapa de ângulos.
# braço possui 4 graus de liberdade. Isto deve ser levado em conta.
# classe deve receber as medidas do braço robótico.

# é esperado que as coordenadas recebidas estejam no eixo de referência do braço
# o eixo de referência do braço tem como origem a sua base.
# o eixo y aponta para frente do braço. O eixo x aponta para a direita do eixo y, e o eixo z aponta para cima.

import numpy as np

class arm4DOF_kinematics():
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
        v = self.l1 * np.sin(theta_1) + self.l1 * np.sin(theta_1 + theta_2) + self.l3 * np.sin(theta_1 + theta_2 + theta_3)

        z = v
        x = u * np.sin(theta_base)
        y = u * np.cos(theta_base)

        return x,y,z

    def compute_IK(self, cartesian_coords:list):
        # braço vai possuir:
        # THETA_BASE: angulo de rotação da base
        # THETA_1: angulo de rotação da primeira junta
        # THETA_2: angulo de rotação da segunda junta
        # THETA_3: angulo de rotação do atuador

        x,y,z = cartesian_coords

        theta_base = np.arctan2(y,x) # trivialmente, o robô deve antes de mais nada se alinhar com o ponto. Isso transforma o problema em um problema de 3DOF

        d = np.sqrt((x**2)+(y**2))  # novo eixo x. Novo eixo y vai ser o z



        return