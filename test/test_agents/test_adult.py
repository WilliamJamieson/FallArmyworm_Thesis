import unittest      as ut
import unittest.mock as mk

import dataclasses as dclass
import itertools   as i_tools

import source.keyword as keyword

import source.agents.agent    as agent
import source.agents.adult    as adult
import source.agents.egg_mass as egg_mass
import source.agents.insect   as insect
import source.agents.larva    as larva
import source.agents.pupa     as agent_pupa

import source.simulation.behaviors  as behaviors
import source.simulation.models     as models
import source.simulation.simulation as simulation

import source.space.agents   as agents
import source.space.location as location
import source.space.space    as space

import source.movement.adult    as movement
import source.reproduction.lay  as lay
import source.reproduction.mate as mate
import source.survival.adult    as survival


class BehaviorsTest(behaviors.Behaviors):
    """Class to add dynamic values for tests"""

    survive_adult = mk.create_autospec(survival.Adult, spec_set=True)
    move_adult    = mk.create_autospec(movement.Adult, spec_set=True)
    lay           = mk.create_autospec(lay.Lay,        spec_set=True)
    mate          = mk.create_autospec(mate.Mate,      spec_set=True)


class SimulationTest(simulation.Simulation):
    """Class to add dynamic values for tests"""

    agents    = mk.create_autospec(agents.Agents, spec_set=True)
    behaviors = mk.create_autospec(BehaviorsTest, spec_set=True)
    space     = mk.create_autospec(space.Space,   spec_set=True)
    models    = mk.create_autospec(models.Models, spec_set=True)


class PupaTest(agent_pupa.Pupa):
    """Class to add dynamic values for tests"""

    unique_id  = mk.MagicMock(spec=str)
    simulation = mk.create_autospec(SimulationTest,    spec_set=True)
    location   = mk.create_autospec(location.Location, spec_set=True)
    mass       = mk.MagicMock(spec=float)
    genotype   = mk.MagicMock(spec=str)


class AdultTest(adult.Adult):
    """Class to add dynamic values for tests"""

    genotype = mk.MagicMock(spec=str)


