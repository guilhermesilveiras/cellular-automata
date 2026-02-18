from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from random import Random
from typing import Dict, List, Optional


class CellState(IntEnum):
    UNAWARE = 0
    BELIEVER = 1
    CORRECTED = 2


@dataclass(frozen=True)
class SimulationConfig:
    width: int = 80
    height: int = 80
    steps: int = 160
    initial_believer_density: float = 0.03
    initial_corrected_density: float = 0.05
    belief_spread_rate: float = 0.60
    factcheck_rate: float = 0.04
    peer_correction_rate: float = 0.45
    relapse_rate: float = 0.07
    toroidal: bool = True
    seed: Optional[int] = None


def _clamp_probability(value: float) -> float:
    return max(0.0, min(1.0, value))


class MisinformationCA:
    """2D stochastic cellular automaton for misinformation dynamics."""

    def __init__(
        self, config: SimulationConfig, initial_grid: Optional[List[List[int]]] = None
    ) -> None:
        self.config = config
        self._validate_config()
        self._rng = Random(config.seed)
        self.time_step = 0
        if initial_grid is None:
            self.grid = self._build_initial_grid()
        else:
            self.grid = self._normalize_grid(initial_grid)

    def _validate_config(self) -> None:
        if self.config.width <= 0 or self.config.height <= 0:
            raise ValueError("width and height must be positive.")
        if self.config.steps < 0:
            raise ValueError("steps must be non-negative.")
        if self.config.initial_believer_density < 0 or self.config.initial_corrected_density < 0:
            raise ValueError("Initial densities must be non-negative.")
        if self.config.initial_believer_density + self.config.initial_corrected_density > 1:
            raise ValueError("Initial densities cannot sum to more than 1.")

    def _normalize_grid(self, initial_grid: List[List[int]]) -> List[List[int]]:
        if len(initial_grid) != self.config.height:
            raise ValueError("Provided grid height does not match config.height.")
        normalized: List[List[int]] = []
        for row in initial_grid:
            if len(row) != self.config.width:
                raise ValueError("Provided grid width does not match config.width.")
            normalized_row = [int(CellState(cell)) for cell in row]
            normalized.append(normalized_row)
        return normalized

    def _build_initial_grid(self) -> List[List[int]]:
        grid: List[List[int]] = []
        p_believer = self.config.initial_believer_density
        p_corrected = self.config.initial_corrected_density
        p_believer_or_corrected = p_believer + p_corrected

        for _ in range(self.config.height):
            row: List[int] = []
            for _ in range(self.config.width):
                draw = self._rng.random()
                if draw < p_believer:
                    row.append(int(CellState.BELIEVER))
                elif draw < p_believer_or_corrected:
                    row.append(int(CellState.CORRECTED))
                else:
                    row.append(int(CellState.UNAWARE))
            grid.append(row)
        return grid

    def _neighbor_positions(self, row: int, col: int) -> List[tuple[int, int]]:
        neighbors: List[tuple[int, int]] = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if self.config.toroidal:
                    nr %= self.config.height
                    nc %= self.config.width
                    neighbors.append((nr, nc))
                elif 0 <= nr < self.config.height and 0 <= nc < self.config.width:
                    neighbors.append((nr, nc))
        return neighbors

    def _count_neighbor_states(self, row: int, col: int) -> Dict[str, int]:
        believer_count = 0
        corrected_count = 0
        neighbors = self._neighbor_positions(row, col)

        for nr, nc in neighbors:
            state = self.grid[nr][nc]
            if state == int(CellState.BELIEVER):
                believer_count += 1
            elif state == int(CellState.CORRECTED):
                corrected_count += 1

        return {
            "believers": believer_count,
            "corrected": corrected_count,
            "total_neighbors": len(neighbors),
        }

    def _transition(self, row: int, col: int, current_state: int) -> int:
        counts = self._count_neighbor_states(row, col)
        total_neighbors = counts["total_neighbors"]
        believer_ratio = counts["believers"] / total_neighbors if total_neighbors else 0.0
        corrected_ratio = counts["corrected"] / total_neighbors if total_neighbors else 0.0

        if current_state == int(CellState.UNAWARE):
            spread_probability = _clamp_probability(
                self.config.belief_spread_rate * believer_ratio
            )
            if self._rng.random() < spread_probability:
                return int(CellState.BELIEVER)
            return int(CellState.UNAWARE)

        if current_state == int(CellState.BELIEVER):
            correction_probability = _clamp_probability(
                self.config.factcheck_rate
                + self.config.peer_correction_rate * corrected_ratio
            )
            if self._rng.random() < correction_probability:
                return int(CellState.CORRECTED)
            return int(CellState.BELIEVER)

        if current_state == int(CellState.CORRECTED):
            relapse_probability = _clamp_probability(
                self.config.relapse_rate * believer_ratio
            )
            if self._rng.random() < relapse_probability:
                return int(CellState.BELIEVER)
            return int(CellState.CORRECTED)

        raise ValueError(f"Unknown cell state: {current_state}")

    def snapshot(self) -> Dict[str, float]:
        unaware_count = 0
        believer_count = 0
        corrected_count = 0

        for row in self.grid:
            for cell in row:
                if cell == int(CellState.UNAWARE):
                    unaware_count += 1
                elif cell == int(CellState.BELIEVER):
                    believer_count += 1
                elif cell == int(CellState.CORRECTED):
                    corrected_count += 1
                else:
                    raise ValueError(f"Unknown cell state in grid: {cell}")

        total_cells = self.config.width * self.config.height
        return {
            "step": self.time_step,
            "unaware_count": unaware_count,
            "believer_count": believer_count,
            "corrected_count": corrected_count,
            "unaware_ratio": unaware_count / total_cells,
            "believer_ratio": believer_count / total_cells,
            "corrected_ratio": corrected_count / total_cells,
        }

    def advance(self) -> Dict[str, float]:
        next_grid: List[List[int]] = []
        new_believers = 0
        new_corrected = 0
        relapses = 0

        for row in range(self.config.height):
            next_row: List[int] = []
            for col in range(self.config.width):
                old_state = self.grid[row][col]
                new_state = self._transition(row, col, old_state)
                if old_state == int(CellState.UNAWARE) and new_state == int(CellState.BELIEVER):
                    new_believers += 1
                elif old_state == int(CellState.BELIEVER) and new_state == int(CellState.CORRECTED):
                    new_corrected += 1
                elif old_state == int(CellState.CORRECTED) and new_state == int(CellState.BELIEVER):
                    relapses += 1
                next_row.append(new_state)
            next_grid.append(next_row)

        self.grid = next_grid
        self.time_step += 1
        step_snapshot = self.snapshot()
        step_snapshot["new_believers"] = new_believers
        step_snapshot["new_corrected"] = new_corrected
        step_snapshot["relapses"] = relapses
        return step_snapshot

    def run(self) -> List[Dict[str, float]]:
        history = [self.snapshot()]
        history[0]["new_believers"] = 0
        history[0]["new_corrected"] = 0
        history[0]["relapses"] = 0
        for _ in range(self.config.steps):
            history.append(self.advance())
        return history


def summarize_history(history: List[Dict[str, float]]) -> Dict[str, float]:
    if not history:
        raise ValueError("history cannot be empty")

    believer_ratios = [float(step["believer_ratio"]) for step in history]
    peak_believer_ratio = max(believer_ratios)
    time_to_peak = int(
        next(
            step["step"]
            for step in history
            if float(step["believer_ratio"]) == peak_believer_ratio
        )
    )

    final_step = history[-1]
    total_exposure = sum(believer_ratios)

    return {
        "peak_believer_ratio": peak_believer_ratio,
        "time_to_peak": time_to_peak,
        "final_believer_ratio": float(final_step["believer_ratio"]),
        "final_corrected_ratio": float(final_step["corrected_ratio"]),
        "total_exposure": total_exposure,
    }
