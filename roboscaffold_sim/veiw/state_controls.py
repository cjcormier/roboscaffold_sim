import tkinter as tk


class StateControls(tk.Frame):
    def __init__(self, parent,
                 updater=lambda x: None,
                 loader=lambda x: None,
                 *args, **kwargs):
        tk.Frame.__init__(self, parent,
                          *args, **kwargs)
        self.parent = parent
        self.updater = updater
        self.loader = loader

        self.rows = 5
        self.row_frames = [tk.Frame(self) for _ in range(self.rows)]
        for i, frame in enumerate(self.row_frames):
            tk.Grid.columnconfigure(self, i, weight=1)
            frame.grid(row=i, column=0, sticky='we')

        self._current_state = 1
        self._max_state = 1
        self.finished = False
        self.play_status = False

        self.bb_step = tk.Button(self.row_frames[0], text='<<',
                                 command=lambda: self.bb_step_callback()
                                 )
        self.bb_step.grid(row=0, column=0)

        self.b_step = tk.Button(self.row_frames[0], text='<',
                                command=lambda: self.b_step_callback()
                                )
        self.b_step.grid(row=0, column=1)

        self.label_text = tk.StringVar()
        self.state_label = tk.Label(self.row_frames[0], textvariable=self.label_text,
                                    width=10)
        self.state_label.grid(row=0, column=2)

        self.f_step = tk.Button(self.row_frames[0], text='>',
                                command=lambda: self.f_step_callback()
                                )
        self.f_step.grid(row=0, column=3)

        self.ff_step = tk.Button(self.row_frames[0], text='>>',
                                 command=lambda: self.ff_step_callback()
                                 )
        self.ff_step.grid(row=0, column=4)

        tk.Grid.columnconfigure(self.row_frames[1], 0, weight=1)
        self.scale = tk.Scale(self.row_frames[1], orient=tk.HORIZONTAL, from_=1,
                              command=lambda _: self.scale_change())
        self.scale.grid(row=1, column=0, columnspan=5, sticky='we')

        self.play_button = tk.Button(self.row_frames[2], text='Play',
                                     command=lambda: self.play()
                                     )
        self.play_button.grid(row=0, column=0)

        self.pause_button = tk.Button(self.row_frames[2], text='Pause',
                                      command=lambda: self.pause()
                                      )
        self.pause_button.grid(row=0, column=1)

        self.rate_label = tk.Label(self.row_frames[2], text='FPS:')
        self.rate_label.grid(row=0, column=2)

        self.rate_textbox = tk.Text(self.row_frames[2], width=6, height=1)
        self.rate_textbox.grid(row=0, column=3)
        self.default_rate = 10
        self.rate_textbox.insert('1.0', self.default_rate)
        self.rate_textbox_color = self.rate_textbox.cget('background')

        tk.Grid.columnconfigure(self.row_frames[3], 1, weight=1)
        self.load_frames_button = tk.Button(self.row_frames[3], text='Load Frames',
                                            command=lambda: self.load())
        self.load_frames_button.grid(row=0, column=0)

        self.load_textbox = tk.Text(self.row_frames[3], width=6, height=1)
        self.load_textbox.grid(row=0, column=1, sticky='we')
        self.load_textbox.insert('1.0', 1000)
        self.load_textbox_color = self.rate_textbox.cget('background')

        self.pause()
        self.update_state()

    def f_step_callback(self):
        self.current_state = min(self.current_state + 1, self.max_state)

    def ff_step_callback(self):
        self.current_state = min(self.current_state + 5, self.max_state)

    def b_step_callback(self):
        self.current_state = max(self.current_state - 1, 1)

    def bb_step_callback(self):
        self.current_state = max(self.current_state - 5, 1)

    def scale_change(self):
        # self.pause()
        self.update_state(True)

    def update_state(self, new_scale=False):
        if new_scale:
            self._current_state = self.scale.get()
        new_text = f'{self.current_state}/{self.max_state}'
        new_text += '' if self.finished else '+'
        self.label_text.set(new_text)

        self.scale.configure(to=self.max_state)
        self.scale.set(self.current_state)
        self.updater(self.current_state - 1)

    def play(self):
        self.play_status = True
        self.rate_textbox.config(state='disabled', background='light grey')
        self.play_button.config(relief='sunken')
        self.pause_button.config(relief='raised')
        self.play_callback()

    def play_callback(self):
        if self.current_state == self.max_state:
            self.pause()
            return

        if self.play_status:
            self.current_state += 1
            delay = 1000//self.rate
            self.parent.after(delay, self.play_callback)

    def pause(self):
        self.play_status = False
        self.rate_textbox.config(state='normal', background=self.rate_textbox_color)
        self.play_button.config(relief='raised')
        self.pause_button.config(relief='sunken')

    @property
    def rate(self):
        text = self.rate_textbox.get('1.0', 'end')
        try:
            val = int(text)
            if not 1 <= val <= 60:
                self.rate_textbox.delete('1.0', 'end')
                self.rate_textbox.insert('1.0', self.default_rate)
                return 1
            return val
        except ValueError:
            self.rate_textbox.delete('1.0', 'end')
            self.rate_textbox.insert('1.0', self.default_rate)
            return 1

    def load(self, load=None):
        if load is None:
            text = self.load_textbox.get('1.0', 'end')
            try:
                load = int(text)
                if not 1 <= load <= 1000:
                    self.load_textbox.delete('1.0', 'end')
                    self.load_textbox.insert('1.0', 1000)
                    load = 1
            except ValueError:
                self.load_textbox.delete('1.0', 'end')
                self.load_textbox.insert('1.0', 1000)
                load = 1
        self.loader(load)
        if self.finished:
            print('No more to load')

    @property
    def max_state(self) -> int:
        return self._max_state

    @max_state.setter
    def max_state(self, value: int):
        self._max_state = value
        self.update_state()

    @property
    def current_state(self) -> int:
        return self._current_state

    @current_state.setter
    def current_state(self, value: int):
        self._current_state = value
        self.update_state()
