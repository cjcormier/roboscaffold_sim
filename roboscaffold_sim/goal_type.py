from enum import Enum, auto


class GoalType(Enum):
    PLACE_BUILD_BLOCK = (0, False, True, False, True)
    PLACE_SCAFFOLD = (1, False, True, True, False)
    PICK_BUILD_BLOCK = (2, True, False, False, True)
    PICK_SCAFFOLD = (3, True, False, True, False)

    def is_pick(self) -> bool:
        return self.value[1]

    def is_place(self) -> bool:
        return self.value[2]

    def is_scaffold(self) -> bool:
        return self.value[3]

    def is_build(self) -> bool:
        return self.value[4]
