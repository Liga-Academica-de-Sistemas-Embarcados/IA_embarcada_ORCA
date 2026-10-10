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

- backend/modelo de segmentação;
- limiares de confiança e da máscara;
- quantidade máxima de objetos por comando;
- comportamento quando nenhum objeto correspondente for encontrado.

## Tempo de execução

- regras de normalização dos comandos;
- comando de parada (`stop`);
- nível de log;
- limites seguros de tempo limite e tentativas.

`config/example.yaml` é intencionalmente um placeholder para o primeiro
formato concreto de configuração.
