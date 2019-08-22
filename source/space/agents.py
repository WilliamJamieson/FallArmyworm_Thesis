import collections as collect

import source.hint    as hint
import source.keyword as keyword

import source.data.counter as count

import source.space.environment as agent_environment


class AgentBin(collect.UserList):
    """
    Class to contain agents

    Variables:
        - dict:
            key:   unique_id
            value: agent

        counts:    counts of attributes of agents
        agent_key: key for type of agent

    Methods:
        activate:   add    agent to bin
        deactivate: remove agent from bin
        count:      add an attribute to count

    Constructors:
        empty: setup a class
    """

    def __init__(self, agents:    hint.agent_list,
                       counts:    hint.counts,
                       agent_key: str):
        super().__init__(agents)

        self.counts   = counts
        self.agent_key = agent_key

    def activate(self, agent: hint.agent) -> None:
        """
        Activate the agent

        Args:
            agent: agent to activate

        Effects:
            add agent to bin
        """

        self.append(agent)
        self.counts.add(agent)

    def deactivate(self, agent: hint.agent) -> None:
        """
        Deactivate the agent

        Args:
            agent: agent to deactivate

        Effects:
            remove agent from bin
        """

        self.remove(agent)
        self.counts.sub(agent)

    @classmethod
    def empty(cls, agent_key: str,
                   attrs:     hint.attrs)  -> 'AgentBin':
        """
        Setup an empty agent bin

        Args:
            agent_key: key for the agent
            attrs:     attributes to track

        Returns:
            a setup class
        """

        counts = count.Counts.empty(attrs)

        return cls([], counts, agent_key)


class AgentsBin(collect.UserDict):
    """
    Class to contain all of the agents in a particular place

    Variables:
        - dict:
            key:   agent_key
            value: bin of agents

        location_key: location for this bin
        environment:  environment at this location

    Methods:
        activate:   add    agent to bin
        deactivate: remove agent from bin
        count:      add an attribute to count
        record:     record the current counts
        refresh:    refresh the stored counts
        dataframes: create dictionary of all the dataframes
    """

    def __init__(self, agents:       hint.agent_bins,
                       location_key: hint.location_key,
                       environment:  hint.environment):
        super().__init__(agents)

        self.location_key = location_key
        self.environment  = environment

    def activate(self, agent: hint.agent) -> None:
        """
        Activate the agent

        Args:
            agent: agent to activate

        Effects:
            add agent to bin
        """

        self[agent.agent_key].activate(agent)

    def deactivate(self, agent: hint.agent) -> None:
        """
        Deactivate the agent

        Args:
            agent: agent to deactivate

        Effects:
            remove agent from bin
        """

        self[agent.agent_key].deactivate(agent)

    def record(self) -> None:
        """
        Record the current counts

        Effect:
            Records all of the data
        """

        for agent_bin in self.values():
            agent_bin.counts.record()

    def refresh(self) -> None:
        """
        Refresh the stored counts

        Effects:
            Refresh all of the stored data
        """

        for agent_bin in self.values():
            agent_bin.counts.refresh()

    def dataframes(self) -> hint.dataframes:
        """
        Create a dictionary of all of dataframes for bin

        Returns:
            a dictionary of dataframes
        """

        dataframes = {}
        for agent_key, agent_bin in self.items():
            key = '{}_{}'.format(self.location_key, agent_key)
            dataframes[key] = agent_bin.counts.dataframe()

        return dataframes

    @classmethod
    def empty(cls, agent_keys:   hint.agent_keys,
                   location_key: hint.location_key,
                   attrs:        hint.attrs_dict,
                   environment:  hint.environment_tuple)  -> 'AgentsBin':
        """
        Setup an empty agent bin

        Args:
            agent_keys:   keys for the agents
            location_key: key for the location
            attrs:        tracking attributes
            environment:  environment inputs

        Returns:
            a setup class
        """
        
        agents = {}
        for agent_key in agent_keys:
            if agent_key in attrs:
                attr = attrs[agent_key]
            else:
                attr = {}

            agents[agent_key] = AgentBin.empty(agent_key, attr)

        environment_dict, init_plant = environment
        if location_key in environment_dict[keyword.bt]:
            environ = agent_environment.Environment.setup(keyword.bt,
                                                          init_plant)
        elif location_key in environment_dict[keyword.not_bt]:
            environ = agent_environment.Environment.setup(keyword.not_bt,
                                                          init_plant)
        else:
            environ = agent_environment.Environment()

        return cls(agents, location_key, environ)


class Agents(collect.UserDict):
    """
    Class to contain all of the agents

    Variables:
        - dict:
            key:   agent_key
            value: bin of agents

    Methods:
        activate:   add    agent to bin
        deactivate: remove agent from bin
        count:      add an attribute to count
    """

    def __init__(self, agents: hint.agents_dict):
        super().__init__(agents)

    def agents(self, agent_key: str) -> list:
        """
        Get a list of all the agents for the given key

        Args:
            agent_key: type of agent

        Returns:
            agents from master location
        """

        return self[(0,)][agent_key]

    def activate(self, agent: hint.agent) -> None:
        """
        Activate the agent

        Args:
            agent: agent to activate

        Effects:
            add agent to bin
        """

        location = agent.location

        for index in range(1, location.depth + 1):
            location_key = location[:index].location_key
            self[location_key].activate(agent)

    def deactivate(self, agent: hint.agent) -> None:
        """
        Deactivate the agent

        Args:
            agent: agent to deactivate

        Effects:
            remove agent from bin
        """

        location = agent.location

        for index in range(1, location.depth + 1):
            location_key = location[:index].location_key
            self[location_key].deactivate(agent)

    def record(self) -> None:
        """
        Record all the current counts

        Effects:
            records all of the current counts
        """

        for agents_bin in self.values():
            agents_bin.record()

    def refresh(self) -> None:
        """
        Refresh all of the stored counts

        Effects:
            refresh all the current counts
        """

        for agents_bin in self.values():
            agents_bin.refresh()

    def dataframes(self) -> hint.dataframes:
        """
        Create a dictionary of all of dataframes

        Returns:
            a dictionary of dataframes
        """

        dataframes = {}
        for agents_bin in self.values():
            dataframes.update(agents_bin.dataframes())

        return dataframes

    @classmethod
    def empty(cls, locations:   hint.locations,
                   agent_keys:  hint.agent_keys,
                   attrs:       hint.attrs_loc,
                   environment: hint.environment_tuple) -> 'Agents':
        """
        Setup an empty agent bin

        Args:
            locations:   keys for the location
            agent_keys:  keys for the agents
            attrs:       tracking attributes
            environment: the arguments to generate an environment

        Returns:
            a setup class
        """

        agents = {}
        for location in locations:
            location_key = location.location_key

            if location_key in attrs:
                attr = attrs[location_key]
            else:
                attr = {}

            agents[location_key] = AgentsBin.empty(agent_keys, location_key,
                                                   attr, environment)

        return cls(agents)
