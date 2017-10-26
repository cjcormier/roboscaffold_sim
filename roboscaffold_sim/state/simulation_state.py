import copy
import traceback
from enum import Enum, auto
from typing import Dict, List, NamedTuple, Optional, TypeVar, Tuple, Set

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

    def __repr__(self):
        return f'{self.coord}:{self.type.name}'


Goals = List[Optional[Goal]]
T = TypeVar('T', bound='SimulationState')
# TODO: make exceptions
# TODO: make interface/abstract class and sub classes
# TODO: function type hinting
# TODO: docstrings


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
        self.cache = Coordinate(0, 1)

    @staticmethod
    def create_base_sim(structure: CoordinateList = list()) -> T:
        sim: T = SimulationState()

        sim.s_blocks[Coordinate(0, 0)] = ScaffoldState(ScaffoldInstruction.STOP)
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

        return len(remaining_set) == 0

    @staticmethod
    def offset_target_structure(target: CoordinateList) -> CoordinateList:
        min_x = min(coord.x for coord in target)
        min_y = min(coord.x for coord in target)

        new_target: CoordinateList = []
        for coord in target:
            new_x = coord.x - min_x - 1
            new_y = coord.y - min_y - 1
            new_target.append(Coordinate(new_x, new_y))

        new_target.sort(key=lambda coord: (-coord.x, coord.y))
        return new_target

    def update(self):
        process_goals = self.validate_goals()
        update_scaffolding = False
        if process_goals:
            update_scaffolding = self.process_goals()

        if update_scaffolding:
            self.update_scaffolding()
        else:
            self.update_robots()

    def validate_goals(self):
        process_goals = False

        # TODO: is a while loop needed
        while True:
            if len(self.goal_stack) == 0:
                process_goals = True
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
            process_goals = True

        return process_goals

    def get_single_robot(self) -> Tuple[Coordinate, BuilderState]:
        if len(self.robots) != 1:
            ValueError('this method requires exactly one robot in the state')

        for coord, robot in self.robots.items():
            return coord, robot

    # TODO: clean up method
    # TODO: Test
    def process_goals(self):
        """Determines the next goal if needed and returns if the scaffolding should update"""
        if len(self.target_structure) == 0:
            return False

        if len(self.goal_stack) == 0:
            next_b_block_location = self.get_next_unfinished_block()
            if next_b_block_location is None:
                self.finished = True
                return False
            else:
                new_goal = Goal(next_b_block_location, GoalType.PLACE_BUILD_BLOCK)
                self.goal_stack = [new_goal]

        robo_coord, robot = self.get_single_robot()

        next_goal = self.goal_stack[-1]
        # TODO: make getting robot better
        if next_goal.type is GoalType.PICK_BUILD_BLOCK or next_goal.type is GoalType.PICK_SCAFFOLD:
            if robot.held_block is not HeldBlock.NONE:
                raise ValueError('Holding block when next goal is picking a block')
            else:
                return True

        elif next_goal.type is GoalType.PLACE_BUILD_BLOCK or GoalType.PLACE_SCAFFOLD:

            # TODO: check if scaffolding is in the way of build block
            if robot.held_block is next_goal.type:
                return True
            elif robot.held_block is HeldBlock.NONE:
                if self.neighbor_coord_is_reachable(robo_coord, next_goal.coord):
                    if self.neighbor_coord_is_reachable(self.cache, next_goal.coord):
                        pick_type = GoalType.PICK_SCAFFOLD if next_goal.type is GoalType.PLACE_SCAFFOLD \
                            else GoalType.PICK_BUILD_BLOCK
                        self.goal_stack.append(Goal(self.cache, pick_type))
                    else:
                        raise ValueError('need new block, but cache is unreachable')
                    return True
                else:
                    next_needed_coord = self.get_next_needed_block(robo_coord, next_goal.coord)
                    self.goal_stack.append(Goal(next_needed_coord, GoalType.PLACE_SCAFFOLD))
                    # TODO: make iterative instead of recursive?
                    return self.process_goals()
            else:
                raise ValueError('Held block does not match next goal')

        return False

    def get_next_unfinished_block(self) -> Optional[Coordinate]:
        for coord in self.target_structure:
            if coord not in self.b_blocks:
                return coord
        return None

    def get_next_needed_block(self, start: Coordinate, goal: Coordinate) -> Coordinate:
        path = self.get_path_to(start, goal, False)
        for path_coord in path:
            if path_coord not in self.s_blocks:
                return path_coord
        raise ValueError('already a path there')

    def get_path_to(self, start: Coordinate, goal: Coordinate, only_scaffold=True) -> List[Coordinate]:

        class SearchTuple(NamedTuple):
            coord: Coordinate
            path: List[Coordinate]

            def __eq__(self, other):
                if isinstance(other, self.__class__):
                    return self.coord == other.coord
                return NotImplemented

            def __ne__(self, other):
                """Define a non-equality test"""
                if isinstance(other, self.__class__):
                    return not self.__eq__(other)
                return NotImplemented

            def __hash__(self):
                return hash(self.coord)

            def __repr__(self):
                return f'{self.coord} -> {len(self.path)}'

        invalid_blocks = set(self.b_blocks)
        neighbors: Set[Coordinate, Tuple[Coordinate]] = {SearchTuple(start, [])}
        explored = set()

        while len(neighbors) != 0:
            working_set = neighbors
            neighbors = set()
            for coord, path in working_set:
                new_path = path[:]
                new_path.append(coord)
                new_neighbors = coord.get_neighbors()
                if goal in new_neighbors:
                    return new_path
                for neighbor in new_neighbors:
                    valid_coordinate = neighbor.x >= 0 and neighbor.y >= 0
                    valid_block = neighbor not in invalid_blocks and (neighbor in self.s_blocks or not only_scaffold)
                    not_cache = neighbor != self.cache

                    search_tuple = SearchTuple(neighbor, new_path)
                    if valid_coordinate and valid_block and neighbor not in explored and not_cache:
                        neighbors.add(search_tuple)
                    explored.add(search_tuple)

    # TODO: Test
    def neighbor_coord_is_reachable(self, start: Coordinate, goal: Coordinate, only_scaffold=True, include_cache=True):
        valid_blocks = set(self.s_blocks.keys())
        if start == goal:
            return True

        if include_cache:
            valid_blocks.add(self.cache)
        if not only_scaffold:
            valid_blocks.update(self.b_blocks.keys())

        if start not in valid_blocks:
            return False

        neighbors = set(start.get_neighbors())
        explored = set()
        while len(neighbors) != 0:
            working_set = neighbors
            neighbors = set()
            for coord in working_set:
                new_neighbors = coord.get_neighbors()
                if goal in new_neighbors:
                    return True

                neighbors.update([x for x in new_neighbors if x in valid_blocks and x not in explored])

        return False

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
                self.pick(coord, robot, block_instruction)
            elif block_instruction is ScaffoldInstruction.PICK_RIGHT:
                robot.turn('right')
                self.pick(coord, robot, block_instruction)
            elif block_instruction is ScaffoldInstruction.PICK_FORWARD:
                self.pick(coord, robot, block_instruction)
            elif block_instruction is ScaffoldInstruction.DROP_LEFT:
                robot.turn('left')
                self.drop(coord, robot)
            elif block_instruction is ScaffoldInstruction.DROP_RIGHT:
                robot.turn('right')
                self.drop(coord, robot)
            elif block_instruction is ScaffoldInstruction.DROP_FORWARD:
                self.drop(coord, robot)

    def pick(self, robo_coord: Coordinate, robot: BuilderState, instruction: GoalType):
        self.validate_robot_position(robo_coord)
        block_coord = robo_coord.get_coord_in_direction(robot.direction)
        wanted_block = HeldBlock.SCAFFOLD if instruction is GoalType.PICK_SCAFFOLD else HeldBlock.BUILD

        if block_coord in self.s_blocks and wanted_block is HeldBlock.SCAFFOLD:
            del self.s_blocks[block_coord]
        elif block_coord in self.b_blocks and wanted_block is HeldBlock.BUILD:
            del self.b_blocks[block_coord]
        elif block_coord == self.cache:
            pass
        else:
            raise LookupError("Invalid block found and not pointed at seed ")

        robot.held_block = wanted_block

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

    def update(self) -> Optional[Exception]:
        try:
            if not self._working_state.finished:
                self._working_state.update()
                self.states.append(copy.deepcopy(self._working_state))
        except Exception as e:
            traceback.print_exception(etype=type(e), value=e, tb=e.__traceback__)
            return e

    def update_loop(self, max_rounds: int = 1000):
        for _ in range(max_rounds):
            if self._working_state.finished:
                break
            else:
                exception = self.update()
                if exception:
                    break
