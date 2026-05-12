import csv
import glob
import os
import random
import statistics
import time
import argparse
import ast
from itertools import product

from main import (
    read_input,
    solve_genetic_algorithm,
    solve_randomized_greedy,
)


OUTPUT_DIR = "benchmark_outputs"
DEFAULT_REPEATS_QUICK = 2
DEFAULT_REPEATS_FULL = 2


def normalize_params(params):
    # Keep deterministic string formatting for CSV keys.
    return str(dict(sorted(params.items())))


def parse_params(params_raw):
    if not params_raw:
        return {}
    try:
        return ast.literal_eval(params_raw)
    except (ValueError, SyntaxError):
        return {}


def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def list_input_files():
    files = glob.glob("input/*.in") + glob.glob("input/*.txt")
    files.sort()
    return files


def run_with_timing(func, args, kwargs):
    start = time.perf_counter()
    _, score = func(*args, **kwargs)
    elapsed = time.perf_counter() - start
    return score, elapsed


def aggregate(values):
    mean_v = statistics.mean(values)
    std_v = statistics.stdev(values) if len(values) > 1 else 0.0
    return mean_v, std_v


def load_existing_rows(csv_path):
    if not os.path.exists(csv_path):
        return []

    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def existing_keys(rows):
    keys = set()
    for row in rows:
        key = (
            row.get("algorithm", ""),
            row.get("dataset", ""),
            row.get("params", ""),
            str(row.get("repeats", "")),
        )
        keys.add(key)
    return keys


def append_rows(csv_path, rows, fieldnames):
    if not rows:
        return

    file_exists = os.path.exists(csv_path)
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)


def summarize_genetic_grid_scores(csv_path, profile):
    if not os.path.exists(csv_path):
        print("\n[Resumo] CSV genético ainda não existe.")
        return

    rows = load_existing_rows(csv_path)
    if not rows:
        print("\n[Resumo] CSV genético vazio.")
        return

    target_pop_sizes = {30, 60, 100, 140}
    target_generations = {80, 150, 250}
    target_mutation_rates = {0.15, 0.3, 0.45}

    grouped = {}

    for row in rows:
        if row.get("algorithm") != "genetic":
            continue
        if row.get("profile") != profile:
            continue

        params = parse_params(row.get("params"))
        pop_size = params.get("pop_size")
        generations = params.get("generations")
        mutation_rate = params.get("mutation_rate")
        if pop_size not in target_pop_sizes:
            continue
        if generations not in target_generations:
            continue
        if mutation_rate not in target_mutation_rates:
            continue

        dataset = row.get("dataset")
        score_mean_raw = row.get("score_mean")
        score_best_raw = row.get("score_best")
        if dataset in (None, "") or score_mean_raw in (None, "") or score_best_raw in (None, ""):
            continue

        key = (pop_size, generations, mutation_rate)
        grouped.setdefault(key, {"datasets": 0, "score_mean_values": [], "score_best_values": []})
        grouped[key]["datasets"] += 1
        grouped[key]["score_mean_values"].append(float(score_mean_raw))
        grouped[key]["score_best_values"].append(float(score_best_raw))

    if not grouped:
        print("\n[Resumo] Não há resultados da grelha genética completa neste perfil.")
        return

    summary = []
    for key, values in grouped.items():
        pop_size, generations, mutation_rate = key
        summary.append({
            "pop_size": pop_size,
            "generations": generations,
            "mutation_rate": mutation_rate,
            "datasets": values["datasets"],
            "score_mean_global": round(statistics.mean(values["score_mean_values"]), 2),
            "score_best_global": int(max(values["score_best_values"])),
        })

    summary.sort(key=lambda r: r["score_mean_global"], reverse=True)

    print("\n=== Resumo Genético (grelha pop_size/generations/mutation_rate) ===")
    print("Top 10 combinações por score médio global:")
    for row in summary[:10]:
        print(
            f"pop={row['pop_size']} gen={row['generations']} mut={row['mutation_rate']} "
            f"datasets={row['datasets']} mean={row['score_mean_global']} best={row['score_best_global']}"
        )

    summary_path = os.path.join(OUTPUT_DIR, "genetic_grid_summary.csv")
    with open(summary_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "pop_size",
                "generations",
                "mutation_rate",
                "datasets",
                "score_mean_global",
                "score_best_global",
            ],
        )
        writer.writeheader()
        writer.writerows(summary)

    print(f"Resumo guardado em: {summary_path}")


