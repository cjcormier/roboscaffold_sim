import tkinter as tk

from roboscaffold_sim.coordinate import Coordinate
from roboscaffold_sim.state.simulation_state import SimulationState
from roboscaffold_sim.veiw.basic_player import BasicPlayer

i = 0


def get_next_coord() -> Coordinate:
    global i
    next_coord = Coordinate(i % 10, i // 10)
    i += 1
    return next_coord


target_structure = [Coordinate(5, 5)]
sim = SimulationState.create_with_target_structure(target_structure)

root = tk.Tk()
player = BasicPlayer(root, sim, load_to=10)
player.grid()
root.mainloop()