class TestAdult(ut.TestCase):
    """test base Adult class"""

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

        self.num_eggs = mk.MagicMock(spec=int)
        self.mate     = mk.MagicMock(spec=str)

        self.survival   = mk.create_autospec(survival.Adult, spec_set=True)
        self.movement = mk.create_autospec(movement.Adult,   spec_set=True)
        self.lay      = mk.create_autospec(lay.Lay,          spec_set=True)
        self.mating   = mk.create_autospec(mate.Mate,        spec_set=True)

        self.Adult = adult.Adult(self.agent_key,
                                 self.unique_id,
                                 self.simulation,
                                 self.location,
                                 self.alive,
                                 self.mass,
                                 self.genotype,
                                 self.age,
                                 self.death,
                                 self.num_eggs,
                                 self.mate,
                                 self.survival,
                                 self.movement,
                                 self.lay,
                                 self.mating)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Adult, agent.Agent)
        self.assertIsInstance(self.Adult, insect.Insect)
        self.assertIsInstance(self.Adult, adult.Adult)

        self.assertEqual(self.Adult.agent_key,  self.agent_key)
        self.assertEqual(self.Adult.unique_id,  self.unique_id)
        self.assertEqual(self.Adult.simulation, self.simulation)
        self.assertEqual(self.Adult.location,   self.location)
        self.assertEqual(self.Adult.alive,      self.alive)

        self.assertEqual(self.Adult.mass,     self.mass)
        self.assertEqual(self.Adult.genotype, self.genotype)
        self.assertEqual(self.Adult.age,      self.age)
        self.assertEqual(self.Adult.death,    self.death)

        self.assertEqual(self.Adult.num_eggs, self.num_eggs)
        self.assertEqual(self.Adult.mate,     self.mate)
        self.assertEqual(self.Adult.survival, self.survival)
        self.assertEqual(self.Adult.movement, self.movement)
        self.assertEqual(self.Adult.lay,      self.lay)
        self.assertEqual(self.Adult.mating,   self.mating)

        # noinspection PyTypeChecker
        self.assertIsInstance(self.Adult._age_count, i_tools.count)
        # noinspection PyTypeChecker
        self.assertEqual(next(self.Adult._age_count),
                         next(i_tools.count(self.age + 1)))

        # noinspection PyTypeChecker
        self.assertIsInstance(self.Adult._id_count, i_tools.count)
        # noinspection PyTypeChecker
        self.assertEqual(next(self.Adult._id_count), next(i_tools.count()))

        self.assertTrue(dclass.is_dataclass(self.Adult))

    def test_survive(self):
        """test run survive behavior"""

        self.assertEqual(self.Adult.survive(), [])
        self.assertEqual(self.survival.survive.call_args_list,
                         [mk.call(self.Adult)])

    def test_move(self):
        """test run move behavior"""

        self.assertEqual(self.Adult.move(), [])
        self.assertEqual(self.movement.move.call_args_list,
                         [mk.call(self.Adult)])
        
    def test_new_unique_id(self):
        """test create a new unique_id for an egg_mass"""

        self.assertEqual(self.Adult.new_unique_id(),
                         str(self.unique_id) + '_0' + keyword.egg_mass)
        self.assertEqual(self.Adult.new_unique_id(),
                         str(self.unique_id) + '_1' + keyword.egg_mass)
        self.assertEqual(self.Adult.new_unique_id(),
                         str(self.unique_id) + '_2' + keyword.egg_mass)
        
    def test_new_egg_location(self):
        """test create a new egg_location"""

        self.simulation.space = mk.create_autospec(space.Space, spec_set=True)

        self.assertGreater(keyword.egg_depth - keyword.adult_depth, 0)
        repeat = keyword.egg_depth - keyword.adult_depth

        self.assertEqual(self.Adult.new_egg_location(),
                         self.simulation.space.extend_location.return_value)
        self.assertEqual(len(self.simulation.space.
                             extend_location.call_args_list), repeat)
        call = self.simulation.space.extend_location.call_args_list.pop(0)
        self.assertEqual(call,
                         mk.call(self.location))
        for call in self.simulation.space.extend_location.call_args_list:
            self.assertEqual(call,
                             mk.call(self.simulation.space.
                                     extend_location.return_value))
        self.assertEqual(len(self.simulation.space.
                             extend_location.call_args_list),
                         repeat - 1)

    def test_population(self):
        """test get the population of the plant"""

        self.simulation.agents = \
            mk.create_autospec(agents.Agents, spec_set=True)
        self.simulation.agents.__getitem__.return_value = \
            mk.create_autospec(agents.AgentsBin, spec_set=True)

        egg_bin = mk.create_autospec(agents.AgentBin, spec_set=True)
        larva_bin = mk.create_autospec(agents.AgentBin, spec_set=True)

        eggs   = [mk.create_autospec(egg_mass.EggMass, spec_set=True)
                  for _ in range(3)]
        larvae = [mk.create_autospec(larva.Larva, spec_set=True)
                  for _ in range(3)]
        egg_bin.  agents = eggs
        larva_bin.agents = larvae
        self.simulation.agents.__getitem__.return_value.\
            __getitem__.side_effect = [egg_bin, larva_bin,
                                       egg_bin, larva_bin]
        # Test calls
        with mk.patch.object(adult, 'len') as mkLen:
            self.assertEqual(self.Adult.population(),
                             mkLen.return_value.__add__.return_value)
            self.assertEqual(mkLen.return_value.__add__.call_args_list,
                             [mk.call(mkLen.return_value)])
            self.assertEqual(mkLen.call_args_list,
                             [mk.call(eggs), mk.call(larvae)])
            self.assertEqual(self.simulation.agents.__getitem__.return_value.
                                __getitem__.call_args_list,
                             [mk.call(keyword.egg_mass),
                              mk.call(keyword.larva)])
            self.assertEqual(self.simulation.agents.__getitem__.call_args_list,
                             [mk.call(self.location.location_key)])

        # Test practical
        self.assertEqual(self.Adult.population(), 6)

    def test_set_mate(self):
        """test set a mate"""

        self.simulation.models = \
            mk.create_autospec(models.Models, spec_set=True)

        self.simulation.models.__getitem__.side_effect = [False, False,
                                                          False, True,
                                                          True]

        this = mk.create_autospec(AdultTest, spec_set=True)

        with mk.patch.object(adult.Adult, 'deactivate',
                             autospec=True) as mkDeactivate:
            with mk.patch.object(adult.Adult, 'transition',
                                 autospec=True) as mkTransition:
                # Not male
                self.Adult.set_mate(this)
                self.assertEqual(self.Adult.mate, this.genotype)
                self.assertEqual(mkDeactivate.call_args_list, [])
                self.assertEqual(mkTransition.call_args_list, [])
                self.assertEqual(self.simulation.models.
                                    __getitem__.call_args_list, [])

                self.Adult.mate = self.mate
                # Is Male
                self.Adult.agent_key = keyword.male
                #   Unlimited male mating
                self.Adult.set_mate(this)
                self.assertEqual(self.Adult.mate, self.mate)
                self.assertEqual(mkDeactivate.call_args_list, [])
                self.assertEqual(mkTransition.call_args_list, [])
                self.assertEqual(self.simulation.models.
                                     __getitem__.call_args_list,
                                 [mk.call(keyword.lifetime_male),
                                  mk.call(keyword.limited)])
                self.simulation.models.reset_mock()
                #   Limited male mating
                self.Adult.set_mate(this)
                self.assertEqual(self.Adult.mate, self.mate)
                self.assertEqual(mkDeactivate.call_args_list, [])
                self.assertEqual(mkTransition.call_args_list,
                                 [mk.call(self.Adult, keyword.mated)])
                self.assertEqual(self.simulation.models.
                                     __getitem__.call_args_list,
                                 [mk.call(keyword.lifetime_male),
                                  mk.call(keyword.limited)])
                self.simulation.models.reset_mock()
                mkTransition.reset_mock()
                #   Lifetime male mating
                self.Adult.set_mate(this)
                self.assertEqual(self.Adult.mate, self.mate)
                self.assertEqual(mkDeactivate.call_args_list,
                                 [mk.call(self.Adult)])
                self.assertEqual(mkTransition.call_args_list, [])
                self.assertEqual(self.simulation.models.
                                 __getitem__.call_args_list,
                                 [mk.call(keyword.lifetime_male)])

    def test__location_keys(self):
        """test get the location keys for reproduction"""

        kwargs = {'test': mk.MagicMock()}

        vertices = {mk.MagicMock(spec=int) for _ in range(3)}

        locs          = []
        location_keys = []
        for _ in vertices:
            loc = mk.create_autospec(location.Location, spec_set=True)
            location_keys.append(loc.location_key)
            locs.append(loc)

        self.location.copy.side_effect = locs

        with mk.patch.object(adult.Adult, 'vertices',
                             autospec=True) as mkVertices:
            mkVertices.return_value = vertices

            self.assertEqual(self.Adult._location_keys(**kwargs), location_keys)
            self.assertEqual(mkVertices.call_args_list,
                             [mk.call(self.Adult, **kwargs)])
            for index, vertex in enumerate(vertices):
                self.assertEqual(locs[index].__setitem__.call_args_list,
                                 [mk.call(keyword.adult_level, vertex)])
                self.assertEqual(self.location.copy.call_args_list[index],
                                 [mk.call()])
            self.assertEqual(len(self.location.copy.call_args_list), 3)

    def test_mates(self):
        """test get the mates"""

        kwargs = {'test': mk.MagicMock()}

        self.simulation.agents = mk.create_autospec(agents.Agents,
                                                    spec_set=True)

        location_keys = []
        agents_bins   = []
        mates         = []
        for _ in range(3):
            location_key = mk.MagicMock(spec=tuple)
            agents_bin   = mk.create_autospec(agents.AgentsBin, spec_set=True)
            male_bin     = mk.create_autospec(agents.AgentBin, spec_set=True)
            adults       = []
            for _ in range(3):
                adults.append(mk.create_autospec(adult.Adult, spec_set=True))
            male_bin.agents = adults
            mates.extend(adults)

            location_keys.append(location_key)
            agents_bin.__getitem__.return_value = male_bin
            agents_bins.append(agents_bin)

        self.simulation.agents.__getitem__.side_effect = agents_bins

        with mk.patch.object(adult.Adult, '_location_keys',
                             autospec=True) as mkKeys:
            mkKeys.return_value = location_keys

            new = self.Adult.mates(**kwargs)
            self.assertEqual(mates, new)

            self.assertEqual(mkKeys.call_args_list,
                             [mk.call(self.Adult, **kwargs)])
            for index, call in enumerate(self.simulation.agents.
                                                 __getitem__.call_args_list):
                self.assertEqual(call,
                                 mk.call(location_keys[index]))
            self.assertEqual(len(self.simulation.agents.
                                 __getitem__.call_args_list), 3)
            for index, agent_bin in enumerate(agents_bins):
                self.assertEqual(agent_bin.__getitem__.call_args_list,
                                 [mk.call(keyword.male)])

    def test_reproduce(self):
        """test reproduce the agents"""

        # Test has a mate
        self.assertEqual(self.Adult.reproduce(),
                         self.lay.lay.return_value)
        self.assertEqual(self.lay.lay.call_args_list,
                         [mk.call(self.Adult)])
        self.assertEqual(self.mating.mate.call_args_list, [])

        # Test no mate
        self.lay.reset_mock()
        self.Adult.mate = None
        self.assertEqual(self.Adult.reproduce(), [])
        self.assertEqual(self.mating.mate.call_args_list,
                         [mk.call(self.Adult)])
        self.assertEqual(self.lay.lay.call_args_list, [])

    def test_reset(self):
        """test reset the mock"""

        self.simulation.models = \
            mk.create_autospec(models.Models, spec_set=True)

        self.simulation.models.__getitem__.side_effect = [True, False]

        with mk.patch.object(adult.Adult, 'transition',
                             autospec=True) as mkTransition:
            # Not female or mated
            self.assertEqual(self.Adult.reset(), [])
            self.assertEqual(self.Adult.mate, self.mate)
            self.assertEqual(self.Adult.num_eggs, self.num_eggs)
            self.assertEqual(self.lay.reset.call_args_list, [])
            self.assertEqual(mkTransition.call_args_list, [])
            self.assertEqual(self.simulation.models.
                                 __getitem__.call_args_list, [])

            # Is female
            self.Adult.agent_key = keyword.female
            #       Female lifetime mate
            self.assertEqual(self.Adult.reset(), [])
            self.assertEqual(self.Adult.mate, self.mate)
            self.assertEqual(self.Adult.num_eggs,
                             self.lay.reset.return_value)
            self.assertEqual(self.lay.reset.call_args_list,
                             [mk.call(self.Adult)])
            self.assertEqual(mkTransition.call_args_list, [])
            self.assertEqual(self.simulation.models.
                                 __getitem__.call_args_list,
                             [mk.call(keyword.lifetime_female)])
            #       Not female lifetime mate
            self.Adult.num_eggs = self.num_eggs
            self.simulation.models.reset_mock()
            self.lay.reset_mock()
            self.assertEqual(self.Adult.reset(), [])
            self.assertEqual(self.Adult.mate, None)
            self.assertEqual(self.Adult.num_eggs,
                             self.lay.reset.return_value)
            self.assertEqual(self.lay.reset.call_args_list,
                             [mk.call(self.Adult)])
            self.assertEqual(mkTransition.call_args_list, [])
            self.assertEqual(self.simulation.models.
                                 __getitem__.call_args_list,
                             [mk.call(keyword.lifetime_female)])

            self.Adult.num_eggs = self.num_eggs
            self.Adult.mate     = self.mate
            self.simulation.models.reset_mock()
            self.lay.reset_mock()
            # Is mated
            self.Adult.agent_key = keyword.mated
            self.assertEqual(self.Adult.reset(), [])
            self.assertEqual(self.Adult.mate, self.mate)
            self.assertEqual(self.Adult.num_eggs, self.num_eggs)
            self.assertEqual(self.lay.reset.call_args_list, [])
            self.assertEqual(mkTransition.call_args_list,
                             [mk.call(self.Adult, keyword.male)])
            self.assertEqual(self.simulation.models.
                                 __getitem__.call_args_list, [])

    def test__set_sex(self):
        """test get the sex of the adult"""

        self.simulation.models = mk.create_autospec(models.Models,
                                                    spec_set=True)
        self.simulation.models.__getitem__.return_value.side_effect = [True,
                                                                       False]

        # With mate
        self.Adult._set_sex()
        self.assertEqual(self.Adult.agent_key, keyword.female)
        self.assertEqual(self.Adult.num_eggs,
                         self.lay.reset.return_value)
        self.assertEqual(self.lay.reset.call_args_list,
                         [mk.call(self.Adult)])
        self.assertEqual(self.simulation.models.__getitem__.call_args_list, [])
        self.lay.reset_mock()
        self.Adult.num_eggs = self.num_eggs

        # No mate
        self.Adult.mate = None
        #       Set female
        self.Adult._set_sex()
        self.assertEqual(self.Adult.agent_key, keyword.female)
        self.assertEqual(self.Adult.num_eggs,  self.num_eggs)
        self.assertEqual(self.simulation.models.
                             __getitem__.return_value.call_args_list,
                         [mk.call(self.genotype)])
        self.assertEqual(self.simulation.models.__getitem__.call_args_list,
                         [mk.call(keyword.init_sex)])
        self.assertEqual(self.lay.reset.call_args_list, [])
        self.simulation.models.reset_mock()
        #       Set male
        self.Adult._set_sex()
        self.assertEqual(self.Adult.agent_key, keyword.male)
        self.assertEqual(self.Adult.num_eggs,  self.num_eggs)
        self.assertEqual(self.simulation.models.
                             __getitem__.return_value.call_args_list,
                         [mk.call(self.genotype)])
        self.assertEqual(self.simulation.models.__getitem__.call_args_list,
                         [mk.call(keyword.init_sex)])
        self.assertEqual(self.lay.reset.call_args_list, [])

    def test_initialize(self):
        """test initialize the agent"""

        self.simulation.behaviors = mk.create_autospec(BehaviorsTest,
                                                       spec_set=True)
        self.simulation.behaviors.survive_adult = self.survival
        self.simulation.behaviors.move_adult    = self.movement
        self.simulation.behaviors.lay           = self.lay
        self.simulation.behaviors.mate          = self.mating

        with mk.patch.object(adult.Adult, '_set_sex', autospec=True) as mkSex:
            # Test regular
            self.Adult = adult.Adult.initialize(self.unique_id,
                                                self.simulation,
                                                self.location,
                                                self.mass,
                                                self.genotype,
                                                self.mate)

            self.assertIsInstance(self.Adult, agent.Agent)
            self.assertIsInstance(self.Adult, insect.Insect)
            self.assertIsInstance(self.Adult, adult.Adult)

            self.assertEqual(self.Adult.agent_key, '')
            self.assertEqual(self.Adult.alive,     True)
            self.assertEqual(self.Adult.age,       0)
            self.assertEqual(self.Adult.death,     keyword.alive)
            self.assertEqual(self.Adult.num_eggs,  0)
            self.assertEqual(mkSex.call_args_list,
                             [mk.call(self.Adult)])

            self.assertEqual(self.Adult.unique_id,  self.unique_id)
            self.assertEqual(self.Adult.simulation, self.simulation)
            self.assertEqual(self.Adult.location,   self.location)

            self.assertEqual(self.Adult.mass,     self.mass)
            self.assertEqual(self.Adult.genotype, self.genotype)

            self.assertEqual(self.Adult.mate,     self.mate)
            self.assertEqual(self.Adult.survival, self.survival)
            self.assertEqual(self.Adult.movement, self.movement)
            self.assertEqual(self.Adult.lay,      self.lay)
            self.assertEqual(self.Adult.mating,   self.mating)

            # noinspection PyTypeChecker
            self.assertIsInstance(self.Adult._age_count, i_tools.count)
            # noinspection PyTypeChecker
            self.assertEqual(next(self.Adult._age_count),
                             next(i_tools.count(1)))

            # noinspection PyTypeChecker
            self.assertIsInstance(self.Adult._id_count, i_tools.count)
            # noinspection PyTypeChecker
            self.assertEqual(next(self.Adult._id_count), next(i_tools.count()))

            self.assertTrue(dclass.is_dataclass(self.Adult))

            mkSex.reset_mock()
            # Test no mate
            self.Adult = adult.Adult.initialize(self.unique_id,
                                                self.simulation,
                                                self.location,
                                                self.mass,
                                                self.genotype)

            self.assertIsInstance(self.Adult, agent.Agent)
            self.assertIsInstance(self.Adult, insect.Insect)
            self.assertIsInstance(self.Adult, adult.Adult)

            self.assertEqual(self.Adult.agent_key, '')
            self.assertEqual(self.Adult.alive,     True)
            self.assertEqual(self.Adult.age,       0)
            self.assertEqual(self.Adult.death,     keyword.alive)
            self.assertEqual(self.Adult.num_eggs,  0)
            self.assertEqual(mkSex.call_args_list,
                             [mk.call(self.Adult)])

            self.assertEqual(self.Adult.unique_id,  self.unique_id)
            self.assertEqual(self.Adult.simulation, self.simulation)
            self.assertEqual(self.Adult.location,   self.location)

            self.assertEqual(self.Adult.mass,     self.mass)
            self.assertEqual(self.Adult.genotype, self.genotype)

            self.assertEqual(self.Adult.mate,     None)
            self.assertEqual(self.Adult.survival, self.survival)
            self.assertEqual(self.Adult.movement, self.movement)
            self.assertEqual(self.Adult.lay,      self.lay)
            self.assertEqual(self.Adult.mating,   self.mating)

            # noinspection PyTypeChecker
            self.assertIsInstance(self.Adult._age_count, i_tools.count)
            # noinspection PyTypeChecker
            self.assertEqual(next(self.Adult._age_count),
                             next(i_tools.count(1)))

            # noinspection PyTypeChecker
            self.assertIsInstance(self.Adult._id_count, i_tools.count)
            # noinspection PyTypeChecker
            self.assertEqual(next(self.Adult._id_count), next(i_tools.count()))

            self.assertTrue(dclass.is_dataclass(self.Adult))

    def test_setup(self):
        """test setup an initial adult"""

        self.simulation.behaviors = mk.create_autospec(BehaviorsTest,
                                                       spec_set=True)
        self.simulation.behaviors.survive_adult = self.survival
        self.simulation.behaviors.move_adult    = self.movement
        self.simulation.behaviors.lay           = self.lay
        self.simulation.behaviors.mate          = self.mating
        self.simulation.space  = mk.create_autospec(space.Space, spec_set=True)
        self.simulation.models = mk.create_autospec(models.Models,
                                                    spec_set=True)

        unique_id_num = mk.MagicMock(spec=int)
        initial_key   = mk.MagicMock(spec=str)

        with mk.patch.object(adult.Adult, '_set_sex', autospec=True) as mkSex:
            # Test regular
            self.Adult = adult.Adult.setup(unique_id_num,
                                           initial_key,
                                           self.simulation,
                                           self.genotype,
                                           self.mate)

            self.assertIsInstance(self.Adult, agent.Agent)
            self.assertIsInstance(self.Adult, insect.Insect)
            self.assertIsInstance(self.Adult, adult.Adult)

            self.assertEqual(self.Adult.unique_id,
                             str(initial_key)   +
                             str(unique_id_num) +
                             keyword.adult)
            self.assertEqual(self.Adult.location,
                             self.simulation.space.new_location.return_value)
            self.assertEqual(self.simulation.space.new_location.call_args_list,
                             [mk.call(keyword.adult_depth)])
            self.assertEqual(self.Adult.mass,
                             self.simulation.models.
                             __getitem__.return_value.return_value)
            self.assertEqual(self.simulation.models.
                             __getitem__.return_value.call_args_list,
                             [mk.call(self.genotype)])
            self.assertEqual(self.simulation.models.
                             __getitem__.call_args_list,
                             [mk.call(keyword.init_mature)])

            self.assertEqual(self.Adult.agent_key, '')
            self.assertEqual(self.Adult.alive,     True)
            self.assertEqual(self.Adult.age,       0)
            self.assertEqual(self.Adult.death,     keyword.alive)
            self.assertEqual(self.Adult.num_eggs,  0)
            self.assertEqual(mkSex.call_args_list,
                             [mk.call(self.Adult)])

            self.assertEqual(self.Adult.simulation, self.simulation)

            self.assertEqual(self.Adult.genotype, self.genotype)

            self.assertEqual(self.Adult.mate,     self.mate)
            self.assertEqual(self.Adult.survival, self.survival)
            self.assertEqual(self.Adult.movement, self.movement)
            self.assertEqual(self.Adult.lay,      self.lay)
            self.assertEqual(self.Adult.mating,   self.mating)

            # noinspection PyTypeChecker
            self.assertIsInstance(self.Adult._age_count, i_tools.count)
            # noinspection PyTypeChecker
            self.assertEqual(next(self.Adult._age_count),
                             next(i_tools.count(1)))

            self.assertTrue(dclass.is_dataclass(self.Adult))

            mkSex.reset_mock()
            self.simulation.space.reset_mock()
            self.simulation.models.reset_mock()
            # Test no mate
            self.Adult = adult.Adult.setup(unique_id_num,
                                           initial_key,
                                           self.simulation,
                                           self.genotype,
                                           self.mate)

            self.assertIsInstance(self.Adult, agent.Agent)
            self.assertIsInstance(self.Adult, insect.Insect)
            self.assertIsInstance(self.Adult, adult.Adult)

            self.assertEqual(self.Adult.unique_id,
                             str(initial_key)   +
                             str(unique_id_num) +
                             keyword.adult)
            self.assertEqual(self.Adult.location,
                             self.simulation.space.new_location.return_value)
            self.assertEqual(self.simulation.space.new_location.call_args_list,
                             [mk.call(keyword.adult_depth)])
            self.assertEqual(self.Adult.mass,
                             self.simulation.models.
                             __getitem__.return_value.return_value)
            self.assertEqual(self.simulation.models.
                             __getitem__.return_value.call_args_list,
                             [mk.call(self.genotype)])
            self.assertEqual(self.simulation.models.
                             __getitem__.call_args_list,
                             [mk.call(keyword.init_mature)])

            self.assertEqual(self.Adult.agent_key, '')
            self.assertEqual(self.Adult.alive,     True)
            self.assertEqual(self.Adult.age,       0)
            self.assertEqual(self.Adult.death,     keyword.alive)
            self.assertEqual(self.Adult.num_eggs,  0)
            self.assertEqual(mkSex.call_args_list,
                             [mk.call(self.Adult)])

            self.assertEqual(self.Adult.simulation, self.simulation)

            self.assertEqual(self.Adult.genotype, self.genotype)

            self.assertEqual(self.Adult.mate,     self.mate)
            self.assertEqual(self.Adult.survival, self.survival)
            self.assertEqual(self.Adult.movement, self.movement)
            self.assertEqual(self.Adult.lay,      self.lay)
            self.assertEqual(self.Adult.mating,   self.mating)

            # noinspection PyTypeChecker
            self.assertIsInstance(self.Adult._age_count, i_tools.count)
            # noinspection PyTypeChecker
            self.assertEqual(next(self.Adult._age_count),
                             next(i_tools.count(1)))

            # noinspection PyTypeChecker
            self.assertIsInstance(self.Adult._id_count, i_tools.count)
            # noinspection PyTypeChecker
            self.assertEqual(next(self.Adult._id_count), next(i_tools.count()))

            self.assertTrue(dclass.is_dataclass(self.Adult))

    def test_advance(self):
        """test advance a pupa into an adult"""

        self.simulation.behaviors = mk.create_autospec(BehaviorsTest,
                                                       spec_set=True)
        self.simulation.behaviors.survive_adult = self.survival
        self.simulation.behaviors.move_adult    = self.movement
        self.simulation.behaviors.lay           = self.lay
        self.simulation.behaviors.mate          = self.mating

        pupa = mk.create_autospec(PupaTest, spec_set=True)
        pupa.unique_id  = self.unique_id
        pupa.simulation = self.simulation
        pupa.location   = self.location
        pupa.mass       = self.mass
        pupa.genotype   = self.genotype

        with mk.patch.object(adult.Adult, '_set_sex', autospec=True) as mkSex:
            self.Adult = adult.Adult.advance(pupa)

            self.assertIsInstance(self.Adult, agent.Agent)
            self.assertIsInstance(self.Adult, insect.Insect)
            self.assertIsInstance(self.Adult, adult.Adult)

            self.assertEqual(self.Adult.agent_key, '')
            self.assertEqual(self.Adult.alive,     True)
            self.assertEqual(self.Adult.age,       0)
            self.assertEqual(self.Adult.death,     keyword.alive)
            self.assertEqual(self.Adult.num_eggs,  0)
            self.assertEqual(mkSex.call_args_list,
                             [mk.call(self.Adult)])

            self.assertEqual(self.Adult.unique_id,  self.unique_id)
            self.assertEqual(self.Adult.simulation, self.simulation)
            self.assertEqual(self.Adult.location,   self.location)

            self.assertEqual(self.Adult.mass,     self.mass)
            self.assertEqual(self.Adult.genotype, self.genotype)

            self.assertEqual(self.Adult.mate,     None)
            self.assertEqual(self.Adult.survival, self.survival)
            self.assertEqual(self.Adult.movement, self.movement)
            self.assertEqual(self.Adult.lay,      self.lay)
            self.assertEqual(self.Adult.mating,   self.mating)

            # noinspection PyTypeChecker
            self.assertIsInstance(self.Adult._age_count, i_tools.count)
            # noinspection PyTypeChecker
            self.assertEqual(next(self.Adult._age_count),
                             next(i_tools.count(1)))

            # noinspection PyTypeChecker
            self.assertIsInstance(self.Adult._id_count, i_tools.count)
            # noinspection PyTypeChecker
            self.assertEqual(next(self.Adult._id_count), next(i_tools.count()))

            self.assertTrue(dclass.is_dataclass(self.Adult))
