# AMPSO: Adaptive Multi-Strategy Particle Swarm Optimisation for Traffic Signal Timing Optimisation

## Overview

This repository presents **AMPSO (Adaptive Multi-Strategy Particle Swarm Optimisation)**, a swarm intelligence-based optimisation framework developed for intelligent traffic signal timing optimisation in urban transportation networks.

The proposed algorithm extends conventional Particle Swarm Optimisation (PSO) through the integration of multiple adaptive search strategies, including diversity-aware parameter adaptation, novelty-guided exploration, adaptive mutation, stagnation detection, and swarm restart mechanisms. These strategies improve exploration capability, mitigate premature convergence, and enhance optimisation performance under varying traffic conditions.

The framework is integrated with the **Simulation of Urban Mobility (SUMO)** platform for realistic traffic simulation and evaluation. Additionally, **Tree-structured Parzen Estimator (TPE) algorithm** is employed to identify effective parameter configurations for improved optimisation performance.

The repository also includes implementations of several baseline optimisation algorithms for comparative evaluation.

---

## Features

* Adaptive Multi-Strategy Particle Swarm Optimisation (AMPSO)
* SUMO-based traffic signal optimisation
* Optuna hyperparameter tuning
* Novelty-guided search mechanism
* Adaptive mutation strategy
* Diversity-aware parameter adjustment
* Stagnation detection and recovery
* Swarm restart mechanism
* Parallel fitness evaluation
* Hyperparameter sensitivity analysis
* Comparative benchmarking framework
* Realistic traffic demand scenarios

---

## Repository Structure

```text
AMPSO/
│
├── Additionalfiles/
│   ├── Traffic signal configuration files
│   └── Additional SUMO XML files
│
├── core/
│   ├── junction_manager.py
│   ├── main_mopso.py
│   ├── MultiSignalBuilder.py
│   ├── sumo_runner.py
│   ├── sumo_runner_final.py
│   └── xml_signal_builder.py
│
├── Demand/
│   ├── generate_flows.py
│   ├── low_traffic.rou.xml
│   ├── medium_low_traffic.rou.xml
│   └── high_traffic.rou.xml
│
├── methods/
│   ├── pso.py
│   ├── ga.py
│   ├── aco.py
│   ├── mopso_novelty.py
│   ├── optuna_tuning.py
│   └── compare_all_methods_pso.py
│
├── Network/
│   └── network_signalized.net.xml
│
├── outputs/
│   ├── Simulation outputs
│   ├── Optimisation results
│   └── Performance metrics
│
├── utils/
│   ├── logger.py
│   ├── metrics_extractor.py
│   ├── phase_detector.py
│   ├── signal_editor.py
│   └── sumo_runner.py
│
└── runsimulation.sumocfg
```

---

## Methodology

### Adaptive Multi-Strategy Particle Swarm Optimisation (AMPSO)

The proposed AMPSO framework incorporates multiple adaptive mechanisms to improve optimisation performance:

### Adaptive Parameter Adjustment

The inertia weight and learning parameters are dynamically adjusted during optimisation to balance exploration and exploitation.

### Diversity-Aware Search

Population diversity is continuously monitored and used to guide the search process, reducing premature convergence.

### Novelty-Guided Exploration

A novelty metric based on particle distances encourages exploration of unexplored regions of the search space.

### Adaptive Mutation

Mutation probability changes according to optimisation progress and stagnation level, helping the swarm escape local optima.

### Stagnation Detection

The algorithm identifies periods of limited improvement and activates recovery strategies.

### Swarm Restart Mechanism

A portion of the swarm is reinitialised when stagnation occurs, restoring diversity and improving global search capability.

---

## Fitness Function

The optimisation objective combines traffic efficiency and exploration capability:

```text
Fitness = 0.8 × Waiting Time + 0.2 × Queue Length + Novelty Reward
```

Where:

* Waiting Time represents average vehicle delay.
* Queue Length represents congestion level.
* Novelty Reward promotes exploration and diversity.

