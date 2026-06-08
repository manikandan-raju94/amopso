import numpy as np
import multiprocessing as mp
import tempfile
import os
import time

from sumo_runner import SumoRunner
from xml_signal_builder import SignalBuilder

# -------------------------------
# SIMPLE GENOME DECODE (DUMMY)
# Replace with your JunctionManager if needed
# -------------------------------
def decode_particle(p):
    cycle_dict = {"J1": 60}
    ratio_dict = {"J1": [20, 20, 20]}
    return cycle_dict, ratio_dict


# -------------------------------
# EVALUATION FUNCTION
# -------------------------------
def evaluate(args):
    xml_string, sumo, cfg, seed, worker_id = args

    port = 8813 + worker_id

    runner = SumoRunner(sumo, cfg)

    fd, path = tempfile.mkstemp(suffix=".xml")

    try:
        with os.fdopen(fd, 'w') as f:
            f.write(xml_string)

        time.sleep(0.2)

        wait, metrics = runner.run(path, seed, port)

    finally:
        time.sleep(0.5)
        if os.path.exists(path):
            os.remove(path)

    return wait, metrics


# -------------------------------
# MOPSO
# -------------------------------
class MOPSO:

    def __init__(self, sumo, cfg):
        self.sumo = sumo
        self.cfg = cfg
        self.builder = SignalBuilder()

    def run(self):

        NUM_PARTICLES = 5
        MAX_ITER = 5

        particles = np.random.uniform(0.3, 1.0, (NUM_PARTICLES, 5))
        velocities = np.random.uniform(-0.1, 0.1, (NUM_PARTICLES, 5))

        pool = mp.Pool(processes=1)  # keep 1 first

        for it in range(MAX_ITER):

            jobs = []

            for i in range(NUM_PARTICLES):
                cycle_dict, ratio_dict = decode_particle(particles[i])
                xml = self.builder.build(cycle_dict, ratio_dict)

                jobs.append((xml, self.sumo, self.cfg, it, i))

            results = pool.map(evaluate, jobs)

            for i, (wait, metrics) in enumerate(results):
                print(f"Particle {i} | Wait: {wait:.2f} | CO2: {metrics['CO2']:.2f}")

            print(f"Iteration {it+1} completed\n")

        pool.close()
        pool.join()


# -------------------------------
# MAIN
# -------------------------------
if __name__ == "__main__":

    SUMO = "sumo"
    CONFIG = "runsimulationoutputfile.sumocfg"

    model = MOPSO(SUMO, CONFIG)
    model.run()