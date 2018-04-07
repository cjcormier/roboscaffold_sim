import tkinter as tk
from roboscaffold_sim.veiw.basic_creater import BasicCreator

if __name__ == '__main__':
    root = tk.Tk()
    creator = BasicCreator(root)
    creator.winfo_toplevel().title("Create Structure")
    creator.grid()
    root.mainloop()