import numpy as np
import os
from concurrent.futures import ProcessPoolExecutor
from core.sumo_runner import SumoRunner
import tempfile

# ================= EVAL =================
def _evaluate(args):
    xml, sumo_bin, cfg, seed, wid, route_file, mode = args
    path = None
    try:
        if xml is None:
            return 9999.0, 9999.0

        runner = SumoRunner(sumo_bin, cfg, mode=mode)
        path = os.path.join(
            os.getcwd(),
            f"amspso_{wid}_{seed}.xml"
        )

        with open(path, "w") as f:
            f.write(xml)

        out = runner.run(path, seed, route_file)
        print(f"Worker {wid} Output = {out}")

        if out is None or len(out) < 3:
            return 9999.0, 9999.0

        return float(out[0]), float(out[2])

    except Exception as e:
        print(f"WORKER {wid} ERROR: {e}")
        return 9999.0, 9999.0

    finally:
        if path and os.path.exists(path):
            os.remove(path)


def parallel_eval(jobs, workers):
    with ProcessPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(_evaluate, jobs))


# ================= NOVELTY =================
def compute_novelty(pos):
    n = len(pos)
    nov = np.zeros(n)
    for i in range(n):
        d = np.linalg.norm(pos - pos[i], axis=1)
        nov[i] = d.sum() / (n - 1)
    if nov.max() > 1e-9:
        nov /= nov.max()
    return nov


# ================= AMSPSO =================
class AMSPSO:

    def __init__(self, jm, sb, sumo_binary, config):
        self.jm = jm
        self.sb = sb
        self.sumo = sumo_binary
        self.cfg = config

        self.best_genome = None
        self.best_wait = float("inf")

    def run(self, route_file, seed=42, mode="fast", **params):

        np.random.seed(seed)

        particles = params.get("particles", 20)
        iters = params.get("iters", 15)
        workers = params.get("workers", 6)

        dims = self.jm.get_genome_length()

        pos = np.random.uniform(0.1, 0.9, (particles, dims))
        vel = np.random.uniform(-0.5, 0.5, (particles, dims))

        pbest = pos.copy()
        pbest_fit = np.full(particles, np.inf)

        best_wait = float("inf")
        best_genome = None

        stagnation = 0
        prev_best = float("inf")

        for it in range(iters):

            progress = it / (iters - 1)

            # ================= DIVERSITY =================
            diversity = np.mean(np.std(pos, axis=0))

            # ================= FULL ADAPTIVE =================
            w = 0.9 - 0.5 * progress

            if diversity < 0.15:
                c1 = 2.5
                c2 = 1.5
            else:
                c1 = 1.5
                c2 = 2.5

            # mutation based on stagnation
            if stagnation > 0:
                mutation = min(0.6, 0.3 * (1 + stagnation))
            else:
                mutation = 0.3 - 0.2 * progress

            # ================= EVAL =================
            jobs = []
            for i in range(particles):
                try:
                    dec = self.jm.decode_genome(pos[i])
                    xml = self.sb.build_string(dec[0], dec[1])
                except Exception as e:
                    print("BUILD ERROR:", e)
                    xml = None

                jobs.append((xml, self.sumo, self.cfg, seed, i, route_file, mode))

            results = parallel_eval(jobs, workers)

            waits = np.array([r[0] for r in results])
            queues = np.array([r[1] for r in results])
            novelty = compute_novelty(pos)

            for i in range(particles):

                if waits[i] >= 9000:
                    continue

                fitness = (
                    0.8 * waits[i] +
                    0.2 * queues[i] +
                    5.0 * novelty[i]
                )

                if fitness < pbest_fit[i]:
                    pbest_fit[i] = fitness
                    pbest[i] = pos[i].copy()

                if waits[i] < best_wait:
                    best_wait = waits[i]
                    best_genome = pos[i].copy()
                    self.best_genome = best_genome.copy()
                    self.best_wait = best_wait

            # ================= STAGNATION =================
            if abs(prev_best - best_wait) < 0.05:
                stagnation += 1
            else:
                stagnation = 0
                prev_best = best_wait

            # restart if stuck
            if stagnation >= 2:
                for i in range(particles // 2):
                    pos[i] = np.random.uniform(0, 1, dims)
                stagnation = 0

            print(f"[{it+1}/{iters}] Best Wait: {best_wait:.2f} | Div: {diversity:.3f}")

            # ================= UPDATE =================
            elite = np.mean(pbest[np.argsort(pbest_fit)[:5]], axis=0)

            for i in range(particles):

                r1, r2 = np.random.rand(dims), np.random.rand(dims)

                vel[i] = (
                    w * vel[i]
                    + c1 * r1 * (pbest[i] - pos[i])
                    + c2 * r2 * (elite - pos[i])
                )

                pos[i] += vel[i]

                if np.random.rand() < mutation:
                    pos[i] += np.random.uniform(-0.2, 0.2, dims)

                pos[i] = np.clip(pos[i], 0, 1)

        return best_wait