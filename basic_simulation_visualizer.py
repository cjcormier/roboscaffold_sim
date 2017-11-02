import tkinter as tk

from roboscaffold_sim.Structures.basic_structures import structures
from roboscaffold_sim.simulators.basic_simulator import BasicSimulation
from roboscaffold_sim.veiw.basic_player import BasicPlayer
import argparse


def use_basic_structure(args):
    sim = BasicSimulation.create_with_target_structure(structures[args.structure])

    root = tk.Tk()
    player = BasicPlayer(root, sim)
    player.grid()
    root.mainloop()


parser = argparse.ArgumentParser(description='Basic simulation player.')

creation_parser = parser.add_subparsers(help='How to create the target structure')

python_parser = creation_parser.add_parser('basic', help='Use a basic python structure')
python_parser.add_argument('structure', type=str,
                           choices=['column', 'square', 'house', 'lip'],
                           help='Structure to use')
python_parser.set_defaults(func=use_basic_structure)


string_parser = creation_parser.add_parser('string', help='Create structure from string, not currently implemented')


csv_parser = creation_parser.add_parser('csv', help='Create structure from csv, not currently implemented')


args = parser.parse_args()
args.func(args)
