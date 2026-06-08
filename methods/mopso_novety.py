import numpy as np
import os
from concurrent.futures import ProcessPoolExecutor
from core.sumo_runner import SumoRunner


# ================= SAFE EVAL =================
def _evaluate(args):
    xml, sumo_bin, cfg, seed, wid, route_file, mode = args
    path = None

    try:
        if xml is None:
            return 9999.0, 9999.0

        runner = SumoRunner(sumo_bin, cfg, mode=mode)

        path = os.path.join(
            os.getcwd(),
            f"mspso_{wid}_{seed}.xml"
        )

        with open(path, "w") as f:
            f.write(xml)

        out = runner.run(path, seed, route_file)

        if out is None or len(out) < 3:
            return 9999.0, 9999.0

        return float(out[0]), float(out[2])

    except Exception as e:
        print("❌ MSPSO Eval Error:", e)
        return 9999.0, 9999.0

    finally:
        if path and os.path.exists(path):
            os.remove(path)


def parallel_eval(jobs, workers=4):
    with ProcessPoolExecutor(max_workers=workers) as executor:
        return list(executor.map(_evaluate, jobs))


# ================= MSPSO =================
class MSPSO:

    def __init__(self, jm, sb, sumo_binary, config):
        self.jm = jm
        self.sb = sb
        self.sumo = sumo_binary
        self.cfg = config

        self.best_genome = None
        self.best_wait = float("inf")
        self.best_score = float("inf")

        self.archive = []

    # ---------- NOVELTY ----------
    def compute_novelty(self, genome):
        if len(self.archive) == 0:
            return 1.0

        arr = np.array(self.archive)
        dists = np.linalg.norm(arr - genome, axis=1)
        return np.mean(dists)

    # ---------- MAIN ----------
    def run(self,
            route_file,
            particles=6,
            iters=10,
            w=0.7, c1=1.5, c2=1.5,
            workers=4,
            seed=42,
            mode="fast"):

        np.random.seed(seed)

        dims = self.jm.get_genome_length()

        pos = np.random.uniform(0.2, 0.8, (particles, dims))
        vel = np.random.uniform(-0.1, 0.1, (particles, dims))

        pbest = pos.copy()
        pbest_fit = np.full(particles, np.inf)

        gbest = None

        prev_best = float("inf")
        no_improve = 0
        patience = 4

        for it in range(iters):

            print(f"\n🚀 MSPSO Iteration {it+1}")

            progress = it / iters

            # -------- JOBS --------
            jobs = []

            for i in range(particles):
                try:
                    decoded = self.jm.decode_genome(pos[i])
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

            results = parallel_eval(jobs, workers)

            waits = np.array([r[0] for r in results])
            queues = np.array([r[1] for r in results])

            q_weight = np.mean(waits) / (np.mean(queues) + 1e-6)

            nov_list = np.array([self.compute_novelty(pos[i]) for i in range(particles)])

            for i in range(particles):

                wait = waits[i]
                queue = queues[i]

                if wait >= 9999:
                    continue

                novelty_penalty = (1 - (nov_list[i] / (1 + nov_list[i])))

                fitness = wait + q_weight * queue + 0.1 * novelty_penalty

                # PBEST
                if fitness < pbest_fit[i]:
                    pbest_fit[i] = fitness
                    pbest[i] = pos[i].copy()

                # GBEST
                if fitness < self.best_score:
                    self.best_score = fitness
                    self.best_wait = wait
                    self.best_genome = pos[i].copy()
                    gbest = pos[i].copy()

                # ARCHIVE
                if novelty_penalty < 0.5:
                    self.archive.append(pos[i].copy())
                    if len(self.archive) > 100:
                        self.archive.pop(0)

            if gbest is None:
                print("⚠️ Reset swarm")
                pos = np.random.uniform(0.2, 0.8, pos.shape)
                continue

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

            # -------- UPDATE --------
            w_dynamic = 0.9 - 0.5 * progress

            for i in range(particles):

                r1, r2 = np.random.rand(dims), np.random.rand(dims)

                vel[i] = (
                    w_dynamic * vel[i]
                    + c1 * r1 * (pbest[i] - pos[i])
                    + c2 * r2 * (gbest - pos[i])
                )

                vel[i] = np.clip(vel[i], -0.3, 0.3)

                pos[i] += vel[i]

                # exploration
                noise_scale = 0.02 * (1 - progress)
                pos[i] += np.random.uniform(-noise_scale, noise_scale, dims)

                pos[i] = np.clip(pos[i], 0.1, 1.0)

        print("\n🏆 FINAL BEST WAIT:", self.best_wait)
        return self.best_wait