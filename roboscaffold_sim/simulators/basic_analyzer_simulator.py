from typing import ClassVar

from roboscaffold_sim.coordinate import Coordinate, CoordinateList, Down
from roboscaffold_sim.errors import RobotActionError, TargetError
from roboscaffold_sim.simulators.basic_simulator import BasicSimulation
from roboscaffold_sim.simulators.basic_strategies.basic_strategy import \
    BasicStrategy
from roboscaffold_sim.simulators.basic_strategies.spine_strat import SpineStrat
from roboscaffold_sim.state.builder_state import BuilderState, HeldBlock
from roboscaffold_sim.state.scaffolding_state import ScaffoldState, SInstruction
from roboscaffold_sim.state.simulation_state import SimulationState


class BasicAnalyzerSimulation(BasicSimulation):
    def __init__(self, start_state: SimulationState = SimulationState(),
                 strategy: ClassVar[BasicStrategy] = SpineStrat) -> None:
        BasicSimulation.__init__(self, start_state, strategy)
        self.sim_state = start_state
        self.strategy = strategy(start_state)

    @staticmethod
    def create_with_target_structure(target: CoordinateList,
                                     strat: ClassVar[BasicStrategy]=SpineStrat):
        if not BasicSimulation.is_valid_structure(target):
            raise TargetError(target, 'Given target is not a valid structure')
        target = strat.configure_target(target)
        return BasicAnalyzerSimulation.create_base_sim(strat, target)


    @staticmethod
    def create_base_sim(strat: ClassVar[BasicStrategy], target: CoordinateList = list()):
        sim_state = SimulationState()

        sim_state.s_blocks[Coordinate(0, 0)] = ScaffoldState(SInstruction.STOP)
        sim_state.robots[Coordinate(0, 0)] = BuilderState()
        sim_state.target_structure = target

        sim = BasicAnalyzerSimulation(sim_state, strat)
        sim.strategy.cache = Down
        return sim

    def update(self):
        robo_coord, robot = self.get_single_robot()
        self.strategy.update(robo_coord, robot)
        if not self.strategy.finished:
            self.update_robots()

    def update_robots(self):
        coord, robot = self.get_single_robot()
        goal = self.strategy.goal_stack[-1]

        del self.sim_state.robots[coord]
        self.sim_state.robots[goal.h_coord] = robot

        block_instruction = self.sim_state.s_blocks[goal.h_coord].instruction

        if block_instruction.is_drop():
            self.drop(goal.coord, robot)
        elif block_instruction.is_pick():
            self.pick(goal.coord, robot)

    def pick(self, block_coord: Coordinate, robot: BuilderState):

        if block_coord in self.sim_state.s_blocks:
            del self.sim_state.s_blocks[block_coord]
            robot.block = HeldBlock.SCAFFOLD
        elif block_coord in self.sim_state.b_blocks:
            self.sim_state.b_blocks.remove(block_coord)
            robot.block = HeldBlock.BUILD
        else:
            raise RobotActionError(f'Attempting to pick an empty block at {block_coord}')

    def drop(self, block_coord: Coordinate, robot: BuilderState):
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
