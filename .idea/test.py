a = 2 ** 16 + 3
b = 0
m = 2 ** 31
seed = 2 ** 16 + 3
x = seed

i = 0
while i < 20:
    x = (a * x + b) % m
    u = (x / m) * 100
    i += 1

    print(int(u))
