import dataclasses as dclass

import source.hint as hint


@dclass.dataclass
class Agent(object):
    """
    Base class to for an agent

    Variables:
        agent_key:  the agent type identifier
        unique_id:  the unique identifier
        simulation: the simulation
        location:   location tuple
        alive:      determine of the agent is alive

    Methods:
        activate:   activate   the agent
        deactivate: deactivate the agent
        transfer:   transfer   the agent
        die:        have agent die
    """

    agent_key:  str
    unique_id:  str
    simulation: hint.simulation
    location:   hint.location
    alive:      bool

    def activate(self) -> None:
        """
        Activate the agent

        Effects:
            activates the agent in the system
        """

        self.simulation.agents.activate(self)

    def deactivate(self) -> None:
        """
        Activate the agent

        Effects:
            deactivates the agent in the system
        """

        self.simulation.agents.deactivate(self)

    def transfer(self, vertex: int,
                       level:  int) -> None:
        """
        Transfer the agent to a new vertex

        Args:
            vertex: vertex
            level:  level of vertex

        Effects:
            removes from current location
            updates location
            adds to new location
        """

        self.simulation.agents.deactivate(self)
        self.location[level] = vertex
        self.simulation.agents.activate(self)

    def transition(self, agent_key: str) -> None:
        """
        Transition the agent_key of the agent

        Args:
            agent_key: new agent key

        Effects:
            removes agent
            updates agent_key
            adds agent back
        """

        self.simulation.agents.deactivate(self)
        self.agent_key = agent_key
        self.simulation.agents.activate(self)

    def vertices(self, **kwargs) -> hint.vertices:
        """
        Get the vertices in the distance neighborhood of this agent's location

        Args:
            **kwargs: the bounds to use

        Returns:
            set of vertices at that distance
        """

        return self.simulation.space.neighborhood(self.location, **kwargs)

    def die(self, death: str = '') -> None:
        """

        Have agent die

        Args:
            death: the type of death

        Effects:
            sets alive to false
            deactivates agent
        """

        self.alive = False
        self.deactivate()

    def reset(self) -> hint.agent_list:
        """
        Reset the agent

        Effects:
            perform a reset
        """

        pass
