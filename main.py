def read_input():
    R, C, F, N, B, T = map(int, input().split())
    
    rides = []
    for _ in range(N):
        a, b, x, y, s, f = map(int, input().split())  #x1,y1,x2,y2, earliest start, latest finish
        rides.append((a, b, x, y, s, f))

    return R, C, F, N, B, T, rides

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

def main():
    R, C, F, N, B, T, rides = read_input()   #rows, columns, vehicles, rides, bonus, steps
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
    
    #Greedy Efficiency Heuristic
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
    
    with open("output.txt", "w") as f:
        for car in cars:
            f.write(str(len(car["rides"])) + " ")
            f.write(" ".join(str(r) for r in car["rides"]))
            f.write("\n")
    
    print("The Final Score was:" , score)


if __name__ == "__main__":
    main()

# a melhor solucao e a que tem mais score?
# por exemplo um carro em (6,0) para percurso ate (6,1) vai ter mais efficiency que um em (0,0) que earliest
# start e 6 e vai ter mais bonus