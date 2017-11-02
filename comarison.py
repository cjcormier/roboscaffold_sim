from roboscaffold_sim.coordinate import Coordinate

dimension = 5


def max_structs(dimension):
    inner_dim = dimension - 1
    outer_size = 2**(dimension**2+1)
    inner_size = 2**(inner_dim**2)

    max_s= outer_size - inner_size
    return max_s


max_s = max_structs(dimension)
print(max_s)


def create_struct(dimension, n):
    struct = set()
    add_inner_struct(dimension, n % (2 ** (dimension ** 2)), struct)
    add_outer_struct(dimension, n // (2 ** (dimension ** 2)), struct)


def add_inner_struct(dimension, n, struct):
    for y in range(dimension):
        for x in range(dimension):
            if n % 2 != 0:
                struct.add(Coordinate(x, 0))
                n -= 1
            n /= 2
            if n == 0:
                return
    raise Exception('n should be 0 and function should have returned by now')


def add_outer_struct(dimension, n, struct):
    for x in range(dimension-1):
        if n % 2 != 0:
            struct.add(Coordinate(x, 0))
            n -= 1
        n /= 2
        if n == 0:
            break
    for y in range(dimension-1):
        if n % 2 != 0:
            struct.add(Coordinate(0, y))
            n -= 1
        n /= 2
        if n == 0:
            break
    if n > 1:
        raise Exception('n should be 0 or 1')
    elif n == 1:
        struct.add(Coordinate(0, 0))


j = 0
while j < max_s:
    j += 1
    create_struct(dimension, j)
    if j % (int(max_s/100+.5)) == 0:
        print(f'{int((j/max_s)*100)}% Done')
