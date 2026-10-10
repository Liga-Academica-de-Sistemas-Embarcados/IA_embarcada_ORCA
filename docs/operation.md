# Operação e Máquina de Estados

## Ciclo normal

Para cada comando diferente de `stop`, o sistema repete a seguinte rotina:

1. Capturar o quadro atual da câmera montada em altura fixa.
2. Segmentar todos os objetos correspondentes ao comando.
3. Selecionar um pixel seguro de coleta para cada objeto detectado.
4. Converter cada pixel em um alvo cartesiano usando a calibração.
5. Mover-se até o objeto, pegá-lo e colocá-lo na posição configurada.
6. Retornar à posição de repouso.
7. Continuar com o próximo objeto correspondente, se houver.
8. Aguardar em repouso o próximo comando.

A ordem exata em que vários objetos serão processados é uma decisão de
implementação, mas deve ser determinística e documentada quando for definida.

## Comportamento de pausa

O comando `stop` é um comando de controle, não uma descrição de objeto:

- nenhum novo ciclo de coleta e colocação começa depois que ele é recebido;
- o trabalho ativo deve terminar em um limite seguro ou entrar no
  comportamento de emergência segura do projeto;
- o braço permanece pausado;
- a inferência permanece pausada;
- qualquer comando posterior diferente de `stop` retoma a operação normal.

A implementação inicial deve definir e testar se `stop` será aceito com
distinção entre maiúsculas e minúsculas e como os espaços em branco serão
normalizados.

## Estados planejados

```text
RESTING
  └─ prompt received ───────────────► CAPTURING

CAPTURING ─► SEGMENTING ─► PLANNING ─► EXECUTING
                                      │
                                      ├─ next object ─► EXECUTING
                                      └─ complete ────► RESTING

Any safe boundary ── stop ───────────► PAUSED
PAUSED ── any non-stop prompt ───────► CAPTURING
```


