from typing import Tuple

from roboscaffold_sim.coordinate import CoordinateList, Coordinate
from roboscaffold_sim.direction import Direction
from roboscaffold_sim.simulators.basic_strategies.spine_strat import SpineStrat
from roboscaffold_sim.state.scaffolding_state import ScaffoldState
from roboscaffold_sim.state.simulation_state import SimulationState


Dir = Direction


class OffsetSpineStrat(SpineStrat):
    def __init__(self, sim_state: SimulationState) -> None:
        SpineStrat.__init__(self, sim_state)
        self.min_y = min(coord.y for coord in sim_state.target_structure)

    @staticmethod
    def target_sort_key_tuple(coord) -> Tuple[int, int, int, int]:
        on_spine = coord.y == 0
        first_term = -coord.x if on_spine else 0
        return on_spine, first_term, coord.x, -coord.y

    @staticmethod
    def configure_target(target: CoordinateList, allow_offset: bool = True) \
            -> CoordinateList:
        if allow_offset:
            min_x = min(coord.x for coord in target)
            min_y = min(coord.y for coord in target)
            max_y = max(coord.y for coord in target)
            offset = Coordinate(1 - min_x, -(max_y - min_y)//2)

            target = [coord + offset for coord in target]

        target.sort(key=OffsetSpineStrat.target_sort_key_tuple)
        return target

    def update_off_block(self, h_coord: Coordinate, work_dir: Dir, work_y: int) -> Dir:

        off_spine_block: ScaffoldState = self.sim_state.s_blocks[Coordinate(h_coord.x, 0)]
        if work_y != h_coord.y != 0:
            dir = Dir.SOUTH if h_coord.y > 0 else Dir.NORTH
            work_dir = off_spine_block.set_drive_instr(work_dir, dir)
        return work_dir
