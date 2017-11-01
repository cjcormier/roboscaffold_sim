from enum import Enum, auto
from roboscaffold_sim.direction import Direction


class HeldBlock(Enum):
    BUILD = auto()
    SCAFFOLD = auto()
    NONE = auto()


class BuilderState:
    def __init__(self) -> None:
        self.block = HeldBlock.NONE
        self.direction = Direction.SOUTH

    def turn(self, direction: Direction):
        if direction == 'left':
            self.direction = self.direction.left()
        elif direction == 'right':
            self.direction = self.direction.right()
        else:
            raise ValueError('Direction should be "left" or "right"')

    def not_holding_block(self):
        return self.block == HeldBlock.NONE
