# Arquitetura do ORCA

## Limites

### Manipulador de entrada

`InputHandler` é o ponto de entrada dos comandos do usuário. Ele recebe
comandos de texto, coordena o processamento do comando com o quadro atual da
câmera e controla o estado pausado acionado pelo comando exato `stop`.

### Cliente do braço

O cliente realiza a percepção e traduz os resultados da imagem em alvos de
movimento:

- `SegmentImage` produz uma máscara para os objetos correspondentes ao comando.
- `FindPickUpPixels` converte uma máscara e pixels brutos em um ou mais valores
  `ObjPixelCoordinates::PixCoords`.
- `PixelToCoords` converte coordenadas de pixels em coordenadas cartesianas
  usando a calibração da câmera fixa.

O cliente não controla diretamente o hardware GPIO ou PWM.

### Servidor do braço

O servidor controla os movimentos específicos do robô:

- `TrajectoriesFactory` cria trajetórias de coleta, colocação e retorno.
- `JointTrajectoryController` executa trajetórias de juntas no ROS 2.
- `GPIOCommunication` traduz a saída do controlador em comandos PWM e se
  comunica com o braço.

O servidor é o único limite que deve conhecer a pinagem do hardware e os
detalhes dos atuadores.

### Interfaces compartilhadas

`src/interfaces/` conterá os contratos de dados pequenos e estáveis trocados
entre os componentes, como:

- comandos de entrada e comandos de pausa/retomada;
- quadros de imagem e máscaras de segmentação;
- coordenadas de pixels e cartesianas;
- objetivos de coleta e colocação e resultados de execução.

Esses contratos devem permanecer independentes de um modelo de inferência ou
fabricante de robô específico.

## Fluxo de dados

```text
UserInterface + ImageProvider
              │
              ▼
        InputHandler
              │ prompt + frame
              ▼
        SegmentImage
              │ mask
              ▼
      FindPickUpPixels
              │ pixel coordinates
              ▼
        PixelToCoords
              │ Cartesian coordinates
              ▼
      TrajectoriesFactory
              │ ROS 2 joint trajectory
              ▼
  JointTrajectoryController
              │ PWM commands
              ▼
     GPIOCommunication → robotic arm
```

## Princípios de projeto

1. Mantenha a percepção, o planejamento de movimento, a comunicação com o
   hardware e a entrada do usuário testáveis separadamente.
2. Mantenha a calibração e as posições de destino na configuração, não no
   código.
3. Torne a posição de repouso um estado de movimento explícito e recuperável.