#!/usr/bin/env python3


import click


def compute_fuel(m):
    fuel = m // 3
    return fuel - 2


def compute_added_fuel(m):
    add = compute_fuel(m)
    if add <= 0:
        return 0
    return add + compute_added_fuel(add)


total_added_fuel = total = 0
with open('input', 'r') as _f:
    for module in _f.readlines():
        fuel = compute_fuel(int(module))
        total += fuel
        fuel += compute_added_fuel(fuel)
        total_added_fuel += fuel

click.secho(f'Total fuel needed: {total}', fg='green')
click.secho(f'Total fuel needed, including fuel itself: {total_added_fuel}', fg='green')
