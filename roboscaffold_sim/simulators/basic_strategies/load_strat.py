from io import TextIOWrapper
from typing import Tuple, List

from roboscaffold_sim.coordinate import Coordinate, Coordinates, CoordinateList
from roboscaffold_sim.goal_type import GoalType as GType
from roboscaffold_sim.simulators.basic_strategies.basic_strategy import \
    BasicStrategy
from roboscaffold_sim.state.builder_state import BuilderState, HeldBlock
from roboscaffold_sim.state.scaffolding_state import ScaffoldState
from roboscaffold_sim.state.simulation_state import SimulationState, Goal, Goals


class LoadStrat(BasicStrategy):
    def __init__(self, sim_state: SimulationState, ) -> None:
        BasicStrategy.__init__(self, sim_state)

        self.seed: Coordinate = Coordinate(0, 0)
        self.cache: Coordinate = Coordinate(0, 1)
        self.goal_stack: Goals = []
        self.curr_index = 0
        self.overall_index = 0
        self.data: List(Goals, Tuple(Coordinate, ScaffoldState)) = []
        self.sim_state = sim_state

    def load(self, file_name: str):
        with open(file_name, 'r') as file:
            self.sim_state.target_structure = self.load_coords(file)
            self.min_x = min(coord.x for coord in self.sim_state.target_structure)
            self.min_y = min(coord.y for coord in self.sim_state.target_structure)

    @staticmethod
    def load_coords(file: TextIOWrapper) -> CoordinateList:
        coords: CoordinateList = []
        line = file.readline()
        for block in line.split():
            coords.append(Coordinate.from_string(block))
        return coords

    def update(self, robo_coord, robot) -> bool:
        goal_finished = self.check_for_finished_goals(robot)
        if goal_finished:
            if self.determine_new_goals(robo_coord, robot):
                self.update_scaffolding(robo_coord, robot)
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
        # TODO: Load from file
        if len(self.sim_state.target_structure) == 0:
            return False

        if self.check_is_finished():
            return False


        pass

    def check_is_finished(self)-> bool:
        # TODO: Load from file
        pass

    def update_scaffolding(self, r_coord: Coordinate, robot: BuilderState):
        # TODO: Load from file
        pass
