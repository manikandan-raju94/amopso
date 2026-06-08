# ================= IMPORTS =================
import optuna
import os
import sys
import glob
from pathlib import Path
from optuna.pruners import MedianPruner

optuna.logging.set_verbosity(optuna.logging.INFO)

# ================= PATH SETUP =================
print("🔎 Locating Project Files...")
search_pattern = "**/Network/network_signalized.net.xml"
found = glob.glob(search_pattern, recursive=True)

if not found:
    raise Exception("❌ network_signalized.net.xml not found")

NET_PATH = found[0]
PROJECT_ROOT = str(Path(NET_PATH).parent.parent)
sys.path.insert(0, PROJECT_ROOT)

# ================= IMPORT PROJECT MODULES =================
from core.junction_manager import JunctionManager
from core.xml_signal_builder import SignalBuilder

from pso import PSO
from mopso_novety import MSPSO as OLD_MSPSO


# 🔥 YOUR ADAPTIVE METHOD
from amopso_apdative import AMSPSO as ADAPTIVE_MSPSO

from ga import GA
from aco import ACO

# ================= CONSTANTS =================
SUMO_BINARY = "sumo"
SUMO_CFG = os.path.join(PROJECT_ROOT, "runsimulation.sumocfg")
LOW_ROUTE = os.path.join(PROJECT_ROOT, "Demand", "medium_low_traffic.rou.xml")

jm = JunctionManager(NET_PATH)
sb = SignalBuilder()

ITERS = 15
N_TRIALS = 20


# ================= TUNING FUNCTION =================
def evaluate_tuning(optimizer, trial, method):

    print(f"\n[Trial {trial.number}] 🚀 {method}")

    try:

        # ================= PSO FAMILY =================
        if method in ["PSO", "HAD_PSO", "MSPSO", "MSPSO_NoRt"]:

            particles = trial.suggest_int("particles", 10, 20)

            if method != "HAD_PSO":
                w = trial.suggest_float("w", 0.5, 0.9)
                c1 = trial.suggest_float("c1", 1.2, 2.2)
                c2 = trial.suggest_float("c2", 1.2, 2.2)
            else:
                w, c1, c2 = 0.5, 1.5, 1.5

            delay = optimizer.run(
                route_file=LOW_ROUTE,
                particles=particles,
                iters=ITERS,
                w=w, c1=c1, c2=c2,
                seed=trial.number * 100 + int(os.getpid())
            )

        # ================= 🔥 ADAPTIVE MSPSO =================
        elif method == "AMOPSO_ADAPTIVE":

          particles = trial.suggest_int("particles", 10, 20)
          c1 = trial.suggest_float("c1", 1.2, 2.5)
          c2 = trial.suggest_float("c2", 1.2, 2.5)

          delay = optimizer.run(
              route_file=LOW_ROUTE,
              particles=particles,
              iters=ITERS,
              c1=c1,
              c2=c2,
              seed=trial.number * 100 + int(os.getpid())
          )

        # ================= GA =================
        elif method == "GA":

            population_size = trial.suggest_int("population_size", 10, 20)
            crossover_rate = trial.suggest_float("crossover_rate", 0.6, 0.9)
            mutation_rate = trial.suggest_float("mutation_rate", 0.05, 0.2)

            delay = optimizer.run(
                route_file=LOW_ROUTE,
                population_size=population_size,
                generations=ITERS,
                crossover_rate=crossover_rate,
                mutation_rate=mutation_rate,
                seed=trial.number * 100 + int(os.getpid())
            )

        # ================= ACO =================
        elif method == "ACO":

            archive_size = trial.suggest_int("archive_size", 8, 15)
            ants = trial.suggest_int("ants", 8, 15)
            q = trial.suggest_float("q", 0.3, 0.8)
            xi = trial.suggest_float("xi", 0.5, 1.0)

            delay = optimizer.run(
                route_file=LOW_ROUTE,
                archive_size=archive_size,
                ants=ants,
                iters=ITERS,
                q=q,
                xi=xi,
                seed=trial.number * 100 + int(os.getpid())
            )

        else:
            raise ValueError("Unknown method")

    except Exception as e:
        print(f"⚠️ Trial Failed: {e}")
        delay = 9999.0

    # ================= REPORT =================
    trial.report(delay, step=0)

    if trial.should_prune():
        print(f"⛔ Trial {trial.number} pruned")
        raise optuna.exceptions.TrialPruned()

    print(f"✅ Score: {delay:.2f}")
    return delay


# ================= STUDY =================
def run_study(method):

    print(f"\n{'='*50}")
    print(f"🚀 STARTING TUNING: {method}")
    print(f"{'='*50}")

    def objective(trial):

        if method == "PSO":
            opt = PSO(jm, sb, SUMO_BINARY, SUMO_CFG)

        
        elif method == "MSPSO":
            opt = OLD_MSPSO(jm, sb, SUMO_BINARY, SUMO_CFG)

        elif method == "AMOPSO_ADAPTIVE":
            opt = ADAPTIVE_MSPSO(jm, sb, SUMO_BINARY, SUMO_CFG)

      

        elif method == "GA":
            opt = GA(jm, sb, SUMO_BINARY, SUMO_CFG)

        elif method == "ACO":
            opt = ACO(jm, sb, SUMO_BINARY, SUMO_CFG)

        else:
            raise ValueError("Unknown method")

        return evaluate_tuning(opt, trial, method)

    study = optuna.create_study(
        direction="minimize",
        study_name=f"{method}_TUNING",
        storage="sqlite:///optuna.db",
        load_if_exists=True,
        pruner=MedianPruner(
            n_startup_trials=5,
            n_warmup_steps=1,
            interval_steps=1
        )
    )

    completed_trials = len([
        t for t in study.trials
        if t.state == optuna.trial.TrialState.COMPLETE
    ])

    remaining_trials = N_TRIALS - completed_trials

    if remaining_trials <= 0:
        print(f"✅ {method} already completed. Skipping...")
    else:
        print(f"🔁 Resuming: {completed_trials} done, {remaining_trials} remaining")

        study.optimize(
            objective,
            n_trials=remaining_trials,
            n_jobs=1
        )

    print(f"\n🏆 BEST RESULT FOR {method}")
    print(f"Best Value: {study.best_value:.2f}")
    print("Best Params:", study.best_params)


# ================= MAIN =================
def main():

    methods = [
        "PSO",
        "HAD_PSO",
        "MSPSO",              # 🔵 baseline
        "AMOPSO_ADAPTIVE",    # 🔥 your novelty
        "MSPSO_NoRt",
        "GA",
        "ACO"
    ]

    for method in methods:
        run_study(method)


if __name__ == "__main__":
    main()