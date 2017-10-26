from enum import Enum, auto


class Direction(Enum):
    NORTH = auto()
    EAST = auto()
    SOUTH = auto()
    WEST = auto()

    def right(self):
        return _right[self]

    def left(self):
        return _left[self]


_right = {
    Direction.NORTH: Direction.EAST,
    Direction.EAST: Direction.SOUTH,
    Direction.SOUTH: Direction.WEST,
    Direction.WEST: Direction.NORTH
}

_left = {
    Direction.NORTH: Direction.WEST,
    Direction.EAST: Direction.NORTH,
    Direction.SOUTH: Direction.EAST,
    Direction.WEST: Direction.SOUTH
}
