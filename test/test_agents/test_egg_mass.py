import unittest      as ut
import unittest.mock as mk

import dataclasses  as dclass
import collections  as collect
import itertools    as i_tools
import numpy        as np
import numpy.random as rnd

import source.keyword as keyword

import source.agents.agent    as agent
import source.agents.egg      as agent_egg
import source.agents.egg_mass as egg_mass
import source.agents.adult    as agent_adult

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


class AdultTest(agent_adult.Adult):
    """Class to add dynamic values for tests"""

    unique_id  = mk.MagicMock(spec=str)
    simulation = mk.create_autospec(SimulationTest,    spec_set=True)
    location   = mk.create_autospec(location.Location, spec_set=True)
    genotype   = mk.MagicMock(spec=str)
    mate       = mk.MagicMock(spec=str)


class EggMassTest(egg_mass.EggMass):
    """Class to add dynamic values for tests"""

    unique_id  = mk.MagicMock(spec=str)
    simulation = mk.create_autospec(SimulationTest,    spec_set=True)
    location   = mk.create_autospec(location.Location, spec_set=True)
    mass       = mk.MagicMock(spec=float)
    genotype   = mk.MagicMock(spec=str)


class EggsTest(egg_mass.Eggs):
    """Class to add dynamic values for tests"""

    mass = mk.MagicMock(spec=float)


class TestEggs(ut.TestCase):
    """test the Eggs list class"""

    def setUp(self):
        """Setup the tests"""

        self.eggs = [mk.create_autospec(agent_egg.Egg, spec_set=True)
                     for _ in range(3)]
        self.mass = mk.MagicMock(spec=float)

        self.Eggs = egg_mass.Eggs(self.eggs,
                                  self.mass)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Eggs, collect.UserList)
        self.assertIsInstance(self.Eggs, egg_mass.Eggs)

        self.assertEqual(self.Eggs.mass, self.mass)

        self.assertEqual(self.Eggs,      self.eggs)
        self.assertEqual(self.Eggs.data, self.eggs)

    def test_activate(self):
        """test activate the eggs"""

        self.Eggs.activate()

        for egg in self.eggs:
            self.assertEqual(egg.activate.call_args_list,
                             [mk.call()])

    def test_deactivate(self):
        """test deactivate the eggs"""

        self.Eggs.deactivate()

        for egg in self.eggs:
            self.assertEqual(egg.deactivate.call_args_list,
                             [mk.call()])

    def test_cannibalize(self):
        """test cannibalize the number of eggs"""

        with mk.patch.object(rnd, 'shuffle') as mkRND:
            for number in range(len(self.eggs)):
                self.Eggs.cannibalize(number)
                self.assertEqual(mkRND.call_args_list,
                                 [mk.call(self.Eggs)])
                mkRND.reset_mock()

                for index in range(number):
                    self.assertEqual(self.eggs[index].die.call_args_list,
                                     [mk.call(keyword.cannibalism)])
                    self.eggs[index].reset_mock()
                for egg in self.eggs:
                    self.assertEqual(egg.die.call_args_list, [])
                    
    def test_initialize(self):
        """test initialize a collection of eggs"""

        survive = mk.create_autospec(survival.Egg,    spec_set=True)
        develop = mk.create_autospec(development.Egg, spec_set=True)

        loc = mk.create_autospec(location.Location, spec_set=True)
        sim = mk.create_autospec(SimulationTest,    spec_set=True)

        sim.behaviors = mk.create_autospec(BehaviorsTest,
                                           spec_set=True)
        sim.behaviors.survive_egg = survive
        sim.behaviors.develop_egg = develop

        mass = mk.create_autospec(EggMassTest, spec_set=True)
        mass.simulation = sim
        mass.location   = loc

        genotypes = [mk.MagicMock(spec=str) for _ in range(3)]

        self.Eggs = egg_mass.Eggs.initialize(mass,
                                             genotypes,
                                             self.mass)
        self.assertIsInstance(self.Eggs, collect.UserList)
        self.assertIsInstance(self.Eggs, egg_mass.Eggs)
        self.assertEqual(self.Eggs.mass, self.mass)

        for index, egg in enumerate(self.Eggs):
            self.assertIsInstance(egg, agent_egg.Egg)

            self.assertEqual(egg.agent_key, keyword.egg)
            self.assertEqual(egg.alive, True)
            self.assertEqual(egg.age, 0)
            self.assertEqual(egg.death, keyword.alive)

            self.assertEqual(egg.unique_id,
                             mass.new_unique_id.return_value)
            self.assertEqual(mass.new_unique_id.call_args_list[index],
                             mk.call())
            self.assertEqual(egg.location,
                             loc.copy.return_value)
            self.assertEqual(loc.copy.call_args_list,
                             mk.call())

            self.assertEqual(egg.simulation, sim)

            self.assertEqual(egg.mass,    self.mass)
            self.assertEqual(egg.genotype, genotypes[index])

            self.assertEqual(egg.egg_mass,    mass)
            self.assertEqual(egg.survival,    survive)
            self.assertEqual(egg.development, develop)

            # noinspection PyTypeChecker
            self.assertIsInstance(egg._age_count, i_tools.count)
            # noinspection PyTypeChecker
            self.assertEqual(next(egg._age_count), next(i_tools.count(1)))

            self.assertTrue(dclass.is_dataclass(egg))
        self.assertEqual(len(self.Eggs), 3)
        self.assertEqual(len(mass.new_unique_id.call_args_list), 3)
        self.assertEqual(len(loc.copy.call_args_list), 3)


