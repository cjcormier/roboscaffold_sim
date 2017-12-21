from roboscaffold_sim.coordinate import CoordinateList, Coordinate
from roboscaffold_sim.direction import Direction
from roboscaffold_sim.simulators.basic_strategies.offset_spine import OffsetSpineStrat
from roboscaffold_sim.state.simulation_state import SimulationState


Dir = Direction


class LongestSpineStrat(OffsetSpineStrat):
    def __init__(self, sim_state: SimulationState) -> None:
        OffsetSpineStrat.__init__(self, sim_state)

    @staticmethod
    def configure_target(target: CoordinateList, allow_offset: bool = True) \
            -> CoordinateList:
        if allow_offset:
            min_x = min(coord.x for coord in target)
            min_y = min(coord.y for coord in target)
            max_y = max(coord.y for coord in target)
            rows = [0]*(max_y-min_y+1)

            centroid_y = sum(coord.y for coord in target) / len(target)
            centroid_y = int(centroid_y+0.5)

            for coord in target:
                rows[coord.y-min_y] += 1

            row_indicies =[]
            row_value = 0
            for i, value in enumerate(rows):
                if value > row_value:
                    row_indicies.append(i+min_y)
                    row_value = value
                elif value == row_value:
                    row_indicies = [i+min_y]

            row_value = centroid_y - row_indicies[0]
            row = row_indicies[0]
            for curr_row in row_indicies[1:]:
                if centroid_y - curr_row < row_value:
                    row = curr_row
            offset = Coordinate(1 - min_x, -row)

            target = [coord + offset for coord in target]

        target.sort(key=OffsetSpineStrat.target_sort_key_tuple)
        return target
