from roboscaffold_sim.coordinate import Coordinate
from roboscaffold_sim.direction import Direction
from roboscaffold_sim.state.block_states import ScaffoldInstruction, ScaffoldState, \
    BuildingBlockState
from roboscaffold_sim.state.builder_state import BuilderState, HeldBlock
from roboscaffold_sim.state.simulation_state import SimulationState, Goal, GoalType
from roboscaffold_sim.veiw.board import Board
import tkinter as tk

from roboscaffold_sim.veiw.state_controls import StateControls

i = 0


def get_next_coord() -> Coordinate:
    global i
    next_coord = Coordinate(i % 10, i // 10)
    i += 1
    return next_coord


root = tk.Tk()
board = Board(root)
board.grid(row=0, column=0, rowspan=4)
board.draw_grid()

state_controls = StateControls(root)
state_controls.grid(row=2, column=1, sticky="s")
state_controls.max_state = 10

s_blocks = {}
b_blocks = {}
robots = {}
for instruction in ScaffoldInstruction:
    s_blocks[get_next_coord()] = ScaffoldState(instruction)

b_blocks[get_next_coord()] = BuildingBlockState()

for direction in Direction:
    for held_block in HeldBlock:
        robot = BuilderState()
        robot.held_block = held_block
        robot.direction = direction
        coord = get_next_coord()
        s_blocks[coord] = ScaffoldState(ScaffoldInstruction.DRIVE_RIGHT)
        robots[coord] = robot

sim = SimulationState()
sim.s_blocks = s_blocks
sim.b_blocks = b_blocks
sim.robots = robots
board.draw_sim(sim)

goal = Goal(get_next_coord(), GoalType.PLACE_SCAFFOLD)
board.draw_goal(goal)
root.mainloop()
