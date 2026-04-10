import sys
from visuals import VisualizadorHashcode


# ==========================================
# I/O
# ==========================================

def read_input():
    rides = []
    if(len(sys.argv) > 1):
        with open(sys.argv[1], 'r') as file:
            content = file.read()
        content = content.split('\n')
        print(content[0].split())
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
    with open(filename, "w") as f:
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
        best_score = 0
        best_finish_time, best_car = None, None
        for car_id, car in enumerate(cars):
            ok, ride_score, finish_time = can_take_ride(car, ride, B)
            if ok:
                efficiency = ride_score / (finish_time - car["time"])
                if best_car is None or efficiency > best_score or (efficiency == best_score and car["time"] < cars[best_car]["time"]):
                    best_car = car_id
                    best_score = efficiency
                    best_finish_time = finish_time
        if best_car is not None:
            score += can_take_ride(cars[best_car], ride, B)[1]
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
    # Usamos um Set para riscar as viagens que já foram atribuídas
    unassigned_rides = set(range(len(rides)))
    score = 0

    # Inicializar frota (adicionamos um "id" para no fim conseguirmos ordenar para o output)
    cars = [{"id": i, "pos": (0,0), "time": 0, "rides": []} for i in range(F)]
    
    # O loop corre enquanto houver viagens por fazer
    while unassigned_rides:
        # 1. Escolher o carro que está livre mais cedo
        cars.sort(key=lambda c: c["time"])
        car = cars[0]
        
        # Se o carro com o tempo mais baixo já tem o tempo "infinito",
        # significa que NENHUM carro consegue fazer mais nenhuma viagem.
        if car["time"] == float('inf'):
            break

        best_ride = None
        best_cost = float('inf')
        best_finish_time = -1
        best_score_earned = 0
        
        # 2. Procurar a melhor viagem para ESTE carro específico
        for ride_id in unassigned_rides:
            a, b, x, y, s, f = rides[ride_id]
            
            # Calcular tempos
            dist_to_start = distance(car["pos"][0], car["pos"][1], a, b)
            arrival_time = car["time"] + dist_to_start
            wait_time = max(0, s - arrival_time)
            
            start_time = arrival_time + wait_time
            ride_dist = distance(a, b, x, y)
            finish_time = start_time + ride_dist
            
            # Se não consegue acabar a tempo, ignorar
            if finish_time > f:
                continue
                
            # 3. A NOSSA HEURÍSTICA DE CUSTO (Menor custo = Melhor viagem)
            wasted_time = dist_to_start + wait_time
            cost = wasted_time
            
            earned_points = ride_dist
            if arrival_time <= s:
                earned_points += B
                # Se garante bónus, "baixamos" o custo artificialmente para a tornar super atrativa!
                cost -= (B * 0.8) 
                
            if cost < best_cost:
                best_cost = cost
                best_ride = ride_id
                best_finish_time = finish_time
                best_score_earned = earned_points
                
        # 4. Atribuir a viagem ao carro
        if best_ride is not None:
            car["rides"].append(best_ride)
            car["time"] = best_finish_time
            car["pos"] = (rides[best_ride][2], rides[best_ride][3])
            unassigned_rides.remove(best_ride)
            score += best_score_earned
        else:
            # Este carro não consegue fazer mais nenhuma viagem válida até ao fim do mundo.
            # Metemos o tempo dele a infinito para ele ir para o fim da fila de espera e não travar o loop.
            car["time"] = float('inf')

    # Voltar a ordenar os carros pelo ID original para o output.txt ficar correto
    cars.sort(key=lambda c: c["id"])
    return cars, score


# ==========================================
# MAIN
# ==========================================

def main():
    R, C, F, N, B, T, rides = read_input()   #rows, columns, vehicles, rides, bonus, steps
    remaining_rides = list(enumerate(rides))
    score = 0

   cars, final_score = solve_greedy(F, B, rides)
    
    write_output(cars, "output.txt")
    
    print("The Final Score was:" , score)

    print("A abrir o simulador visual...")
    app = VisualizadorHashcode(R, C, F, T, B, rides, cars)
    print("acabou o inicializador")
    app.iniciar()


if __name__ == "__main__":
    main()

# a melhor solucao e a que tem mais score?
# por exemplo um carro em (6,0) para percurso ate (6,1) vai ter mais efficiency que um em (0,0) que earliest
# start e 6 e vai ter mais bonus