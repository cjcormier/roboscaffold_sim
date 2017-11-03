from roboscaffold_sim.coordinate import Coordinate
import time

from roboscaffold_sim.errors import TargetError
from roboscaffold_sim.simulators.basic_simulation_analysis import BasicSimulationAnalysis
from roboscaffold_sim.simulators.basic_strategies.centroid_offset_spine import \
    CentroidOffsetSpineStrat
from roboscaffold_sim.simulators.basic_strategies.offset_spine import OffsetSpineStrat
from roboscaffold_sim.simulators.basic_strategies.spine_strat import SpineStrat


def max_structs(dimension):
    inner_dim = dimension - 1
    outer_size = 2**(dimension**2)
    inner_size = 2**(inner_dim**2)

    max_s= outer_size - inner_size
    return max_s


def create_struct(dimension, n):
    struct = list()
    add_inner_struct(dimension, n % (2 ** (dimension ** 2)), struct)
    add_outer_struct(dimension, n // (2 ** (dimension ** 2)), struct)
    return struct


def add_inner_struct(dimension, n, struct):
    for y in range(dimension):
        for x in range(dimension):
            if n % 2:
                struct.append(Coordinate(x, y))
            n //= 2
            if n == 0:
                return
            elif n < 0:
                raise Exception('n should always be positive')
    raise Exception('n should be 0 and function should have returned by now')


def add_outer_struct(dimension, n, struct):
    for x in range(dimension-1):
        if n % 2:
            struct.append(Coordinate(x+1, 0))
        n //= 2
        if n == 0:
            break
        elif n < 0:
            raise Exception('n should always be positive')
    for y in range(dimension-1):
        if n % 2:
            struct.append(Coordinate(0, y+1))
        n //= 2
        if n == 0:
            break
        elif n < 0:
            raise Exception('n should always be positive')
    if n not in [0, 1]:
        raise Exception('n should be 0 or 1')
    elif n:
        struct.append(Coordinate(0, 0))


if __name__ == '__main__':
    dimension = 4
    max_s = max_structs(dimension)
    print(max_s)
    start_time = time.time()

    exceptions = 0
    j = 0
    with open(f'{dimension}_grid_result.csv', 'w') as file:
        file.write('index,spine scaffolding,spine time,offset scaffolding,offset time,'
                   'centroid scaffolding,centroid time\n')
        while j < max_s:
            j += 1
            struct = create_struct(dimension, j)
            try:
                results_spine = BasicSimulationAnalysis.analyze_sim(struct, SpineStrat)
                results_offset = BasicSimulationAnalysis.analyze_sim(struct, OffsetSpineStrat)
                results_centroid = BasicSimulationAnalysis.analyze_sim(struct, CentroidOffsetSpineStrat)

                file.write(f'{j},{results_spine[0]},{results_spine[1]},'
                           f'{results_offset[0]},{results_offset[1]},'
                           f'{results_centroid[0]},{results_centroid[1]}\n')

            except TargetError as e:
                exceptions += 1
            if j % 10000 == 0:
                print(f'{(j/max_s):.2%} {j-exceptions}/{j} {time.time()-start_time:.0f}s')
    end_time = time.time()
    print(f'{end_time-start_time:.0f}s')
