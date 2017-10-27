from enum import Enum, auto

from roboscaffold_sim.direction import Direction


class BuildingBlockState:
    pass


class ScaffoldInstruction(Enum):
    NONE = auto()
    STOP = auto()

    DRIVE_LEFT = auto()
    DRIVE_RIGHT = auto()
    DRIVE_UTURN = auto()

    PICK_LEFT = auto()
    PICK_RIGHT = auto()
    PICK_FORWARD = auto()
    PICK_BACK = auto()

    DROP_LEFT = auto()
    DROP_RIGHT = auto()
    DROP_FORWARD = auto()


class ScaffoldState:
    def __init__(self, instruction: ScaffoldInstruction = ScaffoldInstruction.NONE):
        self.instruction: ScaffoldInstruction = instruction


def get_drive_instr(curr_dir: Direction, desired_dir: Direction) -> ScaffoldInstruction:
    count = 0
    working_dir = curr_dir
    while working_dir != desired_dir:
        working_dir = working_dir.left()
        count += 1

    if count == 0:
        return ScaffoldInstruction.NONE
    elif count == 1:
        return ScaffoldInstruction.DRIVE_LEFT
    elif count == 2:
        return ScaffoldInstruction.DRIVE_UTURN
    elif count == 3:
        return ScaffoldInstruction.DRIVE_RIGHT

    raise Exception('Should not need to turn left more than 3 times')


def get_pick_instr(curr_dir: Direction, desired_dir: Direction) \
        -> ScaffoldInstruction:
    count = 0
    working_dir = curr_dir
    while working_dir != desired_dir:
        working_dir = working_dir.left()
        count += 1

    if count == 0:
        return ScaffoldInstruction.PICK_FORWARD
    elif count == 1:
        return ScaffoldInstruction.PICK_LEFT
    elif count == 2:
        return ScaffoldInstruction.PICK_BACK
    elif count == 3:
        return ScaffoldInstruction.PICK_RIGHT

    raise Exception('Should not need to turn left more than 3 times')


def get_drop_instr(curr_dir: Direction, desired_dir: Direction) \
        -> ScaffoldInstruction:
    count = 0
    working_dir = curr_dir
    while working_dir != desired_dir:
        working_dir = working_dir.left()
        count += 1

    if count == 0:
        return ScaffoldInstruction.DROP_FORWARD
    elif count == 1:
        return ScaffoldInstruction.DROP_LEFT
    elif count == 3:
        return ScaffoldInstruction.DROP_RIGHT

    raise Exception('Should not need to turn left  2 times or more than 3 times')
