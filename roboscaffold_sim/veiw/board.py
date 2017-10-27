import tkinter as tk
from operator import add
from typing import Tuple, List

from roboscaffold_sim.coordinate import Coordinate, CoordinateList
from roboscaffold_sim.direction import Direction
from roboscaffold_sim.state.block_states import ScaffoldInstruction
from roboscaffold_sim.state.builder_state import HeldBlock, BuilderState
from roboscaffold_sim.state.simulation_state import SBlocks, BBlocks, Robots, GoalType, \
    Goal, Goals, SimulationState
from roboscaffold_sim.veiw.tooltip import CanvasTooltip

Color = str


class Board(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.rows = 10
        self.columns = 10
        self.grid_size = 50

        self.line_width = 3
        self.block_line_width = 4
        self.goal_line_width = 3
        self.robot_line_width = 3
        self.block_gap = 3
        self.robot_gap = self.block_line_width + 3
        self.target_gap = 3

        self.grid_color = "#000"
        self.s_block_color = '#fff'
        self.b_block_color = '#000'
        self.block_color = '#000'
        self.robot_color = "#000"
        self.background_color = '#888'

        self.scaffold_colors = {
            ScaffoldInstruction.NONE: '#888',
            ScaffoldInstruction.STOP: '#FFF',

            ScaffoldInstruction.DRIVE_LEFT: '#800',
            ScaffoldInstruction.DRIVE_RIGHT: '#080',
            ScaffoldInstruction.DRIVE_UTURN: '#008',

            ScaffoldInstruction.PICK_LEFT: '#ff0',
            ScaffoldInstruction.PICK_RIGHT: '#0ff',
            ScaffoldInstruction.PICK_FORWARD: '#f0f',

            ScaffoldInstruction.DROP_LEFT: '#f00',
            ScaffoldInstruction.DROP_RIGHT: '#0f0',
            ScaffoldInstruction.DROP_FORWARD: '#00f'
        }

        self.goal_colors = {
            GoalType.PLACE_BUILD_BLOCK: '#fff',
            GoalType.PLACE_SCAFFOLD: '#fff',
            GoalType.PICK_BUILD_BLOCK: '#fff',
            GoalType.PICK_SCAFFOLD: '#fff',
        }

        self.builder_colors = {
            HeldBlock.BUILD: self.b_block_color,
            HeldBlock.SCAFFOLD: self.s_block_color,
            HeldBlock.NONE: '#888'
        }

        needed_width = self.columns*self.grid_size + self.line_width
        needed_height = self.rows*self.grid_size + self.line_width

        self.canvas = tk.Canvas(self, width=needed_width, height=needed_height)
        self.canvas.configure(background=self.background_color)
        self.canvas.grid()

    def draw_grid(self):
        previous_grid = self.canvas.find_withtag('grid')
        self.canvas.delete(previous_grid)

        column_offset = self.grid_size * self.rows + self.line_width
        row_offset = self.grid_size * self.columns + self.line_width

        base_offset = (self.line_width + 1) // 2

        for column in range(self.columns+1):
            x1 = base_offset + self.grid_size*column
            y1 = base_offset
            x2 = base_offset + self.grid_size*column
            y2 = column_offset
            self.canvas.create_line(x1, y1, x2, y2, fill=self.grid_color,
                                    tags='grid', width=self.line_width)

        for row in range(self.rows+1):
            x1 = base_offset
            y1 = base_offset + self.grid_size*row
            x2 = row_offset
            y2 = base_offset + self.grid_size*row
            self.canvas.create_line(x1, y1, x2, y2, fill=self.grid_color,
                                    tags='grid', width=self.line_width)

    def get_grid_center(self, coord: Coordinate):

        block_offset = (self.grid_size+1)//2
        grid_offset = (self.line_width+1)//2

        x = grid_offset + block_offset + self.grid_size * coord.x
        y = grid_offset + block_offset + self.grid_size * coord.y
        return x, y

    @staticmethod
    def get_triangle_vertices(x: int, y: int, edge_size: int, direction: Direction) \
            -> Tuple[int, ...]:
        half_edge_size = (edge_size + 1) // 2

        vert_offsets: List[int] = []
        if direction is Direction.NORTH:
            vert_offsets = [half_edge_size, 0, edge_size, edge_size, 0, edge_size]
        elif direction is Direction.EAST:
            vert_offsets = [0, 0, edge_size, half_edge_size, 0, edge_size]
        elif direction is Direction.SOUTH:
            vert_offsets = [0, 0, edge_size, 0, half_edge_size, edge_size]
        elif direction is Direction.WEST:
            vert_offsets = [edge_size, 0, edge_size, edge_size, 0, half_edge_size]
        return tuple(map(add, [x-half_edge_size, y-half_edge_size] * 3, vert_offsets))

    def draw_sim(self, sim: SimulationState):
        self.canvas.delete('drawn')
        self.draw_s_blocks(sim.s_blocks)
        self.draw_b_blocks(sim.b_blocks)
        self.draw_robots(sim.robots)
        self.draw_target_structure(sim.target_structure)
        self.draw_goals(sim.goal_stack)

    def draw_s_blocks(self, s_blocks: SBlocks):
        for coord, block in s_blocks.items():
            fill_color = self.scaffold_colors[block.instruction]
            # outline_color = self.s_block_color
            self.draw_block(coord, fill_color, self.block_color,
                            tooltip=block.instruction.name)

    def draw_b_blocks(self, b_blocks: BBlocks):
        for coord, block in b_blocks.items():
            self.draw_block(coord, self.block_color, self.block_color,
                            tooltip="BUILDING_BLOCK")

    def draw_block(self, coord: Coordinate, fill: Color, outline: Color, tags=(),
                   tooltip=None):
        edge_size = self.grid_size - 2*self.block_line_width - 2*self.block_gap
        corner_dist = (edge_size+1)//2
        x, y = self.get_grid_center(coord)

        block = self.canvas.create_rectangle(x-corner_dist, y-corner_dist,
                                             x+corner_dist, y+corner_dist,
                                             tags=('block', 'drawn', *tags),
                                             fill=fill, outline=outline,
                                             width=self.block_line_width)
        if tooltip is not None:
            CanvasTooltip(self.canvas, block, text=tooltip, waittime=100)

    def draw_robots(self, robots: Robots):
        for coord, robot in robots.items():
            self.draw_robot(coord, robot)

    def draw_robot(self, coord: Coordinate, robot: BuilderState):
        edge_size = self.grid_size - self.block_line_width - 2*self.block_gap \
                    - 2*self.robot_gap

        x, y = self.get_grid_center(coord)

        vertices = self.get_triangle_vertices(x, y, edge_size, robot.direction)

        fill = self.builder_colors[robot.held_block]
        outline = self.robot_color

        robot_drawing = self.canvas.create_polygon(*vertices, fill=fill, outline=outline,
                                                   width=self.goal_line_width,
                                                   tag=('robot', 'drawn'))

        CanvasTooltip(self.canvas, robot_drawing, waittime=100,
                      text=f'Robot carrying {robot.held_block.name}')

    def draw_goals(self, goals: Goals):
        for count, goal in enumerate(goals):
            self.draw_goal(goal, count)

    def draw_goal(self, goal: Goal, step=None):
        edge_size = self.grid_size - 2*self.block_line_width - 2*self.block_gap
        corner_dist = (edge_size+1)//2
        x, y = self.get_grid_center(goal.coord)
        color = self.goal_colors[goal.type]

        goal_drawing = self.canvas.create_rectangle(x-corner_dist, y-corner_dist,
                                                    x+corner_dist, y+corner_dist,
                                                    tags=('goal', 'drawn'), outline=color,
                                                    width=self.goal_line_width,
                                                    dash=".", dashoffset=3)
        CanvasTooltip(self.canvas, goal_drawing, waittime=100,
                      text=f'GOAL: {goal.type.name}')

        if step is not None:
            goal_label = self.canvas.create_text(x, y, text=str(step),
                                                 tags=('goal', 'drawn'))
            CanvasTooltip(self.canvas, goal_label, waittime=100,
                          text=f'GOAL: {goal.type.name}')

    def draw_target_structure(self, target: CoordinateList):
        for coord in target:
            self.draw_target(coord)

    def draw_target(self, coord: Coordinate):
        edge_size = self.grid_size - 2*self.block_line_width - 2*self.block_gap - 2*self.target_gap
        corner_dist = (edge_size+1)//2
        x, y = self.get_grid_center(coord)
        color = self.b_block_color

        target = self.canvas.create_rectangle(x-corner_dist, y-corner_dist,
                                              x+corner_dist, y+corner_dist,
                                              tags=('target', 'drawn'), outline=color,
                                              width=self.goal_line_width,
                                              dash=".", dashoffset=31)

        CanvasTooltip(self.canvas, target, waittime=100,
                      text=f'Target Structure')
