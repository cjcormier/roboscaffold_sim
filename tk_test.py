from roboscaffold_sim.coordinate import Coordinate
from roboscaffold_sim.direction import Direction
from roboscaffold_sim.state.block_states import ScaffoldInstruction, ScaffoldState, BuildingBlockState
from roboscaffold_sim.state.builder_state import BuilderState, HeldBlock
from roboscaffold_sim.veiw.board import Board
import tkinter as tk

root = tk.Tk()
board = Board(root)
board.grid()
board.draw_grid()
i = 0

s_blocks = {}
b_blocks = {}
robots = {}
for instruction in ScaffoldInstruction:
    s_blocks[Coordinate(i % 10, i//10)] = ScaffoldState(instruction)
    i += 1

b_blocks[Coordinate(i % 10, i//10)] = BuildingBlockState()
i += 1

for direction in Direction:
    for held_block in HeldBlock:
        robot = BuilderState()
        robot.held_block = held_block
        robot.direction = direction
        s_blocks[Coordinate(i % 10, i//10)] = ScaffoldState(ScaffoldInstruction.DRIVE_RIGHT)
        robots[Coordinate(i % 10, i//10)] = robot
        i += 1

board.draw_sim(s_blocks, b_blocks, robots)
root.mainloop()
