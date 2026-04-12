import sys
import math
import random
from visuals import VisualizadorHashcode

# ==========================================
# I/O
# ==========================================

def read_input():
    rides = []
    if(len(sys.argv) > 1):
        with open(sys.argv[1], 'r', encoding='utf-8') as file:
            content = file.read().split('\n')
        R, C, F, N, B, T = map(int, content[0].split())
        for i in range(N):
            a, b, x, y, s, f = map(int, content[i+1].split())
            rides.append((a, b, x, y, s, f))
    else:
        R, C, F, N, B, T = map(int, input().split())
        for _ in range(N):
            rides.append(tuple(map(int, input().split())))
    
    return R, C, F, N, B, T, rides

def distance(a, b, x, y):
    return abs(a - x) + abs(b - y)

# ==========================================
# CORE
# ==========================================

def can_take_ride(car, ride, B):
    a, b, x, y, s, f = ride
    dist_to_start = distance(car["pos"][0], car["pos"][1], a, b)
    arrival = car["time"] + dist_to_start
    start = max(arrival, s)
    ride_dist = distance(a, b, x, y)
    finish = start + ride_dist

    if finish > f:
        return False, 0, None

    score = ride_dist + (B if arrival <= s else 0)
    return True, score, finish

# ==========================================
# SMART GREEDY MELHORADO
# ==========================================

def solve_smart_greedy(F, B, rides):
    rides_sorted = sorted(enumerate(rides), key=lambda x: (x[1][4], x[1][5]))
    unassigned = set(i for i, _ in rides_sorted)

    cars = [{"id": i, "pos": (0,0), "time": 0, "rides": []} for i in range(F)]
    score = 0

    while unassigned:
        cars.sort(key=lambda c: c["time"])
        car = cars[0]

        if car["time"] == float('inf'):
            break

        best = None
        best_cost = float('inf')

        for ride_id in unassigned:
            a, b, x, y, s, f = rides[ride_id]

            dist_to_start = distance(car["pos"][0], car["pos"][1], a, b)
            arrival = car["time"] + dist_to_start
            wait = max(0, s - arrival)
            ride_dist = distance(a, b, x, y)
            finish = arrival + wait + ride_dist

            if finish > f:
                continue

            urgency = max(0, f - finish)

            cost = (
                dist_to_start * 1.0 +
                wait * 0.5 -
                (B if arrival <= s else 0) -
                urgency * 0.1
            )

            if cost < best_cost:
                best_cost = cost
                best = (ride_id, finish, ride_dist + (B if arrival <= s else 0))

        if best:
            ride_id, finish, earned = best
            car["rides"].append(ride_id)
            car["time"] = finish
            car["pos"] = (rides[ride_id][2], rides[ride_id][3])
            score += earned
            unassigned.remove(ride_id)
        else:
            car["time"] = float('inf')

    cars.sort(key=lambda c: c["id"])
    return cars, score

# ==========================================
# RANDOMIZED GREEDY
# ==========================================

def solve_randomized_greedy(F, B, rides, alpha=0.3):
    unassigned = set(range(len(rides)))
    cars = [{"pos": (0,0), "time": 0, "rides": []} for _ in range(F)]
    score = 0

    while unassigned:
        cars.sort(key=lambda c: c["time"])
        car = cars[0]

        candidates = []
        for ride_id in unassigned:
            ok, s, f = can_take_ride(car, rides[ride_id], B)
            if ok:
                candidates.append((ride_id, s, f))

        if not candidates:
            car["time"] = float('inf')
            continue

        candidates.sort(key=lambda x: -x[1])
        k = max(1, int(len(candidates) * alpha))
        ride_id, earned, finish = random.choice(candidates[:k])

        car["rides"].append(ride_id)
        car["time"] = finish
        car["pos"] = (rides[ride_id][2], rides[ride_id][3])
        score += earned

        unassigned.remove(ride_id)

    return cars, score

# ==========================================
# SOLUTION UTILS
# ==========================================

def cars_to_solution(cars):
    return [c["rides"][:] for c in cars]

def solution_to_cars(solution, rides, B):
    cars = []
    score = 0

    for ride_ids in solution:
        car = {"pos": (0,0), "time": 0, "rides": []}

        for ride_id in ride_ids:
            ok, s, finish = can_take_ride(car, rides[ride_id], B)
            if not ok:
                return None, float("-inf")

            score += s
            car["time"] = finish
            car["pos"] = (rides[ride_id][2], rides[ride_id][3])
            car["rides"].append(ride_id)

        cars.append(car)

    return cars, score

# ==========================================
# NEIGHBOR
# ==========================================

def random_neighbor(sol):
    s = [r[:] for r in sol]

    move = random.choice(["relocate", "swap", "reverse"])

    if move == "relocate":
        a = random.randrange(len(s))
        if not s[a]: return s
        ride = s[a].pop(random.randrange(len(s[a])))
        b = random.randrange(len(s))
        s[b].insert(random.randrange(len(s[b])+1), ride)

    elif move == "swap":
        a, b = random.sample(range(len(s)), 2)
        if s[a] and s[b]:
            i = random.randrange(len(s[a]))
            j = random.randrange(len(s[b]))
            s[a][i], s[b][j] = s[b][j], s[a][i]

    else:  # reverse
        a = random.randrange(len(s))
        if len(s[a]) >= 2:
            i, j = sorted(random.sample(range(len(s[a])), 2))
            s[a][i:j] = reversed(s[a][i:j])

    return s

# ==========================================
# HILL CLIMBING
# ==========================================

def solve_hill_climbing(F, B, rides):
    sol = cars_to_solution(solve_randomized_greedy(F, B, rides)[0])
    cars, score = solution_to_cars(sol, rides, B)

    best_score = score
    best_sol = sol

    no_improve = 0

    for _ in range(5000):
        neighbor = random_neighbor(sol)
        ncars, nscore = solution_to_cars(neighbor, rides, B)

        if ncars and nscore > score:
            sol = neighbor
            score = nscore
            no_improve = 0

            if score > best_score:
                best_score = score
                best_sol = sol
        else:
            no_improve += 1

        if no_improve > 800:
            break

    return solution_to_cars(best_sol, rides, B)

# ==========================================
# SIMULATED ANNEALING
# ==========================================

def solve_simulated_annealing(F, B, rides):
    sol = cars_to_solution(solve_randomized_greedy(F, B, rides)[0])
    cars, score = solution_to_cars(sol, rides, B)

    best_sol = sol
    best_score = score

    T = len(rides) * 5

    while T > 0.5:
        for _ in range(500):
            neighbor = random_neighbor(sol)
            ncars, nscore = solution_to_cars(neighbor, rides, B)
            if not ncars:
                continue

            delta = nscore - score
            if delta > 0 or random.random() < math.exp(delta / T):
                sol = neighbor
                score = nscore

                if score > best_score:
                    best_score = score
                    best_sol = sol

        T *= 0.997

    return solution_to_cars(best_sol, rides, B)

# ==========================================
# MAIN
# ==========================================

def main():
    R, C, F, _, B, T, rides = read_input()

    app = VisualizadorHashcode(
        R, C, F, T, B, rides,
        solve_smart_greedy,
        solve_randomized_greedy,
        solve_hill_climbing,
        solve_simulated_annealing,
    )
    app.iniciar()

if __name__ == "__main__":
    main()