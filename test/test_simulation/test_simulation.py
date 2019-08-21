import unittest      as ut
import unittest.mock as mk

import dataclasses  as dclass
import itertools    as i_tools
import numpy.random as rnd

import source.keyword as keyword

import source.schedule.schedule as schedule

import source.agents.adult    as adult
import source.agents.egg_mass as egg_mass
import source.agents.larva    as larva
import source.agents.pupa     as pupa

import source.simulation.behaviors  as behaviors
import source.simulation.models     as models
import source.simulation.simulation as simulation

import source.space.agents as agents
import source.space.space  as space


class TestSimulation(ut.TestCase):
    """test the model Simulation class"""

    def setUp(self):
        """Setup the tests"""

        self.space     = mk.create_autospec(space.Space, spec_set=True)
        self.agents    = mk.create_autospec(agents.Agents, spec_set=True)
        self.schedule  = mk.create_autospec(schedule.Schedule, spec_set=True)
        self.models    = mk.create_autospec(models.Models, spec_set=True)
        self.behaviors = mk.create_autospec(behaviors.Behaviors, spec_set=True)

        self.Simulation = simulation.Simulation(self.space,
                                                self.agents,
                                                self.schedule,
                                                self.models,
                                                self.behaviors)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Simulation, simulation.Simulation)

        self.assertEqual(self.Simulation.space,     self.space)
        self.assertEqual(self.Simulation.agents,    self.agents)
        self.assertEqual(self.Simulation.schedule,  self.schedule)
        self.assertEqual(self.Simulation.models,    self.models)
        self.assertEqual(self.Simulation.behaviors, self.behaviors)

        # noinspection PyTypeChecker
        self.assertIsInstance(self.Simulation._id_count, i_tools.count)
        # noinspection PyTypeChecker
        self.assertEqual(next(self.Simulation._id_count),
                         next(i_tools.count()))

        # noinspection PyTypeChecker
        self.assertIsInstance(self.Simulation._step_count, i_tools.count)
        # noinspection PyTypeChecker
        self.assertEqual(next(self.Simulation._step_count),
                         next(i_tools.count()))

        self.assertTrue(dclass.is_dataclass(self.Simulation))

    def test_count_step(self):
        """test count a step"""

        for index in range(10):
            self.assertEqual(self.Simulation.count_step(), index)

        self.assertEqual(next(self.Simulation._step_count), 10)
        self.assertEqual(next(self.Simulation._id_count), 0)

    def test_new_unique_id(self):
        """test get a new unique_id"""

        for index in range(10):
            self.assertEqual(self.Simulation.new_unique_id(), index)

        self.assertEqual(next(self.Simulation._id_count), 10)
        self.assertEqual(next(self.Simulation._step_count), 0)
        
    def test_populate_egg_masses(self):
        """test generate all new egg_masses"""

        new = mk.create_autospec(egg_mass.EggMass, spec_set=True)

        with mk.patch.object(egg_mass.EggMass, 'setup',
                             autospec=True) as mkSetup:
            with mk.patch.object(simulation.Simulation, 'new_unique_id',
                                 autospec=True) as mkId:
                mkSetup.return_value = new

                self.Simulation.populate_egg_masses((3, 3, 3))

                for index, call in enumerate(mkSetup.call_args_list):
                    self.assertEqual(call,
                                     mk.call(mkId.return_value,
                                             keyword.init,
                                             self.Simulation,
                                             keyword.genotype_keys[index // 3]))
                self.assertEqual(len(mkSetup.call_args_list), 9)
                for call in new.activate.call_args_list:
                    self.assertEqual(call, mk.call())
                self.assertEqual(len(new.activate.call_args_list), 9)
                for call in mkId.call_args_list:
                    self.assertEqual(call, mk.call(self.Simulation))
                self.assertEqual(len(mkId.call_args_list), 9)

    def test_populate_larvae(self):
        """test generate all new larvae"""

        new = mk.create_autospec(larva.Larva, spec_set=True)

        with mk.patch.object(larva.Larva, 'setup',
                             autospec=True) as mkSetup:
            with mk.patch.object(simulation.Simulation, 'new_unique_id',
                                 autospec=True) as mkId:
                mkSetup.return_value = new

                self.Simulation.populate_larvae((3, 3, 3))

                for index, call in enumerate(mkSetup.call_args_list):
                    self.assertEqual(call,
                                     mk.call(mkId.return_value,
                                             keyword.init,
                                             self.Simulation,
                                             keyword.genotype_keys[index // 3]))
                self.assertEqual(len(mkSetup.call_args_list), 9)
                for call in new.activate.call_args_list:
                    self.assertEqual(call, mk.call())
                self.assertEqual(len(new.activate.call_args_list), 9)
                for call in mkId.call_args_list:
                    self.assertEqual(call, mk.call(self.Simulation))
                self.assertEqual(len(mkId.call_args_list), 9)

    def test_populate_pupae(self):
        """test generate all new pupae"""

        new = mk.create_autospec(pupa.Pupa, spec_set=True)

        with mk.patch.object(pupa.Pupa, 'setup',
                             autospec=True) as mkSetup:
            with mk.patch.object(simulation.Simulation, 'new_unique_id',
                                 autospec=True) as mkId:
                mkSetup.return_value = new

                self.Simulation.populate_pupae((3, 3, 3))

                for index, call in enumerate(mkSetup.call_args_list):
                    self.assertEqual(call,
                                     mk.call(mkId.return_value,
                                             keyword.init,
                                             self.Simulation,
                                             keyword.genotype_keys[index // 3]))
                self.assertEqual(len(mkSetup.call_args_list), 9)
                for call in new.activate.call_args_list:
                    self.assertEqual(call, mk.call())
                self.assertEqual(len(new.activate.call_args_list), 9)
                for call in mkId.call_args_list:
                    self.assertEqual(call, mk.call(self.Simulation))
                self.assertEqual(len(mkId.call_args_list), 9)

    def test_populate_adults(self):
        """test generate all new adults"""

        new = mk.create_autospec(adult.Adult, spec_set=True)

        with mk.patch.object(adult.Adult, 'setup',
                             autospec=True) as mkSetup:
            with mk.patch.object(simulation.Simulation, 'new_unique_id',
                                 autospec=True) as mkId:
                mkSetup.return_value = new

                self.Simulation.populate_adults((3, 3, 3))

                for index, call in enumerate(mkSetup.call_args_list):
                    self.assertEqual(call,
                                     mk.call(mkId.return_value,
                                             keyword.init,
                                             self.Simulation,
                                             keyword.genotype_keys[index // 3]))
                self.assertEqual(len(mkSetup.call_args_list), 9)
                for call in new.activate.call_args_list:
                    self.assertEqual(call, mk.call())
                self.assertEqual(len(new.activate.call_args_list), 9)
                for call in mkId.call_args_list:
                    self.assertEqual(call, mk.call(self.Simulation))
                self.assertEqual(len(mkId.call_args_list), 9)
                
    def test_populate_pregnant(self):
        """test generate all new pregnant adults"""

        parents = [[keyword.homo_r, keyword.homo_r],
                   [keyword.homo_r, keyword.homo_s],
                   [keyword.homo_s, keyword.homo_s]]

        new = mk.create_autospec(adult.Adult, spec_set=True)

        with mk.patch.object(adult.Adult, 'setup',
                             autospec=True) as mkSetup:
            with mk.patch.object(simulation.Simulation, 'new_unique_id',
                                 autospec=True) as mkId:
                with mk.patch.object(rnd, 'shuffle') as mkRND:
                    mkSetup.return_value = new

                    self.Simulation.populate_pregnant((3, 3, 3))

                    for index, call in enumerate(mkSetup.call_args_list):
                        self.assertEqual(call,
                                         mk.call(mkId.return_value,
                                                 keyword.init,
                                                 self.Simulation,
                                                 parents[index // 3][0],
                                                 parents[index // 3][1]))
                    self.assertEqual(len(mkSetup.call_args_list), 9)
                    for call in new.activate.call_args_list:
                        self.assertEqual(call, mk.call())
                    self.assertEqual(len(new.activate.call_args_list), 9)
                    for call in mkId.call_args_list:
                        self.assertEqual(call, mk.call(self.Simulation))
                    self.assertEqual(len(mkId.call_args_list), 9)
                    for index, call in enumerate(mkRND.call_args_list):
                        self.assertEqual(call,
                                         mk.call(parents[index // 3]))
                    self.assertEqual(len(mkRND.call_args_list), 9)

    def test_populate(self):
        """test populate the simulation"""

        nums = [(mk.MagicMock(spec=int),
                 mk.MagicMock(spec=int),
                 mk.MagicMock(spec=int)) for _ in range(5)]
        nums = tuple(nums)

        with mk.patch.object(simulation.Simulation, 'populate_egg_masses',
                             autospec=True) as mkEggs:
            with mk.patch.object(simulation.Simulation, 'populate_larvae',
                                 autospec=True) as mkLarvae:
                with mk.patch.object(simulation.Simulation, 'populate_pupae',
                                     autospec=True) as mkPupae:
                    with mk.patch.object(simulation.Simulation,
                                         'populate_adults',
                                         autospec=True) as mkAdults:
                        with mk.patch.object(simulation.Simulation,
                                             'populate_pregnant',
                                             autospec=True) as mkPregnant:
                            # noinspection PyTypeChecker
                            self.Simulation.populate(nums)

                            self.assertEqual(mkEggs.call_args_list,
                                             [mk.call(self.Simulation,
                                                      nums[0])])
                            self.assertEqual(mkLarvae.call_args_list,
                                             [mk.call(self.Simulation,
                                                      nums[1])])
                            self.assertEqual(mkPupae.call_args_list,
                                             [mk.call(self.Simulation,
                                                      nums[2])])
                            self.assertEqual(mkAdults.call_args_list,
                                             [mk.call(self.Simulation,
                                                      nums[3])])
                            self.assertEqual(mkPregnant.call_args_list,
                                             [mk.call(self.Simulation,
                                                      nums[4])])
