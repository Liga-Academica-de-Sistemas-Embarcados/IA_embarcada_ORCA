# Cliente do braço

O cliente do braço contém a percepção visual e a conversão dos resultados de
imagem em alvos para o servidor do robô.

Responsabilidades:

- obter quadros da câmera;
- segmentar objetos correspondentes ao comando;
- selecionar pixels de coleta;
- converter pixels em coordenadas cartesianas;
- solicitar objetivos de movimento ao servidor do braço.

Os componentes de percepção estão em `SegmentImage/`. O detector zero-shot
implementado está documentado em
[`SegmentImage/ZeroShotDet/README.md`](SegmentImage/ZeroShotDet/README.md).

Os módulos esperados a partir do diagrama são `FindPickUpPixels`,
`PickUpPixelsFactory` e `PixelToCoords`. Esses componentes ainda devem
consumir o contrato de saída do detector sem depender de uma implementação
específica de backbone.
