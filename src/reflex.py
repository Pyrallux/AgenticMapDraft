class ReflexAgent:
    def get_action(
        self, team_a_map_strengths, team_b_map_strengths, available_maps, action_index
    ):
        """
        Returns the next action (map name) given the current state of the pick/ban phase.

        :param team_a_map_strengths: dict mapping map names to Team A's strength
        :param team_b_map_strengths: dict mapping map names to Team B's strength
        :param available_maps: set or list of currently available maps
        :param action_index: integer representing the current step in the sequence (0-6)
                             0: Team A Ban 1
                             1: Team B Ban 1
                             2: Team A Pick 1
                             3: Team B Pick 1
                             4: Team A Ban 2
                             5: Team B Ban 2
                             6: Decider
        :return: str, the name of the map chosen for this action
        """
        available_maps = set(available_maps)

        def get_sorted_maps(team_strengths):
            return sorted(
                list(available_maps),
                key=lambda x: team_strengths.get(x, 0),
                reverse=True,
            )

        team_a_sorted = get_sorted_maps(team_a_map_strengths)
        team_b_sorted = get_sorted_maps(team_b_map_strengths)

        if action_index == 0:
            # Team A Ban 1
            # weak maps = list of Team A maps where strength < 0.2 and Team B Strength > 0.2
            # Ban the strongest map for Team B in the weak maps
            # otherwise ban minimizing strength difference
            weak_a_maps = [
                m
                for m in team_a_sorted
                if team_a_map_strengths.get(m, 0) < 0.2
                and team_b_map_strengths.get(m, 0) > 0.2
            ]
            if weak_a_maps:
                strength_diffs = {
                    m: team_a_map_strengths.get(m, 0) - team_b_map_strengths.get(m, 0)
                    for m in weak_a_maps
                }
                return min(strength_diffs, key=strength_diffs.get)
            else:
                strength_diffs = {
                    m: team_a_map_strengths.get(m, 0) - team_b_map_strengths.get(m, 0)
                    for m in available_maps
                }
                return min(strength_diffs, key=strength_diffs.get)

        elif action_index == 1:
            # Team B Ban 1
            # weak maps = list of Team B maps where strength < 0.2 and Team A Strength > 0.2
            # Ban the strongest map for Team A in the weak maps
            # otherwise ban minimizing strength difference
            weak_b_maps = [
                m
                for m in team_b_sorted
                if team_b_map_strengths.get(m, 0) < 0.2
                and team_a_map_strengths.get(m, 0) > 0.2
            ]
            if weak_b_maps:
                strength_diffs = {
                    m: team_b_map_strengths.get(m, 0) - team_a_map_strengths.get(m, 0)
                    for m in weak_b_maps
                }
                return min(strength_diffs, key=strength_diffs.get)
            else:
                strength_diffs = {
                    m: team_b_map_strengths.get(m, 0) - team_a_map_strengths.get(m, 0)
                    for m in available_maps
                }
                return min(strength_diffs, key=strength_diffs.get)

        elif action_index == 2:
            # Team A Pick 1
            # Pick the strongest map for team A, unless it is one of the top 2 strongest maps for team b, otherwise pick maximizing strength difference
            team_b_top2 = team_b_sorted[:2]
            strongest_a = team_a_sorted[0]

            if strongest_a not in team_b_top2:
                return strongest_a
            else:
                strength_diffs = {
                    m: team_a_map_strengths.get(m, 0) - team_b_map_strengths.get(m, 0)
                    for m in available_maps
                }
                return max(strength_diffs, key=strength_diffs.get)

        elif action_index == 3:
            # Team B Pick 1
            # Pick the strongest map for team B, unless its the strongest map for team A, otherwise pick maximizing strength difference
            team_a_top1 = team_a_sorted[0]
            strongest_b = team_b_sorted[0]

            if strongest_b != team_a_top1:
                return strongest_b
            else:
                strength_diffs = {
                    m: team_b_map_strengths.get(m, 0) - team_a_map_strengths.get(m, 0)
                    for m in available_maps
                }
                return max(strength_diffs, key=strength_diffs.get)

        elif action_index == 4:
            # Team A Ban 2
            # Ban weakest map for Team A if strength < 0.2, otherwise ban minimizing strength difference
            weakest_a = team_a_sorted[-1]

            if team_a_map_strengths.get(weakest_a, 0) < 0.2:
                return weakest_a
            else:
                strength_diffs = {
                    m: team_a_map_strengths.get(m, 0) - team_b_map_strengths.get(m, 0)
                    for m in available_maps
                }
                return min(strength_diffs, key=strength_diffs.get)

        elif action_index == 5:
            # Team B Ban 2
            # Ban the second strongest map for team B unless both maps have strength < 0.2, otherwise ban minimizing strength difference
            if (
                team_b_map_strengths.get(team_b_sorted[0], 0) > 0.2
                and len(team_b_sorted) > 1
            ):
                return team_b_sorted[1]
            else:
                strength_diffs = {
                    m: team_b_map_strengths.get(m, 0) - team_a_map_strengths.get(m, 0)
                    for m in available_maps
                }
                return min(strength_diffs, key=strength_diffs.get)

        elif action_index == 6:
            # Decider
            return list(available_maps)[0]

        return None
