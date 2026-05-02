# Runs a simulated tournament between agents, tracking their performance against one another

"""
Each agent will be compared to one another based on their success in 100s simulated head-to-head agent tournaments.
Format:
  Single-elimination brackets with one reflex agent, one minimax heuristic agent, CFR agent, and one randomly selected agent.
  Each agent will be randomly assigned the map pool statistics of a real-world team from our dataset for each tournament fron real-world data.
  Bracket Example:
      Round 1: Reflex vs Random(CFR), Minimax vs CFR
      Round 2: Winner of Round 1 Match 1 vs Winner of Round 1 Match 2
  Each agent's location in the bracket and which team is chosen to be team A or team B will be randomized across each tournament.
Evaluation:
  We will track how each agent performs against each other's unique method and itself.
  Agents which are matched against each other will complete the map draft process and the winner
  of a given match will be determined by having the highest “strength” score on at least two of the three
  maps chosen.
  Overall, the agent with the best win rate across all tournaments will be considered the best suited for this task environment.
"""

import random
import ast
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from reflex import ReflexAgent
from minimax import MinimaxAgent
from cfr import CFRAgent


def load_map_stats():
    df = pd.read_csv("../data/map_stats.csv", index_col=0, skipinitialspace=True)
    # Remove spaces
    df.columns = [col.strip() for col in df.columns]

    # Store team stats as {team_name: {map_name: strength}}
    team_stats = {}
    for team in df.index:
        team_name = str(team).strip()
        team_stats[team_name] = {}
        for map_name in df.columns:
            cell = df.loc[team, map_name]
            if isinstance(cell, str) and cell.strip():
                data = ast.literal_eval(cell.strip())
                team_stats[team_name][map_name] = data.get("strength", 0.0)
            else:
                team_stats[team_name][map_name] = 0.0

    return team_stats, list(df.columns)


def simulate_match(team_a_agent, team_b_agent, team_a_stats, team_b_stats, map_pool):
    available_actions = map_pool.copy()
    action_sequence = []
    action_strength_deltas = []

    for i in range(7):
        current_agent = team_a_agent if i % 2 == 0 else team_b_agent

        chosen_action = current_agent.get_action(
            team_a_stats,
            team_b_stats,
            available_actions,
            i,
        )

        if chosen_action not in available_actions:
            raise ValueError(
                f"Invalid action chosen: {chosen_action} not in available maps {available_actions}"
            )

        available_actions.remove(chosen_action)

        strength_a = team_a_stats.get(chosen_action, 0)
        strength_b = team_b_stats.get(chosen_action, 0)
        strength_delta = strength_a - strength_b

        action_sequence.append(chosen_action)
        action_strength_deltas.append(strength_delta)

    # Determine winner based on map strengths of picked maps
    a_wins = 0
    b_wins = 0
    for action_index in [2, 3, 6]:
        m = action_sequence[action_index]
        strength_a = team_a_stats.get(m, 0)
        strength_b = team_b_stats.get(m, 0)

        if strength_a > strength_b:
            a_wins += 1
        elif strength_b > strength_a:
            b_wins += 1
        else:
            if random.random() < 0.5:
                a_wins += 1
            else:
                b_wins += 1

    winner = "team_a" if a_wins >= 2 else "team_b"
    score = f"{min(a_wins, 2)}-{min(b_wins, 2)}"
    return winner, score, action_sequence, action_strength_deltas


