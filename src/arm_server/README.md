# Servidor do braço

Responsabilidades planejadas:

- aceitar alvos cartesianos de coleta e colocação;
- criar trajetórias seguras para as juntas;
- controlar as juntas por meio do ROS 2;
- comunicar-se com o hardware GPIO/PWM;
- retornar o status da execução e erros de segurança.

Os módulos esperados a partir do diagrama são `TrajectoriesFactory`,
`JointTrajectoryController` e `GPIOCommunication`.

## Cinemática inversa

O módulo
[`inverseKinematics.py`](inverseKinematics/inverseKinematics.py)
implementa a cinemática de posição de um braço com quatro juntas:

- `theta_base`: rotação da base;
- `theta_1`, `theta_2` e `theta_3`: juntas planares.

`compute_FK()` calcula a posição cartesiana `(x, y, z)` a partir dos quatro
ângulos. `compute_IK()` recebe uma posição cartesiana e procura uma solução
analítica para as juntas planares. O algoritmo amostra a orientação do último
elo, resolve as duas primeiras juntas pelo problema geométrico de dois elos,
considera as duas orientações da base e descarta soluções que violem limites
de juntas ou coloquem o cotovelo, o punho ou a ponta abaixo do chão.

Quando `initial_angles` é fornecido, a solução válida mais próxima da
configuração inicial é escolhida. Isso permite manter movimentos próximos do
estado atual do braço:

```python
angles = arm.compute_IK(
    cartesian_coords=[x, y, z],
    initial_angles=current_angles,
    joint_limits=[(-3.14, 3.14)] * 4,
)
```

O parâmetro `min_height` pode ser usado para definir uma altura mínima acima
do plano do chão. `phi_samples` controla a resolução da busca bruta pela
orientação do último elo; valores maiores aumentam a chance de encontrar uma
solução, mas também aumentam o custo computacional.

## Visualizador 3D

O visualizador usa temporariamente `l1 = l2 = l3 = 1 m` e mostra os elos, a
posição desejada e a posição alcançada:

```bash
python tools/visualize_kinematics.py --x 1 --y 1 --z 0.1
```

As coordenadas são informadas em metros. Os ângulos iniciais são opcionais e
devem ser informados em graus:

```bash
python tools/visualize_kinematics.py \
  --x 1 --y 1 --z 0.1 \
  --initial-angles 180 90 90 0
```

Para visualizar somente a configuração inicial, sem executar a cinemática
inversa:

```bash
python tools/visualize_kinematics.py \
  --initial-only \
  --initial-angles 0 30 -45 15
```
