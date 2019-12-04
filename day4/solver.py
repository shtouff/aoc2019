#!/usr/bin/env python3

candidates = []

# cond. 1-2
for n in range(136818, 685979):
    s = str(n)

    # cond. 3: 2 adjacent digits are the same
    candidate = False
    for i in range(5):
        if s[i] == s[i+1]:
            candidate = True
            break
    if not candidate:
        continue

    # cond. 4: increasing digits:
    if ''.join(sorted(s)) != s:
        continue


    candidates.append(n)

print(len(candidates))
