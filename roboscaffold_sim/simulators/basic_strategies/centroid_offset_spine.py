from roboscaffold_sim.coordinate import CoordinateList, Coordinate
from roboscaffold_sim.direction import Direction
from roboscaffold_sim.simulators.basic_strategies.offset_spine import OffsetSpineStrat
from roboscaffold_sim.state.simulation_state import SimulationState


Dir = Direction


class CentroidOffsetSpineStrat(OffsetSpineStrat):
    def __init__(self, sim_state: SimulationState) -> None:
        OffsetSpineStrat.__init__(self, sim_state)

    @staticmethod
    def configure_target(target: CoordinateList, allow_offset: bool = True) \
            -> CoordinateList:
        if allow_offset:
            min_x = min(coord.x for coord in target)
            centroid_y = sum(coord.y for coord in target) / len(target)
            centroid_y = int(centroid_y+0.5)
            offset = Coordinate(1 - min_x, -centroid_y)

            target = [coord + offset for coord in target]

        target.sort(key=OffsetSpineStrat.target_sort_key_tuple)
        return target
