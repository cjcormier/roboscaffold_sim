from typing import Tuple

from roboscaffold_sim.coordinate import CoordinateList, Coordinate
from roboscaffold_sim.direction import Direction
from roboscaffold_sim.simulators.basic_strategies.centroid_offset_spine import CentroidOffsetSpineStrat
from roboscaffold_sim.simulators.basic_strategies.offset_spine import OffsetSpineStrat
from roboscaffold_sim.state.simulation_state import SimulationState


Dir = Direction


class CentroidFlipSpineStrat(CentroidOffsetSpineStrat):
    def __init__(self, sim_state: SimulationState) -> None:
        OffsetSpineStrat.__init__(self, sim_state)
        self.min_y = min(coord.y for coord in sim_state.target_structure)
        self.min_x = min(coord.x for coord in sim_state.target_structure)

    @staticmethod
    def target_sort_key_tuple(coord) -> Tuple[int, ...]:
        on_spine = coord.y == 0
        spine_sort = coord.x if on_spine else 0
        reach_sign = 1 if coord.y > 0 else -1
        return on_spine, spine_sort, -coord.x, reach_sign, -abs(coord.y)

    @staticmethod
    def configure_target(target: CoordinateList, allow_offset: bool = True) \
            -> CoordinateList:
        if allow_offset:
            target = [coord.rotate_180() for coord in target]

            min_x = min(coord.x for coord in target)
            centroid_y = sum(coord.y for coord in target) / len(target)
            centroid_y = int(centroid_y-0.5)
            offset = Coordinate(1-min_x, -centroid_y)

            target = [coord + offset for coord in target]

        target.sort(key=OffsetSpineStrat.target_sort_key_tuple)
        return target