def run_tournament(team_stats, map_pool):
    agent_classes = {
        "Reflex": ReflexAgent,
        "Minimax": MinimaxAgent,
        "CFR": CFRAgent,
    }

    agents = [
        {"name": "Reflex", "instance": ReflexAgent()},
        {"name": "Minimax", "instance": MinimaxAgent()},
        {"name": "CFR", "instance": CFRAgent()},
    ]

    # Add a random duplicate from the existing types
    random_name = random.choice(list(agent_classes.keys()))
    agents.append({"name": random_name, "instance": agent_classes[random_name]()})

    # Shuffle agents to randomize bracket
    random.shuffle(agents)

    # Select 4 random teams for this tournament
    teams = random.sample(list(team_stats.keys()), 4)

    # Assign agents team map pools
    for i, _ in enumerate(agents):
        agents[i]["team_stats"] = team_stats[teams[i]]
        agents[i]["team_name"] = teams[i]

    # Play out Round 1 of the tournmanet
    match1_teams = (agents[0], agents[1])
    match2_teams = (agents[2], agents[3])

    (
        match_1_winner,
        match_1_score,
        match_1_action_sequence,
        match_1_action_strength_deltas,
    ) = simulate_match(
        match1_teams[0]["instance"],
        match1_teams[1]["instance"],
        match1_teams[0]["team_stats"],
        match1_teams[1]["team_stats"],
        map_pool,
    )
    winner1 = match1_teams[0] if match_1_winner == "team_a" else match1_teams[1]

    (
        match_2_winner,
        match_2_score,
        match_2_action_sequence,
        match_2_action_strength_deltas,
    ) = simulate_match(
        match2_teams[0]["instance"],
        match2_teams[1]["instance"],
        match2_teams[0]["team_stats"],
        match2_teams[1]["team_stats"],
        map_pool,
    )
    winner2 = match2_teams[0] if match_2_winner == "team_a" else match2_teams[1]

    # Round 2 (Final)
    (
        final_winner_side,
        final_score,
        final_action_sequence,
        final_action_strength_deltas,
    ) = simulate_match(
        winner1["instance"],
        winner2["instance"],
        winner1["team_stats"],
        winner2["team_stats"],
        map_pool,
    )
    tournament_winner = winner1 if final_winner_side == "team_a" else winner2

    # Compile tournament data for analysis and debugging
    tournament_data = {
        "match_1": {
            "team_a": match1_teams[0]["name"],
            "team_a_name": match1_teams[0]["team_name"],
            "team_b": match1_teams[1]["name"],
            "team_b_name": match1_teams[1]["team_name"],
            "winner": winner1["name"],
            "winner_name": winner1["team_name"],
            "score": match_1_score,
            "draft_seq": match_1_action_sequence,
            "draft_strength_deltas": match_1_action_strength_deltas,
        },
        "match_2": {
            "team_a": match2_teams[0]["name"],
            "team_a_name": match2_teams[0]["team_name"],
            "team_b": match2_teams[1]["name"],
            "team_b_name": match2_teams[1]["team_name"],
            "winner": winner2["name"],
            "winner_name": winner2["team_name"],
            "score": match_2_score,
            "draft_seq": match_2_action_sequence,
            "draft_strength_deltas": match_2_action_strength_deltas,
        },
        "final": {
            "team_a": winner1["name"],
            "team_a_name": winner1["team_name"],
            "team_b": winner2["name"],
            "team_b_name": winner2["team_name"],
            "winner": tournament_winner["name"],
            "winner_name": tournament_winner["team_name"],
            "score": final_score,
            "draft_seq": final_action_sequence,
            "draft_strength_deltas": final_action_strength_deltas,
        },
    }

    return tournament_data


