import numpy as np
import os
from concurrent.futures import ProcessPoolExecutor
from core.sumo_runner import SumoRunner
import tempfile

# ================= SAFE EVAL =================
def _evaluate_particle(args):
    xml, sumo_bin, cfg, seed, wid, route_file, mode = args
    path = None

    try:
        if xml is None:
            return 9999.0, 9999.0

        runner = SumoRunner(sumo_bin, cfg, mode=mode)

        path = os.path.join(
            tempfile.gettempdir(),
            f"pso_{wid}_{seed}.xml"
        )

        with open(path, "w") as f:
            f.write(xml)

        out = runner.run(path, seed, route_file)

        if out is None or len(out) < 3:
            return 9999.0, 9999.0

        return float(out[0]), float(out[2])

    except Exception as e:
        print("❌ PSO Eval Error:", e)
        return 9999.0, 9999.0

    finally:
        if path and os.path.exists(path):
            os.remove(path)


def parallel_evaluate(jobs, workers=4):
    with ProcessPoolExecutor(max_workers=workers) as executor:
        return list(executor.map(_evaluate_particle, jobs))


# ================= PSO =================
class PSO:

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
            particles=6,
            iters=10,
            w=0.9, c1=1.6, c2=1.6,
            seed=42,
            workers=4,
            mode="fast"):

        np.random.seed(seed)

        dims = self.jm.get_genome_length()

        swarm = np.random.uniform(0.2, 0.8, (particles, dims))
        velocity = np.random.uniform(-0.1, 0.1, (particles, dims))

        pbest = swarm.copy()
        pbest_fit = np.full(particles, np.inf)

        gbest = None
        gbest_fit = np.inf

        prev_best = float("inf")
        no_improve = 0
        patience = 4

        for it in range(iters):

            print(f"\n🚀 PSO Iteration {it+1}")

            # -------- BUILD JOBS --------
            jobs = []

            for i in range(particles):
                try:
                    decoded = self.jm.decode_genome(swarm[i])
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

            for i in range(particles):

                wait = waits[i]
                queue = queues[i]

                if wait >= 9999:
                    continue

                fit = wait + q_weight * queue

                # PBEST
                if fit < pbest_fit[i]:
                    pbest_fit[i] = fit
                    pbest[i] = swarm[i].copy()

                # GBEST
                if fit < gbest_fit:
                    gbest_fit = fit
                    gbest = swarm[i].copy()

                    self.best_wait = wait
                    self.best_score = fit
                    self.best_genome = swarm[i].copy()

            if gbest is None:
                print("⚠️ Reset swarm")
                swarm = np.random.uniform(0.2, 0.8, swarm.shape)
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
            w_dynamic = w * (1 - it / iters)

            for i in range(particles):

                r1, r2 = np.random.rand(dims), np.random.rand(dims)

                velocity[i] = (
                    w_dynamic * velocity[i]
                    + c1 * r1 * (pbest[i] - swarm[i])
                    + c2 * r2 * (gbest - swarm[i])
                )

                velocity[i] = np.clip(velocity[i], -0.2, 0.2)

                swarm[i] += velocity[i]

                # late exploration
                if it > 0.7 * iters:
                    swarm[i] += np.random.uniform(-0.02, 0.02, dims)

                swarm[i] = np.clip(swarm[i], 0.1, 1.0)

        if gbest is None:
            raise RuntimeError("❌ PSO failed completely")

        print("\n🏆 PSO FINAL BEST WAIT:", self.best_wait)
        return float(self.best_wait)