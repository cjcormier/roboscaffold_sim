from typing import List, Optional, Set, Iterable

from roboscaffold_sim.direction import Direction

CoordinateList_ = List['Coordinate']
CoordinateSet_ = Set['Coordinate']
Coordinates_ = Iterable[Optional['Coordinate']]


class Coordinate:

    def __init__(self, x: int, y: int) -> None:
        self.x: int = x
        self.y: int = y

    def get_neighbors(self) -> CoordinateList_:
        return [self+Up, self+Right, self+Down, self+Left]

    def rotate_cw(self) -> 'Coordinate':
        return Coordinate(-self.y, self.x)

    def rotate_180(self) -> 'Coordinate':
        return Coordinate(-self.x, -self.y)

    def get_coord_in_direction(self, direction):
        return self + coord_change[direction]

    def get_direction_of_coord(self, other):
        if other.x == self.x:
            if other.y > self.y:
                return Direction.SOUTH
            elif other.y < self.y:
                return Direction.NORTH
        elif other.y == self.y:
            if other.x > self.x:
                return Direction.EAST
            elif other.x < self.x:
                return Direction.WEST
        return None

    def rotate_ccw(self) -> 'Coordinate':
        return Coordinate(self.y, -self.x)

    @staticmethod
    def from_string(string: str):
        string = string.strip('()')
        x, y = tuple(string.split(','))
        return Coordinate(int(x), int(y))

    def __eq__(self, other):
        """Override the default Equals behavior"""
        if isinstance(other, self.__class__):
            return self.x == other.x and self.y == other.y
        return NotImplemented

    def __ne__(self, other):
        """Define a non-equality test"""
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __hash__(self):
        """Override the default hash behavior (that returns the id or the object)"""
        # Assumes x and y within -100 to 100
        # for general hash function use hash((self.x, self.y))
        return self.x*100 + self.y

    def __add__(self, other):
        if isinstance(other, self.__class__):
            return Coordinate(self.x+other.x, self.y+other.y)
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, self.__class__):
            return self.__add__(other)
        return NotImplemented

    def __str__(self):
        return f'({self.x},{self.y})'

    def __repr__(self):
        return f'({self.x},{self.y})'


CoordinateList = List[Coordinate]
CoordinateSet = Set[Coordinate]
Coordinates = Iterable[Optional[Coordinate]]

Up = Coordinate(0, -1)
Right = Coordinate(1, 0)
Down = Coordinate(0, 1)
Left = Coordinate(-1, 0)
Origin = Coordinate(0, 0)

coord_change = {
    Direction.NORTH: Up,
    Direction.EAST: Right,
    Direction.SOUTH: Down,
    Direction.WEST: Left
}
