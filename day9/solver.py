#!/usr/bin/env python3


from enum import Enum
from multiprocessing import Process, Pipe
import sys

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
    ARB = 9    # adjust rel_base
    HALT = 99  # halt


class OPMode(Enum):
    POS = 0    # parameter value is at address
    IMM = 1    # parameter value is immediate
    REL = 2    # parameter value is relative


def parse_opcode(ctx, pointer):
    code = ctx['memory'][pointer] % 100
    return OPCode(code)


def parse_mode(ip, n):
    digit = ip // 10 ** (1 + n) % 10
    return OPMode(digit)


def read_parameters(ctx, pointer, *honor_addresses):
    """"
    first historical mode was position
    parameters that an instruction writes to will never be in immediate mode.
    third mode (relative), is similar to position. So parameters that an instruction writes to (addresses) COULD be in
    relative mode, too.
    So we NEED to know if the read parameter will be used as an address we will write to, hence the honor_addresses.
    """
    n = 0
    for honor_address in honor_addresses:
        n += 1
        mode = parse_mode(ctx['memory'][pointer], n)
        if mode is OPMode.IMM:
            yield ctx['memory'][pointer + n]
        elif mode in (OPMode.POS, OPMode.REL):
            address = ctx['memory'][pointer + n]
            if mode is OPMode.REL:
                address += ctx['rel_base']
            if honor_address:
                yield ctx['memory'].get(address, 0)
            else:
                yield address
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


def op_adjust_rel_base(ctx, pointer):
    p1, pointer = read_parameters(ctx, pointer, True)
    ctx['rel_base'] += p1
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
        OPCode.ARB: op_adjust_rel_base,
    }
    if opcode in op_funcs:
        pointer = op_funcs[opcode](ctx, pointer)
    elif opcode is OPCode.HALT:
        raise HaltError
    else:
        raise UnknownOpcodeError

    return pointer


def run(program, stdin, stdout):
    ctx = {
        'memory': {a: program[a] for a in range(len(program))},
        'stdin': stdin,
        'stdout': stdout,
        'rel_base': 0,
    }
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
    except Exception as e:
        click.secho(f'Unknown exception: {e}. EIP = {pointer}', fg='red')
        raise

    sys.exit(ctx['memory'][0])


def test():
    # program = [109, 1, 204, -1, 1001, 100, 1, 100, 1008, 100, 16, 101, 1006, 101, 0, 99]  # quine
    # program = [1102, 34915192, 34915192, 7, 4, 7, 99, 0]  # 16-digit number
    program = [104, 1125899906842624, 99]  # middle number

    pin, stdout = Pipe(False)

    p = Process(target=run, args=(program, None, stdout))
    p.start()

    p.join()
    stdout.close()
    lines = []
    while True:
        try:
            lines.append(str(pin.recv()))
        except EOFError:
            break

    print(','.join(lines))
    return p.exitcode


def boost():
    program = load_program()

    pin, stdout = Pipe(False)
    stdin, pout = Pipe(False)

    p = Process(target=run, args=(program, stdin, stdout))
    p.start()

    pout.send(1)
    p.join()
    stdout.close()
    lines = []
    while True:
        try:
            lines.append(str(pin.recv()))
        except EOFError:
            break

    print(','.join(lines))
    return p.exitcode


def main():
    click.secho(f'Exit code: {boost()}', fg='magenta')


if __name__ == '__main__':
    main()
