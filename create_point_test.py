import tkinter as tk

from roboscaffold_sim.coordinate import Coordinate
from roboscaffold_sim.simulators.basic_simulator import BasicSimulation
from roboscaffold_sim.veiw.basic_player import BasicPlayer

i = 0


def get_next_coord() -> Coordinate:
    global i
    next_coord = Coordinate(i % 10, i // 10)
    i += 1
    return next_coord


target_structure = [Coordinate(5, 5)]
sim = BasicSimulation.create_with_target_structure(target_structure)

root = tk.Tk()
player = BasicPlayer(root, sim, load_to=100)
player.grid()
root.mainloop()
