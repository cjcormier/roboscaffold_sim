import copy
import traceback
from typing import List, Optional

from roboscaffold_sim.coordinate import CoordinateList
from roboscaffold_sim.simulators.basic_simulator import BasicSimulation


class SimulationStateList:
    def __init__(self, initial_state: BasicSimulation = BasicSimulation()):
        self._working_state: BasicSimulation = initial_state
        self.states: List[BasicSimulation] = [copy.deepcopy(self._working_state)]

    @staticmethod
    def create_with_target_structure(target: CoordinateList):
        initial_state = BasicSimulation.create_with_target_structure(target)
        return SimulationStateList(initial_state)

    @staticmethod
    def create_with_empty_states(num_states: int = 1):
        initial_state = BasicSimulation()
        states = SimulationStateList(initial_state)
        for _ in range(num_states - 1):
            states.states.append(copy.deepcopy(initial_state))

        return states

    def update(self) -> Optional[Exception]:
        try:
            if not self._working_state.finished():
                self._working_state.update()
                self.states.append(copy.deepcopy(self._working_state))
        except Exception as e:
            traceback.print_exception(etype=type(e), value=e, tb=e.__traceback__)
            return e

    def update_loop(self, max_rounds: int = 1000):
        for _ in range(max_rounds):
            if self._working_state.finished():
                break
            else:
                exception = self.update()
                if exception:
                    break
