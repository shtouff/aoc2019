#!/usr/bin/env python3


def load_passwd_sif():
    with open('input', 'r') as sif:
        return sif.readlines()[0].rstrip()


def get_layers(sif, width, height):
    layer_size = width * height
    sif_size = len(sif)
    for i in range(0, sif_size, layer_size):
        yield sif[i:i+layer_size]


def main():
    passed_sif = load_passwd_sif()
    layers = list(get_layers(passed_sif, 25, 6))

    n0s = [layer.count('0') for layer in layers]
    min_n0 = min(n0s)
    layer = layers[n0s.index(min_n0)]

    print(layer.count('1') * layer.count('2'))


if __name__ == '__main__':
    main()
