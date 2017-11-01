from typing import Dict, List, NamedTuple, Optional, Set

from roboscaffold_sim.coordinate import Coordinate, CoordinateList
from roboscaffold_sim.direction import Direction as Dir
from roboscaffold_sim.goal_type import GoalType
from roboscaffold_sim.state.scaffolding_state import ScaffoldState
from roboscaffold_sim.state.builder_state import BuilderState, HeldBlock

SBlocks = Dict[Coordinate, ScaffoldState]
BBlocks = Set[Coordinate]
Robots = Dict[Coordinate, BuilderState]


class Goal(NamedTuple):
    coord: Coordinate
    type: GoalType
    h_coord: Coordinate
    dir: Dir

    def __repr__(self):
        return f'{self.coord}:{self.type.name}'

    def get_block(self) -> HeldBlock:
        if self.type.is_scaffold():
            return HeldBlock.SCAFFOLD
        else:
            return HeldBlock.BUILD


Goals = List[Optional[Goal]]


class SimulationState:
    def __init__(self) -> None:
        self.s_blocks: SBlocks = dict()
        self.b_blocks: BBlocks = set()
        self.robots: Robots = dict()
        self.target_structure: CoordinateList = []
