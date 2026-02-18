# Cellular Automata: Applied Study

Projeto aplicado de autômato celular estocástico para simulação da propagação de desinformação e mitigação por checagem de fatos.

## Estrutura

- `src/misinformation_ca.py`: modelo principal do autômato celular.
- `run_experiments.py`: execução de cenários e exportação de resultados em CSV.
- `tests/test_misinformation_ca.py`: testes unitários.
- `paper/trabalho_automato_celular.md`: artigo científico em formato textual.
- `outputs/misinformation/`: resultados dos experimentos.

## Requisitos

- Python 3.10+

## Como executar

```powershell
python -m unittest discover -s tests -p "test_*.py"
python run_experiments.py
```

## Modelo resumido

Cada célula da grade representa um usuário:

- `UNAWARE`: ainda não foi exposto à narrativa falsa.
- `BELIEVER`: acredita e pode retransmitir a desinformação.
- `CORRECTED`: rejeita a desinformação e pode ajudar a corrigi-la.

As transições são estocásticas e dependem da vizinhança de Moore (8 vizinhos), com atualização síncrona.
