from roboscaffold_sim.state.builder_state import BuilderState
from roboscaffold_sim.veiw.veiw import *
from roboscaffold_sim.state.block_states import ScaffoldState, BuildingBlockState
from pyglet.window.mouse import LEFT

window = pyglet.window.Window(800, 600, caption='Robotic Scaffolding Simulation')


@window.event
def on_draw():
    window.clear()
    draw_grid()
    i = 0

    s_blocks = {}
    robot = BuilderState()
    for instruction in ScaffoldInstruction:
        s_blocks[Coordinate(i % 10, i//10)] = ScaffoldState(instruction)
        i += 1

    draw_s_blocks(s_blocks)

    draw_b_blocks({Coordinate(i % 10, i//10): BuildingBlockState()})
    i += 1

    for direction in Direction:
        robot.direction = direction
        for held_block in HeldBlock:
            robot.held_block = held_block
            draw_s_blocks({Coordinate(i % 10, i//10): ScaffoldState(ScaffoldInstruction.DRIVE_RIGHT)})
            draw_robot(Coordinate(i % 10, i//10), robot)
            i += 1

    draw_state_counter("{}/9999+".format(state_count))


@window.event
def on_mouse_press(x, y, button, modifiers):
    global state_count
    if button is LEFT:
        if within_state_counter_button_left(x, y):
            state_count -= 1
        elif within_state_counter_button_right(x, y):
            state_count += 1


state_count = 0
pyglet.gl.glLineWidth(line_width)
pyglet.app.run()
