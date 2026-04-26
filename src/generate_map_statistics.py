# Calculates Relevant Map Pool Statistics for Each Team in the Dataset

import os
import pandas as pd


def calculate_map_strength(playrate, winrate):
    # Assess unplayed maps with padding
    if playrate is None:
        playrate = 0.15  # Laplace smoothing for unplayed maps

    # Heavier weight on playrate
    WEIGHT_PLAYRATE = 2.5
    WEIGHT_WINRATE = 0.5

    team_strength = (playrate * WEIGHT_PLAYRATE) + (winrate * WEIGHT_WINRATE)

    return team_strength


def calculate_map_statistics(team_name, match_data, map_pool):
    # Calcualtes relevant statistics given data columns for a single team
    # Relevant statistics: winrate, playrate, defense winrate, attack winrate, strength
    team_map_stats = {}

    # Iterate through each map in the given data
    for map_ in map_pool:
        counts = {
            "times_won": 0,
            "times_played": 0,
            "attack_rounds_won": 0,
            "attack_rounds_played": 0,
            "defense_rounds_won": 0,
            "defense_rounds_played": 0,
        }
        stats = {
            "winrate": 0,
            "playrate": 0,
            "defense_winrate": 0,
            "attack_winrate": 0,
            "strength": 0,
        }

        # Filter matches for the current map
        map_matches = match_data[match_data["Map"] == map_]
        for _, match in map_matches.iterrows():
            if match["Team A"] == team_name:
                counts["times_played"] += 1
                if match["Team A Score"] > match["Team B Score"]:
                    counts["times_won"] += 1
                counts["attack_rounds_won"] += match["Team A Attacker Score"]
                counts["attack_rounds_played"] += (
                    match["Team A Attacker Score"] + match["Team B Defender Score"]
                )
                counts["defense_rounds_won"] += match["Team A Defender Score"]
                counts["defense_rounds_played"] += (
                    match["Team A Defender Score"] + match["Team B Attacker Score"]
                )
            elif match["Team B"] == team_name:
                counts["times_played"] += 1
                if match["Team B Score"] > match["Team A Score"]:
                    counts["times_won"] += 1
                counts["attack_rounds_won"] += match["Team B Attacker Score"]
                counts["attack_rounds_played"] += (
                    match["Team B Attacker Score"] + match["Team A Defender Score"]
                )
                counts["defense_rounds_won"] += match["Team B Defender Score"]
                counts["defense_rounds_played"] += (
                    match["Team B Defender Score"] + match["Team A Attacker Score"]
                )

        # Calculate statistics
        if counts["times_played"] > 0:
            stats["winrate"] = counts["times_won"] / counts["times_played"]
            stats["playrate"] = counts["times_played"] / len(match_data)
        if counts["attack_rounds_played"] > 0:
            stats["attack_winrate"] = (
                counts["attack_rounds_won"] / counts["attack_rounds_played"]
            )
        if counts["defense_rounds_played"] > 0:
            stats["defense_winrate"] = (
                counts["defense_rounds_won"] / counts["defense_rounds_played"]
            )
        stats["strength"] = calculate_map_strength(stats["playrate"], stats["winrate"])

        team_map_stats[map_] = stats

    return team_map_stats


if __name__ == "__main__":
    print("Loading map statistics from raw CSV...")

    # Load map statistics from CSV
    df = pd.read_csv("../data/maps_scores.csv")
    print(f"Total matches loaded: {len(df)}")
    # Columns: Tournament,Stage,Match Type,Match Name,Map,Team A,Team A Score,Team A Attacker Score,Team A Defender Score,Team A Overtime Score,Team B,Team B Score,Team B Attacker Score,Team B Defender Score,Team B Overtime Score,Duration

    # Remove all data that isnt for a specific list of tournaments
    VALID_TOURNAMENT_LIST = [
        "VCT 2025: Americas Stage 2",
        "VCT 2025: EMEA Stage 2",
        "VCT 2025: Pacific Stage 2",
        "VCT 2025: China Stage 2",
    ]
    VALID_STAGES = ["Group Stage"]
    df = df[df["Tournament"].isin(VALID_TOURNAMENT_LIST)]
    df = df[df["Stage"].isin(VALID_STAGES)]
    print(
        f"Data filtered for tournaments: {VALID_TOURNAMENT_LIST} and stages: {VALID_STAGES}. Remaining matches: {len(df)}"
    )

    # Get set of unique teams in the remaining data
    unique_teams = set(df["Team A"].unique()).union(set(df["Team B"].unique()))
    print(f"Unique teams found: {len(unique_teams)}")

    # Get the current map pool (7 maps)
    current_map_pool = set(df["Map"].unique())
    print(f"Current map pool identified: {current_map_pool}")
    if len(current_map_pool) > 7:
        print(
            "Error: More than 7 maps found in the dataset. Please verify the map pool."
        )
        exit(1)

    # Generate map statistics for specific teams (replace names with actual teams to analyze)
    team_stats = {}
    for team in unique_teams:
        print(f"Calculating statistics for {team}...")
        # Filter matches for the current team
        team_matches = df[(df["Team A"] == team) | (df["Team B"] == team)]
        team_stats[team] = calculate_map_statistics(
            team, team_matches, current_map_pool
        )

    # Remove old map statistics CSV if it exists
    if os.path.exists("../data/map_stats.csv"):
        os.remove("../data/map_stats.csv")

    # Save map statistics
    print("Map statistics calculation complete. Saving to CSV...")
    pd.DataFrame.from_dict(team_stats, orient="index").to_csv("../data/map_stats.csv")
