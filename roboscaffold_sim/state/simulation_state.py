import copy
from enum import Enum, auto
from typing import Dict, List, NamedTuple, Optional, TypeVar

from roboscaffold_sim.coordinate import Coordinate, CoordinateList, CoordinateSet
from roboscaffold_sim.message.message_queue import MessageQueue
from roboscaffold_sim.state.block_states import BuildingBlockState, ScaffoldState, \
    ScaffoldInstruction
from roboscaffold_sim.state.builder_state import BuilderState, HeldBlock

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
                neighbors.update(coord.get_neighbors())
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

        new_target.sort(key=lambda coord: (coord.x, coord.y))
        return new_target

    def update(self):
        if self.validate_goals():
            self.update_scaffolding()
        else:
            if not self.finished:
                self.update_robots()

    def validate_goals(self):
        get_new_goal = False
        while True:
            if len(self.goal_stack) == 0:
                get_new_goal = True
                break
            curr_goal = self.goal_stack[-1]

            if curr_goal.type == GoalType.PLACE_SCAFFOLD and curr_goal.coord in self.s_blocks:
                pass
            elif curr_goal.type == GoalType.PLACE_BUILD_BLOCK and curr_goal.coord in self.b_blocks:
                pass
            elif curr_goal.type == GoalType.PICK_SCAFFOLD and curr_goal.coord not in self.s_blocks:
                pass
            elif curr_goal.type == GoalType.PICK_BUILD_BLOCK and curr_goal.coord not in self.b_blocks:
                pass
            else:
                break

            self.goal_stack = self.goal_stack[0:-1]
            get_new_goal = True

        if get_new_goal:
            self.get_new_goal()

        return get_new_goal and self.finished

    def get_new_goal(self):
        pass

    def update_robots(self):
        working_set = dict(self.robots)
        for coord, robot in working_set.items():
            block_instruction = self.s_blocks[coord].instruction
            if block_instruction is ScaffoldInstruction.NONE:
                self.move_robot(coord, robot)
            elif block_instruction is ScaffoldInstruction.STOP:
                continue
            elif block_instruction is ScaffoldInstruction.DRIVE_LEFT:
                robot.turn('left')
                self.move_robot(coord, robot)
            elif block_instruction is ScaffoldInstruction.DRIVE_RIGHT:
                robot.turn('right')
                self.move_robot(coord, robot)
            elif block_instruction is ScaffoldInstruction.PICK_LEFT:
                robot.turn('left')
                self.pick(coord, robot)
            elif block_instruction is ScaffoldInstruction.PICK_RIGHT:
                robot.turn('right')
                self.pick(coord, robot)
            elif block_instruction is ScaffoldInstruction.PICK_FORWARD:
                self.pick(coord, robot)
            elif block_instruction is ScaffoldInstruction.DROP_LEFT:
                robot.turn('left')
                self.drop(coord, robot)
            elif block_instruction is ScaffoldInstruction.DROP_RIGHT:
                robot.turn('right')
                self.drop(coord, robot)
            elif block_instruction is ScaffoldInstruction.DROP_FORWARD:
                self.drop(coord, robot)

    def pick(self, robo_coord: Coordinate, robot: BuilderState):
        self.validate_robot_position(robo_coord)
        block_coord = robo_coord.get_coord_in_direction(robot.direction)

        if block_coord in self.s_blocks:
            del self.s_blocks[block_coord]
            robot.held_block = HeldBlock.SCAFFOLD
        elif block_coord in self.b_blocks:
            del self.b_blocks[block_coord]
            robot.held_block = HeldBlock.BUILD
        else:
            raise LookupError("No block found")

    def drop(self, robo_coord: Coordinate, robot: BuilderState):
        self.validate_robot_position(robo_coord)
        block_coord = robo_coord.get_coord_in_direction(robot.direction)
        if robot.held_block is HeldBlock.NONE:
            raise ValueError('Cannot drop NONE Block')

        if block_coord not in self.b_blocks or block_coord not in self.s_blocks:
            raise LookupError('Block already present')

        if robot.held_block is HeldBlock.BUILD:
            self.b_blocks[block_coord] = BuildingBlockState()
        elif robot.held_block is HeldBlock.SCAFFOLD:
            self.s_blocks[block_coord] = ScaffoldState()

    def move_robot(self, robo_coord: Coordinate, robot: BuilderState):
        self.validate_robot_position(robo_coord)
        new_coords = robo_coord.get_coord_in_direction(robot.direction)
        if new_coords in self.robots:
            raise ValueError('Robot in moving position')
        if new_coords not in self.s_blocks:
            raise ValueError('Robot is moving onto a space without scaffolding')

        del self.robots[robo_coord]
        self.robots[new_coords] = robot

    def validate_robot_position(self, robo_coord: Coordinate):
        if robo_coord not in self.robots:
            raise ValueError('Robot does not exist at Coordinates')

    def update_scaffolding(self):
        pass


class SimulationStateList:
    def __init__(self, initial_state: SimulationState = SimulationState()):
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