if __name__ == "__main__":
    # Parse CLI Arguments
    parser = argparse.ArgumentParser(
        description="Evaluate agents in a simulated map draft tournament."
    )
    parser.add_argument(
        "--show-brackets",
        action="store_true",
        help="Display an interactive visualization of each tournament bracket.",
    )
    parser.add_argument(
        "--num-tournaments",
        type=int,
        default=1000,
        help="Number of tournaments to run.",
    )
    args = parser.parse_args()
    NUM_TOURNAMENTS = args.num_tournaments
    SHOW_BRACKETS = args.show_brackets

    # Load Team Map Stats
    TEAM_STATS, ALL_MAPS = load_map_stats()

    tournament_results = []
    # Run Specified Number of Tournamnets
    for _ in range(NUM_TOURNAMENTS):
        t_data = run_tournament(TEAM_STATS, set(ALL_MAPS))
        tournament_results.append(t_data)

    # Initialize win count dictionaries correctly
    agent_stats = {
        name: {
            "tournament_wins": 0,
            "match_wins": 0,
            "match_plays": 0,
            "against_reflex_wins": 0,
            "against_reflex_plays": 0,
            "against_minimax_wins": 0,
            "against_minimax_plays": 0,
            "against_cfr_wins": 0,
            "against_cfr_plays": 0,
        }
        for name in ["Reflex", "Minimax", "CFR"]
    }

    # Calculate win counts
    for tournament in tournament_results:
        m1 = tournament["match_1"]
        m2 = tournament["match_2"]
        f = tournament["final"]

        agent_stats[f["winner"]]["tournament_wins"] += 1

        for match in [m1, m2, f]:
            a = match["team_a"]
            b = match["team_b"]
            w = match["winner"]
            loss_agent = b if w == a else a

            # Match plays and wins
            agent_stats[a]["match_plays"] += 1
            agent_stats[b]["match_plays"] += 1
            agent_stats[w]["match_wins"] += 1

            # Head-to-head tracking
            agent_stats[a][f"against_{b.lower()}_plays"] += 1
            agent_stats[b][f"against_{a.lower()}_plays"] += 1

            agent_stats[w][f"against_{loss_agent.lower()}_wins"] += 1

    # Display Tournament Results
    if SHOW_BRACKETS:
        fig, ax = plt.subplots(figsize=(12, 8))
        plt.subplots_adjust(bottom=0.2)
        current_idx = [0]

        def draw_bracket(idx):
            ax.clear()
            ax.axis("off")
            ax.set_xlim(0, 1.0)
            ax.set_ylim(0, 1.0)
            data = tournament_results[idx]
            ax.set_title(f"Tournament {idx + 1} / {NUM_TOURNAMENTS}", fontsize=16)

            m1 = data["match_1"]
            m2 = data["match_2"]
            f = data["final"]

            box_props = dict(
                boxstyle="round,pad=0.6",
                alpha=1.0,
                facecolor="#cce6ff",
                edgecolor="dodgerblue",
            )

            # Match 1 text
            # Draft sequence: Ban1, Ban2, Pick1, Pick2, Ban3, Ban4, Decider (indx 0-6)
            # Display: Map chosen and strength delta
            text_m1 = (
                f"--- Round 1, Match 1 ---\n"
                f"Team A: {m1['team_a']} ({m1['team_a_name']})\n"
                f"Team B: {m1['team_b']} ({m1['team_b_name']})\n"
                f"Result: {m1['score']} -> {m1['winner']} ({m1['winner_name']})\n"
                f"Draft Sequence:\n"
                f"  Team A Ban 1: {m1['draft_seq'][0]} ({m1['draft_strength_deltas'][0]:+.2f})\n"
                f"  Team B Ban 1: {m1['draft_seq'][1]} ({m1['draft_strength_deltas'][1]:+.2f})\n"
                f"  Team A Pick 1: {m1['draft_seq'][2]} ({m1['draft_strength_deltas'][2]:+.2f})\n"
                f"  Team B Pick 1: {m1['draft_seq'][3]} ({m1['draft_strength_deltas'][3]:+.2f})\n"
                f"  Team A Ban 2: {m1['draft_seq'][4]} ({m1['draft_strength_deltas'][4]:+.2f})\n"
                f"  Team B Ban 2: {m1['draft_seq'][5]} ({m1['draft_strength_deltas'][5]:+.2f})\n"
                f"  Decider: {m1['draft_seq'][6]} ({m1['draft_strength_deltas'][6]:+.2f})\n"
            )
            ax.text(
                0.02,
                0.75,
                text_m1,
                va="center",
                ha="left",
                bbox=box_props,
                fontsize=8,
                zorder=10,
            )

            # Match 2 text
            text_m2 = (
                f"--- Round 1, Match 2 ---\n"
                f"Team A: {m2['team_a']} ({m2['team_a_name']})\n"
                f"Team B: {m2['team_b']} ({m2['team_b_name']})\n"
                f"Result: {m2['score']} -> {m2['winner']} ({m2['winner_name']})\n"
                f"Draft Sequence:\n"
                f"  Team A Ban 1: {m2['draft_seq'][0]} ({m2['draft_strength_deltas'][0]:+.2f})\n"
                f"  Team B Ban 1: {m2['draft_seq'][1]} ({m2['draft_strength_deltas'][1]:+.2f})\n"
                f"  Team A Pick 1: {m2['draft_seq'][2]} ({m2['draft_strength_deltas'][2]:+.2f})\n"
                f"  Team B Pick 1: {m2['draft_seq'][3]} ({m2['draft_strength_deltas'][3]:+.2f})\n"
                f"  Team A Ban 2: {m2['draft_seq'][4]} ({m2['draft_strength_deltas'][4]:+.2f})\n"
                f"  Team B Ban 2: {m2['draft_seq'][5]} ({m2['draft_strength_deltas'][5]:+.2f})\n"
                f"  Decider: {m2['draft_seq'][6]} ({m2['draft_strength_deltas'][6]:+.2f})\n"
            )
            ax.text(
                0.02,
                0.25,
                text_m2,
                va="center",
                ha="left",
                bbox=box_props,
                fontsize=8,
                zorder=10,
            )

            # Final text
            text_f = (
                f"--- Finals ---\n"
                f"Team A: {f['team_a']} ({f['team_a_name']})\n"
                f"Team B: {f['team_b']} ({f['team_b_name']})\n"
                f"Result: {f['score']} -> {f['winner']} ({f['winner_name']})\n"
                f"Draft Sequence:\n"
                f"  Team A Ban 1: {f['draft_seq'][0]} ({f['draft_strength_deltas'][0]:+.2f})\n"
                f"  Team B Ban 1: {f['draft_seq'][1]} ({f['draft_strength_deltas'][1]:+.2f})\n"
                f"  Team A Pick 1: {f['draft_seq'][2]} ({   f['draft_strength_deltas'][2]:+.2f})\n"
                f"  Team B Pick 1: {f['draft_seq'][3]} ({f['draft_strength_deltas'][3]:+.2f})\n"
                f"  Team A Ban 2: {f['draft_seq'][4]} ({f['draft_strength_deltas'][4]:+.2f})\n"
                f"  Team B Ban 2: {f['draft_seq'][5]} ({f['draft_strength_deltas'][5]:+.2f})\n"
                f"  Decider: {f['draft_seq'][6]} ({f['draft_strength_deltas'][6]:+.2f})\n"
            )
            ax.text(
                0.52,
                0.5,
                text_f,
                va="center",
                ha="left",
                bbox=dict(
                    boxstyle="round,pad=0.6",
                    alpha=1.0,
                    facecolor="#fff2cc",
                    edgecolor="gold",
                ),
                fontsize=10,
                zorder=10,
            )

            # Draw connecting bracket lines
            line_kwargs = dict(color="black", linewidth=2, zorder=-1)
            ax.plot([0.20, 0.40], [0.75, 0.75], **line_kwargs)  # Match 1 horizontal
            ax.plot([0.20, 0.40], [0.25, 0.25], **line_kwargs)  # Match 2 horizontal
            ax.plot([0.40, 0.40], [0.25, 0.75], **line_kwargs)  # Vertical connect
            ax.plot([0.40, 0.55], [0.5, 0.5], **line_kwargs)  # Connect to Final

            fig.canvas.draw_idle()

        draw_bracket(0)
        axprev = plt.axes([0.35, 0.05, 0.1, 0.075])
        axnext = plt.axes([0.55, 0.05, 0.1, 0.075])
        bnext = Button(axnext, "Next")
        bprev = Button(axprev, "Previous")

        def next_tournament(event):
            if current_idx[0] < len(tournament_results) - 1:
                current_idx[0] += 1
                draw_bracket(current_idx[0])

        def prev_tournament(event):
            if current_idx[0] > 0:
                current_idx[0] -= 1
                draw_bracket(current_idx[0])

        bnext.on_clicked(next_tournament)
        bprev.on_clicked(prev_tournament)

        plt.show()

    # Evaluate results (matplotlib charts)
    print(f"Tournament results over {NUM_TOURNAMENTS} simulations:")

    fig, axes = plt.subplots(1, 3, figsize=(15, 6))
    fig.suptitle("Agent Performance in Map Draft Tournaments (Winrates %)", fontsize=16)

    for idx, agent in enumerate(["Reflex", "Minimax", "CFR"]):
        stats = agent_stats[agent]

        def safe_div(num, den):
            return (num / den * 100) if den > 0 else 0.0

        t_winrate = safe_div(stats["tournament_wins"], NUM_TOURNAMENTS)
        m_winrate = safe_div(stats["match_wins"], stats["match_plays"])

        vs_reflex = safe_div(
            stats["against_reflex_wins"], stats["against_reflex_plays"]
        )
        vs_minimax = safe_div(
            stats["against_minimax_wins"], stats["against_minimax_plays"]
        )
        vs_cfr = safe_div(stats["against_cfr_wins"], stats["against_cfr_plays"])

        categories = ["Tournament", "Match", "vs Reflex", "vs Minimax", "vs CFR"]
        winrates = [t_winrate, m_winrate, vs_reflex, vs_minimax, vs_cfr]

        ax = axes[idx]
        bars = ax.bar(
            categories, winrates, color=["purple", "cyan", "blue", "orange", "green"]
        )
        ax.set_ylim(0, 105)
        ax.set_title(f"{agent} Agent")
        ax.set_ylabel("Winrate (%)")
        ax.tick_params(axis="x", rotation=45)

        # Add labels
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + 1,
                f"{height:.1f}%",
                ha="center",
                va="bottom",
                fontsize=9,
            )

    plt.tight_layout()
    plt.show()
