import random
import collections


class CFRAgent:
    def __init__(self, iterations=20):
        self.iterations = iterations
        self.regret_sum = collections.defaultdict(float)
        self.strategy_sum = collections.defaultdict(float)

    def get_strategy(self, info_set, current_available):
        strategy = {
            a: max(self.regret_sum[(info_set, a)], 0.0) for a in current_available
        }
        normalizing_sum = sum(strategy.values())
        if normalizing_sum > 0:
            for a in current_available:
                strategy[a] /= normalizing_sum
        else:
            for a in current_available:
                strategy[a] = 1.0 / len(current_available)
        return strategy

    def cfr(
        self,
        available_maps,
        current_index,
        picked_maps,
        i,
        pi0,
        pi1,
        team_a_strengths,
        team_b_strengths,
    ):
        # Base case
        if current_index == 7 or not available_maps:
            return self.eval_terminal(
                team_a_strengths, team_b_strengths, picked_maps, i
            )

        info_set = (available_maps, current_index, picked_maps)

        # 0 for even indices (Team A), 1 for odds (Team B)
        player = current_index % 2

        strategy = self.get_strategy(info_set, available_maps)
        v = 0.0
        v_a = {}

        for a in available_maps:
            next_available = tuple(m for m in available_maps if m != a)
            next_picked = list(picked_maps)

            if current_index == 2:
                next_picked.append((a, "A"))
            elif current_index == 3:
                next_picked.append((a, "B"))
            elif current_index == 6:
                next_picked.append((a, "D"))

            next_pi0 = pi0 * strategy[a] if player == 0 else pi0
            next_pi1 = pi1 * strategy[a] if player == 1 else pi1

            util = self.cfr(
                next_available,
                current_index + 1,
                tuple(next_picked),
                i,
                next_pi0,
                next_pi1,
                team_a_strengths,
                team_b_strengths,
            )
            v_a[a] = util
            v += strategy[a] * util

        if player == i:
            pi_minus_i = pi1 if player == 0 else pi0
            pi_i = pi0 if player == 0 else pi1
            for a in available_maps:
                regret = v_a[a] - v
                self.regret_sum[(info_set, a)] += pi_minus_i * regret
                self.strategy_sum[(info_set, a)] += pi_i * strategy[a]

        return v

    def eval_terminal(
        self, team_a_strengths, team_b_strengths, picked_maps, player_pov
    ):
        a_wins = 0
        b_wins = 0
        for map_name, _ in picked_maps:
            sa = team_a_strengths.get(map_name, 0)
            sb = team_b_strengths.get(map_name, 0)
            if sa > sb:
                a_wins += 1
            elif sb > sa:
                b_wins += 1

        # Return utility from the perspective of the computing player (i)
        # Player 0 = Team A, Player 1 = Team B
        if player_pov == 0:
            return float(a_wins - b_wins)
        else:
            return float(b_wins - a_wins)

    def get_action(
        self, team_a_map_strengths, team_b_map_strengths, available_maps, action_index
    ):
        """
        Returns the next action (map name) given the current state of the pick/ban phase.
        Uses Counterfactual Regret Minimization on the fly to determine the optimal strategy.
        """
        self.regret_sum.clear()
        self.strategy_sum.clear()

        available_maps = tuple(sorted(list(available_maps)))

        # Run standard vanilla CFR iterations
        for _ in range(self.iterations):
            for p in [0, 1]:  # 0: Team A, 1: Team B
                self.cfr(
                    available_maps,
                    action_index,
                    (),
                    p,
                    1.0,
                    1.0,
                    team_a_map_strengths,
                    team_b_map_strengths,
                )

        # Extract strategy for the root node (current info set)
        info_set = (available_maps, action_index, ())

        # We greedily pick the action with the maximum strategy sum
        # (could also sample from probabilities, but max is common for deployment).
        best_action = None
        max_strat = -1.0

        for a in available_maps:
            if self.strategy_sum[(info_set, a)] > max_strat:
                max_strat = self.strategy_sum[(info_set, a)]
                best_action = a

        if best_action is None:
            best_action = random.choice(available_maps)

        return best_action
