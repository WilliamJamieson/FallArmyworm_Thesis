import collections  as collect
import itertools    as i_tools
import numpy.random as rnd

import joblib          as para
import multiprocessing as multi

import source.hint as hint

import source.schedule.actions as agent_actions


class Step(collect.UserList):
    """
    Class to contain a single step on agents:

    Variables:
        - list: list of actions to perform

        number:       number of times to repeat the actions in list
        shuffle:      if we can shuffle the actions in list
        parallel_reg: if we perform actions in parallel by agents
        parallel_loc: if we perform actions in parallel via locations
        level:        level we group agents by
    """

    def __init__(self, actions:      hint.actions_list,
                       number:       int  = 1,
                       shuffle:      bool = False,
                       parallel_reg: bool = False,
                       parallel_loc: bool = False,
                       level:        int  = 0):
        super().__init__(actions)

        self.number  = number
        self.shuffle = shuffle

        self.parallel_reg = parallel_reg
        self.parallel_loc = parallel_loc

        self.level = level

    @staticmethod
    def _perform_agent_action_regular(action: hint.actions,
                                      agents: hint.agent_list) \
            -> hint.agent_list:
        """
        Perform the specific action on the agents

        Args:
            action: action to perform
            agents: list of agents to use

        Returns:
            list of agents to add in
        """

        results = []
        for agent in agents:
            results += action.perform(agent)

        return results

    def _perform_agent_action_parallel(self, action: hint.actions,
                                             agents: hint.agent_list) \
            -> hint.agent_list:
        """
        Perform the specific action on the agents in parallel by agent

        Args:
            action: action to perform
            agents: list of agents to use

        Returns:
            list of agents to add in
        """

        def step(agent: hint.agent_list) -> hint.agent_list:
            """
            Create a loop function to parallelize actions

            Args:
                agent: sub_list of agents

            Returns:
                list of agents to add in
            """

            return self._perform_agent_action_regular(action, agent)

        n = multi.cpu_count()
        splits = [agents[i * n:(i + 1) * n]
                  for i in range((len(agents) + n - 1) // n)]
        values = para.Parallel(n_jobs=n, require='sharedmem')(
            para.delayed(step)(ags) for ags in splits)

        return list(i_tools.chain.from_iterable(values))

    def _perform_agent_action(self, action:    hint.actions,
                                    agent_bin: hint.agents_bin) \
            -> hint.agent_list:
        """
        Perform the specific action on the agent_bin

        Args:
            action:    action to perform
            agent_bin: agent bin to use

        Returns:
            list of agents to add in
        """

        agents: hint.agent_list = agent_bin[action.agent_key]
        rnd.shuffle(agents)

        if self.parallel_reg:
            return self._perform_agent_action_parallel(action, agents)
        else:
            return self._perform_agent_action_regular( action, agents)

    def _perform_actions_step(self, location_key: hint.location_key,
                                    agents:       hint.agents) \
            -> hint.agent_list:
        """
        Perform all the actions at the specific location

        Args:
            location_key: the location to do step
            agents:       the agent storage system

        Returns:
            list of agents to add in
        """

        agent_bin = agents[location_key]

        results = []
        for action in self:
            results += self._perform_agent_action(action, agent_bin)

        return results

    def _perform_regular_step(self, location_keys: hint.location_keys,
                                    agents:        hint.agents) \
            -> hint.agent_list:
        """
        Perform a single step on the agents divided by each location_key

        Args:
            location_keys: the list of location keys
            agents:        the agent storage system

        Returns:
            list of agents to add in
        """

        results = []
        for location_key in location_keys:
            results += self._perform_actions_step(location_key, agents)

        return results

    def _perform_parallel_step(self, location_keys: hint.location_keys,
                                     agents:        hint.agents) \
            -> hint.agent_list:
        """
        Perform a single step on the agents if in parallel

        Args:
            location_keys: the list of location keys
            agents:        the agent storage system

        Returns:
            list of agents to add in
        """

        def step(keys: hint.location_keys) -> hint.agent_list:
            """
            Create a loop function to parallelize actions

            Args:
                keys: sub_list of location keys

            Returns:
                list of agents to add in
            """

            return self._perform_regular_step(keys, agents)

        n = multi.cpu_count()
        splits = [location_keys[i * n:(i + 1) * n]
                  for i in range((len(location_keys) + n - 1) // n)]
        values = para.Parallel(n_jobs=n, require='sharedmem')(
            para.delayed(step)(loc_keys) for loc_keys in splits)

        return list(i_tools.chain.from_iterable(values))

    def _perform_step(self, space:  hint.space,
                            agents: hint.agents) -> hint.agent_list:
        """
        Perform a single repeat of actions

        Args:
            space:  the space system
            agents: the agent storage system

        Returns:
            list of agents to add in
        """

        if self.shuffle:
            rnd.shuffle(self)

        location_keys = space.location_keys[self.level]

        if self.parallel_loc:
            return self._perform_parallel_step(location_keys, agents)
        else:
            return self._perform_regular_step(location_keys, agents)

    def perform(self, space:  hint.space,
                      agents: hint.agents) -> hint.agent_list:
        """
        Perform all the steps on the agents

        Args:
            space:  the space system
            agents: the agent storage system

        Returns:
            list of agents to add in
        """

        results = []
        for _ in range(self.number):
            results += self._perform_step(space, agents)

        return results

    @classmethod
    def setup(cls, actions:      hint.actions_dict,
                   number:       int  = 1,
                   shuffle:      bool = False,
                   parallel_reg: bool = False,
                   parallel_loc: bool = False,
                   level:        int  = 0) -> 'Step':
        """
        Setup the entire step

        Args:
            actions:      dict of actions for each agent type
            number:       number of steps to perform at once
            shuffle:      if the actions can be shuffled
            parallel_reg: if we parallelize on agents
            parallel_loc: if we parallelize on locations
            level:        locations to split across

        Returns:
            A setup simulation step
        """


        if parallel_loc and parallel_reg:
            raise TypeError('Cannot have both location and regular parallel')

        actions_list = []
        for agent_key, action_keys in actions.items():
            new_action = agent_actions.Actions.setup(agent_key, action_keys)
            actions_list.append(new_action)

        return cls(actions_list, number, shuffle,
                   parallel_reg, parallel_loc, level)
