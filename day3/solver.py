#!/usr/bin/env python3


from copy import copy
import click
import sys


def load_wires():
    with open('input', 'r') as program:
        one, two = program.readlines()
        return one.split(','), two.split(',')



def trace_line_from_center(line):
    p = (0, 0)
    pts = [p]
    for move in line:
        direction = move[0]
        length = int(move[1:])
        if direction == 'R':
            pts.extend([(x, p[1]) for x in range(p[0]+1, p[0]+1 + length, 1)])
        elif direction == 'L':
            pts.extend([(x, p[1]) for x in range(p[0]-1, p[0]-1 - length, -1)])
        elif direction == 'U':
            pts.extend([(p[0], y) for y in range(p[1]+1, p[1]+1 + length, 1)])
        elif direction == 'D':
            pts.extend([(p[0], y) for y in range(p[1]-1, p[1]-1 - length, -1)])
        p = pts[-1]

    return pts


def manhattan_distance(pa, pb):
    return abs(pb[0] - pa[0]) + abs(pb[1] - pa[1])


one, two = load_wires()
s1 = set(trace_line_from_center(one))
s2 = set(trace_line_from_center(two))
print(f'{len(s1)} points in wire #1')
print(f'{len(s2)} points in wire #2')

collisions = s1.intersection(s2) - {(0, 0)}
print(f'{len(collisions)} collisions between #1 and #2, minus (0, 0): ')
print(collisions)

distances = [manhattan_distance((0, 0), p) for p in collisions]
print(f'manhattan distances for all these collisions, sorted: ')
print(sorted(distances))
