import time
import csv
import os
import glob
from main import (
    read_input, distance, can_take_ride,
    solve_greedy, solve_smart_greedy,
    solve_hill_climbing, solve_simulated_annealing, solve_genetic_algorithm
)

def run_benchmark():
    ficheiros = glob.glob("input/*.in") + glob.glob("input/*.txt")
    
    if not ficheiros:
        print("Nenhum ficheiro encontrado na pasta 'input/'.")
        return

    # Definir os algoritmos a testar
    algoritmos = [
        {"nome": "Greedy Simples", "func": solve_greedy},
        {"nome": "Smart Greedy", "func": solve_smart_greedy},
        {"nome": "Hill Climbing", "func": solve_hill_climbing},
        {"nome": "Simulated Annealing", "func": solve_simulated_annealing},
        {"nome": "Genetic Algorithm", "func": solve_genetic_algorithm}
    ]

    csv_file = "resultados_benchmark.csv"
    
    # 1. CRIAR O FICHEIRO E O CABEÇALHO LOGO NO INÍCIO
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["Ficheiro", "Rides (N)", "Algoritmo", "Score_Maximo", "Tempo_Medio_Segs"])
        writer.writeheader()

    print(f"A iniciar benchmark em {len(ficheiros)} ficheiros... Os dados serão guardados progressivamente!")

    for ficheiro in ficheiros:
        nome_ficheiro = os.path.basename(ficheiro)
        print(f"\n--- A processar: {nome_ficheiro} ---")
        
        try:
            R, C, F, N, B, T_MAX, rides = read_input(ficheiro)
        except Exception as e:
            print(f"Erro ao ler {nome_ficheiro}: {e}")
            continue

        for algo in algoritmos:
            # Forçamos a 1 única ronda para não demorar uma eternidade no teu computador
            num_runs = 1 
            
            print(f"  A testar {algo['nome']}...", end="", flush=True)
            
            start_time = time.perf_counter()
            _, score = algo["func"](F, B, rides)
            end_time = time.perf_counter()
            
            tempo_gasto = round(end_time - start_time, 4)
            
            # 2. GRAVAR IMEDIATAMENTE NO CSV
            res = {
                "Ficheiro": nome_ficheiro,
                "Rides (N)": N,
                "Algoritmo": algo["nome"],
                "Score_Maximo": score,
                "Tempo_Medio_Segs": tempo_gasto
            }
            
            with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=["Ficheiro", "Rides (N)", "Algoritmo", "Score_Maximo", "Tempo_Medio_Segs"])
                writer.writerow(res)
                
            print(f" Concluído em {tempo_gasto}s! (Guardado)")

    print(f"\n[!] Benchmark concluído! Podes abrir o ficheiro '{csv_file}'.")

if __name__ == "__main__":
    run_benchmark()