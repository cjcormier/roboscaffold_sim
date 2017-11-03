from typing import Tuple, ClassVar

from roboscaffold_sim.coordinate import Coordinate, Down, CoordinateList, CoordinateSet
from roboscaffold_sim.errors import RobotActionError, TargetError
from roboscaffold_sim.simulators.basic_strategies.basic_strategy import \
    BasicStrategy
from roboscaffold_sim.simulators.basic_strategies.spine_strat import SpineStrat
from roboscaffold_sim.state.builder_state import BuilderState, HeldBlock
from roboscaffold_sim.state.scaffolding_state import ScaffoldState, SInstruction
from roboscaffold_sim.state.simulation_state import SimulationState


class BasicSimulation:
    def __init__(self, start_state: SimulationState = SimulationState(),
                 strategy: ClassVar[BasicStrategy] = SpineStrat) -> None:
        self.sim_state = start_state
        self.strategy = strategy(start_state)

    @staticmethod
    def create_base_sim(strat: ClassVar[BasicStrategy], target: CoordinateList = list()):
        sim_state = SimulationState()

        sim_state.s_blocks[Coordinate(0, 0)] = ScaffoldState(SInstruction.STOP)
        sim_state.robots[Coordinate(0, 0)] = BuilderState()
        sim_state.target_structure = target

        sim = BasicSimulation(sim_state, strat)
        sim.strategy.cache = Down
        return sim

    @staticmethod
    def create_with_target_structure(target: CoordinateList,
                                     strat: ClassVar[BasicStrategy]=SpineStrat):
        if not BasicSimulation.validate_target_structure(target):
            raise TargetError(target, 'Given target is not a valid structure')
        target = strat.configure_target(target)
        return BasicSimulation.create_base_sim(strat, target)

    @staticmethod
    def validate_target_structure(target: CoordinateList) -> bool:
        remaining_set: CoordinateSet = {x for x in target[1:]}
        neighbors: CoordinateSet = {target[0]}
        working_set: CoordinateSet = {target[0]}
        while len(working_set) > 0 and len(remaining_set) > 0:
            for coord in working_set:
                neighbors.update(coord.get_neighbors())
            working_set = neighbors.intersection(remaining_set)
            remaining_set = remaining_set.difference(working_set)

        return not remaining_set

    def update(self):
        robo_coord, robot = self.get_single_robot()
        if self.strategy.update(robo_coord, robot) and not self.strategy.finished:
            self.update_robots()

    def get_single_robot(self) -> Tuple[Coordinate, BuilderState]:
        if len(self.sim_state.robots) != 1:
            ValueError('this method requires exactly one robot in the state')

        for coord, robot in self.sim_state.robots.items():
            return coord, robot

    def update_robots(self):
        coord, robot = self.get_single_robot()
        block_instruction = self.sim_state.s_blocks[coord].instruction
        robot.left_turns(block_instruction.get_left_turns())
        if block_instruction.is_drive():
            self.move_robot(coord, robot)
        elif block_instruction.is_drop():
            self.drop(coord, robot)
        elif block_instruction.is_pick():
            self.pick(coord, robot)

    def pick(self, robo_coord: Coordinate, robot: BuilderState):
        block_coord = robo_coord.get_coord_in_direction(robot.direction)

        if block_coord in self.sim_state.s_blocks:
            del self.sim_state.s_blocks[block_coord]
            robot.block = HeldBlock.SCAFFOLD
        elif block_coord in self.sim_state.b_blocks:
            self.sim_state.b_blocks.remove(block_coord)
            robot.block = HeldBlock.BUILD
        else:
            raise RobotActionError(f'Attempting to pick an empty block at {block_coord}')

    def drop(self, robo_coord: Coordinate, robot: BuilderState):
        block_coord = robo_coord.get_coord_in_direction(robot.direction)
        if robot.block is HeldBlock.NONE:
            raise RobotActionError('Cannot drop NONE Block')

        sim_state = self.sim_state
        if block_coord in sim_state.b_blocks or block_coord in sim_state.s_blocks:
            raise RobotActionError('Block already present')

        if robot.block is HeldBlock.BUILD:
            self.sim_state.b_blocks.add(block_coord)
        elif robot.block is HeldBlock.SCAFFOLD:
            self.sim_state.s_blocks[block_coord] = ScaffoldState()

        robot.block = HeldBlock.NONE

    def move_robot(self, robo_coord: Coordinate, robot: BuilderState):
        new_coords = robo_coord.get_coord_in_direction(robot.direction)
        if new_coords not in self.sim_state.s_blocks:
            raise RobotActionError('Robot is moving onto a space without scaffolding')

        del self.sim_state.robots[robo_coord]
        self.sim_state.robots[new_coords] = robot

    def finished(self):
        return self.strategy.finished
