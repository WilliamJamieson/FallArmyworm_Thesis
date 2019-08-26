import collections as collect

import source.hint as hint

import source.schedule.step as agent_step


class Schedule(collect.UserList):
    """
    Class to contain a complete schedule of steps for single simulation step

    Variables:
        - list:
            list in order of the steps needed
    """

    def __init__(self, steps: hint.steps):
        super().__init__(steps)

    def _perform(self, space:  hint.space,
                       agents: hint.agents) -> hint.agent_list:
        """
        Perform complete schedule

        Args:
            space:  the space system
            agents: the agent storage system

        Returns:
            list of agents to add in
        """

        results = []
        for step in self:
            results += step.perform(space, agents)

        return results

    @staticmethod
    def _activate(results: hint.agent_list) -> None:
        """
        Activate all of the result agents

        Args:
            results: the agents to activate

        Effects:
            activates all of the agents
        """

        for agent in results:
            agent.activate()

    def perform(self, space: hint.space,
                      agents: hint.agents) -> None:
        """
        Perform complete schedule

        Args:
            space:  the space system
            agents: the agent storage system

        Effects:
            run a new step
            add the new agents
        """

        results = self._perform(space, agents)
        self._activate(results)

    @classmethod
    def setup(cls, step_tuples: hint.step_tuples) -> 'Schedule':
        """
        Create a schedule of steps

        Args:
            step_tuples: list in order of the steps to schedule

        Returns:
            a setup schedule
        """

        steps = []
        for step_tuple in step_tuples:
            new_step = agent_step.Step.setup(*step_tuple)
            steps.append(new_step)

        return cls(steps)
