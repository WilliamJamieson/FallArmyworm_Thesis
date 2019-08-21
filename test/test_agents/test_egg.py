import unittest      as ut
import unittest.mock as mk

import dataclasses as dclass
import itertools   as i_tools

import source.keyword as keyword

import source.agents.agent    as agent
import source.agents.egg      as egg
import source.agents.egg_mass as egg_mass
import source.agents.insect   as insect

import source.simulation.behaviors  as behaviors
import source.simulation.models     as models
import source.simulation.simulation as simulation

import source.space.agents   as agents
import source.space.location as location
import source.space.space    as space

import source.survival.egg    as survival
import source.development.egg as development


class BehaviorsTest(behaviors.Behaviors):
    """Class to add dynamic values for tests"""

    survive_egg = mk.create_autospec(survival.Egg,    spec_set=True)
    develop_egg = mk.create_autospec(development.Egg, spec_set=True)


class SimulationTest(simulation.Simulation):
    """Class to add dynamic values for tests"""

    agents    = mk.create_autospec(agents.Agents, spec_set=True)
    behaviors = mk.create_autospec(BehaviorsTest, spec_set=True)
    space     = mk.create_autospec(space.Space,   spec_set=True)
    models    = mk.create_autospec(models.Models, spec_set=True)


class TestEgg(ut.TestCase):
    """test base Egg class"""

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
        self.egg_mass    = mk.create_autospec(egg_mass.EggMass,  spec_set=True)
        self.survival    = mk.create_autospec(survival.Egg,      spec_set=True)
        self.development = mk.create_autospec(development.Egg,   spec_set=True)

        self.Egg = egg.Egg(self.agent_key,
                           self.unique_id,
                           self.simulation,
                           self.location,
                           self.alive,
                           self.mass,
                           self.genotype,
                           self.age,
                           self.death,
                           self.egg_mass,
                           self.survival,
                           self.development)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Egg, agent.Agent)
        self.assertIsInstance(self.Egg, insect.Insect)
        self.assertIsInstance(self.Egg, egg.Egg)

        self.assertEqual(self.Egg.agent_key,  self.agent_key)
        self.assertEqual(self.Egg.unique_id,  self.unique_id)
        self.assertEqual(self.Egg.simulation, self.simulation)
        self.assertEqual(self.Egg.location,   self.location)
        self.assertEqual(self.Egg.alive,      self.alive)

        self.assertEqual(self.Egg.mass,     self.mass)
        self.assertEqual(self.Egg.genotype, self.genotype)
        self.assertEqual(self.Egg.age,      self.age)
        self.assertEqual(self.Egg.death,    self.death)

        self.assertEqual(self.Egg.egg_mass,    self.egg_mass)
        self.assertEqual(self.Egg.survival,    self.survival)
        self.assertEqual(self.Egg.development, self.development)

        # noinspection PyTypeChecker
        self.assertIsInstance(self.Egg._age_count, i_tools.count)
        # noinspection PyTypeChecker
        self.assertEqual(next(self.Egg._age_count),
                         next(i_tools.count(self.age + 1)))

        self.assertTrue(dclass.is_dataclass(self.Egg))
        
    def test_deactivate(self):
        """test deactivate the agent"""

        self.simulation.agents = mk.create_autospec(agents.Agents,
                                                    spec_set=True)
        self.Egg.deactivate()
        self.assertEqual(self.simulation.agents.deactivate.call_args_list,
                         [mk.call(self.Egg)])
        self.assertEqual(self.egg_mass.remove.call_args_list,
                         [mk.call(self.Egg)])

        self.simulation.agents.reset_mock()
        self.egg_mass.reset_mock()
        # Test deactivate is passed through to death
        self.Egg.die(keyword.cannibalism)
        self.assertEqual(self.simulation.agents.deactivate.call_args_list,
                         [mk.call(self.Egg)])
        self.assertEqual(self.egg_mass.remove.call_args_list,
                         [mk.call(self.Egg)])
        self.assertEqual(self.Egg.alive, False)
        self.assertEqual(self.Egg.death, keyword.cannibalism)

    def test_survive(self):
        """test run survive behavior"""

        self.assertEqual(self.Egg.survive(), [])
        self.assertEqual(self.survival.survive.call_args_list,
                         [mk.call(self.Egg)])

    def test_develop(self):
        """test run develop behavior"""

        self.assertEqual(self.Egg.develop(), [])
        self.assertEqual(self.development.develop.call_args_list,
                         [mk.call(self.Egg)])

    def test_initialize(self):
        """test initialize a egg"""

        self.simulation.behaviors = mk.create_autospec(BehaviorsTest,
                                                       spec_set=True)
        self.simulation.behaviors.survive_egg = self.survival
        self.simulation.behaviors.develop_egg = self.development

        self.Egg = egg.Egg.initialize(self.unique_id,
                                      self.simulation,
                                      self.location,
                                      self.mass,
                                      self.genotype,
                                      self.egg_mass)

        self.assertIsInstance(self.Egg, agent.Agent)
        self.assertIsInstance(self.Egg, insect.Insect)
        self.assertIsInstance(self.Egg, egg.Egg)

        self.assertEqual(self.Egg.agent_key, keyword.egg)
        self.assertEqual(self.Egg.alive,     True)
        self.assertEqual(self.Egg.age,       0)
        self.assertEqual(self.Egg.death,     keyword.alive)

        self.assertEqual(self.Egg.unique_id,  self.unique_id)
        self.assertEqual(self.Egg.simulation, self.simulation)
        self.assertEqual(self.Egg.location,   self.location)

        self.assertEqual(self.Egg.mass,     self.mass)
        self.assertEqual(self.Egg.genotype, self.genotype)

        self.assertEqual(self.Egg.egg_mass,    self.egg_mass)
        self.assertEqual(self.Egg.survival,    self.survival)
        self.assertEqual(self.Egg.development, self.development)

        # noinspection PyTypeChecker
        self.assertIsInstance(self.Egg._age_count, i_tools.count)
        # noinspection PyTypeChecker
        self.assertEqual(next(self.Egg._age_count), next(i_tools.count(1)))

        self.assertTrue(dclass.is_dataclass(self.Egg))
