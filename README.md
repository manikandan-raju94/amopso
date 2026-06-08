# AMPSO: Adaptive Multi-Strategy Particle Swarm Optimisation for Traffic Signal Timing Optimisation

## Overview

This repository presents **AMPSO (Adaptive Multi-Strategy Particle Swarm Optimisation)**, a swarm intelligence-based optimisation framework developed for intelligent traffic signal timing optimisation in urban transportation networks.

The proposed algorithm extends conventional Particle Swarm Optimisation (PSO) through the integration of multiple adaptive search strategies, including diversity-aware parameter adaptation, novelty-guided exploration, adaptive mutation, stagnation detection, and swarm restart mechanisms. These strategies collectively improve exploration capability, prevent premature convergence, and enhance optimisation performance under dynamic traffic conditions.

The framework is integrated with the **Simulation of Urban Mobility (SUMO)** platform to evaluate traffic signal timing plans in realistic traffic environments. Additionally, **Optuna-based hyperparameter optimisation** is employed to automatically identify high-performing parameter configurations.

This repository includes the AMPSO implementation, hyperparameter optimisation framework, sensitivity analysis experiments, and comparative evaluations against baseline optimisation algorithms.

---

## Key Features

* Adaptive Multi-Strategy Particle Swarm Optimisation (AMPSO)
* SUMO-based traffic signal timing optimisation
* Optuna hyperparameter optimisation
* Diversity-aware adaptive parameter adjustment
* Novelty-guided search mechanism
* Adaptive mutation strategy
* Stagnation detection and recovery
* Swarm restart mechanism
* Parallel fitness evaluation
* Hyperparameter sensitivity analysis
* Comparative benchmarking framework
* Scalable optimisation architecture

---

## Methodology

### Adaptive Parameter Adjustment

The algorithm dynamically adjusts optimisation parameters throughout the search process to balance exploration and exploitation.

### Diversity-Aware Learning

Population diversity is continuously monitored and used to adapt learning behaviour, helping maintain effective exploration of the search space.

### Novelty-Guided Search

A novelty metric based on particle distance encourages exploration of previously unexplored regions, reducing the likelihood of premature convergence.

### Adaptive Mutation Strategy

Mutation probability is adjusted according to optimisation progress and stagnation level, enabling the swarm to escape local optima.

### Stagnation Detection

The optimisation process monitors solution improvement and identifies stagnation when progress becomes limited.

### Swarm Restart Mechanism

When stagnation is detected, a portion of the swarm is reinitialised to restore diversity and improve global search capability.

---

## Fitness Function

The optimisation objective combines multiple traffic performance indicators:

```text
Fitness = 0.8 × Waiting Time + 0.2 × Queue Length + Novelty Reward
```

Where:

* **Waiting Time** represents average vehicle delay.
* **Queue Length** represents traffic congestion levels.
* **Novelty Reward** promotes solution diversity and exploration.

The primary objective is to minimise average vehicle waiting time while maintaining efficient traffic flow.

---

## Hyperparameter Optimisation

The framework employs **Optuna** to automatically identify effective parameter configurations.

### Tuned Parameters

* Number of particles
* Cognitive coefficient (c1)
* Social coefficient (c2)
* Number of optimisation iterations
* Exploration-exploitation settings

### Optimisation Objective

The tuning process seeks to minimise:

* Average vehicle waiting time
* Queue length
* Traffic congestion indicators

The best-performing parameter configuration identified by Optuna is subsequently used in the optimisation experiments.

---

## Hyperparameter Sensitivity Analysis

A comprehensive sensitivity analysis was conducted to evaluate the influence of different parameter settings on optimisation performance.

### Parameters Analysed

* Swarm size (particles)
* Cognitive coefficient (c1)
* Social coefficient (c2)
* Number of iterations
* Random seed variations

### Evaluation Metrics

The impact of parameter variations is assessed using:

* Average vehicle waiting time
* Queue length
* Convergence behaviour
* Optimisation stability

The analysis provides insights into the robustness and reliability of the proposed AMPSO framework.

## Comparative Evaluation

The proposed AMPSO algorithm is evaluated against widely used optimisation approaches for traffic signal control.

### Benchmark Algorithms

* Particle Swarm Optimisation (PSO)
* Genetic Algorithm (GA)
* Multi-Objective Particle Swarm Optimisation (MOPSO)
* Other baseline optimisation methods

All algorithms are evaluated under identical traffic demand scenarios to ensure fair comparison.

## Project Structure


## Requirements

### Software

* Python 3.10 or later
* SUMO (Simulation of Urban Mobility)
* TraCI

### Python Libraries

Install the required packages:

pip install numpy pandas matplotlib optuna

## SUMO Installation

Install SUMO from the official website:

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

## Running the Optimisation

Execute the AMPSO optimisation process:

```bash
python run_ampso.py

## Running Hyperparameter Optimisation

Execute Optuna tuning:

```bash
python optuna_tuning.py
```

## Experimental Outputs

The framework reports:

* Best waiting time
* Average queue length
* Population diversity
* Best signal timing plan
* Convergence statistics

Example:

[1/15] Best Wait: 18.42 | Div: 0.312
[2/15] Best Wait: 17.61 | Div: 0.287
[3/15] Best Wait: 16.58 | Div: 0.243


## Performance Metrics

The following traffic performance indicators are used:

* Average Vehicle Waiting Time
* Queue Length
* Traffic Delay
* Vehicle Throughput
* Convergence Speed
* Computational Efficiency

---

## Research Contributions

1. Development of an Adaptive Multi-Strategy Particle Swarm Optimisation (AMPSO) framework.
2. Diversity-aware adaptive parameter adjustment.
3. Novelty-guided exploration mechanism.
4. Adaptive mutation strategy for escaping local optima.
5. Stagnation detection and swarm restart mechanism.
6. Optuna-based hyperparameter optimisation.
7. Hyperparameter sensitivity analysis.
8. Comparative evaluation against baseline optimisation approaches.
9. Integration with SUMO for realistic traffic signal optimisation.

---

## Applications

This framework can be applied to:

* Intelligent Transportation Systems (ITS)
* Smart City Traffic Management
* Urban Mobility Optimisation
* Traffic Signal Timing Design
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
