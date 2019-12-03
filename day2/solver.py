#!/usr/bin/env python3


from copy import copy
import click
import sys


def load_program():
    with open('input', 'r') as program:
        return [int(e) for e in program.readlines()[0].rstrip().split(',')]


class HaltError(Exception):
    pass


class UnknownOpcodeError(Exception):
    pass


def run_opcode(program, pointer):
    opcode = program[pointer]
    if opcode in (1, 2):
        op1 = program[pointer + 1]
        op2 = program[pointer + 2]
        res = program[pointer + 3]
        old = program[res]
        if opcode == 1:
            program[res] = program[op1] + program[op2]
        else:
            program[res] = program[op1] * program[op2]
        click.secho(f'Value at #{res} changing from {old} to {program[res]}', fg='magenta')
        return pointer + 4
    elif opcode == 99:
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
            click.secho(f'{e:>8}', fg=color, nl=False)
        click.secho('] => [', fg='green', nl=False)
        for e, f in zip(program[v:v+8], memory[v:v+8]):
            if e != f:
                color = 'yellow'
            else:
                color = 'green'
            click.secho(f'{f:>8}', fg=color, nl=False)
        click.secho(']', fg='green')


program = load_program()


def puzzle(noun, verb):
    memory = copy(program)
    pointer = 0

    # fixes from error 1202
    memory[1] = noun
    memory[2] = verb

    try:
        while True:
            pointer = run_opcode(memory, pointer)
    except HaltError:
        click.secho('Program ran successfully:', fg='green')
    except UnknownOpcodeError:
        click.secho(f'Unknown opcode: {memory[pointer]} at position {pointer}:', fg='red')

    dump(program, memory)
    return memory[0]



#print(puzzle(noun=12, verb=2))
for noun in range(100):
    for verb in range(100):
        if puzzle(noun, verb) == 19690720:
            print(f'{noun}, {verb} => {noun*100+verb}')
            sys.exit(0)

