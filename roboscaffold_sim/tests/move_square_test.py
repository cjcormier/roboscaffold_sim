import tkinter as tk

import copy

from roboscaffold_sim.coordinate import Coordinate
from roboscaffold_sim.direction import Direction
from roboscaffold_sim.state.scaffolding_state import SInstruction, ScaffoldState
from roboscaffold_sim.state.builder_state import BuilderState, HeldBlock
from roboscaffold_sim.state.simulation_state import SimulationState
from roboscaffold_sim.veiw.basic_player import BasicPlayer

i = 0


def get_next_coord() -> Coordinate:
    global i
    next_coord = Coordinate(i % 10, i // 10)
    i += 1
    return next_coord


s_blocks = {
    # row 0
    get_next_coord(): ScaffoldState(SInstruction.DRIVE_LEFT),
    get_next_coord(): ScaffoldState(SInstruction.NONE),
    get_next_coord(): ScaffoldState(SInstruction.NONE),
    get_next_coord(): ScaffoldState(SInstruction.NONE),
    get_next_coord(): ScaffoldState(SInstruction.NONE),
    get_next_coord(): ScaffoldState(SInstruction.NONE),
    get_next_coord(): ScaffoldState(SInstruction.NONE),
    get_next_coord(): ScaffoldState(SInstruction.NONE),
    get_next_coord(): ScaffoldState(SInstruction.NONE),
    get_next_coord(): ScaffoldState(SInstruction.DRIVE_LEFT),

    # row 1
    get_next_coord(): ScaffoldState(SInstruction.NONE),
    get_next_coord(): ScaffoldState(SInstruction.STOP),
    get_next_coord(): ScaffoldState(SInstruction.STOP),
    get_next_coord(): ScaffoldState(SInstruction.STOP),
    get_next_coord(): ScaffoldState(SInstruction.STOP),
    get_next_coord(): ScaffoldState(SInstruction.STOP),
    get_next_coord(): ScaffoldState(SInstruction.STOP),
    get_next_coord(): ScaffoldState(SInstruction.STOP),
    get_next_coord(): ScaffoldState(SInstruction.STOP),
    get_next_coord(): ScaffoldState(SInstruction.NONE),

    # row 2
    get_next_coord(): ScaffoldState(SInstruction.NONE),
    get_next_coord(): ScaffoldState(SInstruction.STOP),
    get_next_coord(): ScaffoldState(SInstruction.DRIVE_RIGHT),
    get_next_coord(): ScaffoldState(SInstruction.NONE),
    get_next_coord(): ScaffoldState(SInstruction.NONE),
    get_next_coord(): ScaffoldState(SInstruction.NONE),
    get_next_coord(): ScaffoldState(SInstruction.NONE),
    get_next_coord(): ScaffoldState(SInstruction.DRIVE_RIGHT),
    get_next_coord(): ScaffoldState(SInstruction.STOP),
    get_next_coord(): ScaffoldState(SInstruction.NONE),

    # row 3
    get_next_coord(): ScaffoldState(SInstruction.NONE),
    get_next_coord(): ScaffoldState(SInstruction.STOP),
    get_next_coord(): ScaffoldState(SInstruction.NONE),
    get_next_coord(): ScaffoldState(SInstruction.STOP),
    get_next_coord(): ScaffoldState(SInstruction.STOP),
    get_next_coord(): ScaffoldState(SInstruction.STOP),
    get_next_coord(): ScaffoldState(SInstruction.STOP),
    get_next_coord(): ScaffoldState(SInstruction.NONE),
    get_next_coord(): ScaffoldState(SInstruction.STOP),
    get_next_coord(): ScaffoldState(SInstruction.NONE),

    # row 4
    get_next_coord(): ScaffoldState(SInstruction.NONE),
    get_next_coord(): ScaffoldState(SInstruction.STOP),
    get_next_coord(): ScaffoldState(SInstruction.NONE),
    get_next_coord(): ScaffoldState(SInstruction.STOP),
    get_next_coord(): ScaffoldState(SInstruction.DRIVE_LEFT),
    get_next_coord(): ScaffoldState(SInstruction.DRIVE_LEFT),
    get_next_coord(): ScaffoldState(SInstruction.STOP),
    get_next_coord(): ScaffoldState(SInstruction.NONE),
    get_next_coord(): ScaffoldState(SInstruction.STOP),
    get_next_coord(): ScaffoldState(SInstruction.NONE),

    # row 5
    get_next_coord(): ScaffoldState(SInstruction.NONE),
    get_next_coord(): ScaffoldState(SInstruction.STOP),
    get_next_coord(): ScaffoldState(SInstruction.NONE),
    get_next_coord(): ScaffoldState(SInstruction.STOP),
    get_next_coord(): ScaffoldState(SInstruction.DRIVE_LEFT),
    get_next_coord(): ScaffoldState(SInstruction.DRIVE_LEFT),
    get_next_coord(): ScaffoldState(SInstruction.STOP),
    get_next_coord(): ScaffoldState(SInstruction.NONE),
    get_next_coord(): ScaffoldState(SInstruction.STOP),
    get_next_coord(): ScaffoldState(SInstruction.NONE),

    # row 6
    get_next_coord(): ScaffoldState(SInstruction.NONE),
    get_next_coord(): ScaffoldState(SInstruction.STOP),
    get_next_coord(): ScaffoldState(SInstruction.NONE),
    get_next_coord(): ScaffoldState(SInstruction.STOP),
    get_next_coord(): ScaffoldState(SInstruction.STOP),
    get_next_coord(): ScaffoldState(SInstruction.STOP),
    get_next_coord(): ScaffoldState(SInstruction.STOP),
    get_next_coord(): ScaffoldState(SInstruction.NONE),
    get_next_coord(): ScaffoldState(SInstruction.STOP),
    get_next_coord(): ScaffoldState(SInstruction.NONE),

    # row 7
    get_next_coord(): ScaffoldState(SInstruction.NONE),
    get_next_coord(): ScaffoldState(SInstruction.STOP),
    get_next_coord(): ScaffoldState(SInstruction.DRIVE_RIGHT),
    get_next_coord(): ScaffoldState(SInstruction.NONE),
    get_next_coord(): ScaffoldState(SInstruction.NONE),
    get_next_coord(): ScaffoldState(SInstruction.NONE),
    get_next_coord(): ScaffoldState(SInstruction.NONE),
    get_next_coord(): ScaffoldState(SInstruction.DRIVE_RIGHT),
    get_next_coord(): ScaffoldState(SInstruction.STOP),
    get_next_coord(): ScaffoldState(SInstruction.NONE),

    # row 8
    get_next_coord(): ScaffoldState(SInstruction.NONE),
    get_next_coord(): ScaffoldState(SInstruction.STOP),
    get_next_coord(): ScaffoldState(SInstruction.STOP),
    get_next_coord(): ScaffoldState(SInstruction.STOP),
    get_next_coord(): ScaffoldState(SInstruction.STOP),
    get_next_coord(): ScaffoldState(SInstruction.STOP),
    get_next_coord(): ScaffoldState(SInstruction.STOP),
    get_next_coord(): ScaffoldState(SInstruction.STOP),
    get_next_coord(): ScaffoldState(SInstruction.STOP),
    get_next_coord(): ScaffoldState(SInstruction.NONE),

    # row 9
    get_next_coord(): ScaffoldState(SInstruction.DRIVE_LEFT),
    get_next_coord(): ScaffoldState(SInstruction.NONE),
    get_next_coord(): ScaffoldState(SInstruction.NONE),
    get_next_coord(): ScaffoldState(SInstruction.NONE),
    get_next_coord(): ScaffoldState(SInstruction.NONE),
    get_next_coord(): ScaffoldState(SInstruction.NONE),
    get_next_coord(): ScaffoldState(SInstruction.NONE),
    get_next_coord(): ScaffoldState(SInstruction.NONE),
    get_next_coord(): ScaffoldState(SInstruction.NONE),
    get_next_coord(): ScaffoldState(SInstruction.DRIVE_LEFT),
}

sim = SimulationState()
sim.s_blocks = s_blocks

robot = BuilderState()
robot.direction = Direction.WEST
robot.block = HeldBlock.BUILD
sim.robots[Coordinate(1, 0)] = copy.copy(robot)
robot.direction = Direction.EAST
sim.robots[Coordinate(3, 2)] = copy.copy(robot)
robot.direction = Direction.NORTH
sim.robots[Coordinate(5, 4)] = copy.copy(robot)

root = tk.Tk()
player = BasicPlayer(root, sim)
player.grid()
root.mainloop()
