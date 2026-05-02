import random


class CFRAgent:
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

        # return a random map from the available maps
        # TODO: Actualy implement CFR agent logic
        return random.choice(list(available_maps))
