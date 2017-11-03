import tkinter as tk


class Stats(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.s_blocks_text = tk.StringVar()
        self.length_text = tk.StringVar()

        self.s_blocks_label = tk.Label(self, textvariable=self.s_blocks_text)
        self.s_blocks_label.grid(row=0, column=0, sticky='nw')

        self.length_label = tk.Label(self, textvariable=self.length_text)
        self.length_label.grid(row=1, column=0, sticky='nw')

    def update_text(self, s_blocks: int, length: int) -> None:
        self.s_blocks_text.set(f'Overall scaffolding used: {s_blocks}')
        self.length_text.set(f'Current simulation length: {length}')
        print('text updated')
