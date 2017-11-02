import tkinter as tk

from roboscaffold_sim.Structures.basic_structures import square
from roboscaffold_sim.coordinate import Coordinate
from roboscaffold_sim.simulators.basic_simulator import BasicSimulation
from roboscaffold_sim.veiw.basic_player import BasicPlayer

i = 0


def get_next_coord() -> Coordinate:
    global i
    next_coord = Coordinate(i % 10, i // 10)
    i += 1
    return next_coord


sim = BasicSimulation.create_with_target_structure(square)

root = tk.Tk()
player = BasicPlayer(root, sim)
player.grid()
root.mainloop()
