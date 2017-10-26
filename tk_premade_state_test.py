import tkinter as tk

from roboscaffold_sim.coordinate import Coordinate
from roboscaffold_sim.direction import Direction
from roboscaffold_sim.state.block_states import ScaffoldInstruction, ScaffoldState, \
    BuildingBlockState
from roboscaffold_sim.state.builder_state import BuilderState, HeldBlock
from roboscaffold_sim.state.simulation_state import Goal, GoalType, \
    SimulationStateList
from roboscaffold_sim.veiw.basic_player import BasicPlayer

i = 0


def get_next_coord() -> Coordinate:
    global i
    next_coord = Coordinate(i % 10, i // 10)
    i += 1
    return next_coord


states = SimulationStateList.create_with_empty_states(400)


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

states.states[0].s_blocks = s_blocks
states.states[0].b_blocks = b_blocks
states.states[0].robots = robots
goal = Goal(get_next_coord(), GoalType.PLACE_SCAFFOLD)
states.states[0].target_structure = [get_next_coord()]
states.states[0].goal_stack.append(goal)

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

states.states[1].s_blocks = s_blocks
states.states[1].b_blocks = b_blocks
states.states[1].robots = robots

for _ in range(10):
    states.states[2].target_structure.append(get_next_coord())

root = tk.Tk()
player = BasicPlayer(root, initial_updates=0)
player.state_controls.max_state = len(states.states)
player.states = states
player.force_update()
player.grid()
root.mainloop()
