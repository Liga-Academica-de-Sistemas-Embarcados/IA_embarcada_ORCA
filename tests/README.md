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
