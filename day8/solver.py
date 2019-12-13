#!/usr/bin/env python3

from copy import copy


def load_passwd_sif():
    with open('input', 'r') as sif:
        return sif.readlines()[0].rstrip()


def get_layers(sif, width, height):
    layer_size = width * height
    sif_size = len(sif)
    for offset in range(0, sif_size, layer_size):
        yield sif[offset:offset+layer_size]


def print_layer(layer, width, height):
    for offset in range(0, height*width, width):
        for c in layer[offset:offset+width]:
            if c == '0':
                print('  ', end='')
            elif c == '1':
                print('##', end='')
            else:
                print('  ', end='')
        print('')


def merge_down_layers(layers, width, height):
    visible = copy(layers[0])

    for layer in layers[1:]:
        buffer = []
        for offset in range(width*height):
            if visible[offset] == '2':
                buffer.append(layer[offset])
            else:
                buffer.append(visible[offset])
        visible = ''.join(buffer)
    return visible


def main():
    passwd_sif = load_passwd_sif()
    width = 25
    height = 6

    # passwd_sif = '0222112222120000'
    # width = 2
    # height = 2

    layers = list(get_layers(passwd_sif, width, height))

    n0s = [layer.count('0') for layer in layers]
    min_n0 = min(n0s)
    layer = layers[n0s.index(min_n0)]

    print(layer.count('1') * layer.count('2'))
    # print_layer(layer, width, height)

    visible_layer = merge_down_layers(layers, width, height)
    print_layer(visible_layer, width, height)


if __name__ == '__main__':
    main()