The primary objective is minimising average vehicle waiting time while maintaining efficient traffic flow.

---

## Hyperparameter Optimisation

The framework uses **Optuna** to automatically identify effective AMPSO parameter settings.

### Tuned Parameters

* Number of particles
* Cognitive coefficient (c1)
* Social coefficient (c2)
* Number of iterations
* Random seed settings

### Optimisation Objective

Minimise:

* Average waiting time
* Queue length
* Traffic congestion indicators

The best-performing parameter configuration obtained through Optuna is used in subsequent experiments.

---

## Hyperparameter Sensitivity Analysis

A sensitivity analysis was conducted to evaluate the influence of parameter settings on optimisation performance.

### Evaluated Parameters

* Swarm size (particles)
* Cognitive coefficient (c1)
* Social coefficient (c2)
* Number of iterations

### Evaluation Metrics

* Average waiting time
* Queue length
* Convergence behaviour
* Optimisation stability

The analysis provides insights into the robustness and reliability of the AMPSO framework.

---

## Implemented Algorithms

The repository contains implementations of the following optimisation methods:

* Adaptive Multi-Strategy Particle Swarm Optimisation (AMPSO)
* Particle Swarm Optimisation (PSO)
* Genetic Algorithm (GA)
* Ant Colony Optimisation (ACO)
* Multi-Objective Particle Swarm Optimisation (MOPSO)

All algorithms are evaluated under identical traffic demand scenarios for fair comparison.

---

## Traffic Scenarios

The optimisation framework supports multiple traffic demand levels:

* Low Traffic Scenario
* Medium Traffic Scenario
* High Traffic Scenario

Traffic demand is generated using SUMO route files located in the Demand directory.

---

## Requirements

### Software

* Python 3.10+
* SUMO (Simulation of Urban Mobility)
* TraCI

### Python Libraries

Install dependencies:

```bash
pip install numpy pandas matplotlib optuna
```

---

## SUMO Installation

Download SUMO from:

https://sumo.dlr.de

Configure the SUMO_HOME environment variable.

### Linux

```bash
export SUMO_HOME=/path/to/sumo
```

### Windows

```cmd
set SUMO_HOME=C:\Program Files (x86)\Eclipse\Sumo
```

---

## Running Hyperparameter Tuning

```bash
python methods/optuna_tuning.py
```

---

## Running Comparative Evaluation

```bash
python methods/compare_all_methods_pso.py
```

---

## Performance Metrics

The following metrics are used for evaluation:

* Average Vehicle Waiting Time
* Queue Length
* Traffic Delay
* Vehicle Throughput
* Convergence Performance
* Computational Efficiency

---

## Research Contributions

* Development of an Adaptive Multi-Strategy Particle Swarm Optimisation (AMPSO) framework.
* Diversity-aware adaptive parameter control.
* Novelty-guided search mechanism.
* Adaptive mutation strategy.
* Stagnation detection and swarm restart mechanism.
* Optuna-based hyperparameter tuning.
* Hyperparameter sensitivity analysis.
* Comparative evaluation against PSO, GA, ACO, and MOPSO.
* SUMO-based traffic signal timing optimisation framework.

---

## Applications

This framework can be applied to:

* Intelligent Transportation Systems (ITS)
* Smart City Traffic Management
* Urban Mobility Optimisation
* Traffic Signal Timing Optimisation
* Transportation Engineering Research
* Swarm Intelligence Research
* Metaheuristic Optimisation Studies

---

## Citation

If you use this repository in your research, please cite:

```bibtex
@software{AMPSO2026,
  author = {Manikandan},
  title = {AMPSO: Adaptive Multi-Strategy Particle Swarm Optimisation for Traffic Signal Timing Optimisation},
  year = {2026},
  publisher = {GitHub}
}
```

---

## License

This project is released under the MIT License.

---

## Author

**Manikandan**

School of Computer Science and Engineering

Vellore Institute of Technology (VIT), India
