import sys
import os
import glob
import math
import random
import time
from visuals import VisualizadorHashcode


# ==========================================
# INPUT / OUTPUT
# ==========================================

def read_input(file_path=None):
    """
    Reads the input file and parses the ride-sharing problem instance.

    @param file_path: optional path to input file
    @return: tuple (R, C, F, N, B, T, rides)
    """

    content = []

    # Determine input source (argument, CLI or default folder file)
    if file_path:
        target_file = file_path
    elif len(sys.argv) > 1:
        target_file = sys.argv[1]
    else:
        ficheiros_input = glob.glob("input/*.txt") + glob.glob("input/*.in")
        ficheiros_input.sort()

        if ficheiros_input:
            target_file = ficheiros_input[0]
            print(f"Nenhum argumento fornecido. A usar o ficheiro default: {target_file}")
        else:
            raise FileNotFoundError("Não foi passado nenhum ficheiro e a pasta 'input/' está vazia!")

    # Read file content safely
    try:
        with open(target_file, 'r', encoding='utf-8') as file:
            content = [line for line in file.read().split('\n') if line.strip()]
    except Exception as e:
        print(f"Erro ao ler o ficheiro {target_file}: {e}")
        sys.exit(1)

    rides = []

    # Parse global parameters
    R, C, F, N, B, T = map(int, content[0].split())

    # Parse ride definitions
    for i in range(N):
        a, b, x, y, s, f = map(int, content[i+1].split())
        rides.append((a, b, x, y, s, f))

    return R, C, F, N, B, T, rides


def write_output(cars, filename="output.txt"):
    """
    Writes solution in Google Hash Code format.

    @param cars: list of vehicles with assigned rides
    @param filename: output file name
    """

    with open(filename, "w", encoding='utf-8') as f:
        for car in cars:
            f.write(f"{len(car['rides'])} ")
            f.write(" ".join(str(r) for r in car["rides"]))
            f.write("\n")


# ==========================================
# AUXILIARY FUNCTIONS
# ==========================================

def distance(a, b, x, y):
    """
    Computes Manhattan distance between two grid points.

    @return: integer distance
    """
    return abs(a - x) + abs(b - y)


def can_take_ride(car, ride, B):
    """
    Checks whether a car can perform a ride and computes its reward.

    @param car: dictionary with position, time, rides
    @param ride: tuple (a,b,x,y,s,f)
    @param B: bonus for starting on time

    @return:
        (bool) feasibility,
        (int) score,
        (int) finish time or None
    """

    a, b, x, y, s, f = ride

    # distance from car to ride start
    dist_to_start = distance(car["pos"][0], car["pos"][1], a, b)

    # arrival time at start point
    arrival = car["time"] + dist_to_start

    # actual start time (waiting if early)
    start_time = max(arrival, s)

    # ride duration
    ride_dist = distance(a, b, x, y)

    # completion time
    finish_time = start_time + ride_dist

    # invalid if deadline exceeded
    if finish_time > f:
        return False, 0, None

    # score includes bonus if started on time
    score = ride_dist + (B if arrival <= s else 0)

    return True, score, finish_time


# ==========================================
# ALGORITHMS
# ==========================================

def solve_greedy(F, B, rides):
    """
    Greedy heuristic based on efficiency ratio.

    @param F: number of cars
    @param B: bonus value
    @param rides: list of rides

    @return: (cars, score)
    """

    remaining_rides = list(enumerate(rides))
    score = 0

    # initialize fleet
    cars = [{"pos": (0,0), "time": 0, "rides": []} for _ in range(F)]

    for i, ride in remaining_rides:
        best_car = None
        best_efficiency = -1
        best_finish_time = None
        best_car_time = None

        for car_id, car in enumerate(cars):
            ok, ride_score, finish_time = can_take_ride(car, ride, B)

            if ok:
                efficiency = ride_score / (finish_time - car["time"])

                if best_car is None or efficiency > best_efficiency:
                    best_car = car_id
                    best_efficiency = efficiency
                    best_finish_time = finish_time
                    best_car_time = car["time"]

        if best_car is not None:
            _, ride_score, _ = can_take_ride(cars[best_car], ride, B)

            score += ride_score
            cars[best_car]["rides"].append(i)
            cars[best_car]["pos"] = (ride[2], ride[3])
            cars[best_car]["time"] = best_finish_time

    return cars, score


