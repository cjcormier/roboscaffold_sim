import tkinter as tk

import copy

from roboscaffold_sim.coordinate import Coordinate
from roboscaffold_sim.direction import Direction
from roboscaffold_sim.state.block_states import ScaffoldInstruction, ScaffoldState
from roboscaffold_sim.state.builder_state import BuilderState, HeldBlock
from roboscaffold_sim.state.simulation_state import SimulationState
from roboscaffold_sim.veiw.basic_player import BasicPlayer

i = 0


def get_next_coord() -> Coordinate:
    global i
    next_coord = Coordinate(i % 7, i // 7)
    i += 1
    return next_coord


s_blocks = {get_next_coord(): ScaffoldState(ScaffoldInstruction.DRIVE_RIGHT),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.NONE),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.NONE),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.DRIVE_RIGHT),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.NONE),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.NONE),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.DRIVE_RIGHT),

            get_next_coord(): ScaffoldState(ScaffoldInstruction.NONE),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.STOP),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.STOP),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.NONE),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.STOP),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.STOP),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.NONE),

            get_next_coord(): ScaffoldState(ScaffoldInstruction.NONE),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.STOP),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.STOP),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.NONE),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.STOP),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.STOP),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.NONE),

            get_next_coord(): ScaffoldState(ScaffoldInstruction.DRIVE_RIGHT),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.NONE),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.NONE),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.NONE),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.NONE),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.NONE),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.DRIVE_RIGHT),

            get_next_coord(): ScaffoldState(ScaffoldInstruction.NONE),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.STOP),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.STOP),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.NONE),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.STOP),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.STOP),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.NONE),

            get_next_coord(): ScaffoldState(ScaffoldInstruction.NONE),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.STOP),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.STOP),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.NONE),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.STOP),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.STOP),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.NONE),

            get_next_coord(): ScaffoldState(ScaffoldInstruction.DRIVE_RIGHT),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.NONE),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.NONE),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.DRIVE_RIGHT),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.NONE),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.NONE),
            get_next_coord(): ScaffoldState(ScaffoldInstruction.DRIVE_RIGHT)
            }

sim = SimulationState()
sim.s_blocks = s_blocks

robot = BuilderState()
robot.direction = Direction.EAST
robot.held_block = HeldBlock.BUILD
sim.robots = {Coordinate(1, 0): copy.copy(robot)}

root = tk.Tk()
player = BasicPlayer(root, sim, 100)
player.grid()
root.mainloop()
