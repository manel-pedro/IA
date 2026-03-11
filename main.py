def read_input():
    R, C, F, N, B, T = map(int, input().split())
    rides = []

    for _ in range(N):
        a, b, x, y, s, f = map(int, input().split())
        rides.append((a, b, x, y, s, f))

    return R, C, F, N, B, T, rides


def main():
    R, C, F, N, B, T, rides = read_input()

    print("Grid:", R, C)
    print("Cars:", F)
    print("Rides:", N)
    print("Ride list:", rides)


if __name__ == "__main__":
    main()