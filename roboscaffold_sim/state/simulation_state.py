import copy
import traceback
from enum import Enum, auto
from typing import Dict, List, NamedTuple, Optional, TypeVar, Tuple

from roboscaffold_sim.coordinate import Coordinate, CoordinateList, CoordinateSet, \
    Right, Down, Up, Left
from roboscaffold_sim.direction import Direction as Dir
from roboscaffold_sim.state.block_states import BuildingBlockState, ScaffoldState, \
    ScaffoldInstruction, get_drive_instr, get_drop_instr, get_pick_instr
from roboscaffold_sim.state.builder_state import BuilderState, HeldBlock

SBlocks = Dict[Coordinate, ScaffoldState]
BBlocks = Dict[Coordinate, BuildingBlockState]
Robots = Dict[Coordinate, BuilderState]


class GoalType(Enum):
    PLACE_BUILD_BLOCK = auto()
    PLACE_SCAFFOLD = auto()
    PICK_BUILD_BLOCK = auto()
    PICK_SCAFFOLD = auto()


GType = GoalType


class Goal(NamedTuple):
    coord: Coordinate
    type: GoalType
    h_coord: Coordinate
    dir: Dir

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
        sim.cache = Down
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
        goal_finished = self.check_for_finished_goals()
        update_scaffolding = False
        if goal_finished:
            update_scaffolding = self.get_new_goals()

        if update_scaffolding:
            self.update_scaffolding()
        else:
            if not self.finished:
                self.update_robots()

    def check_for_finished_goals(self):

        if len(self.goal_stack) == 0:
            return True

        curr_goal = self.goal_stack[-1]
        robo_coord, robot = self.get_single_robot()
        valid_place_scaffold = curr_goal.type == GType.PLACE_SCAFFOLD and \
            curr_goal.coord in self.s_blocks
        valid_place_block = curr_goal.type == GType.PLACE_BUILD_BLOCK and \
            curr_goal.coord in self.b_blocks
        valid_pick_scaffold = curr_goal.type == GType.PICK_SCAFFOLD and \
            robot.held_block is HeldBlock.SCAFFOLD
        valid_pick_block = curr_goal.type == GType.PICK_BUILD_BLOCK and \
            robot.held_block is HeldBlock.BUILD

        if valid_place_scaffold or valid_place_block or \
                valid_pick_scaffold or valid_pick_block:
            self.goal_stack = self.goal_stack[0:-1]
            return True

        return False

    def get_single_robot(self) -> Tuple[Coordinate, BuilderState]:
        if len(self.robots) != 1:
            ValueError('this method requires exactly one robot in the state')

        for coord, robot in self.robots.items():
            return coord, robot

    def check_is_finished(self)-> bool:
        if len(self.goal_stack) == 0:
            struct_coord = self.get_next_unfinished_block()
            if struct_coord is None:
                self.finished = True
                return True
            else:
                h_coord = struct_coord + Right
                new_goal = Goal(struct_coord, GType.PLACE_BUILD_BLOCK, h_coord, Dir.WEST)
                self.goal_stack = [new_goal]
        return False

    # TODO: clean up method
    def get_new_goals(self):
        """Determines the next goal if needed, returns if the scaffolding should update"""
        if len(self.target_structure) == 0:
            return False

        if self.check_is_finished():
            return False

        robo_coord, robot = self.get_single_robot()

        next_goal = self.goal_stack[-1]
        if next_goal.type in [GType.PICK_BUILD_BLOCK, GType.PICK_SCAFFOLD]:
            if robot.held_block is not HeldBlock.NONE:
                raise ValueError('Holding block when next goal is picking a block')
            else:
                return True

        elif next_goal.type is GType.PLACE_BUILD_BLOCK or GType.PLACE_SCAFFOLD:
            if self.compare_block_and_goal(robot.held_block, next_goal.type):
                return True
            elif robot.held_block is HeldBlock.NONE:
                if self.coord_is_reachable(robo_coord, next_goal.h_coord):
                    if next_goal.type is GType.PLACE_SCAFFOLD:
                        p_type = GType.PICK_SCAFFOLD
                        unneeded_s_blocks = self.get_next_unneeded_block()
                        if unneeded_s_blocks:
                            coord_offset = Up if unneeded_s_blocks.y else Left
                            p_dir = Dir.SOUTH if unneeded_s_blocks.y else Dir.EAST
                            h_coord = unneeded_s_blocks + coord_offset
                            goal = Goal(unneeded_s_blocks, p_type, h_coord, p_dir)
                        else:
                            goal = Goal(self.cache, p_type, self.seed, Dir.SOUTH)
                    else:
                        if next_goal.coord in self.s_blocks:
                            p_type = GType.PLACE_SCAFFOLD
                            extend_spine = Right
                            while extend_spine in self.s_blocks:
                                extend_spine += Right
                            h_coord = extend_spine + Left
                            goal = Goal(extend_spine, p_type, h_coord, Dir.EAST)
                            self.goal_stack.append(goal)
                            return self.get_new_goals()
                        else:
                            p_type = GType.PICK_BUILD_BLOCK
                            goal = Goal(self.cache, p_type, self.seed, Dir.SOUTH)
                    self.goal_stack.append(goal)
                    return True
                else:
                    next_needed_coord = self.get_next_needed_block(next_goal.coord)
                    if next_needed_coord.y == 0:
                        h_coord = next_needed_coord + Left
                        p_dir = Dir.EAST
                    else:
                        h_coord = next_needed_coord + Up
                        p_dir = Dir.SOUTH
                    self.goal_stack.append(
                        Goal(next_needed_coord, GType.PLACE_SCAFFOLD, h_coord, p_dir))
                    return self.get_new_goals()
            else:
                raise ValueError('Held block does not match next goal')

        return False

    def get_next_unneeded_block(self) -> Optional[Coordinate]:
        reach = None
        spine = None
        for b_coord, block in self.s_blocks.items():
            if b_coord.x < self.goal_stack[-1].h_coord.x and b_coord.y > 0:
                if not reach or b_coord.x <= reach.x or b_coord.y <= reach.y:
                    reach = b_coord
            elif b_coord.x > self.goal_stack[-1].h_coord.x:
                if not spine or b_coord.x > spine.x:
                    spine = b_coord

        return spine if spine else reach

    @staticmethod
    def compare_block_and_goal(block: HeldBlock, goal: GType) -> bool:
        if goal == GType.PICK_SCAFFOLD or goal == GType.PLACE_SCAFFOLD:
            return block is HeldBlock.SCAFFOLD
        else:
            return block is HeldBlock.BUILD

    def get_next_unfinished_block(self) -> Optional[Coordinate]:
        for coord in self.target_structure:
            if coord not in self.b_blocks:
                return coord
        return None

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

    def coord_is_reachable(self, start: Coordinate, goal: Coordinate):
        work_coord = Coordinate(start.x, start.y)

        while work_coord.x != goal.x:
            while work_coord.y != 0:
                work_coord += Up
                if work_coord not in self.s_blocks:
                    return False
            work_coord += Right if work_coord.x < goal.x else Left
            if work_coord not in self.s_blocks:
                return False

        while work_coord.y != goal.y:
            work_coord += Down if work_coord.y < goal.y else Up
            if work_coord not in self.s_blocks:
                return False

        return True

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
                self.pick(coord, robot, self.goal_stack[-1].type)
            elif block_instruction is ScaffoldInstruction.PICK_RIGHT:
                robot.turn('right')
                self.pick(coord, robot, self.goal_stack[-1].type)
            elif block_instruction is ScaffoldInstruction.PICK_FORWARD:
                self.pick(coord, robot, self.goal_stack[-1].type)
            elif block_instruction is ScaffoldInstruction.PICK_BACK:
                robot.turn('left')
                robot.turn('left')
                self.pick(coord, robot, self.goal_stack[-1].type)
            elif block_instruction is ScaffoldInstruction.DROP_LEFT:
                robot.turn('left')
                self.drop(coord, robot)
            elif block_instruction is ScaffoldInstruction.DROP_RIGHT:
                robot.turn('right')
                self.drop(coord, robot)
            elif block_instruction is ScaffoldInstruction.DROP_FORWARD:
                self.drop(coord, robot)

    def pick(self, robo_coord: Coordinate, robot: BuilderState, goal_type: GType):
        block_coord = robo_coord.get_coord_in_direction(robot.direction)
        if goal_type is GType.PICK_SCAFFOLD:
            wanted_block = HeldBlock.SCAFFOLD
        elif goal_type is GType.PICK_BUILD_BLOCK:
            wanted_block = HeldBlock.BUILD
        else:
            raise Exception('Invalid GType for picking')

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
        new_coords = robo_coord.get_coord_in_direction(robot.direction)
        if new_coords in self.robots:
            raise ValueError('Robot in moving position')
        if new_coords not in self.s_blocks:
            raise ValueError('Robot is moving onto a space without scaffolding')

        del self.robots[robo_coord]
        self.robots[new_coords] = robot

    def update_scaffolding(self):
        # assumtions:
        #
        #  always places build blocks to the west
        #  always places scaffolding blocks to the east or south
        #
        #  four turns total at most: at start, onto the spine, off the spine , at goal
        #   some of these will either be unneeded or be at the same block
        #
        #  if not on the spine, return by going north
        #  if not on scaffold column, return by going to the spine and moving horizontally
        next_goal = self.goal_stack[-1]
        h_coord = next_goal.h_coord
        robo_coord, robot = self.get_single_robot()

        working_dir = robot.direction
        working_y = robo_coord.y

        for b_coord, block in self.s_blocks.items():
            block.instruction = ScaffoldInstruction.NONE

        start_block: ScaffoldState = self.s_blocks[robo_coord]

        on_spine_coord: Coordinate = Coordinate(robo_coord.x, 0)
        on_spine_block: ScaffoldState = self.s_blocks[on_spine_coord]

        off_spine_coord: Coordinate = Coordinate(h_coord.x, 0)
        off_spine_block: ScaffoldState = self.s_blocks[off_spine_coord]

        goal_block: ScaffoldState = self.s_blocks[h_coord]

        if robo_coord.x != h_coord.x:
            if working_y != 0:
                start_block.instruction = get_drive_instr(working_dir, Dir.NORTH)
                working_dir = Dir.NORTH

            move_dir = Dir.EAST if robo_coord.x < h_coord.x else Dir.WEST
            on_spine_block.instruction = get_drive_instr(working_dir, move_dir)
            working_dir = move_dir
            working_y = 0
        else:
            if working_y < h_coord.y:
                start_block.instruction = get_drive_instr(working_dir, Dir.SOUTH)
                working_dir = Dir.SOUTH
                working_y = h_coord.y
            elif working_y > h_coord.y:
                start_block.instruction = get_drive_instr(working_dir, Dir.NORTH)
                working_dir = Dir.NORTH
                working_y = 0

        if working_y < h_coord.y != 0:
            off_spine_block.instruction = get_drive_instr(working_dir, Dir.SOUTH)
            working_dir = Dir.SOUTH

        if next_goal.type in [GType.PLACE_BUILD_BLOCK, GType.PLACE_SCAFFOLD]:
            goal_instruction = get_drop_instr(working_dir, next_goal.dir)
        elif next_goal.type in [GType.PICK_BUILD_BLOCK, GType.PICK_SCAFFOLD]:
            goal_instruction = get_pick_instr(working_dir, next_goal.dir)
        else:
            raise Exception('Invalid goal type')

        goal_block.instruction = goal_instruction


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
