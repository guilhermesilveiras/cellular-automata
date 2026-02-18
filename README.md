# Cellular Automata: Applied Misinformation Study

Projeto aplicado de automato celular estocastico para simular a propagacao de desinformacao e avaliar estrategias de mitigacao por checagem de fatos e correcao por pares.

## Tema do trabalho

**Modelagem e Mitigacao da Propagacao de Desinformacao em Comunidades Digitais por Automatos Celulares Estocasticos**

## Objetivo

Responder, com simulacao reproduzivel, a pergunta:

**Quais intervencoes locais reduzem o pico de desinformacao e o dano acumulado na comunidade?**

## Estrutura do repositorio

- `src/misinformation_ca.py`: implementacao do modelo do automato celular.
- `run_experiments.py`: executa cenarios e exporta resultados em CSV.
- `tests/test_misinformation_ca.py`: testes unitarios das regras de transicao.
- `outputs/misinformation/`: resultados das simulacoes.
- `paper/CELLULAR_AUTOMATA_artigo.pdf`: versao final em PDF do artigo.

## Requisitos

- Python 3.10+

## Como executar

```powershell
python -m unittest discover -s tests -p "test_*.py"
python run_experiments.py
```

## Modelo (resumo)

Cada celula representa um usuario em uma grade 2D (80x80), com vizinhanca de Moore (8 vizinhos) e atualizacao sincrona.

Estados:

- `UNAWARE (U)`: ainda nao aderiu a desinformacao.
- `BELIEVER (B)`: acredita e propaga desinformacao.
- `CORRECTED (C)`: foi corrigido e ajuda na correcao de outros.

## Regras de transicao (fundamentacao matematica resumida)

Sejam:

- `n_B`: numero de vizinhos no estado `BELIEVER`.
- `n_C`: numero de vizinhos no estado `CORRECTED`.
- `beta`: taxa de propagacao da desinformacao.
- `gamma`: taxa basal de checagem de fatos.
- `delta`: forca de correcao por pares.
- `rho`: taxa de recaida para desinformacao.

Equacoes:

```text
P(U -> B) = beta * (n_B / 8)
P(B -> C) = gamma + delta * (n_C / 8)
P(C -> B) = rho * (n_B / 8)
```

No codigo, as probabilidades sao limitadas ao intervalo `[0, 1]`.

## Configuracao experimental

- 4 cenarios.
- 20 repeticoes por cenario.
- 160 passos por simulacao.
- Parametros-base: `beta=0.60`, `delta=0.45`, `rho=0.07`, crentes iniciais `3%`, corrigidos iniciais `5%`.

Cenarios:

1. `baixa_verificacao`: `gamma=0.01`
2. `verificacao_moderada`: `gamma=0.04`
3. `verificacao_intensa`: `gamma=0.08`
4. `campanha_alfabetizacao`: `gamma=0.04`, corrigidos iniciais `20%`, `delta=0.55`

## Resultados principais (media de 20 repeticoes)

Fonte: `outputs/misinformation/misinformation_summary.csv`

| Cenario | Pico de crentes | Tempo ate pico | Crentes finais | Exposicao acumulada |
|---|---:|---:|---:|---:|
| baixa_verificacao | 0.4722 | 15.00 | 0.0000 | 8.7702 |
| verificacao_moderada | 0.3204 | 12.70 | 0.0000 | 5.7693 |
| verificacao_intensa | 0.2057 | 11.35 | 0.0000 | 3.9601 |
| campanha_alfabetizacao | 0.1114 | 9.10 | 0.0000 | 2.1508 |

Comparacao com `baixa_verificacao`:

- `verificacao_moderada`: reducao de `32.2%` no pico e `34.2%` na exposicao.
- `verificacao_intensa`: reducao de `56.4%` no pico e `54.8%` na exposicao.
- `campanha_alfabetizacao`: reducao de `76.4%` no pico e `75.5%` na exposicao.

## Conclusao (resumo)

O modelo mostra que aumentar checagem de fatos reduz fortemente a propagacao da desinformacao.  
A melhor estrategia testada foi combinar verificacao com alfabetizacao digital inicial, que minimizou pico e exposicao acumulada.  
Mesmo quando todos os cenarios convergem para crentes finais proximos de zero, a diferenca real entre politicas esta no dano acumulado ao longo do tempo.

## Links

- Repositorio: `https://github.com/guilhermesilveiras/cellular-automata`
- Artigo em markdown (local): `paper/trabalho_automato_celular.md`
- Artigo em PDF (versionado): `paper/CELLULAR_AUTOMATA_artigo.pdf`
