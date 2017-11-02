import tkinter as tk

from roboscaffold_sim.Structures.basic_structures import structures
from roboscaffold_sim.simulators.basic_simulator import BasicSimulation
from roboscaffold_sim.simulators.basic_strategies.centroid_offset_spine import \
    CentroidOffsetSpineStrat
from roboscaffold_sim.simulators.basic_strategies.offset_spine import OffsetSpineStrat
from roboscaffold_sim.simulators.basic_strategies.spine_strat import SpineStrat
from roboscaffold_sim.veiw.basic_player import BasicPlayer
import argparse


def use_basic_structure(args, strat):
    sim = BasicSimulation.create_with_target_structure(structures[args.structure], strat)

    root = tk.Tk()
    player = BasicPlayer(root, sim)
    player.grid()
    root.mainloop()


parser = argparse.ArgumentParser(description='Basic simulation player.')

parser.add_argument('strategy', type=str,
                    choices=['spine', 'offset_spine', 'centroid_spine'], nargs='?',
                    default='spine', help='The strategy to use.')

creation_parser = parser.add_subparsers(help='How to create the target structure')

python_parser = creation_parser.add_parser('basic', help='Use a basic python structure')
python_parser.add_argument('structure', type=str,
                           choices=['column', 'square', 'house', 'lip'],
                           help='Structure to use')
python_parser.set_defaults(create=use_basic_structure)


string_parser = creation_parser.add_parser('string', help='Create structure from string, not currently implemented')


csv_parser = creation_parser.add_parser('csv', help='Create structure from csv, not currently implemented')


if __name__ == '__main__':
    args = parser.parse_args()
    print(args)
    if args.strategy == 'spine':
        strat = SpineStrat
    elif args.strategy == 'offset_spine':
        strat = OffsetSpineStrat
    else:
        strat = CentroidOffsetSpineStrat

    args.create(args, strat)