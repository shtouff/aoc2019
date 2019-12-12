#!/usr/bin/env python3

from enum import Enum
from copy import copy
from itertools import permutations
from multiprocessing import Process, Pipe

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
    user_input = ctx['stdin'].recv()
    ctx['memory'][address] = user_input
    return pointer


def op_output(ctx, pointer):
    p1, pointer = read_parameters(ctx, pointer, True)
    ctx['stdout'].send(p1)
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


def run(program, stdin, stdout):
    ctx = dict(memory=copy(program), stdin=stdin, stdout=stdout)
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


def get_thrusters_power(phase_seq):
    seq_len = len(phase_seq)
    acs = load_program()
    # acs = [3,26,1001,26,-4,26,3,27,1002,27,2,27,1,27,26,27,4,27,1001,28,-1,28,1005,28,6,99,0,0,5]
    # acs = [3,52,1001,52,-5,52,3,53,1,52,56,54,1007,54,5,55,1005,55,26,1001,54,-5,54,1105,1,12,1,53,54,53,1008,54,0,55,1001,55,1,55,2,53,55,53,4,53,1001,56,-1,56,1005,56,6,99,0,0,0,0,10]

    # create crossed pipes from one process to previous
    stdios = {phase: ['stdin', 'stdout'] for phase in phase_seq}
    for i in range(seq_len):
        stdios[phase_seq[i]][0], stdios[phase_seq[i-1]][1] = Pipe()

    processes = {}
    for phase in phase_seq:
        processes[phase] = Process(target=run, args=(acs, stdios[phase][0], stdios[phase][1]))
        processes[phase].start()

    # send phase of each process to stdout of previous process
    for i in range(seq_len):
        stdios[phase_seq[i-1]][1].send(phase_seq[i])

    # send initial signal to stdout of last process
    stdios[phase_seq[-1]][1].send(0)

    # feedback loop
    while True:
        # check if last process is halted
        processes[phase_seq[-1]].join(timeout=1)
        if processes[phase_seq[-1]].exitcode is not None:
            break

    # read last outpout from stdin of first process
    return stdios[phase_seq[0]][0].recv()


def main():
    max_power = 0

    for phase_seq in permutations([5, 6, 7, 8, 9]):
        power = get_thrusters_power(phase_seq)
        if power > max_power:
            click.secho(f'{power} is greater than {max_power}, pivoting.', fg='green')
            max_power = power
    click.secho(f'Max power = {max_power}', fg='magenta')


if __name__ == '__main__':
    main()
