#!/usr/bin/env python3

"""
        G - H       J - K - L
       /           /
COM - B - C - D - E - F
               \
                I


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

7 + 6 + 5 + 5 = 23
4 + 4 + 3 + 2 = 13
1 + 2 + 3 = 6
total = 42

=> il suffit de sommer l'ecart de chaque sommet avec la racine, soit la profondeur de chaque sommet

"""


def load_orbits():
    with open('input', 'r') as orbits:
        for o in orbits.readlines():
            yield o.rstrip().split(')')


def tree_len(root, depth, children):
    return depth + sum([tree_len(child, depth + 1, children) for child in children.get(root, [])])


def main():
    children = {}
    parents = {}
    # for a, b in [
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
    # ]:
    for (a, b) in load_orbits():
        if a in children:
            children[a].append(b)
        else:
            children[a] = [b]
        if b in parents:
            parents[b].append(a)
        else:
            parents[b] = [a]
    vertices = set(parents.keys()).union(set(children.keys()))
    root = [v for v in vertices if len(parents.get(v, [])) == 0][0]

    print(f'racine du graphe: {root}')
    print('total direct + indirects:', tree_len(root, 0, children))


if __name__ == '__main__':
    main()
