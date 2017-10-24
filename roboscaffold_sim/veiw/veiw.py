from typing import List

import pyglet
import tkinter as tk

from roboscaffold_sim.coordinate import Coordinate
from roboscaffold_sim.direction import Direction
from roboscaffold_sim.state.builder_state import HeldBlock, BuilderState
from roboscaffold_sim.state.block_states import ScaffoldInstruction

from roboscaffold_sim.state.simulation_state import SBlocks, BBlocks, SimulationState
from operator import add

VertColors = List[int]
Vertices = List[int]

line_width = 3

rows = 10
columns = 10
grid_size = 50
grid_offset = 10

full_grid_offset = grid_offset + (line_width + 1) // 2

state_button_counter_size = 30
state_button_counter_inner_offset = 5
state_button_counter_spacing = 60
state_button_counter_x_offset = 20
state_button_counter_x = 50*10 + grid_offset + line_width + state_button_counter_x_offset
state_button_counter_y = full_grid_offset

block_gap = 3
robot_gap = line_width + 3

scaffold_colors = {
    ScaffoldInstruction.NONE: [0, 0, 0],
    ScaffoldInstruction.STOP: [255, 255, 255],

    ScaffoldInstruction.DRIVE_LEFT: [128, 0, 0],
    ScaffoldInstruction.DRIVE_RIGHT: [0, 128, 0],

    ScaffoldInstruction.PICK_LEFT: [255, 255, 0],
    ScaffoldInstruction.PICK_RIGHT: [0, 255, 255],
    ScaffoldInstruction.PICK_FORWARD: [255, 0, 255],

    ScaffoldInstruction.DROP_LEFT: [255, 0, 0],
    ScaffoldInstruction.DROP_RIGHT: [0, 255, 0],
    ScaffoldInstruction.DROP_FORWARD: [0, 0, 255]
}

s_block_color = [128, 128, 0]
b_block_color = [0, 128, 128]
robot_color = [128, 0, 128]

builder_colors = {
    HeldBlock.BUILD: b_block_color,
    HeldBlock.SCAFFOLD: s_block_color,
    HeldBlock.NONE: [0, 0, 0]
}

state_counter_square_color = [128, 128, 128]
state_counter_arrow_color = [255, 255, 255]


class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent


