#!/usr/bin/env python3

"""
                          YOU
                         /
        G - H       J - K - L
       /           /
COM - B - C - D - E - F
               \
                I - SAN


H: 1 direct, 2 indirect, 3 total
G: 1 direct, 1 indirect, 2 total
B: 1 direct, 1 total
C: 1 direct, 1 indirect, 2 total
...

H: 3
G: 2
B: 1
C: 2
D: 3
I: 4
E: 4
F: 5
J: 5
K: 6
L: 7
total = 42

=> il suffit de sommer l'ecart de chaque sommet avec la racine, soit la profondeur de chaque sommet
"""


def load_orbits():
    with open('input', 'r') as orbits:
        for o in orbits.readlines():
            yield o.rstrip().split(')')


def tree_count(root, depth, children):
    return depth + sum([tree_count(child, depth + 1, children) for child in children.get(root, [])])


def all_parents(v, parents):
    res = []
    while v in parents:
        res.append(v)
        v = parents[v]
    res.append(v)
    return res


def main():
    children = {}
    parents = {}
    # for (a, b) in [
    #     ('COM', 'B'),
    #     ('B', 'C'),
    #     ('C', 'D'),
    #     ('D', 'E'),
    #     ('E', 'F'),
    #     ('B', 'G'),
    #     ('G', 'H'),
    #     ('D', 'I'),
    #     ('E', 'J'),
    #     ('J', 'K'),
    #     ('K', 'L'),
    #     ('K', 'YOU'),
    #     ('I', 'SAN'),
    # ]:
    for (a, b) in load_orbits():
        if a in children:
            children[a].append(b)
        else:
            children[a] = [b]
        parents[b] = a
    root = (set(children.keys()) - set(parents.keys())).pop()

    print(f'racine du graphe: {root}')
    print('total direct + indirects:', tree_count(root, 0, children))

    your_path = all_parents('YOU', parents)
    santa_path = all_parents('SAN', parents)

    croot = None
    for a, b in zip(reversed(your_path), reversed(santa_path)):
        if a != b:
            break
        croot = a
    orbit_transfer_count = your_path.index(croot) + santa_path.index(croot) - 2

    print(f'racine commune a YOU et SAN: {croot}')
    print(f'Nb de transferts orbitaux: {orbit_transfer_count}')


if __name__ == '__main__':
    main()
