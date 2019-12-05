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
    ADD = 1
    MUL = 2
    IN = 3
    OUT = 4
    HALT = 99


class OPMode(Enum):
    POS = 0
    IMM = 1


def parse_opcode(program, pointer):
    code = program[pointer] % 100
    return OPCode(code)


def parse_mode(ip, n):
    digit = ip // 10 ** (1 + n) % 10
    return OPMode(digit)


def read_parameter(program, pointer, n):
    mode = parse_mode(program[pointer], n)
    if mode is OPMode.IMM:
        return program[pointer + n]
    elif mode is OPMode.POS:
        address = program[pointer + n]
        return program[address]
    else:
        raise UnknownModeError


def run_instruction(program, pointer):
    opcode = parse_opcode(program, pointer)
    if opcode in (OPCode.ADD, OPCode.MUL):
        p1 = read_parameter(program, pointer, 1)
        p2 = read_parameter(program, pointer, 2)
        address = program[pointer + 3]
        old = program[address]
        if opcode is OPCode.ADD:
            program[address] = p1 + p2
        else:
            program[address] = p1 * p2
        click.secho(f'Value at #{address} changing from {old} to {program[address]}', fg='magenta')
        return pointer + 4
    elif opcode is OPCode.IN:
        address = program[pointer + 1]
        user_input = click.prompt('in?', type=int)
        program[address] = user_input
        click.secho(f'in: {input} (at #{address})', fg='yellow')
        return pointer + 2
    elif opcode is OPCode.OUT:
        p1 = read_parameter(program, pointer, 1)
        click.secho(f'out: {p1}', fg='green')
        return pointer + 2
    elif opcode is OPCode.HALT:
        raise HaltError
    else:
        raise UnknownOpcodeError


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

    dump(program, memory)
    return memory[0]


# run([3, 0, 4, 0, 99])
run(load_program())
