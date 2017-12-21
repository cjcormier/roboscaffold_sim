from typing import TextIO, List, Tuple

from roboscaffold_sim.coordinate import Coordinate, Origin, CoordinateList
from roboscaffold_sim.goal_type import GoalType
from roboscaffold_sim.state.scaffolding_state import SInstruction
from roboscaffold_sim.state.simulation_state import Goal


def create_goal(string: str) -> Goal:
    coord, gtype = string.split(':')
    coord = Coordinate.from_string(coord)
    gtype = GoalType[gtype]
    return Goal(coord, gtype, Origin, Origin)


def create_scaffold(string: str) -> Tuple[Coordinate, SInstruction]:
    coord, stype = string.split(':')
    coord = Coordinate.from_string(coord)
    stype = SInstruction[stype]
    return coord, stype


def load_coords(file: TextIO) -> CoordinateList:
    coords: CoordinateList = []
    line = file.readline()
    for block in line.split():
        coords.append(Coordinate.from_string(block))
    return coords


def load(file_name: str) -> Tuple[List[Coordinate], List[Goal], List[SInstruction]]:
    goal_stacks = []
    sinstructions = []
    with open(file_name, 'r') as file:
        target = load_coords(file)
        line = file.readline()
        while line != '':
            goals = line.strip('0123456789 goals:\n').split(' ')
            goals = [create_goal(goal) for goal in goals]
            goal_stacks.append(goals)
            line = file.readline()
            scaffolds = line.strip('0123456789 scafolds:\n').split(' ')
            scaffolds = [create_scaffold(s) for s in scaffolds]
            sinstructions.append(scaffolds)

            line = file.readline()
    return target, goal_stacks, sinstructions


def compare_saves(file_1: str, file_2: str)->bool:
    struct_1, goal_stacks_1, sinstructions_1 = load(file_1)
    struct_2, goal_stacks_2, sinstructions_2 = load(file_2)

    if set(struct_1) != set(struct_2) or len(goal_stacks_1) != len(goal_stacks_2) or \
        len(sinstructions_1) != len(sinstructions_2):
        return False

    for goal_stack_1, goal_stack_2 in zip(goal_stacks_1, goal_stacks_2):
        if set(goal_stack_1) != set(goal_stack_2):
            return False

    for sinstruction_1, sinstruction_2 in zip(sinstructions_1, sinstructions_2):
        if set(sinstruction_1) != set(sinstruction_2):
            return False

    return True
