from enum import Enum, auto

from roboscaffold_sim.direction import Direction


# TODO: Break into seperate classes? use tupes/namedtupes as data
class SInstruction(Enum):
    NONE = auto()
    STOP = auto()

    DRIVE_LEFT = auto()
    DRIVE_RIGHT = auto()
    DRIVE_BACK = auto()

    PICK_LEFT = auto()
    PICK_RIGHT = auto()
    PICK_FORWARD = auto()
    PICK_BACK = auto()

    DROP_LEFT = auto()
    DROP_RIGHT = auto()
    DROP_FORWARD = auto()
    DROP_BACK = auto()

    # TODO: Change from chained if to dict
    def get_left_turns(self) -> int:
        if self in [SInstruction.NONE, SInstruction.PICK_FORWARD, SInstruction.DROP_FORWARD,SInstruction.STOP]:
            return 0
        elif self in [SInstruction.DRIVE_LEFT, SInstruction.PICK_LEFT, SInstruction.DROP_LEFT]:
            return 1
        elif self in [SInstruction.DRIVE_BACK, SInstruction.PICK_BACK, SInstruction.DROP_BACK]:
            return 2
        elif self in [SInstruction.DRIVE_RIGHT, SInstruction.PICK_RIGHT, SInstruction.DROP_RIGHT]:
            return 3

    def is_drive(self):
        return self in [SInstruction.DRIVE_LEFT, SInstruction.DRIVE_RIGHT,
                        SInstruction.DRIVE_BACK, SInstruction.NONE]

    def is_pick(self):
        return self in [SInstruction.PICK_LEFT, SInstruction.PICK_RIGHT,
                        SInstruction.PICK_FORWARD, SInstruction.PICK_BACK]

    def is_drop(self):
        return self in [SInstruction.DROP_LEFT, SInstruction.DROP_RIGHT,
                        SInstruction.DROP_FORWARD, SInstruction.DROP_BACK]


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
            self.instruction = SInstruction.DRIVE_BACK
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
        elif count == 2:
            self.instruction = SInstruction.DROP_BACK
        elif count == 3:
            self.instruction = SInstruction.DROP_RIGHT
        return desired_dir

    def __eq__(self, other):
        """Override the default Equals behavior"""
        if isinstance(other, self.__class__):
            return self.instruction == other.instruction
        return NotImplemented

    def __repr__(self):
        return self.instruction.name
