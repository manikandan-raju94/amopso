import numpy as np
import os
from concurrent.futures import ProcessPoolExecutor
from core.sumo_runner import SumoRunner


# ================= SAFE EVAL =================
def _evaluate_individual(args):
    xml, sumo_bin, cfg, seed, wid, route_file, mode = args
    path = None

    try:
        if xml is None:
            return 9999.0, 9999.0

        runner = SumoRunner(sumo_bin, cfg, mode=mode)

        path = os.path.join(
            os.getcwd(),
            f"ga_{wid}_{seed}.xml"
        )

        with open(path, "w") as f:
            f.write(xml)

        out = runner.run(path, seed, route_file)

        if out is None or len(out) < 3:
            return 9999.0, 9999.0

        return float(out[0]), float(out[2])

    except Exception as e:
        print("❌ GA Eval Error:", e)
        return 9999.0, 9999.0

    finally:
        if path and os.path.exists(path):
            os.remove(path)


def parallel_evaluate(jobs, workers=4):
    with ProcessPoolExecutor(max_workers=workers) as executor:
        return list(executor.map(_evaluate_individual, jobs))


# ================= GA =================
class GA:

    def __init__(self, jm, sb, sumo_binary, config):
        self.jm = jm
        self.sb = sb
        self.sumo = sumo_binary
        self.cfg = config

        self.best_genome = None
        self.best_wait = float("inf")
        self.best_score = float("inf")

    def run(self,
            route_file,
            population_size=6,
            generations=10,
            crossover_rate=0.8,
            mutation_rate=0.1,
            elitism=2,
            seed=42,
            workers=4,
            mode="fast"):

        np.random.seed(seed)

        dims = self.jm.get_genome_length()

        population = np.random.uniform(0.2, 0.8, (population_size, dims))

        prev_best = float("inf")
        no_improve = 0
        patience = 4

        for gen in range(generations):

            print(f"\n🧬 GA Generation {gen+1}")

            # -------- JOBS --------
            jobs = []

            for i in range(population_size):
                try:
                    decoded = self.jm.decode_genome(population[i])
                    cycles, ratios = decoded[0], decoded[1]
                    xml = self.sb.build_string(cycles, ratios)
                except:
                    xml = None

                jobs.append((
                    xml,
                    self.sumo,
                    self.cfg,
                    seed,
                    i,
                    route_file,
                    mode
                ))

            results = parallel_evaluate(jobs, workers)

            waits = np.array([r[0] for r in results])
            queues = np.array([r[1] for r in results])

            q_weight = np.mean(waits) / (np.mean(queues) + 1e-6)

            fitness_scores = []

            for i in range(population_size):

                wait = waits[i]
                queue = queues[i]

                if wait >= 9999:
                    fit = 9999
                else:
                    fit = wait + q_weight * queue

                fitness_scores.append(fit)

                if fit < self.best_score:
                    self.best_score = fit
                    self.best_wait = wait
                    self.best_genome = population[i].copy()

            print(f"✅ Best Wait: {self.best_wait:.2f}")

            # -------- EARLY STOP --------
            if self.best_wait < prev_best:
                prev_best = self.best_wait
                no_improve = 0
            else:
                no_improve += 1

            if no_improve >= patience:
                print("⏹ Early stopping")
                break

            # -------- ELITISM --------
            sorted_idx = np.argsort(fitness_scores)
            elites = population[sorted_idx[:elitism]]

            # -------- SELECTION --------
            selected = []
            for _ in range(population_size):
                i, j = np.random.randint(0, population_size, 2)
                winner = population[i] if fitness_scores[i] < fitness_scores[j] else population[j]
                selected.append(winner)

            selected = np.array(selected)

            # -------- CROSSOVER --------
            next_pop = []

            for i in range(0, population_size, 2):
                p1 = selected[i]
                p2 = selected[(i + 1) % population_size]

                if np.random.rand() < crossover_rate:
                    point = np.random.randint(1, dims)
                    c1 = np.concatenate([p1[:point], p2[point:]])
                    c2 = np.concatenate([p2[:point], p1[point:]])
                else:
                    c1, c2 = p1.copy(), p2.copy()

                next_pop.extend([c1, c2])

            population = np.array(next_pop[:population_size])

            # -------- MUTATION --------
            noise_scale = 0.05 * (1 - gen / generations)

            for i in range(population_size):
                for d in range(dims):
                    if np.random.rand() < mutation_rate:
                        population[i][d] += np.random.uniform(-noise_scale, noise_scale)

            population = np.clip(population, 0.1, 1.0)

            # -------- ELITE INSERT --------
            population[:elitism] = elites

        if self.best_genome is None:
            raise RuntimeError("❌ GA failed completely")

        print("\n🏆 FINAL BEST WAIT:", self.best_wait)
        return float(self.best_wait)