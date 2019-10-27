import unittest      as ut
import unittest.mock as mk

import dataclasses as dclass
import itertools   as i_tools

import source.keyword as keyword

import source.agents.agent    as agent
import source.agents.insect   as insect
import source.agents.egg      as agent_egg
import source.agents.egg_mass as agent_egg_mass
import source.agents.larva    as larva

import source.biomass.gut  as gut
import source.biomass.mass as mass

import source.simulation.behaviors  as behaviors
import source.simulation.models     as models
import source.simulation.simulation as simulation

import source.space.agents   as agents
import source.space.location as location
import source.space.space    as space

import source.development.larva  as development
import source.forage.cannibalism as cannibalism
import source.forage.egg         as forage_egg
import source.forage.larva       as forage_larva
import source.forage.plant       as forage_plant
import source.forage.target      as target_loss
import source.movement.larva     as movement
import source.survival.larva     as survival


class BehaviorsTest(behaviors.Behaviors):
    """Class to add dynamic values for tests"""

    gut           = mk.create_autospec(gut.Gut,                 spec_set=True)
    mass          = mk.create_autospec(mass.Mass,               spec_set=True)
    survive_larva = mk.create_autospec(survival.Larva,          spec_set=True)
    develop_larva = mk.create_autospec(development.Larva,       spec_set=True)
    move_larva    = mk.create_autospec(movement.Larva,          spec_set=True)
    cannibalism   = mk.create_autospec(cannibalism.Cannibalism, spec_set=True)
    forage_plant  = mk.create_autospec(forage_plant.Plant,      spec_set=True)
    forage_egg    = mk.create_autospec(forage_egg.Egg,          spec_set=True)
    forage_larva  = mk.create_autospec(forage_larva.Larva,      spec_set=True)
    loss          = mk.create_autospec(target_loss.Target,      spec_set=True)


class SimulationTest(simulation.Simulation):
    """Class to add dynamic values for tests"""

    agents    = mk.create_autospec(agents.Agents, spec_set=True)
    behaviors = mk.create_autospec(BehaviorsTest, spec_set=True)
    space     = mk.create_autospec(space.Space,   spec_set=True)
    models    = mk.create_autospec(models.Models, spec_set=True)


class EggTest(agent_egg.Egg):
    """Class to add dynamic values for tests"""

    unique_id  = mk.MagicMock(spec=str)
    simulation = mk.create_autospec(SimulationTest,    spec_set=True)
    location   = mk.create_autospec(location.Location, spec_set=True)
    mass       = mk.MagicMock(spec=float)
    genotype   = mk.MagicMock(spec=str)


class EggMassTest(agent_egg_mass.EggMass):
    """Class to add dynamic values for tests"""

    agent_key = keyword.egg_mass


