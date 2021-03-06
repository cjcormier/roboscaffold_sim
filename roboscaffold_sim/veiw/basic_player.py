import tkinter as tk

from roboscaffold_sim.simulators.basic_simulation_list import BasicSimulationList
from roboscaffold_sim.simulators.basic_simulator import BasicSimulation
from roboscaffold_sim.veiw.board import Board
from roboscaffold_sim.veiw.state_controls import StateControls


class BasicPlayer(tk.Frame):
    def __init__(self, parent, starting_state: BasicSimulation, back_context=None, back_name='Back', load_to=1000,
                 *args, **kwargs) -> None:
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.winfo_toplevel().title("RoboScaffold Sim")

        self.states = BasicSimulationList(starting_state)
        self.states.update_loop(load_to-1)

        self.board = Board(self)
        self.board.grid(row=0, column=0, rowspan=4)
        self.board.draw_grid()

        if back_context is not None:
            self.back_context = back_context
            self.create_button = tk.Button(self, text=back_name, command=self.back)
            self.create_button.grid(row=0, column=1, sticky='we')

        self.stat_text = tk.StringVar()
        self.stat_label = tk.Label(self, textvariable=self.stat_text)
        self.stat_label.grid(row=1, column=1, sticky='w')
        self.update_statistics()

        self.state_controls = StateControls(self,
                                            updater=self.get_updater(),
                                            loader=self.get_loader()
                                            )
        self.state_controls.grid(row=2, column=1, sticky="s")

        self.save_frame = tk.Frame(self)
        self.save_frame.grid(row=3, column=1)
        self.save_btn = tk.Button(self.save_frame, text='save', command=self.save)
        self.save_btn.grid(row=0, column=0)
        self.save_label = tk.Label(self.save_frame, text='file name')
        self.save_label.grid(row=1, column=0, padx=1)
        self.save_text = tk.Text(self.save_frame, width=30, height=1)
        self.save_text.grid(row=1, column=1)

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
            self.update_statistics()
        return fun

    def update_statistics(self):
        analysis = self.states.analyze()
        text = f'Overall Statistics: \n' \
               f'Scaffolding used: {analysis[0]}\n' \
               f'Robot updates: {self.states.robot_updates}\n' \
               f'Scaffolding placements: {self.states.scaffold_placements}\n' \
               f'Block placements: {self.states.build_placements}\n' \
               f'Scaffolding update: {self.states.block_updates}'
        self.stat_text.set(text)

    def force_update(self):
        self.board.draw_sim(self.states.states[self.state_controls.current_state-1])

    def save(self):
        file_name = self.save_text.get('1.0', 'end').strip('\n')
        with open(file_name, 'w') as file:
            self.states.save(file)

    def back(self):
        target = self.states.states[0].sim_state.target_structure
        creator = self.back_context(self.winfo_toplevel(), target=target)
        creator.grid()
        creator.winfo_toplevel().title("RoboScaffold Sim")
        self.destroy()