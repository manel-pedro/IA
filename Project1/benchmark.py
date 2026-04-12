import time
import csv
import os
import glob
import statistics
from main import (
    read_input, distance, can_take_ride,
    solve_greedy, solve_smart_greedy,
    solve_hill_climbing, solve_simulated_annealing, solve_genetic_algorithm
)

def run_benchmark():
    resultados = []
    ficheiros = glob.glob("input/*.in") + glob.glob("input/*.txt")
    
    if not ficheiros:
        print("Nenhum ficheiro encontrado na pasta 'input/'.")
        return

    # Definir os algoritmos a testar
    algoritmos = [
        {"nome": "Greedy Simples", "func": solve_greedy, "is_stochastic": False},
        {"nome": "Smart Greedy", "func": solve_smart_greedy, "is_stochastic": False},
        {"nome": "Hill Climbing", "func": solve_hill_climbing, "is_stochastic": True},
        {"nome": "Simulated Annealing", "func": solve_simulated_annealing, "is_stochastic": True},
        {"nome": "Genetic Algorithm", "func": solve_genetic_algorithm, "is_stochastic": True}
    ]

    print(f"A iniciar benchmark em {len(ficheiros)} ficheiros...")

    for ficheiro in ficheiros:
        nome_ficheiro = os.path.basename(ficheiro)
        print(f"\n--- A processar: {nome_ficheiro} ---")
        
        # 1. Carregar dados do ficheiro
        try:
            R, C, F, N, B, T_MAX, rides = read_input(ficheiro)
        except Exception as e:
            print(f"Erro ao ler {nome_ficheiro}: {e}")
            continue

        # 2. Correr cada algoritmo
        for algo in algoritmos:
            runs_scores = []
            runs_times = []
            
            # Se for aleatório, corremos 3 vezes para fazer média. Se for determinístico (Greedy), 1 vez basta.
            num_runs = 3 if algo["is_stochastic"] else 1
            
            print(f"  A testar {algo['nome']} ({num_runs} ronda(s))...", end="", flush=True)
            
            for _ in range(num_runs):
                start_time = time.perf_counter()
                
                # Executar algoritmo
                _, score = algo["func"](F, B, rides)
                
                end_time = time.perf_counter()
                
                runs_scores.append(score)
                runs_times.append(end_time - start_time)
            
            # Calcular médias
            avg_score = sum(runs_scores) / len(runs_scores)
            avg_time = sum(runs_times) / len(runs_times)
            best_score = max(runs_scores)
            
            # Guardar na lista
            resultados.append({
                "Ficheiro": nome_ficheiro,
                "Rides (N)": N,
                "Algoritmo": algo["nome"],
                "Score_Maximo": best_score,
                "Score_Medio": avg_score,
                "Tempo_Medio_Segs": round(avg_time, 4)
            })
            print(" Concluído!")

    # 3. Escrever para CSV
    csv_file = "resultados_benchmark.csv"
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["Ficheiro", "Rides (N)", "Algoritmo", "Score_Maximo", "Score_Medio", "Tempo_Medio_Segs"])
        writer.writeheader()
        for res in resultados:
            writer.writerow(res)
            
    print(f"\n[!] Benchmark concluído! Dados guardados em '{csv_file}'.")

if __name__ == "__main__":
    run_benchmark()