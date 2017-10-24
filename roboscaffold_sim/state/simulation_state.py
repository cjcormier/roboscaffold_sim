from typing import Dict, List, Tuple
from roboscaffold_sim.state.block_states import BuildingBlockState, ScaffoldState
from roboscaffold_sim.message.message_queue import MessageQueue
from roboscaffold_sim.state.builder_state import BuilderState
from roboscaffold_sim.coordinate import Coordinate
from enum import Enum, auto
import copy

SBlocks = Dict[Coordinate, ScaffoldState]
BBlocks = Dict[Coordinate, BuildingBlockState]
Robots = Dict[Coordinate, BuilderState]
Coordinates = List[Coordinate]


class GoalType(Enum):
    PLACE_BUILD_BLOCK = auto()
    PLACE_SCAFFOLD = auto()
    PICK_BUILD_BLOCK = auto()
    PICK_SCAFFOLD = auto()


Goal = Tuple[Coordinate, GoalType]


class SimulationState:
    def __init__(self):
        self.finished: bool = False
        self.s_blocks: SBlocks = dict()
        self.b_blocks: BBlocks = dict()
        self.robots: Robots = dict()

        self.target_structure: Coordinates = []
        self.goal_stack = []

        self.messages: MessageQueue = MessageQueue()
        self.builder: BuilderState = BuilderState()

    @staticmethod
    def create_base_sim(structure: Coordinates = list()):
        sim = SimulationState()

        sim.s_blocks[Coordinate(0, 0)] = ScaffoldState()
        sim.robots[Coordinate(0, 0)] = BuilderState()
        sim.target_structure = structure

    def update(self):
        pass


class SimulationStateList:
    def __init__(self, initial_state: SimulationState):
        self._working_state: SimulationState = initial_state
        self.states: List[SimulationState] = [copy.deepcopy(self._working_state)]

    def update(self):
        if not self._working_state.finished:
            self._working_state.update()
            self.states.append(copy.deepcopy(self._working_state))

    def update_loop(self, max_rounds: int = 1000):
        for _ in range(max_rounds):
            if self._working_state.finished:
                break
            else:
                self.update()
