class MinimaxAgent:
    def __init__(self, max_depth=7):
        self.max_depth = max_depth

    def map_value(self, a, b):
        return a - b
    def eval(self, team_a_strengths, team_b_strengths, picked_maps):
        """
        Heuristic eval for map set
        """
        
        a_wins = 0
        b_wins = 0

        for i, (map_name, _) in enumerate(picked_maps):
            
            a= team_a_strengths.get(map_name, 0)
            b = team_b_strengths.get(map_name, 0)

            if a > b:
                a_wins += 1
            elif b > a:
                b_wins += 1

        return  a_wins - b_wins

    def minimax(
        self,
        team_a_strengths,
        team_b_strengths,
        available_maps,
        action_index,
        picked_maps,
    ):
        # terminal
        if action_index == 7:
            return self.eval(team_a_strengths, team_b_strengths, picked_maps), None
        
        # Action indices: 0=A_ban1, 1=B_ban1, 2=A_pick1, 3=B_pick1, 4=A_ban2, 5=B_ban2, 6=decider
        
        if action_index in [0, 4]:  # A bans - A wants to ban maps that are BAD for A (negative values), so MAXIMIZE
            maximizing = True
        elif action_index in [1, 5]:  # B bans - B wants to ban maps BAD for B (positive for A), so from A's perspective MINIMIZE
            maximizing = False
        elif action_index in [2, 6]:  # A picks - A wants maps GOOD for A (positive values), so MAXIMIZE
            maximizing = True
        elif action_index == 3:  # B picks - B wants maps GOOD for B (negative for A), so MINIMIZE from A's perspective
            maximizing = False

        best_map = next(iter(available_maps))

        if maximizing:
            best_value = float("-inf")
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
            )

            if maximizing:
                if value > best_value:
                    best_value = value
                    best_map = map_name
            else:
                if value < best_value:
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
        )
        return best_map
