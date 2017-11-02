
dimension = 9


def furthest_true(target):
    max_x = 0
    max_y = 0
    for y in range(dimension):
        for x in range(dimension):
            if target[x][y]:
                max_x = x
                max_y = y
    return max_x, max_y


def loop():
    count = 0
    target = [[False for _ in range(dimension)] for _ in range(dimension)]

    while True:
        x = 0
        y = 0
        while target[x][y]:
            target[x][y] = False
            x += 1
            if x == dimension:
                x = 0
                y += 1
                if y == dimension:
                    return count
        target[x][y] = True
        count += 1


print(loop())
