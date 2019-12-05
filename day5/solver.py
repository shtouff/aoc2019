#!/usr/bin/env python3

from enum import Enum
from copy import copy
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


def parse_opcode(program, pointer):
    code = program[pointer] % 100
    return OPCode(code)


def parse_mode(ip, n):
    digit = ip // 10 ** (1 + n) % 10
    return OPMode(digit)


def read_parameters(program, pointer, *honor_modes):
    n = 0
    for honor_mode in honor_modes:
        n += 1
        if not honor_mode:
            yield program[pointer + n]
            continue

        mode = parse_mode(program[pointer], n)
        if mode is OPMode.IMM:
            yield program[pointer + n]
        elif mode is OPMode.POS:
            address = program[pointer + n]
            yield program[address]
        else:
            raise UnknownModeError
    yield pointer + 1 + n  # set EIP to after opcode + parameters


def op_addition(program, pointer):
    p1, p2, address, pointer = read_parameters(program, pointer, True, True, False)
    program[address] = p1 + p2
    return pointer


def op_multiplication(program, pointer):
    p1, p2, address, pointer = read_parameters(program, pointer, True, True, False)
    program[address] = p1 * p2
    return pointer


def op_input(program, pointer):
    address, pointer = read_parameters(program, pointer, False)
    user_input = click.prompt('in?', type=int)
    program[address] = user_input
    click.secho(f'in: {user_input} (at #{address})', fg='yellow')
    return pointer


def op_output(program, pointer):
    p1, pointer = read_parameters(program, pointer, True)
    click.secho(f'out: {p1}', fg='green')
    return pointer


def op_jump_if_true(program, pointer):
    p1, p2, pointer = read_parameters(program, pointer, True, True)
    return p2 if p1 != 0 else pointer


def op_jump_if_false(program, pointer):
    p1, p2, pointer = read_parameters(program, pointer, True, True)
    return p2 if p1 == 0 else pointer


def op_lessthan(program, pointer):
    p1, p2, address, pointer = read_parameters(program, pointer, True, True, False)
    program[address] = 1 if p1 < p2 else 0
    return pointer


def op_equals(program, pointer):
    p1, p2, address, pointer = read_parameters(program, pointer, True, True, False)
    program[address] = 1 if p1 == p2 else 0
    return pointer


def run_instruction(program, pointer):
    opcode = parse_opcode(program, pointer)
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
        pointer = op_funcs[opcode](program, pointer)
    elif opcode is OPCode.HALT:
        raise HaltError
    else:
        raise UnknownOpcodeError

    return pointer


def dump(program, memory):
    for v in range(0, len(program), 8):
        click.secho(f'{v:>3}:  [', fg='green', nl=False)
        for e, f in zip(program[v:v+8], memory[v:v+8]):
            if e != f:
                color = 'magenta'
            else:
                color = 'green'
            click.secho(f'{e:>10}', fg=color, nl=False)
        click.secho('] => [', fg='green', nl=False)
        for e, f in zip(program[v:v+8], memory[v:v+8]):
            if e != f:
                color = 'yellow'
            else:
                color = 'green'
            click.secho(f'{f:>10}', fg=color, nl=False)
        click.secho(']', fg='green')


def run(program):
    memory = copy(program)
    pointer = 0

    try:
        while True:
            pointer = run_instruction(memory, pointer)
    except HaltError:
        click.secho('Program ran successfully:', fg='green')
    except UnknownOpcodeError:
        click.secho(f'Unknown opcode: {memory[pointer]} at position {pointer}:', fg='red')
    except UnknownModeError:
        click.secho(f'Unknown mode: {memory[pointer]} at position {pointer}:', fg='red')

    dump(program, memory)
    return memory[0]


TEST = lambda: run(load_program())

echo_stdin = lambda: run([3, 0, 4, 0, 99])

equal_to_8 = lambda: run([3, 9, 8, 9, 10, 9, 4, 9, 99, -1, 8])
less_than_8 = lambda: run([3, 9, 7, 9, 10, 9, 4, 9, 99, -1, 8])

less_equal_or_greater_than_8 = lambda: run([
    3, 21, 1008, 21, 8, 20, 1005, 20, 22, 107, 8, 21, 20, 1006, 20, 31, 1106, 0, 36, 98, 0, 0, 1002, 21, 125, 20, 4,
    20, 1105, 1, 46, 104, 999, 1105, 1, 46, 1101, 1000, 1, 20, 4, 20, 1105, 1, 46, 98, 99
])

TEST()
