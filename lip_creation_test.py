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


target_structure = [
    Coordinate(5, 5),
    Coordinate(5, 4),
    Coordinate(5, 3),
    Coordinate(5, 2),
    Coordinate(5, 1),

    Coordinate(4, 5),
    Coordinate(4, 4),
    Coordinate(4, 3),
    Coordinate(4, 2),
    Coordinate(4, 1),

    Coordinate(3, 2),
    Coordinate(3, 1),

    Coordinate(2, 2),

    Coordinate(1, 5),
    Coordinate(1, 4),
    Coordinate(1, 3),
    Coordinate(1, 2),
    Coordinate(1, 1),

]
sim = SimulationState.create_with_target_structure(target_structure)

root = tk.Tk()
player = BasicPlayer(root, sim)
player.grid()
root.mainloop()
