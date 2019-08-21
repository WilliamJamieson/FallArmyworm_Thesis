import collections as collect
import dataclasses as dclass

import source.hint as hint


@dclass.dataclass
class Action(object):
    """
    Class to handle having agent perform action

    Variables:
        action_key: string for method to perform

    Methods:
        perform: run the action
    """

    action: str

    def perform(self, agent: hint.agent) -> hint.agent_list:
        """
        Perform the action on the agent

        Args:
            agent: agent to perform action

        Returns:
            a list of agents to add to simulation
        """

        return getattr(agent, self.action)()

    
class Actions(collect.UserList):
    """
    Class to handle performing a list of actions with agent

    Variables:
        dict:
            index: index of action
            value: action to perform

        agent_key: key for agent that will do the actions

    Methods:
        perform: run the actions

    Constructors:
        setup: setup the actions
    """

    def __init__(self, actions: hint.action_list,
                       agent_key: str):
        super().__init__(actions)

        self.agent_key = agent_key

    def perform(self, agent: hint.agent) -> hint.agent_list:
        """
        Perform the all the actions on the agent

        Args:
            agent: agent to perform the actions

        Returns:
            a list of agents to add to simulation
        """

        results = []
        for action in self:
            results += action.perform(agent)

        return results

    @classmethod
    def setup(cls, agent_key: str,
                   actions:   hint.action_keys) -> 'Actions':
        """
        Setup the agent actions

        Args:
            agent_key: key for type of agent
            actions:   list of action keys in order of performance

        Returns:
            A setup action class
        """

        perform = []
        for action in actions:
            perform.append(Action(action))

        return cls(perform, agent_key)
