def read_input():
    R, C, F, N, B, T = map(int, input().split())
    
    rides = []
    for _ in range(N):
        a, b, x, y, s, f = map(int, input().split())  #x1,y1,x2,y2, earliest start, latest finish
        rides.append((a, b, x, y, s, f))

    return R, C, F, N, B, T, rides

def distance(a, b, x, y):
    return abs(a - x) + abs(b - y)

def can_take_ride(car, ride, current_time, score, bonus):
    a, b, x, y, s, f = ride
    time_to_start = distance(car["pos"][0], car["pos"][1], a, b)
    arrival_time = current_time + time_to_start

    if arrival_time > f:
        return False, 0
    if arrival_time <= s:
        score += bonus

    start_time = max(arrival_time, s)
    finish_time = start_time + distance(a, b, x, y)
    
    if finish_time > f:
        return False, 0
    
    score += finish_time - start_time
    return True, score

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

    for car in cars:
        remaining_rides2 = []
        for i, ride in remaining_rides:
            score2= 0
            ok, s = can_take_ride(car, ride, car["time"], score2, B)
            if ok:
                time = distance(ride[0],ride[1],ride[2],ride[3])
                car["rides"].append(i)
                car["pos"] = (ride[2], ride[3])
                car["time"] = max(car["time"], ride[4]) + time
                score += s
            else:
                remaining_rides2.append((i,ride))
        remaining_rides = remaining_rides2
    
    with open("output.txt", "w") as f:
        for car in cars:
            f.write(str(len(car["rides"])) + " ")
            f.write(" ".join(str(r) for r in car["rides"]))
            f.write("\n")
    
    print("The Final Score was:" , score)


if __name__ == "__main__":
    main()