def run_experiment_config(algo_name, algo_func, algo_params, repeats, profile, known_keys, csv_path):
    rows = []
    input_files = list_input_files()
    if not input_files:
        raise FileNotFoundError("Nenhum ficheiro encontrado na pasta input/.")

    params_str = normalize_params(algo_params)

    fieldnames = [
        "algorithm",
        "dataset",
        "R",
        "C",
        "F",
        "N",
        "B",
        "T",
        "profile",
        "repeats",
        "params",
        "score_best",
        "score_mean",
        "score_std",
        "time_mean_s",
        "time_std_s",
    ]

    for input_file in input_files:
        base_name = os.path.basename(input_file)
        skip_key = (algo_name, base_name, params_str, str(repeats))
        if skip_key in known_keys:
            print(f"[skip] {algo_name} {base_name} params={algo_params} já existe no CSV")
            continue

        R, C, F, N, B, T, rides = read_input(input_file)

        scores = []
        times = []

        for run_id in range(repeats):
            random.seed(1234 + run_id)
            score, elapsed = run_with_timing(algo_func, (F, B, rides), algo_params)
            scores.append(score)
            times.append(elapsed)

        score_mean, score_std = aggregate(scores)
        time_mean, time_std = aggregate(times)

        row = {
            "algorithm": algo_name,
            "dataset": base_name,
            "R": R,
            "C": C,
            "F": F,
            "N": N,
            "B": B,
            "T": T,
            "profile": profile,
            "repeats": repeats,
            "params": params_str,
            "score_best": max(scores),
            "score_mean": round(score_mean, 4),
            "score_std": round(score_std, 4),
            "time_mean_s": round(time_mean, 6),
            "time_std_s": round(time_std, 6),
        }
        rows.append(row)

        print(
            f"[{algo_name}] {base_name} params={algo_params} "
            f"best={row['score_best']} mean={row['score_mean']} time={row['time_mean_s']}s"
        )

        append_rows(csv_path, [row], fieldnames)
        known_keys.add(skip_key)

    return rows


def grid_search_genetic(repeats, profile, known_keys, csv_path):
    if profile == "quick":
        pop_sizes = [20, 50, 100]
        generations = [40, 80, 150]
        mutation_rates = [0.2, 0.35]
    else:
        pop_sizes = [30, 60, 100, 140]
        generations = [80, 150, 250]
        mutation_rates = [0.15, 0.3, 0.45]

    for pop_size, generations_n, mutation_rate in product(pop_sizes, generations, mutation_rates):
        params = {
            "pop_size": pop_size,
            "generations": generations_n,
            "mutation_rate": mutation_rate,
        }
        run_experiment_config("genetic", solve_genetic_algorithm, params, repeats, profile, known_keys, csv_path)

    print(f"\nCSV atualizado: {csv_path}")


def grid_search_randomized_greedy(repeats, profile, known_keys, csv_path):
    if profile == "quick":
        alpha_values = [0.2, 0.35, 0.5]
    else:
        alpha_values = [0.1, 0.2, 0.3, 0.5, 0.7]

    for alpha in alpha_values:
        params = {"alpha": alpha}
        run_experiment_config("randomized_greedy", solve_randomized_greedy, params, repeats, profile, known_keys, csv_path)

    print(f"\nCSV atualizado: {csv_path}")


def parse_args():
    parser = argparse.ArgumentParser(description="Sensitivity benchmark with fast profile and resume.")
    parser.add_argument("--profile", choices=["quick", "full"], default="quick", help="quick: <10min target, full: exhaustive")
    parser.add_argument("--repeats", type=int, default=None, help="override repeat count")
    parser.add_argument("--only", choices=["all", "genetic", "randomized_greedy"], default="all", help="run only one algorithm")
    parser.add_argument("--summary-only", action="store_true", help="skip runs and print only score summary from existing CSV")
    return parser.parse_args()


def main():
    args = parse_args()
    ensure_output_dir()

    repeats = args.repeats
    if repeats is None:
        repeats = DEFAULT_REPEATS_QUICK if args.profile == "quick" else DEFAULT_REPEATS_FULL

    print(f"A correr análise de sensibilidade (profile={args.profile}, repeats={repeats})...")

    csv_paths = {
        "genetic": os.path.join(OUTPUT_DIR, "sensitivity_genetic.csv"),
        "randomized_greedy": os.path.join(OUTPUT_DIR, "sensitivity_randomized_greedy.csv"),
    }

    if args.summary_only:
        summarize_genetic_grid_scores(csv_paths["genetic"], args.profile)
        print("\nConcluído.")
        return

    if args.only in ("all", "genetic"):
        existing = load_existing_rows(csv_paths["genetic"])
        known = existing_keys(existing)
        grid_search_genetic(repeats=repeats, profile=args.profile, known_keys=known, csv_path=csv_paths["genetic"])

    if args.only in ("all", "randomized_greedy"):
        existing = load_existing_rows(csv_paths["randomized_greedy"])
        known = existing_keys(existing)
        grid_search_randomized_greedy(repeats=repeats, profile=args.profile, known_keys=known, csv_path=csv_paths["randomized_greedy"])

    summarize_genetic_grid_scores(csv_paths["genetic"], args.profile)

    print("\nConcluído.")


if __name__ == "__main__":
    main()
