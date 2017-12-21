from roboscaffold_sim.coordinate import Coordinate
import time

from roboscaffold_sim.errors import TargetError
from roboscaffold_sim.simulators.basic_simulation_analysis import BasicSimulationAnalysis
from roboscaffold_sim.simulators.basic_strategies.centroid_offset_spine import \
    CentroidOffsetSpineStrat
from roboscaffold_sim.simulators.basic_strategies.longest_spine import LongestSpineStrat
from roboscaffold_sim.simulators.basic_strategies.offset_spine import OffsetSpineStrat
from roboscaffold_sim.simulators.basic_strategies.spine_strat import SpineStrat


def max_structs(dimension):
    inner_dim = dimension - 1
    outer_size = 2**(dimension**2)
    inner_size = 2**(inner_dim**2)

    return outer_size - inner_size


def create_struct(dimension, n):
    structure = list()
    inner_size = 2**((dimension-1)**2)
    add_inner_struct(dimension, n % inner_size, structure)
    add_outer_struct(dimension, n // inner_size, structure)
    return structure


def add_inner_struct(dimension, n, structure):
    # print(f'inner {n}')
    for y in range(dimension-1):
        for x in range(dimension-1):
            if n % 2:
                structure.append(Coordinate(x + 1, y + 1))
            n //= 2
            if n == 0:
                return
            elif n < 0:
                raise Exception('n should always be positive')
    raise Exception(f'n should be 0 and function should have returned by now but is {n}')


def add_outer_struct(dimension, n, structure):
    # print(f'outer {n}')
    for x in range(dimension-1):
        if n % 2:
            # print(f'outer x hit {x+1} at {n}')
            structure.append(Coordinate(x + 1, 0))
        n //= 2
        if n == 0:
            break
        elif n < 0:
            raise Exception('n should always be positive')
    for y in range(dimension-1):
        if n % 2:
            # print(f'outer y hit {y+1} at {n}')
            structure.append(Coordinate(0, y + 1))
        n //= 2
        if n == 0:
            break
        elif n < 0:
            raise Exception('n should always be positive')
    if n not in [0, 1]:
        raise Exception('n should be 0 or 1')
    elif n:
        structure.append(Coordinate(0, 0))


if __name__ == '__main__':
    dim = 5
    max_s = max_structs(dim)
    print(max_s)
    start_time = time.time()

    exceptions = 0
    prev_time = 0
    j = 0
    with open(f'{dim}_grid_result.csv', 'w') as file:
        s = 0
        print_cycle = 50000
        c_r = [0]*4
        c_s = [0]*4
        while j < max_s:
            j += 1
            struct = create_struct(dim, j)
            try:
                spine = BasicSimulationAnalysis.analyze_sim(struct, SpineStrat)
                offset = BasicSimulationAnalysis.analyze_sim(struct, OffsetSpineStrat)
                centroid = BasicSimulationAnalysis.analyze_sim(struct, CentroidOffsetSpineStrat)
                longest = BasicSimulationAnalysis.analyze_sim(struct, LongestSpineStrat)

                results = [spine, offset, centroid, longest]
                min_r = min(results, key=lambda r: r[0])[0]
                min_s = min(results, key=lambda r: r[1])[1]

                for i in range(len(results)):
                    if results[i][0] == min_r:
                        c_r[i] += 1
                    if results[i][1] == min_s:
                        c_s[i] += 1

                s += 1
            except TargetError as e:
                exceptions += 1
            if j % print_cycle == 0:
                time_elapsed = time.time() - start_time
                percentage = j/max_s
                time_est = time_elapsed/percentage
                time_remaining = time_est-time_elapsed

                print(f'{percentage:.2%} {j-exceptions}/{j} {((j-exceptions)/j):.2%} '
                      f'{(s/print_cycle):.2%} {time_elapsed-prev_time:.0f}s {time_elapsed:.0f}s {int(time_est)}s '
                      f'{int(time_remaining)}s')
                prev_time = time_elapsed
                s = 0
    end_time = time.time()
    good_structs = j - exceptions
    print(f'successful structs: {j-good_structs}')
    print(f'robot_moves: '+'|'.join(f'{r}->{r/good_structs:.2%}' for r in c_r))
    print(f'scaffold updates: '+'|'.join(f'{s}->{s/good_structs:.2%}' for s in c_s))
    # print(f'check was true in  {c} cases -> {c/(j-exceptions):.2%} of the valid runs')
    print(f'{end_time-start_time:.0f}s {((j-exceptions)/j):.2%}')