def solve_smart_greedy(F, B, rides):
    """
    Improved greedy considering waiting time and bonus impact.

    @return: (cars, score)
    """

    unassigned_rides = set(range(len(rides)))
    score = 0

    cars = [{"id": i, "pos": (0,0), "time": 0, "rides": []} for i in range(F)]

    while unassigned_rides:

        # always pick the earliest available car
        cars.sort(key=lambda c: c["time"])
        car = cars[0]

        if car["time"] == float('inf'):
            break

        best_ride = None
        best_cost = float('inf')
        best_finish_time = -1
        best_score_earned = 0

        for ride_id in unassigned_rides:
            a, b, x, y, s, f = rides[ride_id]

            dist_to_start = distance(car["pos"][0], car["pos"][1], a, b)
            arrival = car["time"] + dist_to_start
            wait = max(0, s - arrival)

            start_time = arrival + wait
            ride_dist = distance(a, b, x, y)
            finish_time = start_time + ride_dist

            if finish_time > f:
                continue

            wasted_time = dist_to_start + wait
            cost = wasted_time

            earned_points = ride_dist

            # bonus impact adjustment
            if arrival <= s:
                earned_points += B
                cost -= (B * 0.8)

            if cost < best_cost:
                best_cost = cost
                best_ride = ride_id
                best_finish_time = finish_time
                best_score_earned = earned_points

        if best_ride is not None:
            car["rides"].append(best_ride)
            car["time"] = best_finish_time
            car["pos"] = (rides[best_ride][2], rides[best_ride][3])
            unassigned_rides.remove(best_ride)
            score += best_score_earned
        else:
            car["time"] = float('inf')

    cars.sort(key=lambda c: c["id"])
    return cars, score


def solve_randomized_greedy(F, B, rides, alpha=0.3):
    """
    Randomized greedy heuristic (GRASP-like approach).

    @param alpha: randomness factor controlling candidate pool size
    @return: (cars, score)
    """

    unassigned = set(range(len(rides)))
    cars = [{"pos": (0,0), "time": 0, "rides": []} for _ in range(F)]
    score = 0

    while unassigned:
        cars.sort(key=lambda c: c["time"])
        car = cars[0]

        if car["time"] == float('inf'):
            break

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
# META-HEURISTICS UTILITIES
# ==========================================

def cars_to_solution(cars):
    """Converts car-based representation into solution format."""
    return [c["rides"][:] for c in cars]


def solution_to_cars(solution, rides, B):
    """
    Reconstructs car states and evaluates a solution.

    @return: (cars, score)
    """

    cars = []
    score = 0

    for car_id, ride_ids in enumerate(solution):
        car = {"id": car_id, "pos": (0,0), "time": 0, "rides": []}

        for ride_id in ride_ids:
            ok, s, finish_time = can_take_ride(car, rides[ride_id], B)

            if not ok:
                return None, float("-inf")

            score += s
            car["time"] = finish_time
            car["pos"] = (rides[ride_id][2], rides[ride_id][3])
            car["rides"].append(ride_id)

        cars.append(car)

    return cars, score


def random_neighbor(sol):
    """
    Generates a neighboring solution using random perturbations.

    @return: mutated solution
    """

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

    else:
        a = random.randrange(len(s))
        if len(s[a]) >= 2:
            i, j = sorted(random.sample(range(len(s[a])), 2))
            s[a][i:j] = reversed(s[a][i:j])

    return s


# ==========================================
# LOCAL SEARCH
# ==========================================

def solve_hill_climbing(F, B, rides):
    """Hill Climbing optimization."""
    sol = cars_to_solution(solve_randomized_greedy(F, B, rides)[0])
    cars, score = solution_to_cars(sol, rides, B)

    best_score = score
    best_sol = sol
    no_improve = 0

    for _ in range(2000):
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

        if no_improve > 300:
            break

    return solution_to_cars(best_sol, rides, B)


def solve_simulated_annealing(F, B, rides):
    """Simulated Annealing optimization."""
    sol = cars_to_solution(solve_randomized_greedy(F, B, rides)[0])
    cars, score = solution_to_cars(sol, rides, B)

    best_sol = sol
    best_score = score

    T = min(100.0, len(rides))

    while T > 0.5:
        for _ in range(50):
            neighbor = random_neighbor(sol)
            ncars, nscore = solution_to_cars(neighbor, rides, B)

            if not ncars:
                continue

            delta = nscore - score

            if delta > 0 or random.random() < math.exp(delta / T):
                sol = neighbor
                score = nscore

                if score > best_score:
                    best_sol = sol
                    best_score = score

        T *= 0.90

    return solution_to_cars(best_sol, rides, B)


# ==========================================
# GENETIC ALGORITHM
# ==========================================

