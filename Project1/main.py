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
            content = file.read()
        content = content.split('\n')
        R, C, F, N, B, T = map(int, content[0].split())
        for i in range(N):
            a, b, x, y, s, f = map(int, content[i+1].split())  #x1,y1,x2,y2, earliest start, latest finish
            rides.append((a, b, x, y, s, f))
    else:
        R, C, F, N, B, T = map(int, input().split())
        for _ in range(N):
            a, b, x, y, s, f = map(int, input().split())  #x1,y1,x2,y2, earliest start, latest finish
            rides.append((a, b, x, y, s, f))
    
    return R, C, F, N, B, T, rides

def write_output(cars, filename="output.txt"):
    with open(filename, "w", encoding='utf-8') as f:
        for car in cars:
            f.write(f"{len(car['rides'])} ")
            f.write(" ".join(str(r) for r in car["rides"]))
            f.write("\n")


# ==========================================
# FUNÇÕES AUXILIARES
# ==========================================

def distance(a, b, x, y):
    return abs(a - x) + abs(b - y)

def can_take_ride(car, ride, bonus):
    a, b, x, y, s, f = ride
    time_to_start = distance(car["pos"][0], car["pos"][1], a, b)
    arrival_time = car["time"] + time_to_start

    start_time = max(arrival_time, s)
    ride_distance = distance(a, b, x, y)
    finish_time = start_time + ride_distance
    if finish_time > f:
        return False, 0, None

    score = ride_distance
    if arrival_time <= s:
        score += bonus

    return True, score, finish_time


# ==========================================
# ALGORITMOS 
# ==========================================

