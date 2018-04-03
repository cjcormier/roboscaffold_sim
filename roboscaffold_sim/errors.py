from roboscaffold_sim.coordinate import CoordinateList


class RoboScaffoldingError(Exception):
    """Base class for exceptions in this project."""


class TargetError(RoboScaffoldingError):
    """Exception raised for errors regarding target structure.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, target: CoordinateList, message: str) -> None:
        self.target = target
        self.message = message


class GoalError(RoboScaffoldingError):
    """Exception raised for errors regarding goal creation.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message: str) -> None:
        self.message = message


class RobotActionError(RoboScaffoldingError):
    """Exception raised for errors occuring during robot movement and actuation.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message: str)  -> None:
        self.message = message
