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


target_structure = [
    Coordinate(1, 4),
    Coordinate(1, 5),
    Coordinate(1, 6),
    Coordinate(1, 7),
    Coordinate(1, 8),
    Coordinate(1, 9),
    Coordinate(2, 9),
    Coordinate(3, 9),
    Coordinate(4, 9),
    Coordinate(5, 9),
    Coordinate(6, 9),
    Coordinate(6, 8),
    Coordinate(6, 7),
    Coordinate(6, 6),
    Coordinate(6, 5),
    Coordinate(6, 4),
    Coordinate(5, 4),
    Coordinate(4, 4),
    Coordinate(3, 4),
    Coordinate(2, 4),

    Coordinate(1, 3),
    Coordinate(2, 3),
    Coordinate(2, 2),
    Coordinate(3, 2),
    Coordinate(3, 1),
    Coordinate(4, 1),
    Coordinate(4, 2),
    Coordinate(5, 2),
    Coordinate(5, 3),
    Coordinate(6, 3),

]

sim = BasicSimulation.create_with_target_structure(target_structure)

root = tk.Tk()
player = BasicPlayer(root, sim)
player.grid()
root.mainloop()
