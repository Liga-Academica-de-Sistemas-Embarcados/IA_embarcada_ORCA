# Cliente do braço

Responsabilidades planejadas:

- obter quadros da câmera;
- segmentar objetos correspondentes ao comando;
- selecionar pixels de coleta;
- converter pixels em coordenadas cartesianas;
- solicitar objetivos de movimento ao servidor do braço.

Os módulos esperados a partir do diagrama são `SegmentImage`,
`FindPickUpPixels`, `PickUpPixelsFactory` e `PixelToCoords`.
