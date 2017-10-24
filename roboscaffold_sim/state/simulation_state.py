from typing import Dict, List
from roboscaffold_sim.state.block_states import BuildingBlockState, ScaffoldState
from roboscaffold_sim.message.message_queue import MessageQueue
from roboscaffold_sim.state.builder_state import BuilderState
from roboscaffold_sim.coordinate import Coordinate
import copy

SBlocks = Dict[Coordinate, ScaffoldState]
BBlocks = Dict[Coordinate, BuildingBlockState]


class SimulationState:
    def __init__(self):
        seed_coord = Coordinate(0, 0)
        self.s_blocks: SBlocks = {seed_coord: ScaffoldState()}
        self.b_blocks: BBlocks = {()}

        self.messages: MessageQueue = MessageQueue()
        self.builder: BuilderState = BuilderState()

        self.builder_location = Coordinate(0, 0)

    def update(self):
        pass


class SimulationStateList:
    def __init__(self):
        self.working_state: SimulationState = SimulationState()
        self.states: List[SimulationState] = []

    def update(self):
        self.states.append(copy.deepcopy(self.working_state))
        self.working_state.update()

    def update_loop(self, max_rounds: int = 1000):
        for _ in range(max_rounds):
            self.update()
