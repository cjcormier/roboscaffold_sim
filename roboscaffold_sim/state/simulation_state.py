import copy
import traceback
from typing import Dict, List, NamedTuple, Optional, TypeVar, Tuple, Set

from roboscaffold_sim.coordinate import Coordinate, CoordinateList, CoordinateSet, \
    Right, Down, Up, Left
from roboscaffold_sim.direction import Direction as Dir
from roboscaffold_sim.goal_type import GoalType
from roboscaffold_sim.state.scaffolding_state import ScaffoldState, ScaffoldInstruction
from roboscaffold_sim.state.builder_state import BuilderState, HeldBlock

SBlocks = Dict[Coordinate, ScaffoldState]
BBlocks = Set[Coordinate]
Robots = Dict[Coordinate, BuilderState]

GType = GoalType


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
T = TypeVar('T', bound='SimulationState')


# TODO: make exceptions
# TODO: make interface/abstract class and sub classes
# TODO: function type hinting
# TODO: docstrings


class SimulationState:
    def __init__(self):
        self.finished: bool = False
        self.s_blocks: SBlocks = dict()
        self.b_blocks: BBlocks = set()
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
        robo_coord, robot = self.get_single_robot()
        goal_finished = self.check_for_finished_goals(robot)
        update_scaffolding = False
        if goal_finished:
            update_scaffolding = self.determine_new_goals(robo_coord, robot)

        if update_scaffolding:
            self.update_scaffolding(robo_coord, robot)
        else:
            if not self.finished:
                self.update_robots()

    def check_for_finished_goals(self, robot: BuilderState) -> bool:

        if len(self.goal_stack) == 0:
            return True

        g_coord = self.goal_stack[-1].coord
        g_type = self.goal_stack[-1].type
        held_block = robot.block
        place_s_done = g_type == GType.PLACE_SCAFFOLD and g_coord in self.s_blocks
        place_b_done = g_type == GType.PLACE_BUILD_BLOCK and g_coord in self.b_blocks
        pick_s_done = g_type == GType.PICK_SCAFFOLD and held_block is HeldBlock.SCAFFOLD
        pick_b_done = g_type == GType.PICK_BUILD_BLOCK and held_block is HeldBlock.BUILD

        if place_s_done or place_b_done or pick_s_done or pick_b_done:
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

    def determine_new_goals(self, robo_coord: Coordinate, robot: BuilderState) -> bool:
        """Determines the next goal if needed, returns if the scaffolding should update"""
        if len(self.target_structure) == 0:
            return False

        if self.check_is_finished():
            return False

        next_goal = self.goal_stack[-1]
        if next_goal.type.is_pick() and robot.block is not HeldBlock.NONE:
                raise ValueError('Holding block when next goal is picking a block')

        elif next_goal.type.is_place():
            return self.get_place_helper_goal(robo_coord, robot, next_goal)

        return True

    def get_place_helper_goal(self, robo_coord: Coordinate, robot: BuilderState,
                              next_goal: Goal) -> bool:
        if robot.not_holding_block():
            if self.coord_is_reachable(robo_coord, next_goal.h_coord):
                goal, recurse = self.get_needed_block_goal(next_goal)
            else:
                goal = self.get_bridge_goal(next_goal)
                recurse = True

            self.goal_stack.append(goal)
            if recurse:
                return self.get_place_helper_goal(robo_coord, robot, goal)

        elif robot.block != next_goal.get_block():
            raise ValueError('Held block does not match next goal')
        return True

    def get_bridge_goal(self, next_goal: Goal) -> Goal:
        next_needed_coord = self.get_next_needed_block(next_goal.coord)
        if next_needed_coord.y == 0:
            h_coord = next_needed_coord + Left
            p_dir = Dir.EAST
        else:
            h_coord = next_needed_coord + Up
            p_dir = Dir.SOUTH
        return Goal(next_needed_coord, GType.PLACE_SCAFFOLD, h_coord, p_dir)

    def get_needed_block_goal(self, next_goal: Goal) -> Tuple[Goal, bool]:
        if next_goal.type is GType.PLACE_SCAFFOLD:
            return self.find_usable_scaffold(), False
        else:
            if next_goal.coord in self.s_blocks:
                return self.app_remove_blockage_goal(), True
            else:
                p_type = GType.PICK_BUILD_BLOCK
                return Goal(self.cache, p_type, self.seed, Dir.SOUTH), False

    def app_remove_blockage_goal(self) -> Goal:
        p_type = GType.PLACE_SCAFFOLD
        extend_spine = Right
        while extend_spine in self.s_blocks:
            extend_spine += Right
        h_coord = extend_spine + Left
        return Goal(extend_spine, p_type, h_coord, Dir.EAST)

    def find_usable_scaffold(self) -> Goal:
        p_type = GType.PICK_SCAFFOLD
        unneeded_s_blocks = self.get_next_unneeded_block()
        if unneeded_s_blocks:
            coord_offset = Up if unneeded_s_blocks.y else Left
            p_dir = Dir.SOUTH if unneeded_s_blocks.y else Dir.EAST
            h_coord = unneeded_s_blocks + coord_offset
            return Goal(unneeded_s_blocks, p_type, h_coord, p_dir)
        else:
            return Goal(self.cache, p_type, self.seed, Dir.SOUTH)

    def get_next_unneeded_block(self) -> Optional[Coordinate]:
        reach = None
        spine = None
        h_coord = self.goal_stack[0].h_coord
        for b_coord, block in self.s_blocks.items():
            if b_coord.y > 0 and self.reach_check(b_coord, h_coord):
                if not reach or self.reach_compare(reach, b_coord):
                    reach = b_coord
            elif b_coord.x > h_coord.x:
                if not spine or b_coord.x > spine.x:
                    spine = b_coord

        return reach if reach else spine

    @staticmethod
    def reach_check(b_coord: Coordinate, h_coord: Coordinate) -> bool:
        return b_coord.x < h_coord.x or (b_coord.x == h_coord.x and b_coord.y > h_coord.y)

    @staticmethod
    def reach_compare(reach: Coordinate, other: Coordinate) -> bool:
        return other.x > reach.x or (other.x == reach.x and other.y > reach.y)

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

    def coord_is_reachable(self, start: Coordinate, goal: Coordinate) -> bool:
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
            self.b_blocks.remove(block_coord)
        elif block_coord == self.cache:
            pass
        else:
            raise LookupError("Invalid block found and not pointed at seed ")

        robot.block = wanted_block

    def drop(self, robo_coord: Coordinate, robot: BuilderState):
        block_coord = robo_coord.get_coord_in_direction(robot.direction)
        if robot.block is HeldBlock.NONE:
            raise ValueError('Cannot drop NONE Block')

        if block_coord in self.b_blocks or block_coord in self.s_blocks:
            raise LookupError('Block already present')

        if robot.block is HeldBlock.BUILD:
            self.b_blocks.add(block_coord)
        elif robot.block is HeldBlock.SCAFFOLD:
            self.s_blocks[block_coord] = ScaffoldState()

        robot.block = HeldBlock.NONE

    def move_robot(self, robo_coord: Coordinate, robot: BuilderState):
        new_coords = robo_coord.get_coord_in_direction(robot.direction)
        if new_coords in self.robots:
            raise ValueError('Robot in moving position')
        if new_coords not in self.s_blocks:
            raise ValueError('Robot is moving onto a space without scaffolding')

        del self.robots[robo_coord]
        self.robots[new_coords] = robot

    def update_scaffolding(self, r_coord: Coordinate, robot: BuilderState):
        next_goal = self.goal_stack[-1]
        h_coord = next_goal.h_coord

        for b_coord, block in self.s_blocks.items():
            block.instruction = ScaffoldInstruction.NONE

        work_dir, work_y = self.update_start_on_blocks(r_coord, h_coord, robot.direction)
        work_dir = self.update_off_block(h_coord, work_dir, work_y)
        self.update_goal_block(next_goal, h_coord, work_dir)

    def update_start_on_blocks(self, robo_coord: Coordinate,
                               h_coord: Coordinate, work_dir: Dir) -> (Dir, int):

        start_block: ScaffoldState = self.s_blocks[robo_coord]
        on_spine_block: ScaffoldState = self.s_blocks[Coordinate(robo_coord.x, 0)]

        if robo_coord.x != h_coord.x:
            if robo_coord.y != 0:
                work_dir = start_block.set_drive_instr(work_dir, Dir.NORTH)

            move_dir = Dir.EAST if robo_coord.x < h_coord.x else Dir.WEST
            work_dir = on_spine_block.set_drive_instr(work_dir, move_dir)
            return work_dir, 0
        else:
            if robo_coord.y < h_coord.y:
                work_dir = start_block.set_drive_instr(work_dir, Dir.SOUTH)
                return work_dir, h_coord.y
            elif robo_coord.y > h_coord.y:
                work_dir = start_block.set_drive_instr(work_dir, Dir.NORTH)
                return work_dir, h_coord.y
        return work_dir, robo_coord.y

    def update_off_block(self, h_coord: Coordinate, work_dir: Dir, work_y: int) -> Dir:

        off_spine_block: ScaffoldState = self.s_blocks[Coordinate(h_coord.x, 0)]
        if work_y < h_coord.y != 0:
            work_dir = off_spine_block.set_drive_instr(work_dir, Dir.SOUTH)
        return work_dir

    def update_goal_block(self, next_goal: Goal, h_coord: Coordinate, work_dir: Dir):
        goal_block: ScaffoldState = self.s_blocks[h_coord]

        if next_goal.type.is_place():
            goal_block.set_drop_instr(work_dir, next_goal.dir)
        elif next_goal.type.is_pick():
            goal_block.set_pick_instr(work_dir, next_goal.dir)


class SimulationStateList:
    def __init__(self, initial_state: SimulationState = SimulationState()):
        self._working_state: SimulationState = initial_state
        self.states: List[SimulationState] = [copy.deepcopy(self._working_state)]

    @staticmethod
    def create_with_target_structure(target: CoordinateList):
        initial_state = SimulationState.create_with_target_structure(target)
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
