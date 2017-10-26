from typing import List, Optional, TypeVar, Set, Iterable

from roboscaffold_sim.direction import Direction

Coord = TypeVar('Coord', bound='Coordinate')

CoordinateList_ = List[Coord]
CoordinateSet_ = Set[Coord]
Coordinates_ = Iterable[Optional[Coord]]


class Coordinate:

    def __init__(self, x: int, y: int):
        self._x: int = x
        self._y: int = y

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    def get_neighbors(self) -> CoordinateList_:
        return [self+Up, self+Right, self+Down, self+Left]

    def get_coord_in_direction(self, direction):
        coord_change = {
            Direction.NORTH: Up,
            Direction.EAST: Right,
            Direction.SOUTH: Down,
            Direction.WEST: Left
        }
        return self + coord_change[direction]

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
        return hash((self.x, self.y))

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


CoordinateList = List[Coordinate]
CoordinateSet = Set[Coordinate]
Coordinates = Iterable[Optional[Coordinate]]

Up = Coordinate(0, -1)
Right = Coordinate(1, 0)
Down = Coordinate(0, 1)
Left = Coordinate(-1, 0)
