#!/usr/bin/env python3

from enum import Enum
from copy import copy
from itertools import permutations

import click


def load_program():
    with open('input', 'r') as program:
        return [int(e) for e in program.readlines()[0].rstrip().split(',')]


class HaltError(Exception):
    pass


class UnknownOpcodeError(Exception):
    pass


class UnknownModeError(Exception):
    pass


class OPCode(Enum):
    ADD = 1    # addition
    MUL = 2    # multiplication
    IN = 3     # read stdin
    OUT = 4    # write stdout
    JIT = 5    # jump-if-true
    JIF = 6    # jump-if-false
    LT = 7     # less-than
    EQ = 8     # equals
    HALT = 99  # halt


class OPMode(Enum):
    POS = 0    # parameter value is at address
    IMM = 1    # parameter value is immediate


def parse_opcode(ctx, pointer):
    code = ctx['memory'][pointer] % 100
    return OPCode(code)


def parse_mode(ip, n):
    digit = ip // 10 ** (1 + n) % 10
    return OPMode(digit)


def read_parameters(ctx, pointer, *honor_modes):
    n = 0
    for honor_mode in honor_modes:
        n += 1
        if not honor_mode:
            yield ctx['memory'][pointer + n]
            continue

        mode = parse_mode(ctx['memory'][pointer], n)
        if mode is OPMode.IMM:
            yield ctx['memory'][pointer + n]
        elif mode is OPMode.POS:
            address = ctx['memory'][pointer + n]
            yield ctx['memory'][address]
        else:
            raise UnknownModeError
    yield pointer + 1 + n  # set EIP to after opcode + parameters


def op_addition(ctx, pointer):
    p1, p2, address, pointer = read_parameters(ctx, pointer, True, True, False)
    ctx['memory'][address] = p1 + p2
    return pointer


def op_multiplication(ctx, pointer):
    p1, p2, address, pointer = read_parameters(ctx, pointer, True, True, False)
    ctx['memory'][address] = p1 * p2
    return pointer


def op_input(ctx, pointer):
    address, pointer = read_parameters(ctx, pointer, False)
    user_input = ctx['stdin'].pop()
    ctx['memory'][address] = user_input
    return pointer


def op_output(ctx, pointer):
    p1, pointer = read_parameters(ctx, pointer, True)
    ctx['stdout'].append(p1)
    return pointer


def op_jump_if_true(ctx, pointer):
    p1, p2, pointer = read_parameters(ctx, pointer, True, True)
    return p2 if p1 != 0 else pointer


def op_jump_if_false(ctx, pointer):
    p1, p2, pointer = read_parameters(ctx, pointer, True, True)
    return p2 if p1 == 0 else pointer


def op_lessthan(ctx, pointer):
    p1, p2, address, pointer = read_parameters(ctx, pointer, True, True, False)
    ctx['memory'][address] = 1 if p1 < p2 else 0
    return pointer


def op_equals(ctx, pointer):
    p1, p2, address, pointer = read_parameters(ctx, pointer, True, True, False)
    ctx['memory'][address] = 1 if p1 == p2 else 0
    return pointer


def run_instruction(ctx, pointer):
    opcode = parse_opcode(ctx, pointer)
    op_funcs = {
        OPCode.ADD: op_addition,
        OPCode.MUL: op_multiplication,
        OPCode.IN: op_input,
        OPCode.OUT: op_output,
        OPCode.JIT: op_jump_if_true,
        OPCode.JIF: op_jump_if_false,
        OPCode.LT: op_lessthan,
        OPCode.EQ: op_equals,
    }
    if opcode in op_funcs:
        pointer = op_funcs[opcode](ctx, pointer)
    elif opcode is OPCode.HALT:
        raise HaltError
    else:
        raise UnknownOpcodeError

    return pointer


def run(program, phase, sigin):
    ctx = dict(memory=copy(program), stdin=[sigin, phase], stdout=[])
    pointer = 0

    try:
        while True:
            pointer = run_instruction(ctx, pointer)
    except HaltError:
        # no-op
        pass
    except UnknownOpcodeError:
        click.secho(f'Unknown opcode: {ctx["memory"][pointer]} at position {pointer}:', fg='red')
    except UnknownModeError:
        click.secho(f'Unknown mode: {ctx["memory"][pointer]} at position {pointer}:', fg='red')

    return ctx['stdout'].pop()


def get_thrusters_power(phase_seq):
    acs = load_program()
    sigout = 0
    for phase in phase_seq:
        sigout = run(acs, phase=phase, sigin=sigout)
    return sigout


def main():
    max_power = 0

    for phase_seq in permutations([0, 1, 2, 3, 4]):
        power = get_thrusters_power(phase_seq)
        if power > max_power:
            click.secho(f'{power} is greater than {max_power}, pivoting.', fg='green')
            max_power = power

    click.secho(f'Max power = {max_power}', fg='magenta')


if __name__ == '__main__':
    main()
