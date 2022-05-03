"""Solves an instance.

Modify this file to implement your own solvers.

For usage, run `python3 solve.py --help`.
"""

import argparse
from random import *
from pathlib import Path
from typing import Callable, Dict
from math import sqrt
from point import Point

from instance import Instance
from solution import Solution
from file_wrappers import StdinFileWrapper, StdoutFileWrapper


def solve_naive(instance: Instance) -> Solution:
    length = instance.grid_side_length
    service_rad = instance.coverage_radius
    penalty_rad = instance.penalty_radius
    city_list = instance.cities 

    ret = []
    citymap = []
    towermap = []
    #initialize a tower and city map of all zeros
    insert = []
    for i in range(length):
        insert.append(0)
    for j in range(length):
        citymap.append(insert.copy())
        towermap.append(insert.copy())
    #Mark which points contain a city
    for loc in city_list:
        x_part = loc.x
        y_part = loc.y
        citymap[x_part][y_part] = 1
    #BEGIN ALGORITHM
    city_count = len(city_list)
    while(city_count > 0):
        #weights is list of weight values
        #weights_dict is dictionary mapping index of weight value to its point
        weights = []
        weights_dict = {}
        penalties = []
        penalties_dict = {}
        #go through and find the locs that cover the most cities
        for x_set in range(length):
            for y_set in range(length):
                weights_insert, hitlist = check_range(x_set, y_set, service_rad, citymap, length)
                if( weights_insert > 0):
                    weights_dict.update({len(weights): Point(x_set, y_set)})
                    weights.append(weights_insert)
        max_weight = max(weights)
        max_coverage_cities = []
        num_rem = weights.count(max_weight)
        while(num_rem > 0):
            key = weights.index(max_weight)
            key_loc = weights_dict.get(key)
            max_coverage_cities.append(key_loc)
            weights[key] = -1
            num_rem -= 1
        #go through and find the locs that conflict with other towers the least
        for pen in max_coverage_cities:
            pen_insert, conflicts = check_range(pen.x, pen.y, penalty_rad, towermap, length)
            penalties_dict.update({len(penalties): pen})
            penalties.append(pen_insert)

        min_pen = min(penalties)
        min_penalty_cities = []
        nums_rem = penalties.count(min_pen)
        while(nums_rem > 0):
            key = penalties.index(min_pen)
            key_loc = penalties_dict.get(key)
            min_penalty_cities.append(key_loc)
            penalties[key] = 100000000
            nums_rem -= 1
        chosen = randint(0, len(min_penalty_cities) - 1)
        chosen_one = min_penalty_cities[chosen]
        #The towers that result from the min are the ones we want to choose from
        #Update the maps and iterate again
        throw, targets = check_range(chosen_one.x, chosen_one.y, service_rad, citymap, length)
        update_step(towermap, citymap, chosen_one.x, chosen_one.y, targets)
        ret.append(chosen_one)
        if(citymap[chosen_one.x][chosen_one.y] == 1):
            city_count -= 1
        city_count -= len(targets)
    #Return the list of chosen cities [Points]
    return Solution(instance=instance, towers=ret)

def update_step(tower, citymap, x, y, lst):
    for point in lst:
        citymap[point[0]][point[1]] = 0
    tower[x][y] = 1
    return
def check_range(x, y, rs, map, length):
    counter = 0
    lst = []
    for i in range(-1 * rs, rs + 1):
        for j in range(-1 * rs, rs + 1):
            if(x + i >= 0 and y + j >= 0 and x + i < length and y + j < length):
                temp = x + i
                temp2 = y + j
                temp_l = sqrt((temp - x)**2 + (temp2 - y)**2)
                if temp_l <= rs and map[temp][temp2] == 1:
                    counter += 1
                    lst.append((temp, temp2))
    return counter, lst




SOLVERS: Dict[str, Callable[[Instance], Solution]] = {
    "naive": solve_naive
}


# You shouldn't need to modify anything below this line.
def infile(args):
    if args.input == "-":
        return StdinFileWrapper()

    return Path(args.input).open("r")


def outfile(args):
    if args.output == "-":
        return StdoutFileWrapper()

    return Path(args.output).open("w")


def main(args):
    with infile(args) as f:
        instance = Instance.parse(f.readlines())
        solver = SOLVERS[args.solver]
        solution = solver(instance)
        assert solution.valid()
        with outfile(args) as g:
            print("# Penalty: ", solution.penalty(), file=g)
            solution.serialize(g)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Solve a problem instance.")
    parser.add_argument("input", type=str, help="The input instance file to "
                        "read an instance from. Use - for stdin.")
    parser.add_argument("--solver", required=True, type=str,
                        help="The solver type.", choices=SOLVERS.keys())
    parser.add_argument("output", type=str,
                        help="The output file. Use - for stdout.",
                        default="-")
    main(parser.parse_args())
