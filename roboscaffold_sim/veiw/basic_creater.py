import tkinter as tk

from comparison import create_struct
from roboscaffold_sim.simulators.basic_simulator import BasicSimulation
from roboscaffold_sim.structures.basic_structures import structures
from roboscaffold_sim.coordinate import CoordinateList, Coordinate
from roboscaffold_sim.simulators.basic_strategies.centroid_flip_spine import CentroidFlipSpineStrat
from roboscaffold_sim.simulators.basic_strategies.centroid_offset_spine import CentroidOffsetSpineStrat
from roboscaffold_sim.simulators.basic_strategies.offset_spine import OffsetSpineStrat
from roboscaffold_sim.simulators.basic_strategies.spine_strat import SpineStrat
from roboscaffold_sim.veiw.basic_player import BasicPlayer
from roboscaffold_sim.veiw.board import Board

strategies = {
    'spine': SpineStrat,
    'offset_spine': OffsetSpineStrat,
    'centroid_spine': CentroidOffsetSpineStrat,
    'centroid_flip_spine': CentroidFlipSpineStrat
}


class NumCreator(tk.Frame):
    def __init__(self, parent, struct_callback, *args, **kwargs) -> None:
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.callback = struct_callback

        self.dim_label = tk.Label(self, text='Dimension')
        self.dim_label.grid(row=0, column=0)

        self.dim_box = tk.Text(self, width=10, height=1)
        self.dim_box.grid(row=1, column=0)

        self.num_label = tk.Label(self, text='Value')
        self.num_label.grid(row=2, column=0)

        self.num_box = tk.Text(self, width=10, height=1)
        self.num_box.grid(row=3, column=0)

        self.num_button = tk.Button(self, text='From Number', command=self.pressed)
        self.num_button.grid(row=4, column=0)

    def pressed(self):
        dim = self.dim_box.get('1.0', 'end')
        num = self.num_box.get('1.0', 'end')
        try:
            dim = int(dim)
            num = int(num)
        except ValueError:
            print('invalid num')
        self.callback(create_struct(dim, num))


class TargetCreator(tk.Frame):
    def __init__(self, parent, set_struct_callback, struct_callback, *args, **kwargs) -> None:
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.struct_callback = set_struct_callback

        self.label = tk.Label(self, text='Create Target Structure')
        self.label.grid(row=0, column=0, sticky='w')

        self.draw = tk.Button(self, text="Draw Structure", command=self.draw_callback)
        self.draw.grid(row=1, column=0, sticky='sw')

        self.basic_label = tk.Label(self, text='Basic structures')
        self.basic_label.grid(row=2, column=0, sticky='w')

        i = 0
        basic_frame = tk.Frame(self)
        basic_frame.grid(row=3, column=0, columnspan=4)
        for name, target in structures.items():
            structure_button = tk.Button(basic_frame, text=name, command=self.struct_callback(structures[name]))
            structure_button.grid(row=0, column=i)
            i += 1

        self.load = tk.Button(self, text="Load Structure", command=lambda: print('load'))
        self.load.grid(row=4, column=0, sticky='sw')

        self.num_creator = NumCreator(self, struct_callback)
        self.num_creator.grid(row=5, column=0, sticky='sw')

    def draw_callback(self):
        popup = tk.Toplevel()
        popup.title("Draw Structure")

        label = tk.Label(popup, text="Draw your structure")
        label.grid(row=0, column=0)

        exit_button = tk.Button(popup, text='exit', command=popup.destroy)
        exit_button.grid(row=1, column=0)

        popup.focus_force()


class StratChooser(tk.Frame):
    def __init__(self, parent, *args, **kwargs) -> None:
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.strat_label = tk.Label(self, text='Strategy')
        self.strat_label.grid(row=0, column=0, sticky='w')
        self.strategy = tk.StringVar(self)
        self.strategy.set('spine')
        self.strategy_picker = tk.OptionMenu(self, self.strategy, *strategies.keys())
        self.strategy_picker.grid(row=1, column=0, sticky='w')

        self.lang_label = tk.Label(self, text='Language')
        self.lang_label.grid(row=2, column=0, sticky='w')
        self.language = tk.StringVar(self)
        self.language.set('python')
        self.language_picker = tk.OptionMenu(self, self.language, 'python', 'kotlin')
        self.language_picker.grid(row=3, column=0, sticky='w')


class BasicCreator(tk.Frame):
    def __init__(self, parent, *args, **kwargs) -> None:
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.target: CoordinateList = []
        self.parent = parent

        self.board = Board(self)
        self.board.grid(row=0, column=0, rowspan=4)
        self.board.draw_grid()

        self.target_creator = TargetCreator(self, self.create_set_struct, self.set_struct)
        self.target_creator.grid(row=0, column=1, sticky="n")

        self.strat_chooser = StratChooser(self)
        self.strat_chooser.grid(row=1, column=1, sticky="nw")

        self.start = tk.Button(self, text='Start', command=self.start)
        self.start.grid(row=2, column=1)

        self.struct = []

    def create_set_struct(self, struct):
        min_x = min(coord.x for coord in struct)
        min_y = min(coord.y for coord in struct)
        struct = [Coordinate(coord.x-min_x, coord.y-min_y) for coord in struct]

        def callback():
            self.set_struct(struct)
        return callback

    def set_struct(self, struct):
        self.struct = struct
        self.board.canvas.delete('drawn')
        self.board.draw_b_blocks(struct)

    def start(self):
        strat = strategies[self.strat_chooser.strategy.get()]
        sim = BasicSimulation.create_with_target_structure(self.struct, strat)
        player = BasicPlayer(self.parent, sim)
        player.grid()
        player.winfo_toplevel().title("RoboScaffold Sim")
        self.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    player = BasicCreator(root)
    player.winfo_toplevel().title("Create Structure")
    player.grid()
    root.mainloop()
