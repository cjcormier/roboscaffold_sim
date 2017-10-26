import tkinter as tk

from roboscaffold_sim.state.simulation_state import SimulationState, SimulationStateList
from roboscaffold_sim.veiw.board import Board
from roboscaffold_sim.veiw.state_controls import StateControls


class BasicPlayer(tk.Frame):
    def __init__(self, parent, starting_state=SimulationState(), load_to=1000,
                 *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.states = SimulationStateList(starting_state)
        self.states.update_loop(load_to-1)

        self.board = Board(parent)
        self.board.grid(row=0, column=0, rowspan=4)
        self.board.draw_grid()

        self.state_controls = StateControls(parent,
                                            updater=self.update_canvas()
                                            )
        self.state_controls.grid(row=2, column=1, sticky="s")

        self.board.draw_sim(self.states.states[0])
        self.state_controls.max_state = len(self.states.states)

    def update_canvas(self):
        print('passing fun')

        def fun(frame):
            self.board.draw_sim(self.states.states[frame])

        return fun

    def force_update(self):
        self.board.draw_sim(self.states.states[self.state_controls.current_state-1])
