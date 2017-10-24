from enum import Enum, auto


class BuildingBlockState:
    pass


class ScaffoldInstruction(Enum):
    NONE = auto()
    STOP = auto()

    DRIVE_LEFT = auto()
    DRIVE_RIGHT = auto()

    PICK_LEFT = auto()
    PICK_RIGHT = auto()
    PICK_FORWARD = auto()

    DROP_LEFT = auto()
    DROP_RIGHT = auto()
    DROP_FORWARD = auto()


class ScaffoldState:
    def __init__(self, instruction: ScaffoldInstruction = ScaffoldInstruction.NONE):
        self.instruction: ScaffoldInstruction = instruction
