# Human Perceptions of Accountable AI

This repository contains the data and the code described in the paper “Responsibility in Multi-Agent Sequential Decision-Making: Comparing Human Judgments to Formal Models of Causal Attribution" by ["Nripsuta Ani Saxena, Stelios Triantafyllou, Goran Radanovic."], to appear in Proceedings of the IJCAI-ECAI 2026 Special Track on: Human-Centred Artificial Intelligence: Multidisciplinary Contours and Challenges of Next-Generation AI Research and Applications., https://2026.ijcai.org/ijcai-ecai-2026-call-for-papers-human-centred-ai/

---

## Overview

This repository investigates whether formal methods for attributing responsibility to AI agents align with human moral intuitions. We simulate a cooperative card game, compute agent responsibility scores using combinations of **actual causation** (AC) and **responsibility attribution** (RA) definitions, and compare these scores against ratings collected from human participants via a Prolific survey.

See the paper for a full description of the game, the formal definitions, and the experimental design.

---

## Repository Structure

```
ijcai2026_hcai/
├── params.py                    # Experiment configuration
├── run_experiment.py            # Main entry point
├── requirements.txt
├── src/                         # Simulation and computation modules
├── data/                        # Generated trajectories and causes, by bias condition
├── combinations_results/        # Computed responsibility scores, by AC×RA combination
├── ground_truth_all_trajectories_responsibilities_scores.csv
├── qualtrics-survey/            # Qualtrics survey export (.qsf)
└── survey_responses/            # Cleaned participant data, plots, and analysis scripts
```

---

## Installation

```bash
git clone <repo-url>
cd ijcai2026_hcai
pip install -r requirements.txt
```

---

## Running the Experiment

Configure the run in `params.py`, then:

```bash
python run_experiment.py
```

This generates game trajectories, computes actual causes, and produces responsibility scores for all AC × RA combinations across the configured bias conditions. Pre-generated data is already included in `data/` and `combinations_results/`; set `generate_new_data = False` in `params.py` to skip regeneration.

---

## Survey Analysis

Scripts for cleaning raw Qualtrics exports and generating plots are in `survey_responses/`. See [`survey_responses/README.md`](survey_responses/README.md) for usage instructions and a full description of the data formats.
