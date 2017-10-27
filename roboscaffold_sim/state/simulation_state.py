import copy
import traceback
from enum import Enum, auto
from typing import Dict, List, NamedTuple, Optional, TypeVar, Tuple, Set

from roboscaffold_sim.coordinate import Coordinate, CoordinateList, CoordinateSet, \
    Right, Down
from roboscaffold_sim.direction import Direction as Dir
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
        self.seed: Coordinate = Coordinate(0, 0)
        self.cache: Coordinate = Coordinate(0, 0)

    @staticmethod
    def create_base_sim(structure: CoordinateList = list()) -> T:
        sim: T = SimulationState()

        sim.s_blocks[Coordinate(0, 0)] = ScaffoldState(ScaffoldInstruction.STOP)
        sim.robots[Coordinate(0, 0)] = BuilderState()
        sim.target_structure = structure
        sim.cache = Coordinate(0, 0)
        sim.cache = Coordinate(0, 1)
        return sim

    @staticmethod
    def create_with_target_structure(target: CoordinateList):
        sim: T = SimulationState.create_base_sim()
        if SimulationState.validate_target_structure(target):
            target.sort(key=lambda coord: (coord.x, -coord.y))
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

        return new_target

    def update(self):
        process_goals = self.validate_goals()
        update_scaffolding = False
        if process_goals:
            update_scaffolding = self.process_goals()

        if update_scaffolding:
            self.update_scaffolding()
        else:
            if not self.finished:
                self.update_robots()

    def validate_goals(self):

        if len(self.goal_stack) == 0:
            return True

        curr_goal = self.goal_stack[-1]
        robo_coord, robot = self.get_single_robot()
        valid_place_scaffold = curr_goal.type == GoalType.PLACE_SCAFFOLD and \
            curr_goal.coord in self.s_blocks
        valid_place_block = curr_goal.type == GoalType.PLACE_BUILD_BLOCK and \
            curr_goal.coord in self.b_blocks
        valid_pick_scaffold = curr_goal.type == GoalType.PICK_SCAFFOLD and \
            robot.held_block is HeldBlock.SCAFFOLD
        valid_pick_block = curr_goal.type == GoalType.PICK_BUILD_BLOCK and \
            robot.held_block is HeldBlock.BUILD

        if valid_place_scaffold or valid_place_block or \
                valid_pick_scaffold or valid_pick_block:
            self.goal_stack = self.goal_stack[0:-1]
            return True

        return False

    # TODO: make getting robot better
    def get_single_robot(self) -> Tuple[Coordinate, BuilderState]:
        if len(self.robots) != 1:
            ValueError('this method requires exactly one robot in the state')

        for coord, robot in self.robots.items():
            return coord, robot

    # TODO: clean up method
    # TODO: Test
    # TODO; Better function names
    def process_goals(self):
        """Determines the next goal if needed, returns if the scaffolding should update"""
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
        if next_goal.type is GoalType.PICK_BUILD_BLOCK or \
                next_goal.type is GoalType.PICK_SCAFFOLD:
            if robot.held_block is not HeldBlock.NONE:
                raise ValueError('Holding block when next goal is picking a block')
            else:
                return True

        elif next_goal.type is GoalType.PLACE_BUILD_BLOCK or GoalType.PLACE_SCAFFOLD:
            # TODO: check if scaffolding is in the way of build block
            if self.compare_block_and_instruction(robot.held_block, next_goal.type):
                return True
            elif robot.held_block is HeldBlock.NONE:

                # Before just saying to get the block for the location we look ahead
                # check if we can reach this location
                # if we can, add the block pick goal
                # if we can't, find a block we can get to that helps us on our way
                #       Note: choosing this block intelligently can reduce
                #       complexity in other portions of the code

                if self.neighbor_coord_is_reachable(robo_coord, next_goal.coord):
                    if self.neighbor_coord_is_reachable(self.cache, next_goal.coord):
                        if next_goal.type is GoalType.PLACE_SCAFFOLD:
                            pick_type = GoalType.PICK_SCAFFOLD
                        else:
                            pick_type = GoalType.PICK_BUILD_BLOCK
                        self.goal_stack.append(Goal(self.cache, pick_type))
                    else:
                        raise ValueError('need new block, but cache is unreachable')
                    return True
                else:
                    next_needed_coord = self.get_next_needed_block(next_goal.coord)
                    self.goal_stack.append(
                        Goal(next_needed_coord, GoalType.PLACE_SCAFFOLD))
                    # TODO: make iterative instead of recursive?
                    return self.process_goals()
            else:
                raise ValueError('Held block does not match next goal')

        return False

    def compare_block_and_instruction(self, block: HeldBlock,
                                      goal: GoalType) -> bool:
        if goal == GoalType.PICK_SCAFFOLD or goal == GoalType.PLACE_SCAFFOLD:
            return block is HeldBlock.SCAFFOLD
        else:
            return block is HeldBlock.BUILD

    def get_next_unfinished_block(self) -> Optional[Coordinate]:
        for coord in self.target_structure:
            if coord not in self.b_blocks:
                return coord
        return None

    # TODO: be smareter about getting the next block
    def get_next_needed_block(self, goal: Coordinate) -> Coordinate:
        # first move horizontally, then vertically
        curr_block = copy.copy(self.seed)
        while curr_block != goal:
            if curr_block not in self.b_blocks and curr_block not in self.s_blocks:
                return curr_block
            if curr_block.x < goal.x+1:
                curr_block += Right
            elif curr_block.y < goal.y:
                curr_block += Down

        raise ValueError(f'No valid block, last block checked {curr_block}')

        # path = self.get_path_to(start, goal, False)
        # for path_coord in path:
        #     if path_coord not in self.s_blocks:
        #         return path_coord
        # raise ValueError('already a path there')

    def get_path_to(self, start: Coordinate, goal: Coordinate, only_scaffold=True,
                    avoid_cache=True) -> List[Coordinate]:

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
                    valid_block = neighbor not in invalid_blocks and \
                        (neighbor in self.s_blocks or not only_scaffold)
                    cache_check = neighbor != self.cache if avoid_cache else True

                    search_tuple = SearchTuple(neighbor, new_path)
                    if valid_coordinate and neighbor not in explored:
                        if valid_block and cache_check:
                            neighbors.add(search_tuple)
                        explored.add(search_tuple)

    # TODO: Test
    def neighbor_coord_is_reachable(self, start: Coordinate, goal: Coordinate,
                                    only_scaffold=True, include_cache=True):
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
                for neighbor in new_neighbors:
                    valid_coordinate = neighbor.x >= 0 and neighbor.y >= 0
                    valid_block = neighbor in valid_blocks

                    if valid_coordinate and neighbor not in explored:
                        if valid_block:
                            neighbors.add(neighbor)
                        explored.add(neighbor)

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
            elif block_instruction is ScaffoldInstruction.DRIVE_UTURN:
                robot.turn('left')
                robot.turn('left')
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
        if self.goal_stack[-1].type is GoalType.PICK_SCAFFOLD:
            wanted_block = HeldBlock.SCAFFOLD
        else:
            wanted_block = HeldBlock.BUILD

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

        if block_coord in self.b_blocks or block_coord in self.s_blocks:
            raise LookupError('Block already present')

        if robot.held_block is HeldBlock.BUILD:
            self.b_blocks[block_coord] = BuildingBlockState()
        elif robot.held_block is HeldBlock.SCAFFOLD:
            self.s_blocks[block_coord] = ScaffoldState()

        robot.held_block = HeldBlock.NONE

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
        # assumtions:
        #   seed is at (0,0) and all block coords >=0
        #   only picks up blocks from the seed
        #
        #   always places build blocks to the west
        #   always places scaffolding blocks to the east or south
        #
        #   three turns total at most: at start, in path, at goal
        #
        #   if not on scaffold row, can return by going north
        #   if not on scaffold column can return by going east
        next_goal = self.goal_stack[-1]
        g_coord = next_goal.coord
        robot_coord, robot = self.get_single_robot()
        working_dir = robot.direction
        for _, block in self.s_blocks.items():
            block.instruction = ScaffoldInstruction.NONE

        standing_block: ScaffoldState = self.s_blocks[robot_coord]

        if next_goal.type == GoalType.PICK_BUILD_BLOCK or \
                next_goal.type == GoalType.PICK_SCAFFOLD:

            path_block: ScaffoldState = self.s_blocks[Coordinate(robot_coord.x, 0)]
            goal_block: ScaffoldState = self.s_blocks[Coordinate(0, 0)]

            if robot_coord.y != 0:
                standing_block.instruction = \
                    SimulationState.get_drive_instruction(working_dir, Dir.NORTH)
                working_dir = Dir.NORTH

            if robot_coord.x != 0:
                path_block.instruction = \
                    SimulationState.get_drive_instruction(working_dir, Dir.WEST)
                working_dir = Dir.WEST

            goal_block.instruction = \
                SimulationState.get_pick_instruction(working_dir, Dir.SOUTH)

        elif next_goal.type == GoalType.PLACE_BUILD_BLOCK:
            path_block: ScaffoldState = self.s_blocks[Coordinate(g_coord.x+1, 0)]
            goal_block: ScaffoldState = self.s_blocks[Coordinate(g_coord.x+1, g_coord.y)]

            if robot_coord.x != g_coord.x+1:
                standing_block.instruction = \
                    SimulationState.get_drive_instruction(working_dir, Dir.EAST)
                working_dir = Dir.EAST

            if robot_coord.y != g_coord.y:
                path_block.instruction = \
                    SimulationState.get_drive_instruction(working_dir, Dir.SOUTH)
                working_dir = Dir.SOUTH

            goal_block.instruction = \
                SimulationState.get_drop_instruction(working_dir, Dir.WEST)

        elif next_goal.type == GoalType.PLACE_SCAFFOLD:

            if g_coord.y == 0:
                goal_block: ScaffoldState = self.s_blocks[Coordinate(g_coord.x-1, 0)]

                if robot_coord.x != g_coord.x-1:
                    standing_block.instruction = \
                        SimulationState.get_drive_instruction(working_dir, Dir.EAST)
                    working_dir = Dir.EAST

                goal_block.instruction = self.get_drop_instruction(working_dir, Dir.EAST)

            else:
                path_block: ScaffoldState = self.s_blocks[Coordinate(g_coord.x, 0)]
                goal_block: ScaffoldState = self.s_blocks[Coordinate(g_coord.x, g_coord.y-1)]

                if robot_coord.x != g_coord.x:
                    standing_block.instruction = \
                        SimulationState.get_drive_instruction(working_dir, Dir.EAST)
                    working_dir = Dir.EAST

                if robot_coord.y != g_coord.y -1:
                    path_block.instruction = \
                        SimulationState.get_drive_instruction(working_dir, Dir.SOUTH)
                    working_dir = Dir.SOUTH

                goal_block.instruction = \
                    SimulationState.get_drop_instruction(working_dir, Dir.SOUTH)

    @staticmethod
    def get_drive_instruction(curr_dir: Dir, desired_dir: Dir) \
            -> ScaffoldInstruction:
        count = 0
        working_dir = curr_dir
        while working_dir != desired_dir:
            working_dir = working_dir.left()
            count += 1

        if count == 0:
            return ScaffoldInstruction.NONE
        elif count == 1:
            return ScaffoldInstruction.DRIVE_LEFT
        elif count == 2:
            return ScaffoldInstruction.DRIVE_UTURN
        elif count == 3:
            return ScaffoldInstruction.DRIVE_RIGHT

        raise Exception('Should not need to turn left more than 3 times')

    @staticmethod
    def get_pick_instruction(curr_dir: Dir, desired_dir: Dir) \
            -> ScaffoldInstruction:
        count = 0
        working_dir = curr_dir
        while working_dir != desired_dir:
            working_dir = working_dir.left()
            count += 1

        if count == 0:
            return ScaffoldInstruction.PICK_FORWARD
        elif count == 1:
            return ScaffoldInstruction.PICK_LEFT
        elif count == 3:
            return ScaffoldInstruction.PICK_RIGHT

        raise Exception('Should not need to turn left  2 times or more than 3 times')

    @staticmethod
    def get_drop_instruction(curr_dir: Dir, desired_dir: Dir) \
            -> ScaffoldInstruction:
        count = 0
        working_dir = curr_dir
        while working_dir != desired_dir:
            working_dir = working_dir.left()
            count += 1

        if count == 0:
            return ScaffoldInstruction.DROP_FORWARD
        elif count == 1:
            return ScaffoldInstruction.DROP_LEFT
        elif count == 3:
            return ScaffoldInstruction.DROP_RIGHT

        raise Exception('Should not need to turn left  2 times or more than 3 times')


class SimulationStateList:
    def __init__(self, initial_state: SimulationState = SimulationState()):
        self._working_state: SimulationState = initial_state
        self.states: List[SimulationState] = [copy.deepcopy(self._working_state)]

    @staticmethod
    def create_with_goal_structure(goal):
        initial_state = SimulationState.create_with_target_structure(goal)
        return SimulationStateList(initial_state)

    @staticmethod
    def create_with_empty_states(num_states: int = 1):
        initial_state = SimulationState()
        states = SimulationStateList(initial_state)
        for _ in range(num_states - 1):
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
