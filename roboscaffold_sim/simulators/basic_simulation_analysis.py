import traceback
from typing import Optional, Tuple, ClassVar

from roboscaffold_sim.coordinate import CoordinateList
from roboscaffold_sim.simulators.basic_simulator import BasicSimulation
from roboscaffold_sim.simulators.basic_strategies.basic_strategy import BasicStrategy


class BasicSimulationAnalysis:
    def __init__(self, initial_state: BasicSimulation = BasicSimulation()) -> None:
        self._working_state: BasicSimulation = initial_state
        self._b_blocks = 0
        self._s_blocks = 0
        self._time = 0

    @staticmethod
    def analyze_sim(target: CoordinateList, strat: ClassVar[BasicStrategy]) -> Tuple[int, int, int]:
        sim = BasicSimulation.create_with_target_structure(target, strat)
        return BasicSimulationAnalysis(sim).analyze()

    def update(self) -> Optional[Exception]:
        try:
            if not self._working_state.finished():
                self._working_state.update()
        except Exception as e:
            traceback.print_exception(etype=type(e), value=e, tb=e.__traceback__)
            return e

    def analyze(self) -> Tuple[int, int, int]:
        while True:
            if self._working_state.finished():
                break
            else:
                if self.update():
                    break
            self.analyze_step()
        return self._b_blocks, self._s_blocks, self._time

    def analyze_step(self) -> None:
        if not self._working_state:
            raise Exception("No simulation in SimulationList")
        self._s_blocks = max(len(self._working_state.sim_state.s_blocks), self._s_blocks)
        self._b_blocks = max(len(self._working_state.sim_state.b_blocks), self._b_blocks)
        self._time += 1