def crossover(parent1, parent2, F):
    """
    Genetic crossover operator avoiding duplicates.

    @return: child solution
    """

    child = [[] for _ in range(F)]
    used_rides = set()

    for i in range(F // 2):
        for ride in parent1[i]:
            if ride not in used_rides:
                child[i].append(ride)
                used_rides.add(ride)

    for i in range(F // 2, F):
        for ride in parent2[i]:
            if ride not in used_rides:
                child[i].append(ride)
                used_rides.add(ride)

    return child


def solve_genetic_algorithm(F, B, rides, pop_size=100, generations=250, mutation_rate=0.4):
    """
    Genetic Algorithm optimization engine.

    @return: (best_solution, best_score)
    """

    population = []

    base_sol = cars_to_solution(solve_randomized_greedy(F, B, rides)[0])
    population.append(base_sol)

    for _ in range(pop_size - 1):
        population.append(random_neighbor(base_sol))

    best_overall_cars = None
    best_overall_score = float('-inf')

    for gen in range(generations):

        fitness_scores = []
        valid_population = []

        for sol in population:
            cars, score = solution_to_cars(sol, rides, B)

            if cars is not None:
                fitness_scores.append(score)
                valid_population.append(sol)

                if score > best_overall_score:
                    best_overall_score = score
                    best_overall_cars = cars

        if not valid_population:
            break

        paired = list(zip(valid_population, fitness_scores))
        paired.sort(key=lambda x: x[1], reverse=True)

        elite_count = max(2, int(pop_size * 0.2))
        new_population = [p[0] for p in paired[:elite_count]]

        mating_pool = [p[0] for p in paired[:max(2, len(paired)//2)]]

        while len(new_population) < pop_size:
            parent1 = random.choice(mating_pool)
            parent2 = random.choice(mating_pool)

            child = crossover(parent1, parent2, F)

            if random.random() < mutation_rate:
                child = random_neighbor(child)

            new_population.append(child)

        population = new_population

    return best_overall_cars, best_overall_score


# ==========================================
# MAIN
# ==========================================

def terminal_mode():
    """Interactive CLI mode for running experiments."""

    ficheiros = glob.glob("input/*.in") + glob.glob("input/*.txt")
    ficheiros.sort()

    if not ficheiros:
        print("\n[ERRO] Nenhum ficheiro encontrado na pasta 'input/'.")
        return

    print("\n==============================")
    print(" FILE SELECTION")
    print("==============================")

    for i, f in enumerate(ficheiros):
        print(f" [{i+1}] {os.path.basename(f)}")

    try:
        op_ficheiro = int(input("\nChoose file: ")) - 1
        ficheiro_escolhido = ficheiros[op_ficheiro]
    except:
        print("Invalid option.")
        return

    algoritmos = [
        ("Greedy Simples", solve_greedy),
        ("Smart Greedy", solve_smart_greedy),
        ("Randomized Greedy", solve_randomized_greedy),
        ("Hill Climbing", solve_hill_climbing),
        ("Simulated Annealing", solve_simulated_annealing),
        ("Genetic Algorithm", solve_genetic_algorithm)
    ]

    print("\n==============================")
    print(" ALGORITHM SELECTION")
    print("==============================")

    for i, (nome, _) in enumerate(algoritmos):
        print(f" [{i+1}] {nome}")

    try:
        op_algo = int(input("\nChoose algorithm: ")) - 1
        nome_algo, func_algo = algoritmos[op_algo]
    except:
        print("Invalid option.")
        return

    R, C, F, N, B, T_MAX, rides = read_input(ficheiro_escolhido)

    start = time.perf_counter()
    cars_schedule, score = func_algo(F, B, rides)
    end = time.perf_counter()

    print(f"\nDone in {end - start:.4f}s")
    print(f"Score: {score}")

    output_name = f"output_{os.path.basename(ficheiro_escolhido)}"
    write_output(cars_schedule, output_name)

    print(f"Saved: {output_name}")


def main():
    """Program entry point."""

    print("==============================")
    print(" SELF-DRIVING RIDES SYSTEM")
    print("==============================")

    print("1 - Terminal Mode")
    print("2 - Visual Mode")
    print("0 - Exit")

    op = input("Select option: ")

    if op == "1":
        terminal_mode()

    elif op == "2":
        R, C, F, _, B, T_MAX, rides = read_input()

        app = VisualizadorHashcode(
            R, C, F, T_MAX, B, rides,
            solve_greedy,
            solve_smart_greedy,
            solve_randomized_greedy,
            solve_hill_climbing,
            solve_simulated_annealing,
            solve_genetic_algorithm,
            read_input,
        )
        app.iniciar()

    elif op == "0":
        print("Exiting...")

    else:
        print("Invalid option.")


if __name__ == "__main__":
    main()