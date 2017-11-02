from typing import Optional

from roboscaffold_sim.coordinate import Coordinate, CoordinateList
from roboscaffold_sim.state.builder_state import BuilderState
from roboscaffold_sim.state.simulation_state import SimulationState
import abc


class BasicStrategy:
    __metaclass__ = abc.ABCMeta

    def __init__(self, sim_state: SimulationState):
        self.sim_state = sim_state
        self.finished: bool = False

    @abc.abstractmethod
    def update(self, robo_coord, robot) -> bool:
        pass

    @abc.abstractmethod
    def update_scaffolding(self, robo_coord: Coordinate, robot: BuilderState):
        pass

    @abc.abstractmethod
    def determine_new_goals(self, robo_coord: Coordinate, robot: BuilderState):
        pass

    @abc.abstractmethod
    def get_next_unfinished_block(self) -> Optional[Coordinate]:
        pass

    @staticmethod
    @abc.abstractmethod
    def configure_target(target: CoordinateList, allow_offset: bool=True) -> CoordinateList:
        pass
