from enum import Enum, auto

from roboscaffold_sim.direction import Direction


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
    DROP_BEHIND = auto()


class ScaffoldState:
    def __init__(self, instruction: ScaffoldInstruction = ScaffoldInstruction.NONE):
        self.instruction: ScaffoldInstruction = instruction

    def set_drive_instr(self, curr_dir: Direction, desired_dir: Direction) -> Direction:
        count = 0
        working_dir = curr_dir
        while working_dir != desired_dir:
            working_dir = working_dir.left()
            count += 1

        if count == 0:
            self.instruction = ScaffoldInstruction.NONE
        elif count == 1:
            self.instruction = ScaffoldInstruction.DRIVE_LEFT
        elif count == 2:
            self.instruction = ScaffoldInstruction.DRIVE_UTURN
        elif count == 3:
            self.instruction = ScaffoldInstruction.DRIVE_RIGHT
        return desired_dir

    def set_pick_instr(self, curr_dir: Direction, desired_dir: Direction) -> Direction:
        count = 0
        working_dir = curr_dir
        while working_dir != desired_dir:
            working_dir = working_dir.left()
            count += 1

        if count == 0:
            self.instruction = ScaffoldInstruction.PICK_FORWARD
        elif count == 1:
            self.instruction = ScaffoldInstruction.PICK_LEFT
        elif count == 2:
            self.instruction = ScaffoldInstruction.PICK_BACK
        elif count == 3:
            self.instruction = ScaffoldInstruction.PICK_RIGHT
        return desired_dir

    def set_drop_instr(self, curr_dir: Direction, desired_dir: Direction) -> Direction:
        count = 0
        working_dir = curr_dir
        while working_dir != desired_dir:
            working_dir = working_dir.left()
            count += 1

        if count == 0:
            self.instruction = ScaffoldInstruction.DROP_FORWARD
        elif count == 1:
            self.instruction = ScaffoldInstruction.DROP_LEFT
        elif count == 3:
            self.instruction = ScaffoldInstruction.DROP_RIGHT
        return desired_dir

    def __repr__(self):
        return self.instruction.name
