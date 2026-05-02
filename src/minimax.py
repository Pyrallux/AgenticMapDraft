class MinimaxAgent:
    def __init__(self, max_depth=7):
        self.max_depth = max_depth

    def eval(self, team_a_strengths, team_b_strengths, picked_maps):
        """
        Heuristic eval for map set
        """

        score = 0

        for map_name, picker in picked_maps:
            a_strength = team_a_strengths.get(map_name, 0)
            b_strength = team_b_strengths.get(map_name, 0)

            if picker == "A":
                score += a_strength - b_strength
            elif picker == "B":
                score += a_strength - b_strength

        return score

    def minimax(
        self,
        team_a_strengths,
        team_b_strengths,
        available_maps,
        action_index,
        picked_maps,
        depth,
        maximizing_player,
    ):

        # terminal
        if depth == self.max_depth or len(available_maps) == 1:
            return self.eval(team_a_strengths, team_a_strengths, picked_maps), None

        best_map = None

        if maximizing_player:
            best_value = float("-inf")

            for map_name in available_maps:
                next_available = available_maps.copy()
                next_available.remove(map_name)

                next_picked = picked_maps.copy()

                if action_index == 2:
                    next_picked.append((map_name, "A"))
                elif action_index == 3:
                    next_picked.append((map_name, "B"))
                elif action_index == 6:
                    next_picked.append((map_name, "D"))

                value, _ = self.minimax(
                    team_a_strengths,
                    team_b_strengths,
                    next_available,
                    action_index + 1,
                    next_picked,
                    depth + 1,
                    False,
                )

                if value > best_value:
                    best_value = value
                    best_map = map_name
            return best_value, best_map
        else:
            best_value = float("inf")

            for map_name in available_maps:
                next_available = available_maps.copy()
                next_available.remove(map_name)

                next_picked = picked_maps.copy()

                if action_index == 2:
                    next_picked.append((map_name, "A"))
                elif action_index == 3:
                    next_picked.append((map_name, "B"))
                elif action_index == 6:
                    next_picked.append((map_name, "D"))

                value, _ = self.minimax(
                    team_a_strengths,
                    team_b_strengths,
                    next_available,
                    action_index + 1,
                    next_picked,
                    depth + 1,
                    True,
                )

                if value > best_value:
                    best_value = value
                    best_map = map_name
            return best_value, best_map

    def get_action(
        self, team_a_strengths, team_b_strengths, available_maps, action_index
    ):
        available_maps = set(available_maps)

        _, best_map = self.minimax(
            team_a_strengths,
            team_b_strengths,
            available_maps,
            action_index,
            [],
            0,
            (action_index % 2 == 0),
        )

        return best_map
