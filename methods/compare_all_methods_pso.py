# ================= IMPORTS =================
import os
import sys
import pandas as pd
import numpy as np
import optuna
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import freeze_support
from concurrent.futures import ProcessPoolExecutor
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)
# ================= CONFIG =================
TRAIN_ITERS = 15
TRAIN_SIZE = 15
TRAININGS = 50
EVAL_RUNS = 10
EVAL_EPISODES = 10
WORKERS = 6

ROOT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

RAW_FILE = os.path.join(ROOT_DIR, "final_results_low.csv")

DB_PATH = f"sqlite:///{os.path.join(ROOT_DIR, 'optuna.db')}"

for p in [
    ROOT_DIR,
    os.path.join(ROOT_DIR, "core"),
    os.path.join(ROOT_DIR, "methods")
]:
    if p not in sys.path:
        sys.path.insert(0, p)

# ================= IMPORT =================
from core.junction_manager import JunctionManager
from core.MultiSignalBuilder import MultiSignalBuilder
from core.sumo_runner import SumoRunner
from amopso_apdative import AMSPSO

# ================= FILES =================

ROOT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

SUMO_BINARY = "sumo"  # or "sumo-gui"

SUMO_CFG = os.path.join(
    ROOT_DIR,
    "runsimulation.sumocfg"
)

SCENARIOS = {
    "low": os.path.join(
        ROOT_DIR,
        "Demand",
        "low_traffic.rou.xml"
    ),

    "medium": os.path.join(
        ROOT_DIR,
        "Demand",
        "medium_low_traffic.rou.xml"
    ),
}

TRAIN_SCENARIO = SCENARIOS["medium"]
EVAL_ROUTE = SCENARIOS["low"]

NET_FILE = os.path.join(
    ROOT_DIR,
    "Network",
    "network_signalized.net.xml"
)

jm = JunctionManager(NET_FILE)
sb = MultiSignalBuilder(template_file=NET_FILE)

# ================= LOAD OPTUNA =================
def get_best_params():
    try:
        study = optuna.load_study(
            study_name="AMOPSO_ADAPTIVE_TUNING",
            storage=DB_PATH
        )
        return study.best_params
    except Exception as e:
        print("⚠️ Optuna load error:", e)
        return {}




def main():
    print("ROOT_DIR =", ROOT_DIR)
    print("DB_PATH =", DB_PATH)
    print("DB EXISTS =", os.path.exists(os.path.join(ROOT_DIR, "methods", "optuna.db")))
    print("NET EXISTS =", os.path.exists(NET_FILE))
    print("CFG EXISTS =", os.path.exists(SUMO_CFG))
    best_params = get_best_params()

    # ================= LOAD OLD CSV =================
    if os.path.exists(RAW_FILE):
        old_df = pd.read_csv(RAW_FILE)
        old_df = old_df[old_df["method"] != "AMSPSO"]
    else:
        old_df = pd.DataFrame()

    # ================= TRAIN AMSPSO =================
    trained_models = []

    print("\n⚡ TRAIN AMSPSO (OPTUNA + FAIR)")

    for t in range(1, TRAININGS + 1):

        seed = 42 + t * 10

        model = AMSPSO(
            jm,
            sb,
            SUMO_BINARY,
            SUMO_CFG
        )

        params = {
            "particles": min(
                best_params.get("particles", TRAIN_SIZE),
                TRAIN_SIZE
            ),
            "c1": best_params.get("c1", 2.0),
            "c2": best_params.get("c2", 2.0),
            "mutation": best_params.get("mutation", 0.3),
            "iters": TRAIN_ITERS,
            "workers": WORKERS
        }

        print(f"Run {t} Params:", params)

        model.run(
            route_file=TRAIN_SCENARIO,
            seed=seed,
            mode="fast",
            **params
        )

        if model.best_genome is not None:
            trained_models.append(
                (t, model.best_genome)
            )

    print("✅ AMSPSO TRAIN DONE")

   # ================= EVALUATION =================
    results = []

    print("\n📊 EVALUATION START")

    for t, genome in trained_models:

        decoded = jm.decode_genome(genome)

        if len(decoded) == 3:
            c, r, o = decoded
        else:
            c, r = decoded
            o = None

        signal_file = sb.build(c, r, o)

        for run in range(1, EVAL_RUNS + 1):

            seeds = list(range(1, EVAL_EPISODES + 1))

            res = run_eval(signal_file, seeds, "smart")

            if res:
                results.append({
                    "method": "AMSPSO",
                    "avg_wait": res[0],
                    "avg_queue": res[1]
                })

            res_full = run_eval(signal_file, seeds, "full")

            if res_full:
                results.append({
                    "method": "AMSPSO_FULL",
                    "avg_wait": res_full[0],
                    "avg_queue": res_full[1]
                })

        # ================= SAVE =================
        new_df = pd.DataFrame(results)

        final_df = pd.concat(
            [old_df, new_df],
            ignore_index=True
        )

        final_df.to_csv(
            RAW_FILE,
            index=False
        )

        print("✅ RESULTS SAVED")

        # ================= SUMMARY =================
        print("\n📊 FINAL SUMMARY")

        print(
            final_df.groupby("method")["avg_wait"]
            .agg(["mean", "std"])
        )

        print("\n📊 AMSPSO (1800)")

        print(
            final_df[
                final_df["method"] == "AMSPSO"
            ]["avg_wait"].agg(["mean", "std"])
        )

        print("\n📊 AMSPSO FULL (3600)")

        print(
            final_df[
                final_df["method"] == "AMSPSO_FULL"
            ]["avg_wait"].agg(["mean", "std"])
        )

# ================= EVAL FUNCTION =================
def _eval_task(args):
    signal_file, seed, mode = args

    runner = SumoRunner(
        SUMO_BINARY,
        SUMO_CFG,
        mode=mode
    )

    return runner.run(
        signal_file,
        seed,
        route_file=EVAL_ROUTE
    )


def run_eval(signal_file, seeds, mode):

    tasks = [
        (signal_file, s, mode)
        for s in seeds
    ]

    with ProcessPoolExecutor(max_workers=WORKERS) as executor:
        results_eval = list(
            executor.map(_eval_task, tasks)
        )

    clean = [
        r for r in results_eval
        if r is not None and len(r) == 3 and r[0] < 9000
    ]

    if not clean:
        return None

    waits = [r[0] for r in clean]
    queues = [r[2] for r in clean]

    return np.mean(waits), np.mean(queues)

if __name__ == "__main__":
    freeze_support()
    main()

