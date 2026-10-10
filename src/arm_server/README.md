# Servidor do braço

Responsabilidades planejadas:

- aceitar alvos cartesianos de coleta e colocação;
- criar trajetórias seguras para as juntas;
- controlar as juntas por meio do ROS 2;
- comunicar-se com o hardware GPIO/PWM;
- retornar o status da execução e erros de segurança.

Os módulos esperados a partir do diagrama são `TrajectoriesFactory`,
`JointTrajectoryController` e `GPIOCommunication`.