class TestLarva(ut.TestCase):
    """test base Larva class"""

    def setUp(self):
        """Setup the tests"""

        self.agent_key = mk.MagicMock(spec=str)
        self.unique_id = mk.MagicMock(spec=str)
        self.alive     = mk.MagicMock(spec=bool)
        self.mass      = mk.MagicMock(spec=float)
        self.genotype  = mk.MagicMock(spec=str)
        self.age       = mk.MagicMock(spec=int)
        self.death     = mk.MagicMock(spec=str)

        self.simulation = mk.create_autospec(SimulationTest,    spec_set=True)
        self.location   = mk.create_autospec(location.Location, spec_set=True)

        self.plant_gut = mk.MagicMock(spec=float)
        self.egg_gut   = mk.MagicMock(spec=float)
        self.larva_gut = mk.MagicMock(spec=float)
        self.full      = mk.MagicMock(spec=bool)
        self.starve    = mk.MagicMock(spec=bool)

        self.target      = mk.create_autospec(EggMassTest,       spec_set=True)
        self.gut         = mk.create_autospec(gut.Gut,           spec_set=True)
        self.biomass     = mk.create_autospec(mass.Mass,         spec_set=True)
        self.survival    = mk.create_autospec(survival.Larva,    spec_set=True)
        self.development = mk.create_autospec(development.Larva, spec_set=True)
        self.movement    = mk.create_autospec(movement.Larva,    spec_set=True)

        self.forage_plant = mk.create_autospec(forage_plant.Plant,
                                               spec_set=True)
        self.forage_egg   = mk.create_autospec(forage_egg.Egg,
                                               spec_set=True)
        self.forage_larva = mk.create_autospec(forage_larva.Larva,
                                               spec_set=True)
        self.loss         = mk.create_autospec(target_loss.Target,
                                               spec_set=True)
        self.cannibalism  = mk.create_autospec(cannibalism.Cannibalism,
                                               spec_set=True)

        self.Larva = larva.Larva(self.agent_key,
                                 self.unique_id,
                                 self.simulation,
                                 self.location,
                                 self.alive,
                                 self.mass,
                                 self.genotype,
                                 self.age,
                                 self.death,
                                 self.plant_gut,
                                 self.egg_gut,
                                 self.larva_gut,
                                 self.full,
                                 self.starve,
                                 self.gut,
                                 self.biomass,
                                 self.survival,
                                 self.development,
                                 self.movement,
                                 self.forage_plant,
                                 self.forage_egg,
                                 self.forage_larva,
                                 self.loss,
                                 self.cannibalism,
                                 self.target)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Larva, agent.Agent)
        self.assertIsInstance(self.Larva, insect.Insect)
        self.assertIsInstance(self.Larva, larva.Larva)

        self.assertEqual(self.Larva.agent_key,  self.agent_key)
        self.assertEqual(self.Larva.unique_id,  self.unique_id)
        self.assertEqual(self.Larva.simulation, self.simulation)
        self.assertEqual(self.Larva.location,   self.location)
        self.assertEqual(self.Larva.alive,      self.alive)

        self.assertEqual(self.Larva.mass,       self.mass)
        self.assertEqual(self.Larva.genotype,   self.genotype)
        self.assertEqual(self.Larva.age,        self.age)
        self.assertEqual(self.Larva.death,      self.death)

        self.assertEqual(self.Larva.plant_gut,    self.plant_gut)
        self.assertEqual(self.Larva.egg_gut,      self.egg_gut)
        self.assertEqual(self.Larva.larva_gut,    self.larva_gut)
        self.assertEqual(self.Larva.full,         self.full)
        self.assertEqual(self.Larva.starve,       self.starve)
        self.assertEqual(self.Larva.gut,          self.gut)
        self.assertEqual(self.Larva.biomass,      self.biomass)
        self.assertEqual(self.Larva.survival,     self.survival)
        self.assertEqual(self.Larva.development,  self.development)
        self.assertEqual(self.Larva.movement,     self.movement)
        self.assertEqual(self.Larva.forage_plant, self.forage_plant)
        self.assertEqual(self.Larva.forage_egg,   self.forage_egg)
        self.assertEqual(self.Larva.forage_larva, self.forage_larva)
        self.assertEqual(self.Larva.loss,         self.loss)
        self.assertEqual(self.Larva.cannibalism,  self.cannibalism,)
        self.assertEqual(self.Larva.target,       self.target)

        # noinspection PyTypeChecker
        self.assertIsInstance(self.Larva._age_count, i_tools.count)
        # noinspection PyTypeChecker
        self.assertEqual(next(self.Larva._age_count),
                         next(i_tools.count(self.age + 1)))

        self.assertTrue(dclass.is_dataclass(self.Larva))

    def test_active(self):
        """test if this is active"""

        self.mass.__gt__.side_effect = [True, False]

        # test active
        self.assertTrue(self.Larva.active)
        self.assertEqual(self.mass.__gt__.call_args_list,
                         [mk.call(0)])

        self.mass.reset_mock()
        # test inactive
        self.assertFalse(self.Larva.active)
        self.assertEqual(self.mass.__gt__.call_args_list,
                         [mk.call(0)])

    def test__can_consume(self):
        """test if larva can consume"""

        # Not alive
        self.Larva.alive = False
        self.assertFalse(self.Larva._can_consume)

        # Alive and full
        self.Larva.alive = True
        self.assertTrue(self.Larva._can_consume)

    def test__has_target(self):
        """test if this larva has a target"""

        # has target given and active
        self.Larva.target.active = True
        self.assertTrue(self.Larva._has_target)

        # has target given but inactive
        self.Larva.target.active = False
        self.assertFalse(self.Larva._has_target)

        # no target given
        self.Larva.target = None
        self.assertFalse(self.Larva._has_target)

    def test_add_plant(self):
        """test add_plant"""

        available = mk.MagicMock(spec=float)
        amount    = mk.MagicMock(spec=float)

        # Test not full
        self.gut.amount.return_value = (amount, False)
        self.assertEqual(self.Larva.add_plant(available),
                         amount)
        self.assertEqual(self.Larva.plant_gut,
                         self.plant_gut.__add__.return_value)
        self.assertEqual(self.plant_gut.__add__.call_args_list,
                         [mk.call(amount)])
        self.assertEqual(self.Larva.full, self.full)
        self.assertEqual(self.gut.amount.call_args_list,
                         [mk.call(self.Larva, available)])

        self.Larva.plant_gut = self.plant_gut
        self.plant_gut.reset_mock()
        self.gut.amount.reset_mock()
        # Test full
        self.gut.amount.return_value = (amount, True)
        self.assertEqual(self.Larva.add_plant(available),
                         amount)
        self.assertEqual(self.Larva.plant_gut,
                         self.plant_gut.__add__.return_value)
        self.assertEqual(self.plant_gut.__add__.call_args_list,
                         [mk.call(amount)])
        self.assertEqual(self.Larva.full, True)
        self.assertNotEqual(self.full,    True)
        self.assertEqual(self.gut.amount.call_args_list,
                         [mk.call(self.Larva, available)])

    def test_add_egg(self):
        """test add_egg"""

        available = mk.MagicMock(spec=float)
        amount    = mk.MagicMock(spec=float)

        # Test not full
        self.gut.amount.return_value = (amount, False)
        self.assertEqual(self.Larva.add_egg(available),
                         amount)
        self.assertEqual(self.Larva.egg_gut,
                         self.egg_gut.__add__.return_value)
        self.assertEqual(self.egg_gut.__add__.call_args_list,
                         [mk.call(amount)])
        self.assertEqual(self.Larva.full, self.full)
        self.assertEqual(self.gut.amount.call_args_list,
                         [mk.call(self.Larva, available)])

        self.Larva.egg_gut = self.egg_gut
        self.egg_gut.reset_mock()
        self.gut.amount.reset_mock()
        # Test full
        self.gut.amount.return_value = (amount, True)
        self.assertEqual(self.Larva.add_egg(available),
                         amount)
        self.assertEqual(self.Larva.egg_gut,
                         self.egg_gut.__add__.return_value)
        self.assertEqual(self.egg_gut.__add__.call_args_list,
                         [mk.call(amount)])
        self.assertEqual(self.Larva.full, True)
        self.assertNotEqual(self.full,    True)
        self.assertEqual(self.gut.amount.call_args_list,
                         [mk.call(self.Larva, available)])

    def test_add_larva(self):
        """test add_larva"""

        available = mk.MagicMock(spec=float)
        amount    = mk.MagicMock(spec=float)

        # Test not full
        self.gut.amount.return_value = (amount, False)
        self.assertEqual(self.Larva.add_larva(available),
                         amount)
        self.assertEqual(self.Larva.larva_gut,
                         self.larva_gut.__add__.return_value)
        self.assertEqual(self.larva_gut.__add__.call_args_list,
                         [mk.call(amount)])
        self.assertEqual(self.Larva.full, self.full)
        self.assertEqual(self.gut.amount.call_args_list,
                         [mk.call(self.Larva, available)])

        self.Larva.larva_gut = self.larva_gut
        self.larva_gut.reset_mock()
        self.gut.amount.reset_mock()
        # Test full
        self.gut.amount.return_value = (amount, True)
        self.assertEqual(self.Larva.add_larva(available),
                         amount)
        self.assertEqual(self.Larva.larva_gut,
                         self.larva_gut.__add__.return_value)
        self.assertEqual(self.larva_gut.__add__.call_args_list,
                         [mk.call(amount)])
        self.assertEqual(self.Larva.full, True)
        self.assertNotEqual(self.full,    True)
        self.assertEqual(self.gut.amount.call_args_list,
                         [mk.call(self.Larva, available)])

    def test_grow(self):
        """test grow the larva"""

        self.biomass.grow.return_value.__lt__.side_effect = [False, True]

        # Larva is not alive
        self.Larva.alive = False
        #   Test that it does not starve
        self.assertEqual(self.Larva.grow(), [])
        self.assertEqual(self.Larva.mass, self.mass)
        self.assertEqual(self.mass.__add__.call_args_list, [])
        self.assertEqual(self.biomass.grow.call_args_list, [])
        self.assertEqual(self.Larva.starve, self.starve)

        # Larva is alive
        self.Larva.alive = True
        #   Test that it does not starve
        self.assertEqual(self.Larva.grow(), [])
        self.assertEqual(self.Larva.mass,
                         self.mass.__add__.return_value)
        self.assertEqual(self.mass.__add__.call_args_list,
                         [mk.call(self.biomass.grow.return_value)])
        self.assertEqual(self.biomass.grow.call_args_list,
                         [mk.call(self.Larva)])
        self.assertEqual(self.Larva.starve, self.starve)
        self.assertEqual(self.biomass.grow.return_value.__lt__.call_args_list,
                         [mk.call(0)])

        self.biomass.reset_mock()
        self.mass.reset_mock()
        self.Larva.mass = self.mass
        self.mass.reset_mock()

        #   Test that it does starve
        self.assertEqual(self.Larva.grow(), [])
        self.assertEqual(self.Larva.mass, self.mass)
        self.assertEqual(self.mass.__add__.call_args_list, [])
        self.assertEqual(self.biomass.grow.call_args_list,
                         [mk.call(self.Larva)])
        self.assertEqual(self.Larva.starve, True)
        self.assertEqual(self.biomass.grow.return_value.__lt__.call_args_list,
                         [mk.call(0)])

    def test_survive(self):
        """test run survive behavior"""

        # Larva is not alive
        self.Larva.alive = False
        self.assertEqual(self.Larva.survive(), [])
        self.assertEqual(self.survival.survive.call_args_list, [])

        # Larva is alive
        self.Larva.alive = True
        self.assertEqual(self.Larva.survive(), [])
        self.assertEqual(self.survival.survive.call_args_list,
                         [mk.call(self.Larva)])

    def test_develop(self):
        """test run develop behavior"""

        # Larva is not alive
        self.Larva.alive = False
        self.assertEqual(self.Larva.develop(), [])
        self.assertEqual(self.development.develop.call_args_list, [])

        # Larva is alive
        self.Larva.alive = True
        self.assertEqual(self.Larva.develop(), [])
        self.assertEqual(self.development.develop.call_args_list,
                         [mk.call(self.Larva)])

    def test_move(self):
        """test run move behavior"""

        with mk.patch.object(larva.Larva, '_can_consume',
                             autospec=True) as mkCan:
            with mk.patch.object(larva.Larva, '_has_target',
                                 autospec=True) as mkHas:
                mkCan.__get__ = mk.MagicMock(side_effect=[False, True, True])
                mkHas.__get__ = mk.MagicMock(side_effect=[       True, False])

                # Cannot consume
                self.assertEqual(self.Larva.move(), [])
                self.assertEqual(self.movement.move.call_args_list, [])

                # Can consume and has target
                self.assertEqual(self.Larva.move(), [])
                self.assertEqual(self.movement.move.call_args_list, [])

                # Can consume and does not have target
                self.assertEqual(self.Larva.move(), [])
                self.assertEqual(self.movement.move.call_args_list,
                                 [mk.call(self.Larva)])

    def test__consume_plant(self):
        """test consume the plant"""

        with mk.patch.object(larva.Larva, '_can_consume',
                             autospec=True) as mkCan:
            mkCan.__get__ = mk.MagicMock(side_effect=[False, True])

            # Cannot consume
            self.Larva._consume_plant()
            self.assertEqual(self.forage_plant.consume.call_args_list, [])

            # Can consume
            self.Larva._consume_plant()
            self.assertEqual(self.forage_plant.consume.call_args_list,
                             [mk.call(self.Larva)])

    def test_consume_egg(self):
        """test consume the egg"""

        egg_mass = mk.create_autospec(agent_egg_mass.EggMass, spec_set=True)

        self.Larva.consume_egg(egg_mass)
        self.assertEqual(self.Larva.target, egg_mass)
        self.assertEqual(self.forage_egg.consume.call_args_list,
                         [mk.call(self.Larva, egg_mass)])

    def test_consume_larva(self):
        """test consume the larva"""

        target = mk.create_autospec(larva.Larva, spec_set=True)

        self.Larva.consume_larva(target)
        self.assertEqual(self.Larva.target, target)
        self.assertEqual(self.forage_larva.consume.call_args_list,
                         [mk.call(self.Larva, target)])

    def test__consume_target(self):
        """test consume the target"""

        with mk.patch.object(larva.Larva, '_has_target',
                             autospec=True) as mkHas:
            mkHas.__get__ = mk.MagicMock(side_effect=[False, True, True])

            # Has no target
            self.Larva._consume_target()
            self.assertEqual(self.loss.consume.call_args_list, [])

            # Has target and is not alive
            self.Larva.alive = False
            self.Larva._consume_target()
            self.assertEqual(self.loss.consume.call_args_list, [])

            # Has target and is alive
            self.Larva.alive = True
            self.Larva._consume_target()
            self.assertEqual(self.loss.consume.call_args_list,
                             [mk.call(self.Larva)])

    def test__location_keys(self):
        """test get the location keys for cannibalism"""

        kwargs = {'test': mk.MagicMock()}

        vertices = {mk.MagicMock(spec=int) for _ in range(3)}

        locs          = []
        location_keys = []
        for _ in vertices:
            loc = mk.create_autospec(location.Location, spec_set=True)
            location_keys.append(loc.location_key)
            locs.append(loc)

        self.location.copy.side_effect = locs

        with mk.patch.object(larva.Larva, 'vertices',
                             autospec=True) as mkVertices:
            mkVertices.return_value = vertices

            self.assertEqual(self.Larva._location_keys(**kwargs), location_keys)
            self.assertEqual(mkVertices.call_args_list,
                             [mk.call(self.Larva, **kwargs)])
            for index, vertex in enumerate(vertices):
                self.assertEqual(locs[index].__setitem__.call_args_list,
                                 [mk.call(keyword.larva_level, vertex)])
                self.assertEqual(self.location.copy.call_args_list[index],
                                 [mk.call()])
            self.assertEqual(len(self.location.copy.call_args_list), 3)

    def test_targets(self):
        """test get the targets"""

        kwargs = {'test': mk.MagicMock()}

        self.simulation.agents = mk.create_autospec(agents.Agents,
                                                    spec_set=True)

        location_keys = []
        agents_bins   = []
        targets       = []
        for index in range(3):
            location_key = mk.MagicMock(spec=tuple)
            agents_bin   = mk.create_autospec(agents.AgentsBin, spec_set=True)
            egg_bin      = mk.create_autospec(agents.AgentBin, spec_set=True)
            larva_bin    = mk.create_autospec(agents.AgentBin, spec_set=True)

            eggs   = []
            larvae = []
            if index == 0:
                larvae.append(self.Larva)

            for _ in range(3):
                eggs.append(mk.create_autospec(EggMassTest, spec_set=True))
                larvae.append(mk.create_autospec(larva.Larva, spec_set=True))
            egg_bin.  agents = eggs
            larva_bin.agents = larvae
            targets.extend(eggs)
            targets.extend(larvae)
            agents_bin.__getitem__.side_effect = [egg_bin, larva_bin]

            location_keys.append(location_key)
            agents_bins.  append(agents_bin)

        self.simulation.agents.__getitem__.side_effect = agents_bins

        self.assertIn(self.Larva, targets)
        with mk.patch.object(larva.Larva, '_location_keys',
                             autospec=True) as mkKeys:
            mkKeys.return_value = location_keys

            new = self.Larva.targets(**kwargs)
            self.assertEqual(len(targets), len(new) + 1)
            targets.remove(self.Larva)
            self.assertEqual(targets, new)

            self.assertEqual(mkKeys.call_args_list,
                             [mk.call(self.Larva, **kwargs)])
            for index, call in enumerate(self.simulation.agents.
                                                 __getitem__.call_args_list):
                self.assertEqual(call,
                                 mk.call(location_keys[index]))
            self.assertEqual(len(self.simulation.agents.
                                    __getitem__.call_args_list), 3)
            for index, agent_bin in enumerate(agents_bins):
                self.assertEqual(agent_bin.__getitem__.call_args_list,
                                 [mk.call(keyword.egg_mass),
                                  mk.call(keyword.larva)])

    def test_consume(self):
        """test run the consume system"""

        with mk.patch.object(larva.Larva, '_consume_target') as mkTarget:
            with mk.patch.object(larva.Larva, '_consume_plant') as mkPlant:
                master = mk.MagicMock()
                master.attach_mock(mkTarget,         'target')
                master.attach_mock(mkPlant,          'plant')
                master.attach_mock(self.cannibalism, 'cannibalism')

                self.assertEqual(self.Larva.consume(), [])
                self.assertEqual(master.mock_calls,
                                 [mk.call.target(),
                                  mk.call.cannibalism.cannibalism(self.Larva),
                                  mk.call.plant()])

    def test_reset(self):
        """test empty the gut system"""

        self.assertEqual(self.Larva.reset(), [])
        self.assertEqual(self.Larva.plant_gut, 0)
        self.assertEqual(self.Larva.egg_gut,   0)
        self.assertEqual(self.Larva.larva_gut, 0)
        self.assertEqual(self.Larva.full,      False)

    def test_initialize(self):
        """test initialize a larva"""

        self.simulation.behaviors = mk.create_autospec(BehaviorsTest,
                                                       spec_set=True)
        self.simulation.behaviors.gut           = self.gut
        self.simulation.behaviors.mass          = self.biomass
        self.simulation.behaviors.survive_larva = self.survival
        self.simulation.behaviors.develop_larva = self.development
        self.simulation.behaviors.move_larva    = self.movement
        self.simulation.behaviors.cannibalism   = self.cannibalism
        self.simulation.behaviors.forage_plant  = self.forage_plant
        self.simulation.behaviors.forage_egg    = self.forage_egg
        self.simulation.behaviors.forage_larva  = self.forage_larva

        self.Larva = larva.Larva.initialize(self.unique_id,
                                            self.simulation,
                                            self.location,
                                            self.mass,
                                            self.genotype)

        self.assertIsInstance(self.Larva, agent.Agent)
        self.assertIsInstance(self.Larva, insect.Insect)
        self.assertIsInstance(self.Larva, larva.Larva)

        self.assertEqual(self.Larva.agent_key, keyword.larva)
        self.assertEqual(self.Larva.alive,     True)
        self.assertEqual(self.Larva.age,       0)
        self.assertEqual(self.Larva.death,     keyword.alive)

        self.assertEqual(self.Larva.plant_gut, 0)
        self.assertEqual(self.Larva.egg_gut,   0)
        self.assertEqual(self.Larva.larva_gut, 0)
        self.assertEqual(self.Larva.full,      False)
        self.assertEqual(self.Larva.starve,    False)
        self.assertEqual(self.Larva.target,    None)

        self.assertEqual(self.Larva.unique_id,  self.unique_id)
        self.assertEqual(self.Larva.simulation, self.simulation)
        self.assertEqual(self.Larva.location,   self.location)

        self.assertEqual(self.Larva.mass,       self.mass)
        self.assertEqual(self.Larva.genotype,   self.genotype)

        self.assertEqual(self.Larva.gut,          self.gut)
        self.assertEqual(self.Larva.biomass,      self.biomass)
        self.assertEqual(self.Larva.survival,     self.survival)
        self.assertEqual(self.Larva.development,  self.development)
        self.assertEqual(self.Larva.movement,     self.movement)
        self.assertEqual(self.Larva.forage_plant, self.forage_plant)
        self.assertEqual(self.Larva.forage_egg,   self.forage_egg)
        self.assertEqual(self.Larva.forage_larva, self.forage_larva)
        self.assertEqual(self.Larva.cannibalism,  self.cannibalism,)

        # noinspection PyTypeChecker
        self.assertIsInstance(self.Larva._age_count, i_tools.count)
        # noinspection PyTypeChecker
        self.assertEqual(next(self.Larva._age_count), next(i_tools.count(1)))

        self.assertTrue(dclass.is_dataclass(self.Larva))

    def test_setup(self):
        """test setup an initial larva"""

        self.simulation.behaviors = mk.create_autospec(BehaviorsTest,
                                                       spec_set=True)
        self.simulation.behaviors.gut           = self.gut
        self.simulation.behaviors.mass          = self.biomass
        self.simulation.behaviors.survive_larva = self.survival
        self.simulation.behaviors.develop_larva = self.development
        self.simulation.behaviors.move_larva    = self.movement
        self.simulation.behaviors.cannibalism   = self.cannibalism
        self.simulation.behaviors.forage_plant  = self.forage_plant
        self.simulation.behaviors.forage_egg    = self.forage_egg
        self.simulation.behaviors.forage_larva  = self.forage_larva
        self.simulation.space  = mk.create_autospec(space.Space, spec_set=True)
        self.simulation.models = mk.create_autospec(models.Models,
                                                    spec_set=True)

        unique_id_num = mk.MagicMock(spec=int)
        initial_key   = mk.MagicMock(spec=str)

        self.Larva = larva.Larva.setup(unique_id_num,
                                       initial_key,
                                       self.simulation,
                                       self.genotype)

        self.assertIsInstance(self.Larva, agent.Agent)
        self.assertIsInstance(self.Larva, insect.Insect)
        self.assertIsInstance(self.Larva, larva.Larva)

        self.assertEqual(self.Larva.unique_id,
                         str(initial_key)   +
                         str(unique_id_num) +
                         keyword.larva)
        self.assertEqual(self.Larva.location,
                         self.simulation.space.new_location.return_value)
        self.assertEqual(self.simulation.space.new_location.call_args_list,
                         [mk.call(keyword.larva_depth)])
        self.assertEqual(self.Larva.mass,
                         self.simulation.models.
                         __getitem__.return_value.return_value)
        self.assertEqual(self.simulation.models.
                         __getitem__.return_value.call_args_list,
                         [mk.call(self.genotype)])
        self.assertEqual(self.simulation.models.
                         __getitem__.call_args_list,
                         [mk.call(keyword.init_juvenile)])

        self.assertEqual(self.Larva.agent_key, keyword.larva)
        self.assertEqual(self.Larva.alive,     True)
        self.assertEqual(self.Larva.age,       0)
        self.assertEqual(self.Larva.death,     keyword.alive)

        self.assertEqual(self.Larva.plant_gut, 0)
        self.assertEqual(self.Larva.egg_gut,   0)
        self.assertEqual(self.Larva.larva_gut, 0)
        self.assertEqual(self.Larva.full,      False)
        self.assertEqual(self.Larva.starve,    False)
        self.assertEqual(self.Larva.target,    None)

        self.assertEqual(self.Larva.simulation, self.simulation)

        self.assertEqual(self.Larva.genotype,   self.genotype)

        self.assertEqual(self.Larva.gut,          self.gut)
        self.assertEqual(self.Larva.biomass,      self.biomass)
        self.assertEqual(self.Larva.survival,     self.survival)
        self.assertEqual(self.Larva.development,  self.development)
        self.assertEqual(self.Larva.movement,     self.movement)
        self.assertEqual(self.Larva.forage_plant, self.forage_plant)
        self.assertEqual(self.Larva.forage_egg,   self.forage_egg)
        self.assertEqual(self.Larva.forage_larva, self.forage_larva)
        self.assertEqual(self.Larva.cannibalism,  self.cannibalism,)

        # noinspection PyTypeChecker
        self.assertIsInstance(self.Larva._age_count, i_tools.count)
        # noinspection PyTypeChecker
        self.assertEqual(next(self.Larva._age_count), next(i_tools.count(1)))

        self.assertTrue(dclass.is_dataclass(self.Larva))

    def test_advance(self):
        """test advance a egg into a larva"""

        self.simulation.behaviors = mk.create_autospec(BehaviorsTest,
                                                       spec_set=True)
        self.simulation.behaviors.gut           = self.gut
        self.simulation.behaviors.mass          = self.biomass
        self.simulation.behaviors.survive_larva = self.survival
        self.simulation.behaviors.develop_larva = self.development
        self.simulation.behaviors.move_larva    = self.movement
        self.simulation.behaviors.cannibalism   = self.cannibalism
        self.simulation.behaviors.forage_plant  = self.forage_plant
        self.simulation.behaviors.forage_egg    = self.forage_egg
        self.simulation.behaviors.forage_larva  = self.forage_larva
        self.simulation.behaviors.target        = self.loss

        egg = mk.create_autospec(EggTest, spec_set=True)
        egg.unique_id  = self.unique_id
        egg.simulation = self.simulation
        egg.location   = self.location
        egg.mass       = self.mass
        egg.genotype   = self.genotype

        self.Larva = larva.Larva.advance(egg)

        self.assertIsInstance(self.Larva, agent.Agent)
        self.assertIsInstance(self.Larva, insect.Insect)
        self.assertIsInstance(self.Larva, larva.Larva)

        self.assertEqual(self.Larva.agent_key, keyword.larva)
        self.assertEqual(self.Larva.alive,     True)
        self.assertEqual(self.Larva.age,       0)
        self.assertEqual(self.Larva.death,     keyword.alive)

        self.assertEqual(self.Larva.plant_gut, 0)
        self.assertEqual(self.Larva.egg_gut,   0)
        self.assertEqual(self.Larva.larva_gut, 0)
        self.assertEqual(self.Larva.full,      False)
        self.assertEqual(self.Larva.starve,    False)
        self.assertEqual(self.Larva.target,    None)

        self.assertEqual(self.Larva.unique_id,  self.unique_id)
        self.assertEqual(self.Larva.simulation, self.simulation)
        self.assertEqual(self.Larva.location,   self.location)

        self.assertEqual(self.Larva.mass,       self.mass)
        self.assertEqual(self.Larva.genotype,   self.genotype)

        self.assertEqual(self.Larva.gut,          self.gut)
        self.assertEqual(self.Larva.biomass,      self.biomass)
        self.assertEqual(self.Larva.survival,     self.survival)
        self.assertEqual(self.Larva.development,  self.development)
        self.assertEqual(self.Larva.movement,     self.movement)
        self.assertEqual(self.Larva.forage_plant, self.forage_plant)
        self.assertEqual(self.Larva.forage_egg,   self.forage_egg)
        self.assertEqual(self.Larva.forage_larva, self.forage_larva)
        self.assertEqual(self.Larva.loss,         self.loss)
        self.assertEqual(self.Larva.cannibalism,  self.cannibalism)

        # noinspection PyTypeChecker
        self.assertIsInstance(self.Larva._age_count, i_tools.count)
        # noinspection PyTypeChecker
        self.assertEqual(next(self.Larva._age_count), next(i_tools.count(1)))

        self.assertTrue(dclass.is_dataclass(self.Larva))
