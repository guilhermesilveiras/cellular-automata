from __future__ import annotations

import csv
import statistics
from dataclasses import replace
from pathlib import Path
from typing import Dict, List

from src.misinformation_ca import MisinformationCA, SimulationConfig, summarize_history

OUTPUT_DIR = Path("outputs") / "misinformation"
RUNS_FILE = OUTPUT_DIR / "misinformation_runs.csv"
AGGREGATE_FILE = OUTPUT_DIR / "misinformation_summary.csv"
TIMESERIES_FILE = OUTPUT_DIR / "misinformation_timeseries.csv"

REPETITIONS = 20
BASE_SEED = 2026

SCENARIOS = {
    "baixa_verificacao": {
        "factcheck_rate": 0.01,
    },
    "verificacao_moderada": {
        "factcheck_rate": 0.04,
    },
    "verificacao_intensa": {
        "factcheck_rate": 0.08,
    },
    "campanha_alfabetizacao": {
        "factcheck_rate": 0.04,
        "initial_corrected_density": 0.20,
        "peer_correction_rate": 0.55,
    },
}

SUMMARY_METRICS = [
    "peak_believer_ratio",
    "time_to_peak",
    "final_believer_ratio",
    "final_corrected_ratio",
    "total_exposure",
]


def base_config() -> SimulationConfig:
    return SimulationConfig(
        width=80,
        height=80,
        steps=160,
        initial_believer_density=0.03,
        initial_corrected_density=0.05,
        belief_spread_rate=0.60,
        factcheck_rate=0.04,
        peer_correction_rate=0.45,
        relapse_rate=0.07,
        toroidal=True,
        seed=None,
    )


def _stddev(values: List[float]) -> float:
    return statistics.stdev(values) if len(values) > 1 else 0.0


def run_all_experiments() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    all_runs: List[Dict[str, float]] = []
    aggregate_rows: List[Dict[str, float]] = []
    timeseries_rows: List[Dict[str, float]] = []

    scenario_names = list(SCENARIOS.keys())
    for scenario_index, scenario_name in enumerate(scenario_names):
        overrides = SCENARIOS[scenario_name]
        scenario_runs: List[Dict[str, float]] = []
        scenario_history_buffer: List[List[Dict[str, float]]] = []

        for rep in range(REPETITIONS):
            seed = BASE_SEED + scenario_index * 1000 + rep
            config = replace(base_config(), seed=seed, **overrides)
            sim = MisinformationCA(config)
            history = sim.run()
            summary = summarize_history(history)
            run_row: Dict[str, float] = {
                "scenario": scenario_name,
                "rep": rep,
                "seed": seed,
                **summary,
            }
            scenario_runs.append(run_row)
            scenario_history_buffer.append(history)
            all_runs.append(run_row)

        # Mean trajectory by step for selected ratios.
        steps = len(scenario_history_buffer[0])
        for step in range(steps):
            believer_vals = [
                run_history[step]["believer_ratio"] for run_history in scenario_history_buffer
            ]
            corrected_vals = [
                run_history[step]["corrected_ratio"] for run_history in scenario_history_buffer
            ]
            timeseries_rows.append(
                {
                    "scenario": scenario_name,
                    "step": step,
                    "mean_believer_ratio": statistics.mean(believer_vals),
                    "mean_corrected_ratio": statistics.mean(corrected_vals),
                }
            )

        aggregate_row: Dict[str, float] = {"scenario": scenario_name}
        for metric in SUMMARY_METRICS:
            values = [float(row[metric]) for row in scenario_runs]
            aggregate_row[f"{metric}_mean"] = statistics.mean(values)
            aggregate_row[f"{metric}_std"] = _stddev(values)
        aggregate_rows.append(aggregate_row)

    _write_runs_csv(all_runs)
    _write_aggregate_csv(aggregate_rows)
    _write_timeseries_csv(timeseries_rows)

    print("Experimentos concluídos.")
    for row in aggregate_rows:
        scenario = str(row["scenario"])
        final_ratio = float(row["final_believer_ratio_mean"])
        peak_ratio = float(row["peak_believer_ratio_mean"])
        print(
            f"- {scenario}: pico médio de crentes={peak_ratio:.3f}, "
            f"fração final de crentes={final_ratio:.3f}"
        )
    print(f"Arquivos salvos em: {OUTPUT_DIR}")


def _write_runs_csv(rows: List[Dict[str, float]]) -> None:
    fieldnames = ["scenario", "rep", "seed"] + SUMMARY_METRICS
    with RUNS_FILE.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_aggregate_csv(rows: List[Dict[str, float]]) -> None:
    fieldnames = ["scenario"]
    for metric in SUMMARY_METRICS:
        fieldnames.append(f"{metric}_mean")
        fieldnames.append(f"{metric}_std")
    with AGGREGATE_FILE.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_timeseries_csv(rows: List[Dict[str, float]]) -> None:
    fieldnames = ["scenario", "step", "mean_believer_ratio", "mean_corrected_ratio"]
    with TIMESERIES_FILE.open("w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    run_all_experiments()
