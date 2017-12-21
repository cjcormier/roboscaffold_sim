from copy import deepcopy, copy
from typing import Tuple, List, TextIO, Optional

from roboscaffold_sim.coordinate import Coordinate, CoordinateList, Origin
from roboscaffold_sim.goal_type import GoalType as GType, GoalType
from roboscaffold_sim.simulators.basic_strategies.basic_strategy import \
    BasicStrategy
from roboscaffold_sim.simulators.load_save import create_goal, create_scaffold, load_coords, load
from roboscaffold_sim.state.builder_state import BuilderState, HeldBlock
from roboscaffold_sim.state.scaffolding_state import ScaffoldState, SInstruction
from roboscaffold_sim.state.simulation_state import SimulationState, Goal, Goals


class LoadStrat(BasicStrategy):
    def __init__(self, sim_state: SimulationState = SimulationState()) -> None:
        BasicStrategy.__init__(self, sim_state)

        self.seed: Coordinate = Coordinate(0, 0)
        self.cache: Coordinate = Coordinate(0, 1)
        self.goal_stack: Goals = []
        self.index = 0
        self.goal_stacks: List[Goals] = []
        self.sinstructions: List[List[Tuple[Coordinate, SInstruction]]] = []

    @staticmethod
    def configure_target(target: CoordinateList, allow_offset: bool = True) -> CoordinateList:
        return target

    def load(self, file_name: str):
        self.sim_state.target_structure, self.goal_stacks, self.sinstructions = load(file_name)
        self.update(*self.sim_state.get_single_robot())

    def update(self, robo_coord: Coordinate, robot: BuilderState) -> bool:
        goal_finished = self.check_for_finished_goals(robot)
        if goal_finished:
            if self.index == len(self.goal_stacks):
                self.finished = True
                return False
            else:
                self.determine_new_goals(robo_coord, robot)
                self.update_scaffolding(robo_coord, robot)
                self.index += 1
                return False
        return True

    def check_for_finished_goals(self, robot: BuilderState) -> bool:

        if len(self.goal_stack) == 0:
            return True

        g_coord = self.goal_stack[-1].coord
        g_type = self.goal_stack[-1].type
        held_block = robot.block
        sim_state = self.sim_state
        if (g_type == GType.PICK_SCAFFOLD and held_block is HeldBlock.SCAFFOLD) or \
                (g_type == GType.PICK_BUILD_BLOCK and held_block is HeldBlock.BUILD) or \
                (g_type == GType.PLACE_SCAFFOLD and g_coord in sim_state.s_blocks) or \
                (g_type == GType.PLACE_BUILD_BLOCK and g_coord in sim_state.b_blocks):
            if self.cache == g_coord and g_coord in sim_state.s_blocks and g_type == GType.PLACE_SCAFFOLD:
                del sim_state.s_blocks[self.cache]
            self.goal_stack = self.goal_stack[0:-1]
            return True

        return False

    def determine_new_goals(self, robo_coord: Coordinate, robot: BuilderState):
        """Determines the next goal if needed, returns if the scaffolding should update"""
        self.goal_stack = self.goal_stacks[self.index]
        next_goal = self.goal_stack[-1]
        if next_goal.coord == self.cache and next_goal.type.is_pick():
            if next_goal.type.is_build():
                self.sim_state.b_blocks.add(self.cache)
            else:
                self.sim_state.s_blocks[self.cache] = ScaffoldState()

    def update_scaffolding(self, r_coord: Coordinate, robot: BuilderState):
        for coord, block in self.sim_state.s_blocks.items():
            block.instruction = SInstruction.NONE
        instructions = self.sinstructions[self.index]
        for coord, instruction in instructions:
            self.sim_state.s_blocks[coord].instruction = instruction

    def __deepcopy__(self, memo):
        # TODO: Maybe make special copy method for strategies?
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        result.seed = copy(self.seed)
        result.cache = copy(self.seed)
        result.sim_state = deepcopy(self.sim_state, memo)
        result.goal_stack = deepcopy(self.goal_stack, memo)

        result.finished = self.finished
        return result

    def get_next_unfinished_block(self) -> Optional[Coordinate]:
        pass
