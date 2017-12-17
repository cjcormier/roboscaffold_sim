import copy
import traceback
from typing import List, Optional, Tuple

from roboscaffold_sim.simulators.basic_simulator import BasicSimulation
from roboscaffold_sim.state.builder_state import HeldBlock
from roboscaffold_sim.state.simulation_state import SBlocks


class BasicSimulationList:
    def __init__(self, initial_state: BasicSimulation = BasicSimulation()) -> None:
        self._working_state: BasicSimulation = initial_state
        self.states: List[BasicSimulation] = [copy.deepcopy(self._working_state)]
        self._b_blocks = 0
        self._s_blocks = 0
        self._last_check = 0
        self.robot_updates = 0
        self.scaffold_placements = 0
        self.build_placements = 0
        self.block_updates = 0

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

    def update_loop(self, max_rounds: int = 1000):
        for _ in range(max_rounds):
            if self._working_state.finished() or self.update():
                break

    def analyze(self) -> Tuple[int, int, int]:
        if not self.states:
            raise Exception("No simulation in SimulationList")
        last_check = self._last_check
        if len(self.states) > last_check:
            s_blocks = max(len(x.sim_state.s_blocks) for x in self.states[last_check:])
            b_blocks = max(len(x.sim_state.b_blocks) for x in self.states[last_check:])
            self._s_blocks = max(s_blocks, self._s_blocks)
            self._b_blocks = max(b_blocks, self._b_blocks)
        while len(self.states) > last_check:
            if last_check > 0:
                prev_state = self.states[last_check-1].sim_state
                curr_state = self.states[last_check].sim_state
                if prev_state.robots.keys() != curr_state.robots.keys():
                    self.robot_updates += 1
                if prev_state.get_single_robot()[1].block != curr_state.get_single_robot()[1].block:
                    blocks = (prev_state.get_single_robot()[1].block, curr_state.get_single_robot()[1].block)
                    if HeldBlock.SCAFFOLD in blocks:
                        self.scaffold_placements += 1
                    elif HeldBlock.BUILD in blocks:
                        self.build_placements += 1
                if self.check_block_update(prev_state.s_blocks, curr_state.s_blocks):
                    self.block_updates += 1
            last_check += 1

        self._last_check = last_check
        return self._s_blocks, self._b_blocks, self._last_check

    @staticmethod
    def check_block_update(prev_blocks: SBlocks, curr_blocks: SBlocks):
        common_coords = set(prev_blocks.keys()).intersection(set(curr_blocks.keys()))
        for coord in common_coords:
            if prev_blocks[coord] != curr_blocks[coord]:
                return True
        return False
