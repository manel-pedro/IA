# Plano de Benchmark e Sensibilidade de Parametros

## Objetivo
Medir como a performance (score e tempo) muda quando variamos parametros dos algoritmos estocasticos.

## Metricas
- score_best: melhor score obtido nas repeticoes
- score_mean: media de score nas repeticoes
- score_std: estabilidade (quanto menor, mais estavel)
- time_mean_s: tempo medio de execucao
- time_std_s: variacao de tempo

## Desenho experimental
- Executar por dataset em `input/`
- Repetir cada configuracao varias vezes (minimo 5)
- Definir seed por repeticao para comparar configuracoes de forma justa
- Guardar resultados em CSV para analise posterior

## Parametros que fazem sentido variar

### 1) Genetic Algorithm
- `pop_size` (tamanho da populacao): controla exploracao por geracao
- `generations` (numero de geracoes): controla profundidade da evolucao
- `mutation_rate` (taxa de mutacao): controla diversidade e fuga de otimos locais

Sugestao inicial de grelha:
- pop_size: [30, 60, 100, 140]
- generations: [80, 150, 250]
- mutation_rate: [0.15, 0.30, 0.45]

### 2) Randomized Greedy
- `alpha`: controla aleatoriedade da escolha na RCL

Sugestao inicial:
- alpha: [0.1, 0.2, 0.3, 0.5, 0.7]

## Como correr
1. Gerar resultados de sensibilidade:
   - `python benchmark_sensitivity.py`
2. Gerar graficos:
   - `python plot_benchmark.py`
3. Ver PNGs em:
   - `benchmark_outputs/plots/`

## Leitura dos resultados
- Se `score_mean` sobe e `score_std` desce: melhoria real e estavel
- Se `score_mean` sobe mas `time_mean_s` explode: trade-off (qualidade vs tempo)
- Procurar "joelho da curva": ponto onde aumentar parametro quase nao melhora score

## Proximo passo recomendado
Depois da primeira ronda, fixar 1 parametro e refinar os outros em volta da melhor zona.
