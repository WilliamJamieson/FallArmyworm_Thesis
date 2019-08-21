import unittest      as ut
import unittest.mock as mk

import dataclasses as dclass
import itertools   as i_tools

import source.keyword as keyword

import source.agents.agent  as agent
import source.agents.larva  as agent_larva
import source.agents.pupa   as pupa
import source.agents.insect as insect

import source.simulation.behaviors  as behaviors
import source.simulation.models     as models
import source.simulation.simulation as simulation

import source.space.agents   as agents
import source.space.location as location
import source.space.space    as space

import source.survival.pupa    as survival
import source.development.pupa as development


class BehaviorsTest(behaviors.Behaviors):
    """Class to add dynamic values for tests"""

    survive_pupa = mk.create_autospec(survival.Pupa,    spec_set=True)
    develop_pupa = mk.create_autospec(development.Pupa, spec_set=True)


class SimulationTest(simulation.Simulation):
    """Class to add dynamic values for tests"""

    agents    = mk.create_autospec(agents.Agents, spec_set=True)
    behaviors = mk.create_autospec(BehaviorsTest, spec_set=True)
    space     = mk.create_autospec(space.Space,   spec_set=True)
    models    = mk.create_autospec(models.Models, spec_set=True)


class LarvaTest(agent_larva.Larva):
    """Class to add dynamic values for tests"""

    unique_id  = mk.MagicMock(spec=str)
    simulation = mk.create_autospec(SimulationTest,    spec_set=True)
    location   = mk.create_autospec(location.Location, spec_set=True)
    mass       = mk.MagicMock(spec=float)
    genotype   = mk.MagicMock(spec=str)


