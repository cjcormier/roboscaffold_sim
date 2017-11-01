from enum import Enum, auto

from roboscaffold_sim.direction import Direction


class SInstruction(Enum):
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
    def __init__(self, instruction: SInstruction = SInstruction.NONE) -> None:
        self.instruction: SInstruction = instruction

    def set_drive_instr(self, curr_dir: Direction, desired_dir: Direction) -> Direction:
        count = 0
        working_dir = curr_dir
        while working_dir != desired_dir:
            working_dir = working_dir.left()
            count += 1

        if count == 0:
            self.instruction = SInstruction.NONE
        elif count == 1:
            self.instruction = SInstruction.DRIVE_LEFT
        elif count == 2:
            self.instruction = SInstruction.DRIVE_UTURN
        elif count == 3:
            self.instruction = SInstruction.DRIVE_RIGHT
        return desired_dir

    def set_pick_instr(self, curr_dir: Direction, desired_dir: Direction) -> Direction:
        count = 0
        working_dir = curr_dir
        while working_dir != desired_dir:
            working_dir = working_dir.left()
            count += 1

        if count == 0:
            self.instruction = SInstruction.PICK_FORWARD
        elif count == 1:
            self.instruction = SInstruction.PICK_LEFT
        elif count == 2:
            self.instruction = SInstruction.PICK_BACK
        elif count == 3:
            self.instruction = SInstruction.PICK_RIGHT
        return desired_dir

    def set_drop_instr(self, curr_dir: Direction, desired_dir: Direction) -> Direction:
        count = 0
        working_dir = curr_dir
        while working_dir != desired_dir:
            working_dir = working_dir.left()
            count += 1

        if count == 0:
            self.instruction = SInstruction.DROP_FORWARD
        elif count == 1:
            self.instruction = SInstruction.DROP_LEFT
        elif count == 3:
            self.instruction = SInstruction.DROP_RIGHT
        return desired_dir

    def __repr__(self):
        return self.instruction.name
