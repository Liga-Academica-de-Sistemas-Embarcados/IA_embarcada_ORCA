# Testes

Organize os testes por componente:

```text
tests/
├── arm_client/
├── arm_server/
├── input_handler/
└── interfaces/
```

Os primeiros testes devem abranger o tratamento de comandos, o comportamento
de pausa/retomada de `stop`, a conversão de pixels para coordenadas, a geração
de trajetórias e o retorno seguro à posição de repouso.

## Teste interativo de percepção

[`arm_client/test_zero_shot_webcam.py`](arm_client/test_zero_shot_webcam.py)
é um smoke test para validar a inferência zero-shot com uma câmera local:

```bash
python3 tests/arm_client/test_zero_shot_webcam.py \
  --prompt bottle \
  --camera 0 \
  --threshold 0.5
```

O script usa os checkpoints padrão em
`src/arm_client/SegmentImage/weights/`, mantém o embedding do prompt em
cache e exibe as caixas detectadas. O parâmetro `--device cuda` pode ser
usado quando PyTorch e os pesos estiverem configurados para GPU.
