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

    def left_turns(self, times: int) -> None:
        for _ in range(times):
            self.direction = self.direction.left()

    def not_holding_block(self):
        return self.block == HeldBlock.NONE
