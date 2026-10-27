# Configuração do Desenvolvimento

O repositório contém uma implementação inicial do cliente de percepção
zero-shot. As dependências de execução incluem Python, PyTorch, OpenCV,
NumPy, `timm` e as dependências usadas pelo MobileCLIP. O detector e seus
checkpoints estão descritos em
[`src/arm_client/SegmentImage/ZeroShotDet/README.md`](../src/arm_client/SegmentImage/ZeroShotDet/README.md).

## Fluxo planejado

1. Instalar a distribuição selecionada do ROS 2 e as dependências de
   inferência.
2. Copiar a configuração de exemplo para um arquivo de configuração local
   fora do controle de versão.
3. Executar testes em nível de componente sem hardware.
4. Executar verificações da câmera e da segmentação com quadros gravados.
5. Executar testes de movimento com o braço desabilitado ou em uma simulação.
6. Executar testes de hardware em baixa velocidade e com o espaço de trabalho
   livre.

## Teste de webcam

O smoke test interativo usa a câmera local e desenha as caixas detectadas em
uma janela OpenCV:

```bash
python3 tests/arm_client/test_zero_shot_webcam.py \
  --prompt bottle \
  --camera 0 \
  --threshold 0.5
```

Pressione `q` ou `Esc` para sair. O teste não substitui testes automatizados:
ele exige uma câmera, pesos locais, um ambiente gráfico e uma instalação
compatível das dependências de inferência.

   