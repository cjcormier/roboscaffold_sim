import traceback
from typing import Optional, Tuple, ClassVar

from roboscaffold_sim.coordinate import CoordinateList
from roboscaffold_sim.simulators.basic_analyzer_simulator import BasicAnalyzerSimulation
from roboscaffold_sim.simulators.basic_strategies.basic_strategy import BasicStrategy


class BasicSimulationAnalysis:
    def __init__(self, initial_state: BasicAnalyzerSimulation = BasicAnalyzerSimulation()) -> None:
        self._working_state: BasicAnalyzerSimulation = initial_state
        self._moves = 0
        self._time = 0

    @staticmethod
    def analyze_sim(target: CoordinateList, strat: ClassVar[BasicStrategy]) -> Tuple[int, int]:
        sim = BasicAnalyzerSimulation.create_with_target_structure(target, strat)
        return BasicSimulationAnalysis(sim).analyze()

    def update(self) -> Optional[Exception]:
        try:
            self._working_state.update()
            self.analyze_step()
        except Exception as e:
            traceback.print_exception(etype=type(e), value=e, tb=e.__traceback__)
            return e

    def analyze(self) -> Tuple[int, int]:
        while True:
            if self._working_state.finished or self.update():
                break
        return self._moves, self._time

    def analyze_step(self) -> None:
        if not self._working_state:
            raise Exception("No simulation in SimulationList")
        goal_stack = self._working_state.strategy.goal_stack
        if goal_stack:
            g_coord = self._working_state.strategy.goal_stack[-1].coord
            r_coord, r_state = self._working_state.get_single_robot()
            if g_coord.x != r_coord.x:
                self._moves += abs(g_coord.y) + abs(r_coord.y) + abs(r_coord.x-g_coord.x)
            else:
                self._moves += abs(g_coord.y - r_coord.y)
        self._time += 1
