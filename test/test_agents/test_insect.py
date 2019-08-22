import unittest      as ut
import unittest.mock as mk

import dataclasses as dclass
import itertools   as i_tools

import source.keyword as keyword

import source.agents.agent  as agent
import source.agents.insect as insect

import source.simulation.simulation as simulation

import source.space.agents      as agents
import source.space.environment as environment
import source.space.location    as location


class SimulationTest(simulation.Simulation):
    """Class to add dynamic values for tests"""

    agents = mk.create_autospec(agents.Agents, spec_set=True)


class EnvironmentTest(environment.Environment):
    """Class to add dynamic values for tests"""

    bt    = mk.MagicMock(spec=str)
    plant = mk.MagicMock(spec=float)


class AgentsBinTest(agents.AgentsBin):
    """Class to add dynamic values for tests"""

    environment = mk.create_autospec(EnvironmentTest, spec_set=True)


class TestInsect(ut.TestCase):
    """test base Insect class"""

    def setUp(self):
        """Setup the tests"""

        self.agent_key = mk.MagicMock(spec=str)
        self.unique_id = mk.MagicMock(spec=str)
        self.alive     = mk.MagicMock(spec=bool)
        self.mass      = mk.MagicMock(spec=float)
        self.genotype  = mk.MagicMock(spec=str)
        self.age       = mk.MagicMock(spec=int)
        self.death     = mk.MagicMock(spec=str)

        self.simulation = mk.create_autospec(SimulationTest,
                                             spec_set=True)
        self.location   = mk.create_autospec(location.Location,
                                             spec_set=True)

        self.Insect = insect.Insect(self.agent_key,
                                    self.unique_id,
                                    self.simulation,
                                    self.location,
                                    self.alive,
                                    self.mass,
                                    self.genotype,
                                    self.age,
                                    self.death)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Insect, agent.Agent)
        self.assertIsInstance(self.Insect, insect.Insect)

        self.assertEqual(self.Insect.agent_key,  self.agent_key)
        self.assertEqual(self.Insect.unique_id,  self.unique_id)
        self.assertEqual(self.Insect.simulation, self.simulation)
        self.assertEqual(self.Insect.location,   self.location)
        self.assertEqual(self.Insect.alive,      self.alive)

        self.assertEqual(self.Insect.mass,       self.mass)
        self.assertEqual(self.Insect.genotype,   self.genotype)
        self.assertEqual(self.Insect.age,        self.age)
        self.assertEqual(self.Insect.death,      self.death)

        # noinspection PyTypeChecker
        self.assertIsInstance(self.Insect._age_count, i_tools.count)
        # noinspection PyTypeChecker
        self.assertEqual(next(self.Insect._age_count),
                         next(i_tools.count(self.age + 1)))

        self.assertTrue(dclass.is_dataclass(self.Insect))

    def test_bt(self):
        """test get the bt state of the plant"""

        self.simulation.agents = mk.create_autospec(agents.Agents,
                                                    spec_set=True)
        self.simulation.agents.__getitem__.return_value = \
            mk.create_autospec(AgentsBinTest, spec_set=True)
        self.simulation.agents.__getitem__.return_value.environment = \
            mk.create_autospec(EnvironmentTest, spec_set=True)
        self.location.__getitem__.return_value = \
            mk.create_autospec(location.Location, spec_set=True)

        self.assertEqual(self.Insect.bt,
                         self.simulation.agents.__getitem__.return_value.
                            environment.bt)
        self.assertEqual(self.simulation.agents.__getitem__.call_args_list,
                         [mk.call(self.location.__getitem__.return_value.
                                    location_key)])
        self.assertEqual(self.location.__getitem__.call_args_list,
                         [mk.call(slice(None, keyword.bt_depth, None))])

    def test_plant(self):
        """test get the plant mass"""

        self.simulation.agents = mk.create_autospec(agents.Agents,
                                                    spec_set=True)
        self.simulation.agents.__getitem__.return_value = \
            mk.create_autospec(AgentsBinTest, spec_set=True)
        self.simulation.agents.__getitem__.return_value.environment = \
            mk.create_autospec(EnvironmentTest, spec_set=True)
        self.location.__getitem__.return_value = \
            mk.create_autospec(location.Location, spec_set=True)

        self.assertEqual(self.Insect.plant,
                         self.simulation.agents.__getitem__.return_value.
                         environment.plant)
        self.assertEqual(self.simulation.agents.__getitem__.call_args_list,
                         [mk.call(self.location.__getitem__.return_value.
                                  location_key)])
        self.assertEqual(self.location.__getitem__.call_args_list,
                         [mk.call(slice(None, keyword.plant_depth, None))])

    def test_advance_age(self):
        """test age the agent"""

        counter = i_tools.count(self.age + 1)

        self.assertEqual(self.Insect.advance_age(), [])
        self.assertNotEqual(self.Insect.age, self.age)
        self.assertEqual(self.Insect.age,
                         next(counter))
        self.assertEqual(self.Insect.age,
                         self.age.__add__.return_value)

        self.assertEqual(self.Insect.advance_age(), [])
        self.assertNotEqual(self.Insect.age,
                            self.age.__add__.return_value)
        self.assertEqual(self.Insect.age,
                         next(counter))
        self.assertEqual(self.Insect.age,
                         self.age.__add__.return_value.__add__.return_value)
        
    def test_die(self):
        """test have agent die"""

        death = mk.MagicMock(spec=str)

        with mk.patch.object(agent.Agent, 'die', autospec=True) as mkDie:
            self.Insect.die(death)
            self.assertEqual(self.Insect.death, death)
            self.assertEqual(mkDie.call_args_list, [mk.call(self.Insect)])
