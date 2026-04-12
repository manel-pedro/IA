import time
import csv
import os
import glob

# Import core problem functions and optimization algorithms
from main import (
    read_input, distance, can_take_ride,
    solve_greedy, solve_smart_greedy, solve_randomized_greedy,
    solve_hill_climbing, solve_simulated_annealing, solve_genetic_algorithm
)

def run_benchmark():
    """
    Executes a full benchmark over all input files.

    This function iterates through all problem instances located in the
    'input/' directory and evaluates multiple optimization algorithms.

    For each file and algorithm, it measures:
        - Solution quality (maximum score achieved)
        - Execution time (in seconds)

    The results are stored incrementally in a CSV file.

    @return: None
    """

    # Retrieve all input files with supported extensions
    ficheiros = glob.glob("input/*.in") + glob.glob("input/*.txt")
    
    # Sort files alphabetically to ensure reproducibility of results
    ficheiros.sort()
    
    # Validate existence of input files
    if not ficheiros:
        print("No input files found in 'input/' directory.")
        return

    # Define the set of algorithms to benchmark
    # Each entry includes:
    #   - 'nome': identifier for reporting
    #   - 'func': corresponding solving function
    algoritmos = [
        {"nome": "Greedy Simple", "func": solve_greedy},
        {"nome": "Smart Greedy", "func": solve_smart_greedy},
        {"nome": "Randomized Greedy", "func": solve_randomized_greedy},
        {"nome": "Hill Climbing", "func": solve_hill_climbing},
        {"nome": "Simulated Annealing", "func": solve_simulated_annealing},
        {"nome": "Genetic Algorithm", "func": solve_genetic_algorithm}
    ]

    # Output CSV file path
    csv_file = "resultados_benchmark.csv"
    
    # Initialize CSV file with header
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "Ficheiro",
                "Rides (N)",
                "Algoritmo",
                "Score_Maximo",
                "Tempo_Medio_Segs"
            ]
        )
        writer.writeheader()

    print(f"Starting benchmark on {len(ficheiros)} files...")

    # Iterate through each input file
    for ficheiro in ficheiros:
        nome_ficheiro = os.path.basename(ficheiro)
        print(f"\n--- Processing: {nome_ficheiro} ---")
        
        try:
            # Parse input file
            # @return:
            #   R (int): number of rows
            #   C (int): number of columns
            #   F (int): number of vehicles
            #   N (int): number of rides
            #   B (int): bonus for starting on time
            #   T_MAX (int): simulation time horizon
            #   rides (list): list of ride objects
            R, C, F, N, B, T_MAX, rides = read_input(ficheiro)

        except Exception as e:
            # Handle file reading errors gracefully
            print(f"Error reading {nome_ficheiro}: {e}")
            continue

        # Execute each algorithm on the current dataset
        for algo in algoritmos:
            print(f"  Running {algo['nome']}...", end="", flush=True)
            
            # Start high-precision timer
            start_time = time.perf_counter()
            
            # Execute algorithm
            # @param F (int): number of vehicles
            # @param B (int): bonus value
            # @param rides (list): list of ride requests
            # @return:
            #   solution (any): assignment of rides to vehicles
            #   score (int): total score achieved
            _, score = algo["func"](F, B, rides)
            
            # End timer
            end_time = time.perf_counter()
            
            # Compute elapsed time
            tempo_gasto = round(end_time - start_time, 4)
            
            # Store results in dictionary format
            res = {
                "Ficheiro": nome_ficheiro,
                "Rides (N)": N,
                "Algoritmo": algo["nome"],
                "Score_Maximo": score,
                "Tempo_Medio_Segs": tempo_gasto
            }
            
            # Append results immediately to CSV file
            # This ensures partial results are preserved in long runs
            with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(
                    file,
                    fieldnames=[
                        "Ficheiro",
                        "Rides (N)",
                        "Algoritmo",
                        "Score_Maximo",
                        "Tempo_Medio_Segs"
                    ]
                )
                writer.writerow(res)
                
            print(f" Done in {tempo_gasto}s (saved)")

    # Final status message
    print(f"\n Benchmark completed! Results saved to '{csv_file}'.")


# Entry point of the program
# Ensures that the benchmark runs only when the script is executed directly
if __name__ == "__main__":
    run_benchmark()