class TestEggMass(ut.TestCase):
    """test the EggMass agent class"""

    def setUp(self):
        """Setup the tests"""

        self.agent_key = mk.MagicMock(spec=str)
        self.unique_id = mk.MagicMock(spec=str)
        self.alive     = mk.MagicMock(spec=bool)

        self.simulation = mk.create_autospec(SimulationTest,    spec_set=True)
        self.location   = mk.create_autospec(location.Location, spec_set=True)

        self.eggs = mk.create_autospec(EggsTest, spec_set=True)

        self.EggMass = egg_mass.EggMass(self.agent_key,
                                        self.unique_id,
                                        self.simulation,
                                        self.location,
                                        self.alive,
                                        self.eggs)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.EggMass, agent.Agent)
        self.assertIsInstance(self.EggMass, egg_mass.EggMass)

        self.assertEqual(self.EggMass.agent_key,  self.agent_key)
        self.assertEqual(self.EggMass.unique_id,  self.unique_id)
        self.assertEqual(self.EggMass.simulation, self.simulation)
        self.assertEqual(self.EggMass.location,   self.location)
        self.assertEqual(self.EggMass.alive,      self.alive)

        # noinspection PyTypeChecker
        self.assertIsInstance(self.EggMass._id_count, i_tools.count)
        # noinspection PyTypeChecker
        self.assertEqual(next(self.EggMass._id_count), next(i_tools.count()))

        self.assertTrue(dclass.is_dataclass(self.EggMass))
        
    def test_active(self):
        """test if the egg_mass is active"""

        with mk.patch.object(egg_mass, 'len') as mkLen:
            mkLen.return_value.__gt__.side_effect = [False, True, True]

            # Len is False
            self.assertFalse(self.EggMass.active)
            self.assertEqual(mkLen.return_value.__gt__.call_args_list,
                             [mk.call(0)])
            self.assertEqual(mkLen.call_args_list,
                             [mk.call(self.eggs)])

            mkLen.reset_mock()
            # Len is True, alive is False
            self.EggMass.alive = False
            self.assertFalse(self.EggMass.active)
            self.assertEqual(mkLen.return_value.__gt__.call_args_list,
                             [mk.call(0)])
            self.assertEqual(mkLen.call_args_list,
                             [mk.call(self.eggs)])

            mkLen.reset_mock()
            # Len is True, alive is True
            self.EggMass.alive = True
            self.assertTrue(self.EggMass.active)
            self.assertEqual(mkLen.return_value.__gt__.call_args_list,
                             [mk.call(0)])
            self.assertEqual(mkLen.call_args_list,
                             [mk.call(self.eggs)])

    def test_inactive(self):
        """test if egg_mass is inactive"""

        with mk.patch.object(egg_mass, 'len') as mkLen:
            mkLen.return_value.__le__.side_effect = [False, True, True]

            # Len is False
            self.assertFalse(self.EggMass.inactive)
            self.assertEqual(mkLen.return_value.__le__.call_args_list,
                             [mk.call(0)])
            self.assertEqual(mkLen.call_args_list,
                             [mk.call(self.eggs)])

            mkLen.reset_mock()
            # Len is True, alive is False
            self.EggMass.alive = False
            self.assertFalse(self.EggMass.inactive)
            self.assertEqual(mkLen.return_value.__le__.call_args_list,
                             [mk.call(0)])
            self.assertEqual(mkLen.call_args_list,
                             [mk.call(self.eggs)])

            mkLen.reset_mock()
            # Len is True, alive is True
            self.EggMass.alive = True
            self.assertTrue(self.EggMass.inactive)
            self.assertEqual(mkLen.return_value.__le__.call_args_list,
                             [mk.call(0)])
            self.assertEqual(mkLen.call_args_list,
                             [mk.call(self.eggs)])

    def test_activate(self):
        """test activate the egg_mass"""

        with mk.patch.object(agent.Agent, 'activate',
                             autospec=True) as mkActivate:
            self.EggMass.activate()
            self.assertEqual(mkActivate.call_args_list,
                             [mk.call(self.EggMass)])
            self.assertEqual(self.eggs.activate.call_args_list,
                             [mk.call()])

    def test_deactivate(self):
        """test deactivate the egg_mass"""

        with mk.patch.object(agent.Agent, 'deactivate',
                             autospec=True) as mkDeactivate:
            self.EggMass.deactivate()
            self.assertEqual(mkDeactivate.call_args_list,
                             [mk.call(self.EggMass)])
            self.assertEqual(self.eggs.deactivate.call_args_list,
                             [mk.call()])

    def test__feed_number(self):
        """test get the number of eggs to feed on"""

        amount = mk.MagicMock(spec=float)

        ceil  = mk.MagicMock(spec=int)
        floor = mk.MagicMock(spec=int)

        ceil. __le__.side_effect = [True, False, False]
        floor.__le__.side_effect = [      True,  False]

        with mk.patch.object(np, 'ceil') as mkCeil:
            with mk.patch.object(np, 'floor') as mkFloor:
                with mk.patch.object(egg_mass, 'len') as mkLen:
                    with mk.patch.object(egg_mass, 'int') as mkInt:
                        # Test get ceil
                        mkInt.side_effect = [ceil, floor]
                        self.assertEqual(self.EggMass._feed_number(amount),
                                         ceil)
                        self.assertEqual(mkInt.call_args_list,
                                         [mk.call(mkCeil.return_value),
                                          mk.call(mkFloor.return_value)])
                        self.assertEqual(mkCeil.call_args_list,
                                         [mk.call(amount.
                                                  __truediv__.return_value)])
                        self.assertEqual(mkFloor.call_args_list,
                                         [mk.call(amount.
                                                  __truediv__.return_value)])
                        self.assertEqual(amount.__truediv__.call_args_list,
                                         [mk.call(self.eggs.mass)])
                        self.assertEqual(ceil.__le__.call_args_list,
                                         [mk.call(mkLen.return_value)])
                        self.assertEqual(floor.__le__.call_args_list, [])
                        self.assertEqual(mkLen.call_args_list,
                                         [mk.call(self.eggs)])

                        mkInt.reset_mock()
                        mkLen.reset_mock()
                        mkCeil.reset_mock()
                        mkFloor.reset_mock()
                        ceil.reset_mock()
                        amount.reset_mock()
                        # Test get floor
                        mkInt.side_effect = [ceil, floor]
                        self.assertEqual(self.EggMass._feed_number(amount),
                                         floor)
                        self.assertEqual(mkInt.call_args_list,
                                         [mk.call(mkCeil.return_value),
                                          mk.call(mkFloor.return_value)])
                        self.assertEqual(mkCeil.call_args_list,
                                         [mk.call(amount.
                                                  __truediv__.return_value)])
                        self.assertEqual(mkFloor.call_args_list,
                                         [mk.call(amount.
                                                  __truediv__.return_value)])
                        self.assertEqual(amount.__truediv__.call_args_list,
                                         [mk.call(self.eggs.mass)])
                        self.assertEqual(ceil.__le__.call_args_list,
                                         [mk.call(mkLen.return_value)])
                        self.assertEqual(floor.__le__.call_args_list,
                                         [mk.call(mkLen.return_value)])
                        self.assertEqual(mkLen.call_args_list,
                                         [mk.call(self.eggs)])

                        mkInt.reset_mock()
                        mkLen.reset_mock()
                        mkCeil.reset_mock()
                        mkFloor.reset_mock()
                        ceil.reset_mock()
                        floor.reset_mock()
                        amount.reset_mock()
                        # Test get floor
                        mkInt.side_effect = [ceil, floor]
                        with self.assertRaisesRegex(RuntimeError,
                                                    'Tried to consume too much '
                                                    'egg'):
                            self.EggMass._feed_number(amount)
                        self.assertEqual(mkInt.call_args_list,
                                         [mk.call(mkCeil.return_value),
                                          mk.call(mkFloor.return_value)])
                        self.assertEqual(mkCeil.call_args_list,
                                         [mk.call(amount.
                                                  __truediv__.return_value)])
                        self.assertEqual(mkFloor.call_args_list,
                                         [mk.call(amount.
                                                  __truediv__.return_value)])
                        self.assertEqual(amount.__truediv__.call_args_list,
                                         [mk.call(self.eggs.mass)])
                        self.assertEqual(ceil.__le__.call_args_list,
                                         [mk.call(mkLen.return_value)])
                        self.assertEqual(floor.__le__.call_args_list,
                                         [mk.call(mkLen.return_value)])
                        self.assertEqual(mkLen.call_args_list,
                                         [mk.call(self.eggs)])
    
    def test_feed(self):
        """test feed on amount of eggs"""

        amount = mk.MagicMock(spec=float)

        with mk.patch.object(egg_mass.EggMass, '_feed_number',
                             autospec=True) as mkFeed:
            with mk.patch.object(egg_mass.EggMass, 'deactivate',
                                 autospec=True) as mkDeactivate:
                with mk.patch.object(egg_mass.EggMass, 'inactive',
                                     autospec=True) as mkInactive:
                    mkInactive.__get__ = mk.MagicMock(side_effect=[False, True])

                    # Test if no deactivate
                    self.EggMass.feed(amount)
                    self.assertEqual(self.eggs.cannibalize.call_args_list,
                                     [mk.call(mkFeed.return_value)])
                    self.assertEqual(mkFeed.call_args_list,
                                     [mk.call(self.EggMass, amount)])
                    self.assertEqual(mkDeactivate.call_args_list, [])

                    mkFeed.reset_mock()
                    self.eggs.reset_mock()
                    # Test if deactivate
                    self.EggMass.feed(amount)
                    self.assertEqual(self.eggs.cannibalize.call_args_list,
                                     [mk.call(mkFeed.return_value)])
                    self.assertEqual(mkFeed.call_args_list,
                                     [mk.call(self.EggMass, amount)])
                    self.assertEqual(mkDeactivate.call_args_list,
                                     [mk.call(self.EggMass)])
                    
    def test_remove(self):
        """test remove an egg from egg_mass"""
        
        egg = mk.create_autospec(EggsTest, spec_set=True)
        
        self.EggMass.remove(egg)
        self.assertEqual(self.eggs.remove.call_args_list,
                         [mk.call(egg)])
        
    def test_new_unique_id(self):
        """test generate a new unique_id"""

        counter = i_tools.count()

        self.assertEqual(self.EggMass.new_unique_id(),
                         str(self.unique_id) + str(next(counter)))
        self.assertEqual(self.EggMass.new_unique_id(),
                         '{}1'.format(self.unique_id))
        self.assertEqual(self.EggMass.new_unique_id(),
                         '{}2'.format(self.unique_id))

    def test__alleles(self):
        """test get the alleles for a genotype"""

        # homo_r
        self.assertEqual(self.EggMass._alleles(keyword.homo_r),
                         keyword.homo_r_alleles)
        self.assertEqual(self.EggMass._alleles(keyword.homo_r),
                         (0, 0))

        # hetero
        self.assertEqual(self.EggMass._alleles(keyword.hetero),
                         keyword.hetero_alleles)
        self.assertEqual(self.EggMass._alleles(keyword.hetero),
                         (0, 1))

        # homo_s
        self.assertEqual(self.EggMass._alleles(keyword.homo_s),
                         keyword.homo_s_alleles)
        self.assertEqual(self.EggMass._alleles(keyword.homo_s),
                         (1, 1))

        # Error
        genotype = mk.MagicMock(spec=str)
        with self.assertRaisesRegex(RuntimeError,
                                    'Invalid genotype_key: '
                                    '{}'.format(genotype)):
            self.EggMass._alleles(genotype)
            
    def test__generate_genotype(self):
        """test genotype from alleles"""

        # Test abstract
        mother_alleles = mk.MagicMock(spec=tuple)
        father_alleles = mk.MagicMock(spec=tuple)

        mother = mk.MagicMock(spec=int)
        father = mk.MagicMock(spec=int)

        mother.__add__.side_effect = [keyword.homo_r_value,
                                      keyword.hetero_value,
                                      keyword.homo_s_value]
        with mk.patch.object(rnd, 'choice') as mkRND:
            mkRND.side_effect = [mother, father,
                                 mother, father,
                                 mother, father]

            # homo_r
            self.assertEqual(self.EggMass._generate_genotype(mother_alleles,
                                                             father_alleles),
                             keyword.homo_r)
            self.assertEqual(mkRND.call_args_list,
                             [mk.call(mother_alleles), mk.call(father_alleles)])
            self.assertEqual(mother.__add__.call_args_list,
                             [mk.call(father)])

            mother.reset_mock()
            mkRND.reset_mock()
            # hetero
            self.assertEqual(self.EggMass._generate_genotype(mother_alleles,
                                                             father_alleles),
                             keyword.hetero)
            self.assertEqual(mkRND.call_args_list,
                             [mk.call(mother_alleles), mk.call(father_alleles)])
            self.assertEqual(mother.__add__.call_args_list,
                             [mk.call(father)])

            mother.reset_mock()
            mkRND.reset_mock()
            # homo_s
            self.assertEqual(self.EggMass._generate_genotype(mother_alleles,
                                                             father_alleles),
                             keyword.homo_s)
            self.assertEqual(mkRND.call_args_list,
                             [mk.call(mother_alleles), mk.call(father_alleles)])
            self.assertEqual(mother.__add__.call_args_list,
                             [mk.call(father)])

        # Test practical
        #       homo_r x homo_r
        self.assertEqual(self.EggMass
                             ._generate_genotype(keyword.homo_r_alleles,
                                                 keyword.homo_r_alleles),
                         keyword.homo_r)
        #       homo_r x homo_s
        self.assertEqual(self.EggMass
                         ._generate_genotype(keyword.homo_r_alleles,
                                             keyword.homo_s_alleles),
                         keyword.hetero)
        #       homo_s x homo_r
        self.assertEqual(self.EggMass
                         ._generate_genotype(keyword.homo_s_alleles,
                                             keyword.homo_r_alleles),
                         keyword.hetero)
        #       homo_s x homo_s
        self.assertEqual(self.EggMass
                         ._generate_genotype(keyword.homo_s_alleles,
                                             keyword.homo_s_alleles),
                         keyword.homo_s)
    
    def test_genotypes(self):
        """test generate genotypes"""

        mother = mk.MagicMock(spec=str)
        father = mk.MagicMock(spec=str)

        mother_alleles = mk.MagicMock(spec=tuple)
        father_alleles = mk.MagicMock(spec=tuple)

        genotypes = []
        for _ in range(3):
            genotypes.append(mk.MagicMock(spec=str))

        with mk.patch.object(egg_mass.EggMass, '_generate_genotype',
                             autospec=True) as mkGenerate:
            with mk.patch.object(egg_mass.EggMass, '_alleles',
                                 autospec=True) as mkAlleles:
                mkGenerate.side_effect = genotypes
                mkAlleles. side_effect = [mother_alleles, father_alleles]

                self.assertEqual(self.EggMass.genotypes(3, mother, father),
                                 genotypes)
                for call in mkGenerate.call_args_list:
                    self.assertEqual(call,
                                     mk.call(mother_alleles, father_alleles))
                self.assertEqual(len(mkGenerate.call_args_list), 3)
                self.assertEqual(mkAlleles.call_args_list,
                                 [mk.call(mother), mk.call(father)])
                
    def test_empty(self):
        """test initialize egg_mass without eggs"""

        self.EggMass = egg_mass.EggMass.empty(self.unique_id,
                                              self.simulation,
                                              self.location)

        self.assertIsInstance(self.EggMass, agent.Agent)
        self.assertIsInstance(self.EggMass, egg_mass.EggMass)

        self.assertEqual(self.EggMass.agent_key, keyword.egg_mass)
        self.assertEqual(self.EggMass.alive,     True)

        self.assertEqual(self.EggMass.unique_id,  self.unique_id)
        self.assertEqual(self.EggMass.simulation, self.simulation)
        self.assertEqual(self.EggMass.location,   self.location)

        self.assertIsInstance(self.EggMass.eggs, egg_mass.Eggs)
        self.assertEqual(self.EggMass.eggs,      [])
        self.assertEqual(self.EggMass.eggs.mass, -1)

        # noinspection PyTypeChecker
        self.assertIsInstance(self.EggMass._id_count, i_tools.count)
        # noinspection PyTypeChecker
        self.assertEqual(next(self.EggMass._id_count), next(i_tools.count()))

        self.assertTrue(dclass.is_dataclass(self.EggMass))

    def test_initialize(self):
        """test initialize the egg_mass"""

        survive = mk.create_autospec(survival.Egg,    spec_set=True)
        develop = mk.create_autospec(development.Egg, spec_set=True)
        self.simulation.behaviors = mk.create_autospec(BehaviorsTest,
                                                       spec_set=True)
        self.simulation.behaviors.survive_egg = survive
        self.simulation.behaviors.develop_egg = develop
        self.simulation.models = mk.create_autospec(models.Models,
                                                    spec_set=True)

        number    = mk.MagicMock(spec=int)
        mass      = mk.MagicMock(spec=float)
        genotypes = [mk.MagicMock(spec=str) for _ in range(3)]
        locations = [mk.create_autospec(location.Location, spec_set=True)
                     for _ in range(3)]

        self.simulation.models.\
            __getitem__.return_value.side_effect = [number, mass]
        self.location.copy.side_effect = locations

        mother = mk.MagicMock(spec=str)
        father = mk.MagicMock(spec=str)

        with mk.patch.object(egg_mass.EggMass, 'genotypes',
                             autospec=True) as mkGenotypes:
            mkGenotypes.return_value = genotypes

            self.EggMass = egg_mass.EggMass.initialize(self.unique_id,
                                                       self.simulation,
                                                       self.location,
                                                       mother, father)
            self.assertEqual(self.EggMass.agent_key, keyword.egg_mass)
            self.assertEqual(self.EggMass.alive,     True)

            self.assertEqual(self.EggMass.unique_id,  self.unique_id)
            self.assertEqual(self.EggMass.simulation, self.simulation)
            self.assertEqual(self.EggMass.location,   self.location)

            self.assertIsInstance(self.EggMass.eggs, egg_mass.Eggs)
            self.assertEqual(self.EggMass.eggs.mass, mass)

            for index, egg in enumerate(self.EggMass.eggs):
                self.assertIsInstance(egg, agent_egg.Egg)

                self.assertEqual(egg.agent_key, keyword.egg)
                self.assertEqual(egg.alive, True)
                self.assertEqual(egg.age, 0)
                self.assertEqual(egg.death, keyword.alive)

                self.assertEqual(egg.unique_id,
                                 str(self.unique_id) + str(index))
                self.assertEqual(egg.location, locations[index])

                self.assertEqual(egg.simulation, self.simulation)

                self.assertEqual(egg.mass,     mass)
                self.assertEqual(egg.genotype, genotypes[index])

                self.assertEqual(egg.egg_mass,    self.EggMass)
                self.assertEqual(egg.survival,    survive)
                self.assertEqual(egg.development, develop)
            self.assertEqual(len(self.EggMass.eggs), 3)

            self.assertEqual(self.simulation.models.
                                __getitem__.return_value.call_args_list,
                             [mk.call(mother),
                              mk.call(number, mother)])
            self.assertEqual(self.simulation.models.
                                 __getitem__.call_args_list,
                             [mk.call(keyword.init_num),
                              mk.call(keyword.init_mass)])
            self.assertEqual(mkGenotypes.call_args_list,
                             [mk.call(self.EggMass, number, mother, father)])

    def test_setup(self):
        """test setup an initial egg_mass"""

        survive = mk.create_autospec(survival.Egg,    spec_set=True)
        develop = mk.create_autospec(development.Egg, spec_set=True)
        self.simulation.behaviors = mk.create_autospec(BehaviorsTest,
                                                       spec_set=True)
        self.simulation.behaviors.survive_egg = survive
        self.simulation.behaviors.develop_egg = develop
        self.simulation.space  = mk.create_autospec(space.Space, spec_set=True)
        self.simulation.models = mk.create_autospec(models.Models,
                                                    spec_set=True)

        self.simulation.space.new_location.return_value = self.location

        mass      = mk.MagicMock(spec=float)
        locations = [mk.create_autospec(location.Location, spec_set=True)
                     for _ in range(3)]

        unique_id_num = mk.MagicMock(spec=int)
        initial_key   = mk.MagicMock(spec=str)

        parents = [[keyword.homo_r, keyword.homo_r],
                   [keyword.homo_r, keyword.homo_s],
                   [keyword.homo_s, keyword.homo_s]]

        with mk.patch.object(rnd, 'shuffle'):
            for index_i, genotype in enumerate(keyword.genotype_keys):
                self.simulation.models.\
                    __getitem__.return_value.side_effect = [3, mass]
                self.location.copy.side_effect = locations

                self.EggMass = egg_mass.EggMass.setup(unique_id_num,
                                                      initial_key,
                                                      self.simulation,
                                                      genotype)
                self.assertEqual(self.EggMass.agent_key, keyword.egg_mass)
                self.assertEqual(self.EggMass.alive,     True)

                self.assertEqual(self.EggMass.unique_id,
                                 str(initial_key) + str(unique_id_num)
                                                  + keyword.egg_mass)
                self.assertEqual(self.EggMass.location,   self.location)
                self.assertEqual(self.simulation.space.
                                 new_location.call_args_list,
                                 [mk.call(keyword.egg_depth)])

                self.assertEqual(self.EggMass.simulation, self.simulation)

                self.assertIsInstance(self.EggMass.eggs, egg_mass.Eggs)
                self.assertEqual(self.EggMass.eggs.mass, mass)

                for index_j, egg in enumerate(self.EggMass.eggs):
                    self.assertIsInstance(egg, agent_egg.Egg)

                    self.assertEqual(egg.agent_key, keyword.egg)
                    self.assertEqual(egg.alive, True)
                    self.assertEqual(egg.age, 0)
                    self.assertEqual(egg.death, keyword.alive)

                    self.assertEqual(egg.unique_id,
                                     self.EggMass.unique_id + str(index_j))
                    self.assertEqual(egg.location, locations[index_j])

                    self.assertEqual(egg.simulation, self.simulation)

                    self.assertEqual(egg.mass,     mass)
                    self.assertEqual(egg.genotype, genotype)

                    self.assertEqual(egg.egg_mass,    self.EggMass)
                    self.assertEqual(egg.survival,    survive)
                    self.assertEqual(egg.development, develop)
                self.assertEqual(len(self.EggMass.eggs), 3)

                self.assertEqual(self.simulation.models.
                                 __getitem__.return_value.call_args_list,
                                 [mk.call(   parents[index_i][0]),
                                  mk.call(3, parents[index_i][0])])
                self.assertEqual(self.simulation.models.
                                 __getitem__.call_args_list,
                                 [mk.call(keyword.init_num),
                                  mk.call(keyword.init_mass)])

                self.simulation.space.reset_mock()
                self.simulation.models.reset_mock()

    def test_birth(self):
        """test birth a new egg_mass"""

        survive = mk.create_autospec(survival.Egg,    spec_set=True)
        develop = mk.create_autospec(development.Egg, spec_set=True)
        self.simulation.behaviors = mk.create_autospec(BehaviorsTest,
                                                       spec_set=True)
        self.simulation.behaviors.survive_egg = survive
        self.simulation.behaviors.develop_egg = develop
        self.simulation.models = mk.create_autospec(models.Models,
                                                    spec_set=True)

        number    = mk.MagicMock(spec=int)
        mass      = mk.MagicMock(spec=float)
        genotypes = [mk.MagicMock(spec=str) for _ in range(3)]
        locations = [mk.create_autospec(location.Location, spec_set=True)
                     for _ in range(3)]

        self.simulation.models. \
            __getitem__.return_value.side_effect = [number, mass]
        self.location.copy.side_effect = locations

        adult = mk.create_autospec(AdultTest, spec_set=True)
        adult.simulation = self.simulation

        adult.new_unique_id.return_value    = self.unique_id
        adult.new_egg_location.return_value = self.location

        with mk.patch.object(egg_mass.EggMass, 'genotypes',
                             autospec=True) as mkGenotypes:
            mkGenotypes.return_value = genotypes

            self.EggMass = egg_mass.EggMass.birth(adult)
            self.assertEqual(self.EggMass.agent_key, keyword.egg_mass)
            self.assertEqual(self.EggMass.alive,     True)

            self.assertEqual(self.EggMass.unique_id,  self.unique_id)
            self.assertEqual(self.EggMass.simulation, self.simulation)
            self.assertEqual(self.EggMass.location,   self.location)

            self.assertIsInstance(self.EggMass.eggs, egg_mass.Eggs)
            self.assertEqual(self.EggMass.eggs.mass, mass)

            for index, egg in enumerate(self.EggMass.eggs):
                self.assertIsInstance(egg, agent_egg.Egg)

                self.assertEqual(egg.agent_key, keyword.egg)
                self.assertEqual(egg.alive, True)
                self.assertEqual(egg.age, 0)
                self.assertEqual(egg.death, keyword.alive)

                self.assertEqual(egg.unique_id,
                                 str(self.unique_id) + str(index))
                self.assertEqual(egg.location, locations[index])

                self.assertEqual(egg.simulation, self.simulation)

                self.assertEqual(egg.mass,     mass)
                self.assertEqual(egg.genotype, genotypes[index])

                self.assertEqual(egg.egg_mass,    self.EggMass)
                self.assertEqual(egg.survival,    survive)
                self.assertEqual(egg.development, develop)
            self.assertEqual(len(self.EggMass.eggs), 3)

            self.assertEqual(self.simulation.models.
                             __getitem__.return_value.call_args_list,
                             [mk.call(adult.genotype),
                              mk.call(number, adult.genotype)])
            self.assertEqual(self.simulation.models.
                             __getitem__.call_args_list,
                             [mk.call(keyword.init_num),
                              mk.call(keyword.init_mass)])
            self.assertEqual(mkGenotypes.call_args_list,
                             [mk.call(self.EggMass, number,
                                      adult.genotype, adult.mate)])
