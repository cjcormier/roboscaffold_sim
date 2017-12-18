from typing import Optional, Tuple

import copy

from roboscaffold_sim.coordinate import Coordinate, Right, Up, Left, Down, CoordinateList
from roboscaffold_sim.direction import Direction as Dir
from roboscaffold_sim.errors import GoalError
from roboscaffold_sim.goal_type import GoalType as GType
from roboscaffold_sim.simulators.basic_strategies.basic_strategy import \
    BasicStrategy
from roboscaffold_sim.state.builder_state import BuilderState, HeldBlock
from roboscaffold_sim.state.scaffolding_state import SInstruction, ScaffoldState
from roboscaffold_sim.state.simulation_state import SimulationState, Goal


class SpineStrat(BasicStrategy):
    def __init__(self, sim_state: SimulationState) -> None:
        BasicStrategy.__init__(self, sim_state)

        self.seed: Coordinate = Coordinate(0, 0)
        self.cache: Coordinate = Coordinate(0, 1)
        self.goal_stack = list()

    @staticmethod
    def reach_check(b_coord: Coordinate, h_coord: Coordinate) -> bool:
        diff_columns = b_coord.x != h_coord.x and (b_coord.y or b_coord.x > h_coord.x)

        same_side = (b_coord.y > 0 and h_coord.y > 0) or (b_coord.y < 0 and h_coord.y < 0)
        further = abs(b_coord.y) > abs(h_coord.y)
        same_column = b_coord.x == h_coord.x and (further if same_side else True)

        return diff_columns or same_column

    @staticmethod
    def reach_compare(reach: Coordinate, other: Coordinate) -> bool:
        return other.x > reach.x or (other.x == reach.x and abs(other.y) > abs(reach.y))

    @staticmethod
    def configure_target(target: CoordinateList, allow_offset: bool=True) \
            -> CoordinateList:
        target.sort(key=lambda coord: (coord.x, -coord.y))
        if allow_offset:
            min_x = min(coord.x for coord in target)
            min_y = min(coord.y for coord in target)
            offset = Coordinate(1-min_x, 1-min_y)

            target = [coord + offset for coord in target]
        return target

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
        if len(self.sim_state.target_structure) == 0:
            return False

        if self.check_is_finished():
            return False

        next_goal = self.goal_stack[-1]
        if next_goal.type.is_pick() and robot.block is not HeldBlock.NONE:
            raise GoalError('Holding block when next goal is picking a block')

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
            raise GoalError('Held block does not match next goal')
        return True

    def get_needed_block_goal(self, next_goal: Goal) -> Tuple[Goal, bool]:
        if next_goal.type is GType.PLACE_SCAFFOLD:
            return self.find_usable_scaffold(), False
        else:
            if next_goal.coord in self.sim_state.s_blocks:
                return self.app_remove_blockage_goal(next_goal.coord), True
            else:
                p_type = GType.PICK_BUILD_BLOCK
                self.sim_state.b_blocks.add(self.cache)
                return Goal(self.cache, p_type, self.seed, Dir.SOUTH), False

    def check_is_finished(self)-> bool:
        if len(self.goal_stack) == 0:
            struct_coord = self.get_next_unfinished_block()
            if struct_coord is None:
                self.finished = True
                return True
            else:
                h_coord = struct_coord + (Right if struct_coord.y else Left)
                dir = Dir.WEST if struct_coord.y else Dir.EAST
                new_goal = Goal(struct_coord, GType.PLACE_BUILD_BLOCK, h_coord, dir)
                self.goal_stack = [new_goal]
        return False

    def get_bridge_goal(self, next_goal: Goal) -> Goal:
        next_needed_coord = self.get_next_needed_block(next_goal.h_coord)
        if next_needed_coord.y == 0:
            h_coord = next_needed_coord + Left
            p_dir = Dir.EAST
        else:
            p_dir = Dir.SOUTH if next_goal.coord.y > 0 else Dir.NORTH
            h_coord = next_needed_coord + (Up if next_goal.coord.y > 0 else Down)
        return Goal(next_needed_coord, GType.PLACE_SCAFFOLD, h_coord, p_dir)

    def find_usable_scaffold(self) -> Goal:
        p_type = GType.PICK_SCAFFOLD
        unneeded_s_blocks = self.get_next_unneeded_block()
        if unneeded_s_blocks:
            coord_offset = Up if unneeded_s_blocks.y > 0 else Down if unneeded_s_blocks.y else Left
            p_dir = Dir.SOUTH if unneeded_s_blocks.y > 0 else Dir.NORTH if unneeded_s_blocks.y else Dir.EAST
            h_coord = unneeded_s_blocks + coord_offset
            return Goal(unneeded_s_blocks, p_type, h_coord, p_dir)
        else:
            self.sim_state.s_blocks[self.cache] = ScaffoldState()
            return Goal(self.cache, p_type, self.seed, Dir.SOUTH)

    def app_remove_blockage_goal(self, goal_coord: Coordinate) -> Goal:
        p_type = GType.PLACE_SCAFFOLD
        if goal_coord.y != 0:
            extend_spine = Right
            while extend_spine in self.sim_state.s_blocks:
                extend_spine += Right
            h_coord = extend_spine + Left
            return Goal(extend_spine, p_type, h_coord, Dir.EAST)
        else:
            return Goal(self.cache, p_type, self.seed, Dir.SOUTH)

    def get_next_needed_block(self, goal: Coordinate) -> Coordinate:
        # first move horizontally, then vertically
        curr_block = copy.copy(self.seed)
        sim_state = self.sim_state
        while curr_block != goal:
            if not (curr_block in sim_state.b_blocks or curr_block in sim_state.s_blocks):
                return curr_block
            if curr_block.x < goal.x:
                curr_block += Right
            elif curr_block.y < goal.y:
                curr_block += Down
            elif curr_block.y > goal.y:
                curr_block += Up

        if not (curr_block in sim_state.b_blocks or curr_block in sim_state.s_blocks):
            return curr_block

        raise GoalError(f'No valid block, last block checked {curr_block}')

    def get_next_unneeded_block(self) -> Optional[Coordinate]:
        reach = None
        spine = None
        h_coord = self.goal_stack[0].h_coord
        for b_coord, block in self.sim_state.s_blocks.items():
            if b_coord.y != 0 and self.reach_check(b_coord, h_coord):
                if not reach or self.reach_compare(reach, b_coord):
                    reach = b_coord
            elif b_coord.x > h_coord.x:
                if not spine or b_coord.x > spine.x:
                    spine = b_coord

        return reach if reach else spine

    def coord_is_reachable(self, start: Coordinate, goal: Coordinate) -> bool:
        work_coord = Coordinate(start.x, start.y)

        while work_coord.x != goal.x:
            while work_coord.y != 0:
                work_coord += Up if work_coord.y > 0 else Down
                if work_coord not in self.sim_state.s_blocks:
                    return False
            work_coord += Right if work_coord.x < goal.x else Left
            if work_coord not in self.sim_state.s_blocks:
                return False

        while work_coord.y != goal.y:
            work_coord += Down if work_coord.y < goal.y else Up
            if work_coord not in self.sim_state.s_blocks:
                return False

        return True

    def update_scaffolding(self, r_coord: Coordinate, robot: BuilderState):
        next_goal = self.goal_stack[-1]
        h_coord = next_goal.h_coord

        for b_coord, block in self.sim_state.s_blocks.items():
            block.instruction = SInstruction.NONE

        work_dir, work_y = self.update_start_on_blocks(r_coord, h_coord, robot.direction)
        work_dir = self.update_off_block(h_coord, work_dir, work_y)
        self.update_goal_block(next_goal, h_coord, work_dir)

    def update_start_on_blocks(self, robo_coord: Coordinate,
                               h_coord: Coordinate, work_dir: Dir) -> (Dir, int):

        start_block = self.sim_state.s_blocks[robo_coord]
        on_spine_block = self.sim_state.s_blocks[Coordinate(robo_coord.x, 0)]

        if robo_coord.x != h_coord.x:
            if robo_coord.y != 0:
                dir = Dir.NORTH if robo_coord.y > 0 else Dir.SOUTH
                work_dir = start_block.set_drive_instr(work_dir, dir)

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

        off_spine_block: ScaffoldState = self.sim_state.s_blocks[Coordinate(h_coord.x, 0)]
        if work_y != h_coord.y != 0:
            dir = Dir.SOUTH if h_coord.y > 0 else Dir.NORTH
            work_dir = off_spine_block.set_drive_instr(work_dir, dir)
        return work_dir

    def update_goal_block(self, next_goal: Goal, h_coord: Coordinate, work_dir: Dir) -> None:
        goal_block: ScaffoldState = self.sim_state.s_blocks[h_coord]

        if next_goal.type.is_place():
            goal_block.set_drop_instr(work_dir, next_goal.dir)
        elif next_goal.type.is_pick():
            goal_block.set_pick_instr(work_dir, next_goal.dir)

    def get_next_unfinished_block(self) -> Optional[Coordinate]:
        for coord in self.sim_state.target_structure:
            if coord not in self.sim_state.b_blocks:
                return coord
        return None