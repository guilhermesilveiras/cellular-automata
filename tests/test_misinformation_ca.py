import unittest

from src.misinformation_ca import CellState, MisinformationCA, SimulationConfig


class TransitionRuleTests(unittest.TestCase):
    def test_unaware_becomes_believer_when_exposure_is_maximal(self) -> None:
        config = SimulationConfig(
            width=3,
            height=3,
            steps=1,
            initial_believer_density=0.0,
            initial_corrected_density=0.0,
            belief_spread_rate=1.0,
            factcheck_rate=0.0,
            peer_correction_rate=0.0,
            relapse_rate=0.0,
            toroidal=False,
            seed=1,
        )
        initial_grid = [
            [CellState.BELIEVER, CellState.BELIEVER, CellState.BELIEVER],
            [CellState.BELIEVER, CellState.UNAWARE, CellState.BELIEVER],
            [CellState.BELIEVER, CellState.BELIEVER, CellState.BELIEVER],
        ]
        sim = MisinformationCA(config, initial_grid=initial_grid)
        sim.advance()
        self.assertEqual(sim.grid[1][1], int(CellState.BELIEVER))

    def test_believer_is_corrected_when_factcheck_is_certain(self) -> None:
        config = SimulationConfig(
            width=3,
            height=3,
            steps=1,
            initial_believer_density=0.0,
            initial_corrected_density=0.0,
            belief_spread_rate=0.0,
            factcheck_rate=1.0,
            peer_correction_rate=0.0,
            relapse_rate=0.0,
            toroidal=False,
            seed=1,
        )
        initial_grid = [
            [CellState.UNAWARE, CellState.UNAWARE, CellState.UNAWARE],
            [CellState.UNAWARE, CellState.BELIEVER, CellState.UNAWARE],
            [CellState.UNAWARE, CellState.UNAWARE, CellState.UNAWARE],
        ]
        sim = MisinformationCA(config, initial_grid=initial_grid)
        sim.advance()
        self.assertEqual(sim.grid[1][1], int(CellState.CORRECTED))

    def test_corrected_can_relapse_under_believer_pressure(self) -> None:
        config = SimulationConfig(
            width=3,
            height=3,
            steps=1,
            initial_believer_density=0.0,
            initial_corrected_density=0.0,
            belief_spread_rate=0.0,
            factcheck_rate=0.0,
            peer_correction_rate=0.0,
            relapse_rate=1.0,
            toroidal=False,
            seed=1,
        )
        initial_grid = [
            [CellState.BELIEVER, CellState.BELIEVER, CellState.BELIEVER],
            [CellState.BELIEVER, CellState.CORRECTED, CellState.BELIEVER],
            [CellState.BELIEVER, CellState.BELIEVER, CellState.BELIEVER],
        ]
        sim = MisinformationCA(config, initial_grid=initial_grid)
        sim.advance()
        self.assertEqual(sim.grid[1][1], int(CellState.BELIEVER))

    def test_zero_rates_keep_grid_stable(self) -> None:
        config = SimulationConfig(
            width=3,
            height=3,
            steps=5,
            initial_believer_density=0.0,
            initial_corrected_density=0.0,
            belief_spread_rate=0.0,
            factcheck_rate=0.0,
            peer_correction_rate=0.0,
            relapse_rate=0.0,
            toroidal=False,
            seed=1,
        )
        initial_grid = [
            [CellState.UNAWARE, CellState.BELIEVER, CellState.CORRECTED],
            [CellState.CORRECTED, CellState.UNAWARE, CellState.BELIEVER],
            [CellState.BELIEVER, CellState.CORRECTED, CellState.UNAWARE],
        ]
        sim = MisinformationCA(config, initial_grid=initial_grid)
        initial_int_grid = [[int(cell) for cell in row] for row in initial_grid]
        sim.run()
        self.assertEqual(sim.grid, initial_int_grid)

    def test_history_conserves_population(self) -> None:
        config = SimulationConfig(width=10, height=8, steps=5, seed=123)
        sim = MisinformationCA(config)
        history = sim.run()

        self.assertEqual(len(history), config.steps + 1)
        for snapshot in history:
            total_count = (
                snapshot["unaware_count"]
                + snapshot["believer_count"]
                + snapshot["corrected_count"]
            )
            self.assertEqual(total_count, config.width * config.height)
            ratio_sum = (
                snapshot["unaware_ratio"]
                + snapshot["believer_ratio"]
                + snapshot["corrected_ratio"]
            )
            self.assertAlmostEqual(ratio_sum, 1.0, places=6)


if __name__ == "__main__":
    unittest.main()
