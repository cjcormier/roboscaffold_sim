from enum import Enum, auto

from roboscaffold_sim.coordinate import Coordinate
from roboscaffold_sim.direction import Direction


class HeldBlock(Enum):
    BUILD = auto()
    SCAFFOLD = auto()
    NONE = auto()


class BuilderState:
    def __init__(self):
        self.held_block = HeldBlock.NONE
        self.direction = Direction.NORTH

    def __eq__(self, other):
        """Override the default Equals behavior"""
        if isinstance(other, self.__class__):
            return self.coordinate == other.coordinate
        return NotImplemented

    def __ne__(self, other):
        """Define a non-equality test"""
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented
