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

    @staticmethod
    def target_sort_key_tuple(coord) -> Tuple[int, ...]:
        on_spine = coord.y == 0
        spine_sort = -coord.x if on_spine else 0
        reach_sign = 1 if coord.y > 0 else -1
        return on_spine, spine_sort, coord.x, reach_sign, -abs(coord.y)

    @staticmethod
    def configure_target(target: CoordinateList, allow_offset: bool = True) \
            -> CoordinateList:
        if allow_offset:
            min_x = min(coord.x for coord in target)
            min_y = min(coord.y for coord in target)
            max_y = max(coord.y for coord in target)
            offset = Coordinate(1 - min_x, -int(round((max_y - min_y)/2)))

            target = [coord + offset for coord in target]

        target.sort(key=OffsetSpineStrat.target_sort_key_tuple)
        return target
