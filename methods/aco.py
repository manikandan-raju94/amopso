import numpy as np
import os
from concurrent.futures import ProcessPoolExecutor
from core.sumo_runner import SumoRunner


# ================= SAFE EVAL =================
def _evaluate_ant(args):
    xml, sumo_bin, cfg, seed, wid, route_file, mode = args
    path = None

    try:
        if xml is None:
            return 9999.0, 9999.0

        runner = SumoRunner(sumo_bin, cfg, mode=mode)

        path = os.path.join(
            os.getcwd(),
            f"aco_{wid}_{seed}.xml"
        )

        with open(path, "w") as f:
            f.write(xml)

        out = runner.run(path, seed, route_file)

        if out is None or len(out) < 3:
            return 9999.0, 9999.0

        return float(out[0]), float(out[2])

    except Exception as e:
        print("❌ ACO Eval Error:", e)
        return 9999.0, 9999.0

    finally:
        if path and os.path.exists(path):
            os.remove(path)


def parallel_evaluate(jobs, workers=4):
    with ProcessPoolExecutor(max_workers=workers) as executor:
        return list(executor.map(_evaluate_ant, jobs))


# ================= ACO =================
class ACO:

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
            archive_size=10,
            ants=10,
            iters=30,
            q=0.5,
            xi=0.85,
            seed=42,
            workers=4,
            mode="fast"):

        np.random.seed(seed)

        dims = self.jm.get_genome_length()
        print("Genome Length:", dims)

        archive = np.random.uniform(0.2, 0.8, (archive_size, dims))
        archive_fitness = np.full(archive_size, np.inf)

        for it in range(iters):

            print(f"\n🐜 ACO Iteration {it+1}")

            # -------- SORT --------
            idx_sort = np.argsort(archive_fitness)
            archive = archive[idx_sort]
            archive_fitness = archive_fitness[idx_sort]

            # -------- PROBABILITIES --------
            weights = np.exp(-np.arange(archive_size) / (q * archive_size))
            probs = weights / np.sum(weights)

            ants_population = []

            for k in range(ants):
                idx = np.random.choice(archive_size, p=probs)
                mean = archive[idx]

                sigma = np.zeros(dims)
                for d in range(dims):
                    sigma[d] = max(1e-3, xi * np.mean(np.abs(archive[:, d] - mean[d])))

                new_sol = np.random.normal(mean, sigma)
                new_sol = np.clip(new_sol, 0.1, 1.0)

                ants_population.append(new_sol)

            ants_population = np.array(ants_population)

            # -------- BUILD JOBS --------
            jobs = []

            for i in range(ants):
                try:
                    decoded = self.jm.decode_genome(ants_population[i])
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

            new_fitness = []

            for i in range(ants):

                wait = waits[i]
                queue = queues[i]

                if wait >= 9999:
                    fit = 9999
                else:
                    fit = wait + q_weight * queue

                new_fitness.append(fit)

                if fit < self.best_score:
                    self.best_score = fit
                    self.best_wait = wait
                    self.best_genome = ants_population[i].copy()

            print(f"✅ Best Wait: {self.best_wait:.2f}")

            # -------- UPDATE --------
            combined = np.vstack((archive, ants_population))
            combined_fitness = np.concatenate((archive_fitness, new_fitness))

            idx_sort = np.argsort(combined_fitness)

            archive = combined[idx_sort[:archive_size]]
            archive_fitness = combined_fitness[idx_sort[:archive_size]]

        if self.best_genome is None:
            raise RuntimeError("❌ ACO failed completely")

        print("\n🏆 FINAL BEST WAIT:", self.best_wait)
        return float(self.best_wait)