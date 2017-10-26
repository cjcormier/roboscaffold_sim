from enum import Enum, auto
from roboscaffold_sim.direction import Direction


class HeldBlock(Enum):
    BUILD = auto()
    SCAFFOLD = auto()
    NONE = auto()


class BuilderState:
    def __init__(self):
        self.held_block = HeldBlock.NONE
        self.direction = Direction.NORTH

    def turn(self, direction):
        if direction == 'left':
            self.direction = self.direction.left()
        elif direction == 'right':
            self.direction = self.direction.left()
        else:
            raise ValueError('Direction should be "left" or "right"')
