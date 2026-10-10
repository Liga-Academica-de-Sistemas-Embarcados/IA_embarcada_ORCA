# Projeto ORCA

ORCA é um sistema de braço robótico zero-shot. O usuário fornece um comando em
linguagem natural, e o sistema encontra todos os objetos correspondentes no
quadro da câmera, pega cada objeto, coloca-o no destino configurado e retorna o
braço à sua posição de repouso.

A câmera é montada em uma altura fixa. A inferência e as operações de pegar e
colocar continuam até que o usuário digite `stop`. Nesse momento, todo o
sistema é pausado e permanece pausado até que outro comando seja informado.

## Status do projeto

Este repositório atualmente contém a estrutura do projeto e a documentação do
sistema. A implementação em tempo de execução será adicionada gradualmente.

## Estrutura do repositório

```text
.
├── docs/                 # Arquitetura, configuração, operação e decisões de projeto
├── src/
│   ├── arm_client/       # Câmera, segmentação, pixels-alvo e coordenadas
│   ├── arm_server/       # Trajetórias, controle das juntas e hardware GPIO/PWM
│   ├── input_handler/    # Comandos do usuário e comportamento de pausa/retomada
│   └── interfaces/       # Mensagens compartilhadas e contratos entre componentes
├── tests/                # Testes organizados por componente
├── config/               # Configurações de hardware, câmera, calibração e destino
├── launch/               # Futuros pontos de entrada de inicialização/configuração
├── LICENSE
└── README.md
```

## Fluxo geral

1. `InputHandler` recebe um comando e um quadro de imagem.
2. `SegmentImage` identifica os objetos descritos pelo comando.
3. `FindPickUpPixels` escolhe pixels de coleta para os objetos correspondentes.
4. `PixelToCoords` converte as posições da imagem em coordenadas cartesianas.
5. `TrajectoriesFactory` cria uma trajetória segura de coleta e colocação.
6. `JointTrajectoryController` envia comandos das juntas ao braço.
7. `GPIOCommunication` envia sinais PWM ao hardware.
8. O braço retorna à posição de repouso antes do próximo objeto ou comando.

Consulte [docs/architecture.md](docs/architecture.md) para conhecer os
contratos dos componentes e [docs/operation.md](docs/operation.md) para o
comportamento esperado em tempo de execução.

## Diagrama do projeto

![Diagrama da arquitetura do Projeto ORCA](docs/diagrams/ORCAdiagram.png)

O diagrama completo da arquitetura também está disponível em
[docs/diagrams/ORCAdiagram.png](docs/diagrams/ORCAdiagram.png).

## Pré-requisitos planejados

- ROS 2
- Um braço robótico compatível e uma interface GPIO/PWM
- Uma câmera montada em altura fixa
- Um backend compatível de segmentação/inferência zero-shot

As versões exatas e as instruções específicas do hardware serão documentadas
quando a implementação for definida.

## Documentação

- [Arquitetura](docs/architecture.md)
- [Operação e máquina de estados](docs/operation.md)
- [Configuração](docs/configuration.md)
- [Configuração do desenvolvimento](docs/development.md)
- [Contribuição](CONTRIBUTING.md)
- [Código de conduta](CODE_OF_CONDUCT.md)

## Licença

Este projeto é distribuído sob a [Licença MIT](LICENSE).