def solve_greedy(F, B, rides):
    remaining_rides = list(enumerate(rides))
    score = 0

    cars = []
    for _ in range(F):
        car = {
            "pos": (0,0),    
            "time": 0,    
            "rides": []      
        }
        cars.append(car)
    
    for i, ride in remaining_rides:
        best_efficiency = -1
        best_finish_time = None
        best_car = None
        best_car_time = None
        for car_id, car in enumerate(cars):
            ok, ride_score, finish_time = can_take_ride(car, ride, B)
            if ok:
                efficiency = ride_score / (finish_time - car["time"])
                if best_car is None:
                    best_car = car_id
                    best_efficiency = efficiency
                    best_finish_time = finish_time
                    best_car_time = car["time"]
                elif efficiency > best_efficiency or (efficiency == best_efficiency and car["time"] < best_car_time):
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
    Greedy Inteligente: 
    - Pega sempre no carro que fica livre mais cedo.
    - Escolhe a viagem que minimiza o tempo desperdiçado (viagem vazia + espera).
    - Dá forte prioridade a viagens onde o bónus é garantido.
    """
    unassigned_rides = set(range(len(rides)))
    score = 0

    cars = [{"id": i, "pos": (0,0), "time": 0, "rides": []} for i in range(F)]
    
    while unassigned_rides:
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
            arrival_time = car["time"] + dist_to_start
            wait_time = max(0, s - arrival_time)
            
            start_time = arrival_time + wait_time
            ride_dist = distance(a, b, x, y)
            finish_time = start_time + ride_dist
            
            if finish_time > f:
                continue
                
            wasted_time = dist_to_start + wait_time
            cost = wasted_time
            
            earned_points = ride_dist
            if arrival_time <= s:
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


def cars_to_solution(cars):
    return [car["rides"][:] for car in cars]


def solution_to_cars(solution, rides, B):
    cars = []
    score = 0

    for car_id, ride_ids in enumerate(solution):
        car = {
            "id": car_id,
            "pos": (0, 0),
            "time": 0,
            "rides": []
        }

        for ride_id in ride_ids:
            a, b, x, y, s, f = rides[ride_id]
            travel_time = distance(car["pos"][0], car["pos"][1], a, b)
            arrival_time = car["time"] + travel_time
            start_time = max(arrival_time, s)
            ride_distance = distance(a, b, x, y)
            finish_time = start_time + ride_distance

            if finish_time > f:
                return None, float("-inf")

            score += ride_distance
            if arrival_time <= s:
                score += B

            car["rides"].append(ride_id)
            car["pos"] = (x, y)
            car["time"] = finish_time

        cars.append(car)

    return cars, score


def build_initial_solution(F, B, rides, method="smart"):
    if method == "greedy":
        cars, _ = solve_greedy(F, B, rides)
    else:
        cars, _ = solve_smart_greedy(F, B, rides)
    return cars_to_solution(cars)


def random_neighbor(solution):
    neighbor = [ride_list[:] for ride_list in solution]
    non_empty_cars = [index for index, ride_list in enumerate(neighbor) if ride_list]

    if not non_empty_cars:
        return neighbor

    move_type = random.choice(["relocate", "swap_between_cars", "swap_within_car"])

    if move_type == "relocate":
        source_car = random.choice(non_empty_cars)
        ride_index = random.randrange(len(neighbor[source_car]))
        ride_id = neighbor[source_car].pop(ride_index)

        destination_car = random.randrange(len(neighbor))
        insert_index = random.randrange(len(neighbor[destination_car]) + 1)
        neighbor[destination_car].insert(insert_index, ride_id)
        return neighbor

    if move_type == "swap_between_cars" and len(non_empty_cars) >= 2:
        car_a, car_b = random.sample(non_empty_cars, 2)
        ride_a_index = random.randrange(len(neighbor[car_a]))
        ride_b_index = random.randrange(len(neighbor[car_b]))
        neighbor[car_a][ride_a_index], neighbor[car_b][ride_b_index] = neighbor[car_b][ride_b_index], neighbor[car_a][ride_a_index]
        return neighbor

    cars_with_two_rides = [index for index, ride_list in enumerate(neighbor) if len(ride_list) >= 2]
    if cars_with_two_rides:
        car_id = random.choice(cars_with_two_rides)
        ride_a_index, ride_b_index = random.sample(range(len(neighbor[car_id])), 2)
        neighbor[car_id][ride_a_index], neighbor[car_id][ride_b_index] = neighbor[car_id][ride_b_index], neighbor[car_id][ride_a_index]
        return neighbor

    source_car = random.choice(non_empty_cars)
    ride_index = random.randrange(len(neighbor[source_car]))
    ride_id = neighbor[source_car].pop(ride_index)
    destination_car = random.randrange(len(neighbor))
    neighbor[destination_car].append(ride_id)
    return neighbor


def solve_hill_climbing(F, B, rides, initial_method="smart", max_iterations=4000, max_no_improve=400, neighborhood_size=30):
    current_solution = build_initial_solution(F, B, rides, initial_method)
    current_cars, current_score = solution_to_cars(current_solution, rides, B)

    best_cars = current_cars
    best_score = current_score
    no_improve = 0

    for _ in range(max_iterations):
        candidate_solution = None
        candidate_cars = None
        candidate_score = float("-inf")

        for _ in range(neighborhood_size):
            neighbor = random_neighbor(current_solution)
            neighbor_cars, neighbor_score = solution_to_cars(neighbor, rides, B)
            if neighbor_cars is not None and neighbor_score > candidate_score:
                candidate_solution = neighbor
                candidate_cars = neighbor_cars
                candidate_score = neighbor_score

        if candidate_solution is None:
            break

        if candidate_score > current_score:
            current_solution = candidate_solution
            current_cars = candidate_cars
            current_score = candidate_score
            no_improve = 0

            if current_score > best_score:
                best_cars = current_cars
                best_score = current_score
        else:
            no_improve += 1

        if no_improve >= max_no_improve:
            break

    return best_cars, best_score


def solve_simulated_annealing(F, B, rides, initial_method="smart", initial_temperature=None, cooling_rate=0.995, min_temperature=0.5, iterations_per_temperature=200):
    current_solution = build_initial_solution(F, B, rides, initial_method)
    current_cars, current_score = solution_to_cars(current_solution, rides, B)

    best_cars = current_cars
    best_score = current_score

    if initial_temperature is None:
        initial_temperature = max(100.0, len(rides) * 10.0)

    temperature = initial_temperature

    while temperature > min_temperature:
        for _ in range(iterations_per_temperature):
            neighbor = random_neighbor(current_solution)
            neighbor_cars, neighbor_score = solution_to_cars(neighbor, rides, B)
            if neighbor_cars is None:
                continue

            delta = neighbor_score - current_score
            if delta >= 0 or random.random() < math.exp(delta / temperature):
                current_solution = neighbor
                current_cars = neighbor_cars
                current_score = neighbor_score

                if current_score > best_score:
                    best_cars = current_cars
                    best_score = current_score

        temperature *= cooling_rate

    return best_cars, best_score


def crossover(parent1, parent2, F):
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

def solve_genetic_algorithm(F, B, rides, pop_size=20, generations=100, mutation_rate=0.4):
    population = []
    base_sol_smart = build_initial_solution(F, B, rides, "smart")
    population.append(base_sol_smart)
    
    for _ in range(pop_size - 1):
        mutated = random_neighbor(base_sol_smart)
        for _ in range(random.randint(1, 5)):
            mutated = random_neighbor(mutated)
        population.append(mutated)
        
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

def main():
    print("A ler dados do ficheiro...")
    R, C, F, _, B, T, rides = read_input()

    print("A abrir o simulador visual...")
    app = VisualizadorHashcode(
        R,
        C,
        F,
        T,
        B,
        rides,
        solve_greedy,
        solve_smart_greedy,
        solve_hill_climbing,
        solve_simulated_annealing,
        solve_genetic_algorithm,
    )
    app.iniciar()


if __name__ == "__main__":
    main()

# a melhor solucao e a que tem mais score?
# por exemplo um carro em (6,0) para percurso ate (6,1) vai ter mais efficiency que um em (0,0) que earliest
# start e 6 e vai ter mais bonus