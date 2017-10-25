import copy
from enum import Enum, auto
from typing import Dict, List, NamedTuple, Optional, TypeVar

from roboscaffold_sim.coordinate import Coordinate, CoordinateList, CoordinateSet
from roboscaffold_sim.message.message_queue import MessageQueue
from roboscaffold_sim.state.block_states import BuildingBlockState, ScaffoldState
from roboscaffold_sim.state.builder_state import BuilderState

SBlocks = Dict[Coordinate, ScaffoldState]
BBlocks = Dict[Coordinate, BuildingBlockState]
Robots = Dict[Coordinate, BuilderState]


class GoalType(Enum):
    PLACE_BUILD_BLOCK = auto()
    PLACE_SCAFFOLD = auto()
    PICK_BUILD_BLOCK = auto()
    PICK_SCAFFOLD = auto()


class Goal(NamedTuple):
    coord: Coordinate
    type: GoalType


Goals = List[Optional[Goal]]
T = TypeVar('T', bound='SimulationState')


class SimulationState:
    def __init__(self):
        self.finished: bool = False
        self.s_blocks: SBlocks = dict()
        self.b_blocks: BBlocks = dict()
        self.robots: Robots = dict()

        self.target_structure: CoordinateList = []
        self.goal_stack: Goals = []

        self.messages: MessageQueue = MessageQueue()
        self.builder: BuilderState = BuilderState()

    @staticmethod
    def create_base_sim(structure: CoordinateList = list()) -> T:
        sim: T = SimulationState()

        sim.s_blocks[Coordinate(0, 0)] = ScaffoldState()
        sim.robots[Coordinate(0, 0)] = BuilderState()
        sim.target_structure = structure
        return sim

    @staticmethod
    def create_with_target_structure(target: CoordinateList):
        sim: T = SimulationState.create_base_sim()
        if SimulationState.validate_target_structure(target):
            sim.target_structure = target
            return sim
        else:
            raise ValueError('Given target is not a valid structure')

    @staticmethod
    def validate_target_structure(target: CoordinateList) -> bool:
        remaining_set: CoordinateSet = {x for x in target[1:]}
        neighbors: CoordinateSet = {target[0]}
        working_set: CoordinateSet = {target[0]}
        while len(working_set) > 0 and len(remaining_set) > 0:
            for coord in working_set:
                neighbors.update(coord.neighbors)
            working_set = neighbors.intersection(remaining_set)
            remaining_set = remaining_set.difference(working_set)

        return len(remaining_set) > 0

    @staticmethod
    def offset_target_structure(target: CoordinateList) -> CoordinateList:
        min_x = min(coord.x for coord in target)
        min_y = min(coord.x for coord in target)

        new_target: CoordinateList = []
        for coord in target:
            new_x = coord.x - min_x - 1
            new_y = coord.y - min_y - 1
            new_target.append(Coordinate(new_x, new_y))
        return new_target

    def update(self):
        pass


class SimulationStateList:
    def __init__(self, initial_state: SimulationState = None):
        if initial_state is None:
            initial_state = SimulationState()
        self._working_state: SimulationState = initial_state
        self.states: List[SimulationState] = [copy.deepcopy(self._working_state)]

    @staticmethod
    def create_with_goal_structure(goal):
        initial_state = SimulationState.create_with_target_structure(goal)
        return SimulationStateList(initial_state)

    @staticmethod
    def create_with_empty_states(num_states: int=1):
        initial_state = SimulationState()
        states = SimulationStateList(initial_state)
        for _ in range(num_states-1):
            states.states.append(copy.deepcopy(initial_state))

        return states

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
