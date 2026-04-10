# Work Structure for Sunday Delivery

## 1) Problem Framing (based on your current code)
Your current solver is a constructive greedy for Google Hash Code rides:
- Decision: assign rides to vehicles in order.
- Objective: maximize total score = traveled distance + on-time bonus.
- Constraints: each ride used at most once, each car follows time feasibility, finish before latest finish.

This is a combinatorial optimization problem, so metaheuristics are appropriate.

## 2) Algorithms to Develop (recommended order)

### A. Baseline 1: Current Greedy (already exists)
Keep your current implementation as baveline.
Output needed:
- score
- runtime
- rides served

### B. Baseline 2: Randomized Greedy (must add)
Modify greedy tie-breaking and candidate choice with randomness.
- Build a restricted candidate list (RCL) with top-k feasible moves.
- Pick one randomly.
Why: gives diverse initial solutions for metaheuristics.

### C. Hill Climbing (first metaheuristic)
Start from one solution (greedy or randomized greedy).
Neighborhood moves:
- relocate one ride from car A to car B
- swap two rides between cars
- swap order of two rides inside one car
Accept only improving moves.
Stop when no improvement for X iterations.

### D. Simulated Annealing (second metaheuristic)
Use same neighborhood moves as Hill Climbing.
Accept worse moves with probability exp(-delta/T).
Parameters:
- T0 (initial temperature)
- alpha (cooling rate)
- iter_per_temp

### E. Genetic Algorithm (third metaheuristic)
Representation:
- chromosome = assignment/order of rides by vehicle
Pipeline:
- population initialization (randomized greedy + random variants)
- selection (tournament)
- crossover (vehicle-wise merge + repair)
- mutation (relocate/swap/random insertion)
- elitism (keep best)

Optional if time remains: Tabu Search (short-term memory to avoid cycling).

## 3) Minimal Refactor Needed Before Metaheuristics
Create reusable functions in your code:
- evaluate_solution(solution, rides, B, T) -> score, feasible
- build_initial_solution(method="greedy"|"randomized")
- neighbors(solution) -> candidate solutions

Without this refactor, implementing SA/GA will be hard and slower.

## 4) Experimental Protocol (what you must report)
For each algorithm and dataset:
- best score
- average score over 10 runs (important for stochastic methods)
- standard deviation
- average runtime

Comparison table columns:
- dataset
- greedy
- randomized greedy
- hill climbing
- simulated annealing
- genetic algorithm

## 5) Parameter Grid (small but solid)
Use a small search grid to stay on schedule.

Hill Climbing:
- max_no_improve: [200, 500]

Simulated Annealing:
- T0: [50, 100]
- alpha: [0.99, 0.995]
- iter_per_temp: [100, 300]

Genetic Algorithm:
- pop_size: [20, 40]
- mutation_rate: [0.05, 0.15]
- generations: [50, 100]
- tournament_k: [3, 5]

## 6) Deadline Plan (today -> Sunday)

Friday (today):
- refactor scoring/evaluation
- add randomized greedy
- generate datasets

Saturday:
- implement Hill Climbing
- implement Simulated Annealing
- run first comparisons

Sunday:
- implement GA (or finalize SA+HC if GA is not stable)
- run final experiment batch
- prepare report table + conclusions

## 7) Delivery Priority (if you run out of time)
Priority order:
1. Greedy + Randomized Greedy + Hill Climbing
2. Simulated Annealing
3. Genetic Algorithm

A good HC+SA comparison with clean experiments is better than a broken GA.
