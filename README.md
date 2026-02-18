# Cellular Automata: Applied Misinformation Study

Projeto aplicado de autômato celular estocástico para simular a propagação de desinformação e avaliar estratégias de mitigação por checagem de fatos e correção por pares.

## Tema do trabalho

**Modelagem e Mitigação da Propagação de Desinformação em Comunidades Digitais por Autômatos Celulares Estocásticos**

## Objetivo

Responder, com simulação reproduzível, à pergunta:

**Quais intervenções locais reduzem o pico de desinformação e o dano acumulado na comunidade?**

## Estrutura do repositório

- `src/misinformation_ca.py`: implementação do modelo do autômato celular.
- `run_experiments.py`: executa cenários e exporta resultados em CSV.
- `tests/test_misinformation_ca.py`: testes unitários das regras de transição.
- `outputs/misinformation/`: resultados das simulações.
- `paper/CELLULAR_AUTOMATA_artigo.pdf`: versão final em PDF do artigo.

## Requisitos

- Python 3.10+

## Como executar

```powershell
python -m unittest discover -s tests -p "test_*.py"
python run_experiments.py
```

## Modelo

Cada célula representa um usuário em uma grade 2D (80x80), com vizinhança de Moore (8 vizinhos) e atualização síncrona.

Estados:

- `UNAWARE (U)`: ainda não aderiu à desinformação.
- `BELIEVER (B)`: acredita e propaga desinformação.
- `CORRECTED (C)`: foi corrigido e ajuda na correção de outros.

## Regras de transição e fundamentação matemática

Sejam:

- `n_B`: número de vizinhos no estado `BELIEVER`.
- `n_C`: número de vizinhos no estado `CORRECTED`.
- `beta`: taxa de propagação da desinformação.
- `gamma`: taxa basal de checagem de fatos.
- `delta`: força de correção por pares.
- `rho`: taxa de recaída para desinformação.

$$
P(U \rightarrow B) = \beta \cdot \frac{n_B}{8}
$$

$$
P(B \rightarrow C) = \gamma + \delta \cdot \frac{n_C}{8}
$$

$$
P(C \rightarrow B) = \rho \cdot \frac{n_B}{8}
$$

No código, as probabilidades são limitadas ao intervalo `[0, 1]`.

## Configuração experimental

- 4 cenários.
- 20 repetições por cenário.
- 160 passos por simulação.
- Parâmetros-base: `beta=0.60`, `delta=0.45`, `rho=0.07`, crentes iniciais `3%`, corrigidos iniciais `5%`.

Cenários:

1. `baixa_verificacao`: `gamma=0.01`
2. `verificacao_moderada`: `gamma=0.04`
3. `verificacao_intensa`: `gamma=0.08`
4. `campanha_alfabetizacao`: `gamma=0.04`, corrigidos iniciais `20%`, `delta=0.55`

## Resultados principais

Fonte: `outputs/misinformation/misinformation_summary.csv`

| Cenário | Pico de crentes | Tempo até o pico | Crentes finais | Exposição acumulada |
|---|---:|---:|---:|---:|
| baixa_verificacao | 0.4722 | 15.00 | 0.0000 | 8.7702 |
| verificacao_moderada | 0.3204 | 12.70 | 0.0000 | 5.7693 |
| verificacao_intensa | 0.2057 | 11.35 | 0.0000 | 3.9601 |
| campanha_alfabetizacao | 0.1114 | 9.10 | 0.0000 | 2.1508 |

Comparação com `baixa_verificacao`:

- `verificacao_moderada`: redução de `32.2%` no pico e `34.2%` na exposição.
- `verificacao_intensa`: redução de `56.4%` no pico e `54.8%` na exposição.
- `campanha_alfabetizacao`: redução de `76.4%` no pico e `75.5%` na exposição.

## Conclusão

O modelo mostra que aumentar a checagem de fatos reduz fortemente a propagação da desinformação.  
A melhor estratégia testada foi combinar verificação com alfabetização digital inicial, que minimizou pico e exposição acumulada.  
Mesmo quando todos os cenários convergem para crentes finais próximos de zero, a diferença real entre políticas está no dano acumulado ao longo do tempo.

## Links

- Repositório: `https://github.com/guilhermesilveiras/cellular-automata`
- Artigo em Markdown (local): `paper/trabalho_automato_celular.md`
- Artigo em PDF (versionado): `paper/CELLULAR_AUTOMATA_artigo.pdf`
