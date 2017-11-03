import copy
import traceback
from typing import List, Optional, Tuple

from roboscaffold_sim.simulators.basic_simulator import BasicSimulation


class BasicSimulationList:
    def __init__(self, initial_state: BasicSimulation = BasicSimulation()) -> None:
        self._working_state: BasicSimulation = initial_state
        self.states: List[BasicSimulation] = [copy.deepcopy(self._working_state)]
        self._b_blocks = 0
        self._s_blocks = 0
        self._last_check = 0

    @staticmethod
    def create_with_empty_states(num_states: int = 1):
        initial_state = BasicSimulation()
        states = BasicSimulationList(initial_state)
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

    def update_loop(self, max_rounds: int = 1000, print_res: bool=True):
        for _ in range(max_rounds):
            if self._working_state.finished():
                break
            else:
                if self.update():
                    break

        self.analyze()
        if print_res:
            print(f'Analyzed the {self._last_check} loaded states, currently '
                  f'{self._s_blocks} scaffolding has been used and {self._b_blocks} '
                  f'building blocks have beend used.')

    def analyze(self) -> Tuple[int, int, int]:
        if not self.states:
            raise Exception("No simulation in SimulationList")
        last_check = self._last_check
        if len(self.states) > self._last_check:
            s_blocks = max(len(x.sim_state.s_blocks) for x in self.states[last_check:])
            b_blocks = max(len(x.sim_state.b_blocks) for x in self.states[last_check:])
            self._s_blocks = max(s_blocks, self._s_blocks)
            self._b_blocks = max(b_blocks, self._b_blocks)

            time = len(self.states)
            self._last_check = time

        return self._s_blocks, self._b_blocks, self._last_check
