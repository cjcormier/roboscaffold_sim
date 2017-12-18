from enum import Enum

from roboscaffold_sim.direction import Direction


# TODO: Break into seperate classes? use tupes/namedtupes as data
class SInstruction(Enum):
    NONE = (0, 0, True, False, False)
    STOP = (1, 0, False, False, False)

    DRIVE_LEFT = (2, 1, True, False, False)
    DRIVE_RIGHT = (3, 3, True, False, False)
    DRIVE_BACK = (4, 2, True, False, False)

    PICK_LEFT = (5, 1, False, True, False)
    PICK_RIGHT = (6, 3, False, True, False)
    PICK_FORWARD = (7, 0, False, True, False)
    PICK_BACK = (8, 2, False, True, False)

    DROP_LEFT = (9, 1, False, False, True)
    DROP_RIGHT = (10, 3, False, False, True)
    DROP_FORWARD = (11, 0, False, False, True)
    DROP_BACK = (12, 2, False, False, True)

    # TODO: Change from chained if to dict
    def get_left_turns(self) -> int:
        return self.value[1]

    def is_drive(self):
        return self.value[2]

    def is_pick(self):
        return self.value[3]

    def is_drop(self):
        return self.value[4]


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
