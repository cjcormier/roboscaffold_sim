from typing import List, Optional, TypeVar, Set, Iterable

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


CoordinateList = List[Coordinate]
CoordinateSet = Set[Coordinate]
Coordinates = Iterable[Optional[Coordinate]]

Up = Coordinate(1, 0)
Right = Coordinate(0, 1)
Down = Coordinate(-1, 0)
Left = Coordinate(0, -1)