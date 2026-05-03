class MinimaxAgent:
    def __init__(self, max_depth=7):
        self.max_depth = max_depth
        # This will be set when get_action is called
        self.is_team_a = True

    def map_value(self, a, b):
        return a - b
    
    def eval(self, team_a_strengths, team_b_strengths, picked_maps):
        """
        Heuristic eval for map set
        Returns value from the perspective of the agent playing
        """
        
        a_wins = 0
        b_wins = 0

        for i, (map_name, _) in enumerate(picked_maps):
            
            a = team_a_strengths.get(map_name, 0)
            b = team_b_strengths.get(map_name, 0)

            if a > b:
                a_wins += 1
            elif b > a:
                b_wins += 1

        # If agent is Team A, maximize (a_wins - b_wins)
        # If agent is Team B, maximize (b_wins - a_wins)
        if self.is_team_a:
            return a_wins - b_wins
        else:
            return b_wins - a_wins

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
        
        # Determine if current player is the agent or opponent
        # Action indices: 0=A_ban1, 1=B_ban1, 2=A_pick1, 3=B_pick1, 4=A_ban2, 5=B_ban2, 6=decider
        
        if self.is_team_a:
            # Agent is Team A
            if action_index in [0, 2, 4, 6]:  # A's turns (ban1, pick1, ban2, decider)
                maximizing = True
            else:  # B's turns
                maximizing = False
        else:
            # Agent is Team B
            if action_index in [1, 3, 5, 6]:  # B's turns (ban1, pick1, ban2, decider)
                maximizing = True
            else:  # A's turns
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
        # Determine if this agent is Team A or Team B based on action_index pattern
        # In the tournament, action_index 0,2,4,6 are Team A's turns; 1,3,5 are Team B's turns
        # Since get_action is called for the agent, we can infer which team they are
        available_maps = set(available_maps)
        
        # Store whether this agent is Team A
        if action_index in [0, 2, 4, 6]:
            self.is_team_a = True
        else:
            self.is_team_a = False

        _, best_map = self.minimax(
            team_a_strengths,
            team_b_strengths,
            available_maps,
            action_index,
            [],
        )
        return best_map