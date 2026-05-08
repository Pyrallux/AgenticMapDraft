# AgenticMapDraft

## Running the Project

```bash
pip install -r requirements.txt
cd src
python generate_map_statistics.py
python run_tournament_eval.py --num-tournaments 10000
```

Note: this will likely take a significant amount of time to run. Try reducing the number of tournaments for a quicker test run.

## Project Structure

```
.
├── README.md                          # Project documentation and running instructions
├── requirements.txt                   # Python package dependencies
├── data/
│   ├── map_stats.csv                  # Calculated map statistics for each team (generated)
│   └── maps_scores.csv                # Map performance scores from tournament data (from dataset)
└── src/
    ├── reflex.py                      # Simple reflex agent with hand-coded decision rules
    ├── minimax.py                     # Minimax game tree search agent for map drafting
    ├── cfr.py                         # Counterfactual regret minimization agent
    ├── generate_map_statistics.py     # Computes map statistics from raw dataset (run first)
    └── run_tournament_eval.py         # Runs simulated tournament evaluation (run second)
```

## Data

- [Valorant Champion Tour 2021-2026 Data](https://www.kaggle.com/datasets/ryanluong1/valorant-champion-tour-2021-2023-data) - Kaggle
