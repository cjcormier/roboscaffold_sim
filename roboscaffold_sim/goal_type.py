from enum import Enum, auto


# TODO: Decide if these should be different classes, use tupes/namedtupes as data
class GoalType(Enum):
    PLACE_BUILD_BLOCK = auto()
    PLACE_SCAFFOLD = auto()
    PICK_BUILD_BLOCK = auto()
    PICK_SCAFFOLD = auto()

    def is_pick(self) -> bool:
        return self in [self.PICK_SCAFFOLD, self.PICK_BUILD_BLOCK]

    def is_place(self) -> bool:
        return self in [self.PLACE_SCAFFOLD, self.PLACE_BUILD_BLOCK]

    def is_scaffold(self) -> bool:
        return self in [self.PLACE_SCAFFOLD, self.PICK_SCAFFOLD]

    def is_build(self) -> bool:
        return self in [self.PLACE_BUILD_BLOCK, self.PICK_BUILD_BLOCK]
