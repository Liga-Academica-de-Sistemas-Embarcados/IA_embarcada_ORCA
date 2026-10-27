# Configuração

Os arquivos de configuração serão adicionados em `config/`. Mantenha os
valores específicos de cada máquina fora do código-fonte e não faça commit de
credenciais.

A configuração inicial deve abranger:

## Câmera

- identificador do dispositivo;
- resolução da imagem e taxa de quadros;
- altura de montagem fixa e orientação da câmera;
- calibração entre a câmera e o espaço de trabalho.

## Espaço de trabalho e colocação

- limites do espaço de trabalho;
- posição de destino/colocação;
- distância livre dos objetos e altura de aproximação;
- posição de repouso.

## Hardware do braço

- limites das juntas;
- pinos GPIO e intervalos PWM;
- temporização do controlador;
- modelo de braço compatível.

## Inferência

- backend/modelo de segmentação. A implementação atual usa MobileCLIP como
  backbone congelado e um decoder SAGS treinável;
- caminhos dos checkpoints do backbone e do decoder;
- dispositivo de execução (`cpu` ou `cuda`);
- tamanho da imagem de entrada e limiar da máscara;
- quantidade máxima de objetos por comando;
- comportamento quando nenhum objeto correspondente for encontrado.

Para o teste interativo atual, esses parâmetros podem ser informados pela
linha de comando. Os caminhos padrão são relativos ao repositório e apontam
para:

- `src/arm_client/SegmentImage/weights/mobileclip_s0.pt`;
- `src/arm_client/SegmentImage/weights/sags_mobileclip_s0_v2.pt`.

## Tempo de execução

- regras de normalização dos comandos;
- comando de parada (`stop`);
- nível de log;
- limites seguros de tempo limite e tentativas.

`config/example.yaml` é intencionalmente um placeholder para o primeiro
formato concreto de configuração.