class TestPupa(ut.TestCase):
    """test base Pupa class"""

    def setUp(self):
        """Setup the tests"""

        self.agent_key = mk.MagicMock(spec=str)
        self.unique_id = mk.MagicMock(spec=str)
        self.alive     = mk.MagicMock(spec=bool)
        self.mass      = mk.MagicMock(spec=float)
        self.genotype  = mk.MagicMock(spec=str)
        self.age       = mk.MagicMock(spec=int)
        self.death     = mk.MagicMock(spec=str)

        self.simulation  = mk.create_autospec(SimulationTest,    spec_set=True)
        self.location    = mk.create_autospec(location.Location, spec_set=True)

        self.survival    = mk.create_autospec(survival.Pupa,    spec_set=True)
        self.development = mk.create_autospec(development.Pupa, spec_set=True)

        self.Pupa = pupa.Pupa(self.agent_key,
                              self.unique_id,
                              self.simulation,
                              self.location,
                              self.alive,
                              self.mass,
                              self.genotype,
                              self.age,
                              self.death,
                              self.survival,
                              self.development)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Pupa, agent.Agent)
        self.assertIsInstance(self.Pupa, insect.Insect)
        self.assertIsInstance(self.Pupa, pupa.Pupa)

        self.assertEqual(self.Pupa.agent_key,  self.agent_key)
        self.assertEqual(self.Pupa.unique_id,  self.unique_id)
        self.assertEqual(self.Pupa.simulation, self.simulation)
        self.assertEqual(self.Pupa.location,   self.location)
        self.assertEqual(self.Pupa.alive,      self.alive)

        self.assertEqual(self.Pupa.mass,     self.mass)
        self.assertEqual(self.Pupa.genotype, self.genotype)
        self.assertEqual(self.Pupa.age,      self.age)
        self.assertEqual(self.Pupa.death,    self.death)

        self.assertEqual(self.Pupa.survival,    self.survival)
        self.assertEqual(self.Pupa.development, self.development)

        # noinspection PyTypeChecker
        self.assertIsInstance(self.Pupa._age_count, i_tools.count)
        # noinspection PyTypeChecker
        self.assertEqual(next(self.Pupa._age_count),
                         next(i_tools.count(self.age + 1)))

        self.assertTrue(dclass.is_dataclass(self.Pupa))

    def test_survive(self):
        """test run survive behavior"""

        self.assertEqual(self.Pupa.survive(), [])
        self.assertEqual(self.survival.survive.call_args_list,
                         [mk.call(self.Pupa)])

    def test_develop(self):
        """test run develop behavior"""

        self.assertEqual(self.Pupa.develop(), [])
        self.assertEqual(self.development.develop.call_args_list,
                         [mk.call(self.Pupa)])
        
    def test_initialize(self):
        """test initialize a pupa"""

        self.simulation.behaviors = mk.create_autospec(BehaviorsTest,
                                                       spec_set=True)
        self.simulation.behaviors.survive_pupa = self.survival
        self.simulation.behaviors.develop_pupa = self.development

        self.Pupa = pupa.Pupa.initialize(self.unique_id,
                                         self.simulation,
                                         self.location,
                                         self.mass,
                                         self.genotype)

        self.assertIsInstance(self.Pupa, agent.Agent)
        self.assertIsInstance(self.Pupa, insect.Insect)
        self.assertIsInstance(self.Pupa, pupa.Pupa)

        self.assertEqual(self.Pupa.agent_key, keyword.pupa)
        self.assertEqual(self.Pupa.alive,     True)
        self.assertEqual(self.Pupa.age,       0)
        self.assertEqual(self.Pupa.death,     keyword.alive)

        self.assertEqual(self.Pupa.unique_id,  self.unique_id)
        self.assertEqual(self.Pupa.simulation, self.simulation)
        self.assertEqual(self.Pupa.location,   self.location)

        self.assertEqual(self.Pupa.mass,     self.mass)
        self.assertEqual(self.Pupa.genotype, self.genotype)

        self.assertEqual(self.Pupa.survival,    self.survival)
        self.assertEqual(self.Pupa.development, self.development)

        # noinspection PyTypeChecker
        self.assertIsInstance(self.Pupa._age_count, i_tools.count)
        # noinspection PyTypeChecker
        self.assertEqual(next(self.Pupa._age_count), next(i_tools.count(1)))

        self.assertTrue(dclass.is_dataclass(self.Pupa))

    def test_setup(self):
        """test setup an initial pupa"""

        self.simulation.behaviors = mk.create_autospec(BehaviorsTest,
                                                       spec_set=True)
        self.simulation.behaviors.survive_pupa = self.survival
        self.simulation.behaviors.develop_pupa = self.development
        self.simulation.space  = mk.create_autospec(space.Space, spec_set=True)
        self.simulation.models = mk.create_autospec(models.Models,
                                                    spec_set=True)

        unique_id_num = mk.MagicMock(spec=int)
        initial_key   = mk.MagicMock(spec=str)

        self.Pupa = pupa.Pupa.setup(unique_id_num,
                                    initial_key,
                                    self.simulation,
                                    self.genotype)

        self.assertIsInstance(self.Pupa, agent.Agent)
        self.assertIsInstance(self.Pupa, insect.Insect)
        self.assertIsInstance(self.Pupa, pupa.Pupa)

        self.assertEqual(self.Pupa.unique_id,
                         str(initial_key)   +
                         str(unique_id_num) +
                         keyword.pupa)
        self.assertEqual(self.Pupa.location,
                         self.simulation.space.new_location.return_value)
        self.assertEqual(self.simulation.space.new_location.call_args_list,
                         [mk.call(keyword.pupa_depth)])
        self.assertEqual(self.Pupa.mass,
                         self.simulation.models.
                            __getitem__.return_value.return_value)
        self.assertEqual(self.simulation.models.
                            __getitem__.return_value.call_args_list,
                         [mk.call(self.genotype)])
        self.assertEqual(self.simulation.models.
                            __getitem__.call_args_list,
                         [mk.call(keyword.init_mature)])

        self.assertEqual(self.Pupa.agent_key, keyword.pupa)
        self.assertEqual(self.Pupa.alive,     True)
        self.assertEqual(self.Pupa.age,       0)
        self.assertEqual(self.Pupa.death,     keyword.alive)

        self.assertEqual(self.Pupa.simulation, self.simulation)

        self.assertEqual(self.Pupa.genotype, self.genotype)

        self.assertEqual(self.Pupa.survival,    self.survival)
        self.assertEqual(self.Pupa.development, self.development)

        # noinspection PyTypeChecker
        self.assertIsInstance(self.Pupa._age_count, i_tools.count)
        # noinspection PyTypeChecker
        self.assertEqual(next(self.Pupa._age_count), next(i_tools.count(1)))

        self.assertTrue(dclass.is_dataclass(self.Pupa))

    def test_advance(self):
        """test advance a larva into a pupa"""

        self.simulation.behaviors = mk.create_autospec(BehaviorsTest,
                                                       spec_set=True)
        self.simulation.behaviors.survive_pupa = self.survival
        self.simulation.behaviors.develop_pupa = self.development

        larva = mk.create_autospec(LarvaTest, spec_set=True)
        larva.unique_id  = self.unique_id
        larva.simulation = self.simulation
        larva.location   = self.location
        larva.mass       = self.mass
        larva.genotype   = self.genotype

        self.Pupa = pupa.Pupa.advance(larva)

        self.assertIsInstance(self.Pupa, agent.Agent)
        self.assertIsInstance(self.Pupa, insect.Insect)
        self.assertIsInstance(self.Pupa, pupa.Pupa)

        self.assertEqual(self.Pupa.agent_key, keyword.pupa)
        self.assertEqual(self.Pupa.alive,     True)
        self.assertEqual(self.Pupa.age,       0)
        self.assertEqual(self.Pupa.death,     keyword.alive)

        self.assertEqual(self.Pupa.unique_id,  self.unique_id)
        self.assertEqual(self.Pupa.simulation, self.simulation)
        self.assertEqual(self.Pupa.location,   self.location)

        self.assertEqual(self.Pupa.mass,     self.mass)
        self.assertEqual(self.Pupa.genotype, self.genotype)

        self.assertEqual(self.Pupa.survival,    self.survival)
        self.assertEqual(self.Pupa.development, self.development)

        # noinspection PyTypeChecker
        self.assertIsInstance(self.Pupa._age_count, i_tools.count)
        # noinspection PyTypeChecker
        self.assertEqual(next(self.Pupa._age_count), next(i_tools.count(1)))

        self.assertTrue(dclass.is_dataclass(self.Pupa))
