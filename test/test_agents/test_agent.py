import unittest      as ut
import unittest.mock as mk

import dataclasses as dclass

import source.keyword as keyword

import source.agents.agent as agent

import source.simulation.simulation as simulation

import source.space.agents   as agents
import source.space.location as location
import source.space.space    as space


class SimulationTest(simulation.Simulation):
    """Class to add dynamic values for tests"""

    agents = mk.create_autospec(agents.Agents, spec_set=True)
    space  = mk.create_autospec(space.Space,   spec_set=True)


class TestAgent(ut.TestCase):
    """test base Agent class"""

    def setUp(self):
        """Setup the tests"""

        self.agent_key = mk.MagicMock(spec=str)
        self.unique_id = mk.MagicMock(spec=str)
        self.alive     = mk.MagicMock(spec=bool)

        self.simulation = mk.create_autospec(SimulationTest,    spec_set=True)
        self.location   = mk.create_autospec(location.Location, spec_set=True)

        self.Agent = agent.Agent(self.agent_key,
                                 self.unique_id,
                                 self.simulation,
                                 self.location,
                                 self.alive)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Agent, agent.Agent)

        self.assertEqual(self.Agent.agent_key,  self.agent_key)
        self.assertEqual(self.Agent.unique_id,  self.unique_id)
        self.assertEqual(self.Agent.simulation, self.simulation)
        self.assertEqual(self.Agent.location,   self.location)
        self.assertEqual(self.Agent.alive,      self.alive)

        self.assertTrue(dclass.is_dataclass(self.Agent))

    def test_activate(self):
        """test activate the agent"""

        self.simulation.agents = mk.create_autospec(agents.Agents,
                                                    spec_set=True)

        self.Agent.activate()
        self.assertEqual(self.simulation.agents.activate.call_args_list,
                         [mk.call(self.Agent)])

    def test_deactivate(self):
        """test deactivate the agent"""

        self.simulation.agents = mk.create_autospec(agents.Agents,
                                                    spec_set=True)

        self.Agent.deactivate()
        self.assertEqual(self.simulation.agents.deactivate.call_args_list,
                         [mk.call(self.Agent)])

    def test_transfer(self):
        """test transfer to new vertex"""

        self.simulation.agents = mk.create_autospec(agents.Agents,
                                                    spec_set=True)

        vertex = mk.MagicMock(spec=int)
        level  = mk.MagicMock(spec=int)

        master = mk.MagicMock()
        master.attach_mock(self.simulation.agents, 'agents')
        master.attach_mock(self.location,          'location')

        self.Agent.transfer(vertex, level)
        self.assertEqual(master.mock_calls,
                         [mk.call.agents.deactivate(self.Agent),
                          mk.call.location.__setitem__(level, vertex),
                          mk.call.agents.activate(self.Agent)])

    def test_transition(self):
        """test transition agent_key of agent"""

        self.simulation.agents = mk.create_autospec(agents.Agents,
                                                    spec_set=True)

        agent_key = mk.MagicMock(spec=str)

        master = mk.MagicMock()
        master.attach_mock(self.simulation.agents, 'agents')

        self.Agent.transition(agent_key)
        self.assertEqual(self.Agent.agent_key, agent_key)
        self.assertEqual(master.mock_calls,
                         [mk.call.agents.deactivate(self.Agent),
                          mk.call.agents.activate(self.Agent)])

    def test_vertices(self):
        """test get the vertices for the agent's location at some distance"""

        self.simulation.space = mk.create_autospec(space.Space, spec_set=True)

        kwargs   = {keyword.upper: mk.MagicMock(spec=float),
                    keyword.lower: mk.MagicMock(spec=float)}

        self.assertEqual(self.Agent.vertices(**kwargs),
                         self.simulation.space.neighborhood.return_value)
        self.assertEqual(self.simulation.space.neighborhood.call_args_list,
                         [mk.call(self.location, **kwargs)])

    def test_die(self):
        """test have agent die"""

        with mk.patch.object(agent.Agent, 'deactivate',
                             autospec=True) as mkDeactivate:
            self.Agent.die()
            self.assertEqual(self.Agent.alive, False)
            self.assertEqual(mkDeactivate.call_args_list, [mk.call(self.Agent)])

    def test_reset(self):
        """test reset the agent"""

        self.assertIsNone(self.Agent.reset())