def initialize_grid():
    vertices = []

    column_offset = grid_offset + grid_size * rows + line_width
    row_offset = grid_offset + grid_size * columns + line_width

    for column in range(columns+1):
        x1 = full_grid_offset + grid_size*column
        y1 = grid_offset
        x2 = full_grid_offset + grid_size*column
        y2 = column_offset
        vertices.extend([x1, y1, x2, y2])

    for row in range(rows+1):
        x1 = grid_offset
        y1 = full_grid_offset + grid_size*row
        x2 = row_offset
        y2 = full_grid_offset + grid_size*row
        vertices.extend([x1, y1, x2, y2])

    return pyglet.graphics.vertex_list(len(vertices)//2, ('v2i', tuple(vertices)))


def get_triangle_vertices(x: int, y: int, edge_size: int, direction: Direction) \
        -> Vertices:
    half_edge_size = (edge_size+1)//2

    vert_offsets: Vertices = []
    if direction is Direction.NORTH:
        vert_offsets = [0, 0, edge_size, 0, half_edge_size, edge_size]
    elif direction is Direction.EAST:
        vert_offsets = [0, 0, edge_size, half_edge_size, 0, edge_size]
    elif direction is Direction.SOUTH:
        vert_offsets = [half_edge_size, 0,  edge_size, edge_size, 0, edge_size]
    elif direction is Direction.WEST:
        vert_offsets = [edge_size, 0,  edge_size, edge_size, 0, half_edge_size]
    return list(map(add, [x, y]*3, vert_offsets))


def draw_robot(coord: Coordinate, builder: BuilderState):
    edge_size = grid_size - 2*line_width - 2*block_gap - 2*robot_gap

    block_offset = line_width + block_gap + robot_gap

    x = full_grid_offset + block_offset + grid_size*coord.x
    y = full_grid_offset + block_offset + grid_size*coord.y

    verticies = tuple(get_triangle_vertices(x, y, edge_size, builder.direction))

    fill_color = builder_colors[builder.held_block]
    outline_color = robot_color

    # Fill
    pyglet.graphics.draw(3, pyglet.gl.GL_POLYGON,
                         ('v2i', verticies), ('c3B', tuple(fill_color*3))
                         )

    # Outline
    pyglet.graphics.draw(3, pyglet.gl.GL_LINE_LOOP,
                         ('v2i', verticies), ('c3B', tuple(outline_color*3))
                         )


def draw_block(coord: Coordinate, fill_color: VertColors, outline_color: VertColors):
    edge_size = grid_size - 2*line_width - 2*block_gap

    block_offset = line_width + block_gap

    x = full_grid_offset + block_offset + grid_size*coord.x
    y = full_grid_offset + block_offset + grid_size*coord.y

    vertices = (x, y, x+edge_size, y, x+edge_size, y+edge_size, x, y+edge_size)

    # Fill
    pyglet.graphics.draw(4, pyglet.gl.GL_POLYGON,
                         ('v2i', vertices), ('c3B', tuple(fill_color*4))
                         )

    # Outline
    pyglet.graphics.draw(4, pyglet.gl.GL_LINE_LOOP,
                         ('v2i', vertices), ('c3B', tuple(outline_color*4))
                         )
    pass


def draw_s_blocks(blocks: SBlocks):
    for coord, block in blocks.items():
        fill_color = scaffold_colors[block.instruction]
        outline_color = s_block_color
        draw_block(coord, fill_color, outline_color)


def draw_b_blocks(blocks: BBlocks):
    for coord, block in blocks.items():
        draw_block(coord, b_block_color, b_block_color)


def draw_grid():
    grid_vertex_list.draw(pyglet.gl.GL_LINES)


def draw_sim(sim: SimulationState):
    draw_s_blocks(sim.s_blocks)
    draw_b_blocks(sim.b_blocks)
    draw_robot(sim.builder_location, sim.builder)


def draw_state_counter(text):
    x = state_button_counter_x
    y = state_button_counter_y
    spacing = state_button_counter_spacing
    edge_size = state_button_counter_size

    draw_state_counter_button(x, y, edge_size, Direction.WEST)
    draw_state_counter_button(x+edge_size+2*spacing, y, edge_size, Direction.EAST)

    label = pyglet.text.Label(text, font_name='Times New Roman', font_size=16,
                              x=x+edge_size+spacing, y=y,
                              anchor_x='center', anchor_y='bottom')
    label.draw()


def draw_state_counter_button(x, y, edge_size, direction):
    corner_offsets = (0, 0, edge_size, 0, edge_size, edge_size, 0,  edge_size)
    square_verts = tuple(map(add, [x, y]*4, corner_offsets))

    arrow_x = x + state_button_counter_inner_offset
    arrow_y = y + state_button_counter_inner_offset
    arrow_edge_size = edge_size - 2*state_button_counter_inner_offset

    arrow_verts = tuple(get_triangle_vertices(arrow_x, arrow_y,
                                              arrow_edge_size, direction))

    pyglet.graphics.draw(4, pyglet.gl.GL_POLYGON,
                         ('v2i', square_verts),
                         ('c3B', tuple(state_counter_square_color*4))
                         )

    pyglet.graphics.draw(3, pyglet.gl.GL_POLYGON,
                         ('v2i', arrow_verts),
                         ('c3B', tuple(state_counter_arrow_color*3))
                         )


def within_state_counter_button_left(x, y):
    size = state_button_counter_size
    x_bound = state_button_counter_x
    y_bound = state_button_counter_y
    x_in_bounds = x_bound < x < x_bound + size
    y_in_bounds = y_bound < y < y_bound + size
    return x_in_bounds and y_in_bounds


def within_state_counter_button_right(x, y):
    size = state_button_counter_size
    x_bound = state_button_counter_x + 2*state_button_counter_spacing + size
    y_bound = state_button_counter_y
    x_in_bounds = x_bound < x < x_bound + size
    y_in_bounds = y_bound < y < y_bound + size
    return x_in_bounds and y_in_bounds


grid_vertex_list = initialize_grid()
