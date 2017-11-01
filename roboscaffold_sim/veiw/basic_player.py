import tkinter as tk

from roboscaffold_sim.simulators.basic_simulation_list import BasicSimulationList
from roboscaffold_sim.simulators.basic_simulator import BasicSimulation
from roboscaffold_sim.veiw.board import Board
from roboscaffold_sim.veiw.state_controls import StateControls


class BasicPlayer(tk.Frame):
    def __init__(self, parent, starting_state: BasicSimulation, load_to=1000,
                 *args, **kwargs) -> None:
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.states = BasicSimulationList(starting_state)
        self.states.update_loop(load_to-1)

        self.board = Board(parent)
        self.board.grid(row=0, column=0, rowspan=4)
        self.board.draw_grid()

        self.state_controls = StateControls(parent,
                                            updater=self.get_updater(),
                                            loader=self.get_loader()
                                            )
        self.state_controls.grid(row=2, column=1, sticky="s")

        self.board.draw_sim(self.states.states[0])
        self.state_controls.max_state = len(self.states.states)
        self.state_controls.finished = self.states.states[-1].finished

    def get_updater(self):
        def fun(frame):
            self.board.draw_sim(self.states.states[frame])
        return fun

    def get_loader(self):
        def fun(to_load):
            self.states.update_loop(to_load)
            self.state_controls.finished = self.states.states[-1].finished
            self.state_controls.max_state = len(self.states.states)
        return fun

    def force_update(self):
        self.board.draw_sim(self.states.states[self.state_controls.current_state-1])
