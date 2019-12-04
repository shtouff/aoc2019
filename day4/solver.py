#!/usr/bin/env python3

from itertools import groupby

candidates = []

# cond. 1-2
for n in range(136818, 685979+1):
    s = str(n)

    # cond. 3&5: 2 and only 2 adjacent digits are the same
    groups = [digit for digit, group in groupby(s) if len(list(group)) == 2]
    if len(groups) == 0:
        continue

    # cond. 4: increasing digits
    if ''.join(sorted(s)) != s:
        continue

    candidates.append(n)


print(len(candidates))
