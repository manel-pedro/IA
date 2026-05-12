import ast
import csv
import os
from collections import defaultdict
from statistics import mean

import matplotlib.pyplot as plt


OUTPUT_DIR = "benchmark_outputs"
PLOTS_DIR = os.path.join(OUTPUT_DIR, "plots")


def ensure_dirs():
    os.makedirs(PLOTS_DIR, exist_ok=True)


def read_csv_rows(path):
    with open(path, "r", encoding="utf-8") as f:
        sample = f.read(2048)
        if not sample.strip():
            return []

        f.seek(0)
        first_line = f.readline().strip().lower()
        f.seek(0)

        # Backward compatibility: some generated files may miss the header row.
        has_header = "algorithm" in first_line and "dataset" in first_line
        if has_header:
            reader = csv.DictReader(f)
            return list(reader)

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
        reader = csv.DictReader(f, fieldnames=fieldnames)
        return list(reader)


def parse_params(row):
    try:
        params_raw = row.get("params")
        if not params_raw:
            return {}
        return ast.literal_eval(params_raw)
    except (ValueError, SyntaxError, TypeError):
        return {}


def aggregate_lines(rows, x_param, y_metric):
    # Aggregate repeated experiments (different profiles/repeats) into one line per dataset.
    agg = defaultdict(list)

    for row in rows:
        params = parse_params(row)
        x_val = params.get(x_param)
        if x_val is None:
            continue

        dataset = row.get("dataset", "unknown")
        y_raw = row.get(y_metric)
        if y_raw in (None, ""):
            continue

        try:
            y_val = float(y_raw)
        except ValueError:
            continue

        agg[(dataset, x_val)].append(y_val)

    by_dataset = defaultdict(list)
    for (dataset, x_val), y_values in agg.items():
        by_dataset[dataset].append((float(x_val), mean(y_values)))

    for dataset in by_dataset:
        by_dataset[dataset].sort(key=lambda pair: pair[0])

    return by_dataset


def draw_panel(ax, line_data, x_label, y_label, title):
    if not line_data:
        ax.set_title(f"{title}\n(sem dados)")
        ax.axis("off")
        return

    for dataset, values in sorted(line_data.items()):
        x = [v[0] for v in values]
        y = [v[1] for v in values]
        ax.plot(x, y, marker="o", linewidth=1.8, label=dataset)

    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)


def aggregate_genetic_multifactor(genetic_rows):
    # Key: (pop_size, generations, mutation_rate) -> list of score_mean across datasets/runs.
    score_by_combo = defaultdict(list)

    # Track per-dataset best to compute relative score (% of best dataset score).
    dataset_best = defaultdict(float)
    raw_rows = []

    for row in genetic_rows:
        params = parse_params(row)
        pop_size = params.get("pop_size")
        generations = params.get("generations")
        mutation_rate = params.get("mutation_rate")
        if pop_size is None or generations is None or mutation_rate is None:
            continue

        try:
            score = float(row.get("score_mean", ""))
        except ValueError:
            continue

        dataset = row.get("dataset", "unknown")
        dataset_best[dataset] = max(dataset_best[dataset], score)
        raw_rows.append((dataset, pop_size, generations, mutation_rate, score))
        score_by_combo[(pop_size, generations, mutation_rate)].append(score)

    relative_by_combo = defaultdict(list)
    for dataset, pop_size, generations, mutation_rate, score in raw_rows:
        best = dataset_best.get(dataset, 0.0)
        if best > 0:
            relative_by_combo[(pop_size, generations, mutation_rate)].append((score / best) * 100.0)

    absolute_mean = {
        combo: mean(values) for combo, values in score_by_combo.items() if values
    }
    relative_mean = {
        combo: mean(values) for combo, values in relative_by_combo.items() if values
    }

    return absolute_mean, relative_mean


def plot_genetic_multifactor_score(genetic_rows):
    absolute_mean, relative_mean = aggregate_genetic_multifactor(genetic_rows)
    if not absolute_mean:
        print("Sem dados genéticos suficientes para gráfico multifator.")
        return

    mutation_rates = sorted({combo[2] for combo in absolute_mean.keys()})

    fig_abs, axs_abs = plt.subplots(1, len(mutation_rates), figsize=(6 * len(mutation_rates), 5), squeeze=False)
    for idx, mutation_rate in enumerate(mutation_rates):
        ax = axs_abs[0][idx]
        generations_set = sorted({c[1] for c in absolute_mean if c[2] == mutation_rate})

        for generations in generations_set:
            pairs = []
            for pop_size, gen, mut in absolute_mean:
                if gen == generations and mut == mutation_rate:
                    pairs.append((pop_size, absolute_mean[(pop_size, gen, mut)]))
            pairs.sort(key=lambda p: p[0])
            if pairs:
                x = [p[0] for p in pairs]
                y = [p[1] for p in pairs]
                ax.plot(x, y, marker="o", linewidth=1.8, label=f"gen={generations}")

        ax.set_title(f"mutation_rate={mutation_rate}")
        ax.set_xlabel("Population size")
        ax.set_ylabel("Score médio (absoluto)")
        ax.grid(alpha=0.25)
        ax.legend(fontsize=8)

    fig_abs.suptitle("Genetic: variação de score por pop_size, generations e mutation_rate", fontsize=14, fontweight="bold")
    fig_abs.tight_layout(rect=(0, 0, 1, 0.94))
    out_abs = os.path.join(PLOTS_DIR, "genetic_score_multifactor_absolute.png")
    fig_abs.savefig(out_abs, dpi=150)
    plt.close(fig_abs)
    print(f"Gerado: {out_abs}")

    if relative_mean:
        fig_rel, axs_rel = plt.subplots(1, len(mutation_rates), figsize=(6 * len(mutation_rates), 5), squeeze=False)
        for idx, mutation_rate in enumerate(mutation_rates):
            ax = axs_rel[0][idx]
            generations_set = sorted({c[1] for c in relative_mean if c[2] == mutation_rate})

            for generations in generations_set:
                pairs = []
                for pop_size, gen, mut in relative_mean:
                    if gen == generations and mut == mutation_rate:
                        pairs.append((pop_size, relative_mean[(pop_size, gen, mut)]))
                pairs.sort(key=lambda p: p[0])
                if pairs:
                    x = [p[0] for p in pairs]
                    y = [p[1] for p in pairs]
                    ax.plot(x, y, marker="o", linewidth=1.8, label=f"gen={generations}")

            ax.set_title(f"mutation_rate={mutation_rate}")
            ax.set_xlabel("Population size")
            ax.set_ylabel("Score relativo médio (%)")
            ax.set_ylim(0, 105)
            ax.grid(alpha=0.25)
            ax.legend(fontsize=8)

        fig_rel.suptitle("Genetic: score relativo por combinação de parâmetros", fontsize=14, fontweight="bold")
        fig_rel.tight_layout(rect=(0, 0, 1, 0.94))
        out_rel = os.path.join(PLOTS_DIR, "genetic_score_multifactor_relative.png")
        fig_rel.savefig(out_rel, dpi=150)
        plt.close(fig_rel)
        print(f"Gerado: {out_rel}")


def main():
    ensure_dirs()

    genetic_csv = os.path.join(OUTPUT_DIR, "sensitivity_genetic.csv")
    genetic_rows = read_csv_rows(genetic_csv) if os.path.exists(genetic_csv) else []

    if not genetic_rows:
        print("Sem dados para plotar. Corre primeiro os benchmarks.")
        return

    plot_genetic_multifactor_score(genetic_rows)


if __name__ == "__main__":
    main()
