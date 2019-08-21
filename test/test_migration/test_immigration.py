import unittest      as ut
import unittest.mock as mk

import dataclasses  as dclass
import collections  as collect
import numpy.random as rnd
import scipy.stats  as stats

import source.keyword as keyword

import source.agents.adult    as adult
import source.agents.egg_mass as egg_mass
import source.agents.larva    as larva
import source.agents.pupa     as pupa

import source.migration.immigration as immigration

import source.simulation.simulation as main_simulation


class TestImmigration(ut.TestCase):
    """test Immigration class"""

    def setUp(self):
        """Setup the tests"""

        self.lam       = mk.MagicMock(spec=float)
        self.genotype  = mk.MagicMock(spec=str)
        self.agent_key = mk.MagicMock(spec=str)

        self.Immigration = immigration.Immigration(self.lam,
                                                   self.genotype,
                                                   self.agent_key)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Immigration, immigration.Immigration)

        self.assertEqual(self.Immigration.lam,       self.lam)
        self.assertEqual(self.Immigration.genotype,  self.genotype)
        self.assertEqual(self.Immigration.agent_key, self.agent_key)

        self.assertTrue(dclass.is_dataclass(self.Immigration))

    def test__number(self):
        """test get the number of immigrants"""

        with mk.patch.object(stats.poisson, 'rvs') as mkRVS:
            with mk.patch.object(immigration, 'int') as mkInt:
                self.assertEqual(self.Immigration._number(),
                                 mkInt.return_value)
                self.assertEqual(mkInt.call_args_list,
                                 [mk.call(mkRVS.return_value)])
                self.assertEqual(mkRVS.call_args_list,
                                 [mk.call(self.lam)])

    def test__immigrate_egg_masses(self):
        """test immigrate egg_masses into simulation"""

        simulation = mk.create_autospec(main_simulation.Simulation,
                                        spec_set=True)
        new = [mk.create_autospec(egg_mass.EggMass, spec_set=True)
               for _ in range(3)]

        with mk.patch.object(immigration.Immigration, '_number',
                             autospec=True) as mkNumber:
            with mk.patch.object(egg_mass.EggMass, 'setup',
                                 autospec=True) as mkSetup:
                mkNumber.return_value = 3
                mkSetup.side_effect = new

                self.Immigration._immigrate_egg_masses(simulation)
                self.assertEqual(mkNumber.call_args_list,
                                 [mk.call(self.Immigration)])
                for index, agent in enumerate(new):
                    self.assertEqual(mkSetup.call_args_list[index],
                                     mk.call(simulation.
                                                new_unique_id.return_value,
                                             keyword.immigrant,
                                             simulation,
                                             self.genotype))
                    self.assertEqual(simulation.
                                     new_unique_id.call_args_list[index],
                                     mk.call())
                    self.assertEqual(agent.activate.call_args_list,
                                     [mk.call()])
                self.assertEqual(len(mkSetup.call_args_list), 3)
                self.assertEqual(len(simulation.
                                        new_unique_id.call_args_list), 3)

    def test__immigrate_larvae(self):
        """test immigrate larvae into simulation"""

        simulation = mk.create_autospec(main_simulation.Simulation,
                                        spec_set=True)
        new = [mk.create_autospec(larva.Larva, spec_set=True)
               for _ in range(3)]

        with mk.patch.object(immigration.Immigration, '_number',
                             autospec=True) as mkNumber:
            with mk.patch.object(larva.Larva, 'setup',
                                 autospec=True) as mkSetup:
                mkNumber.return_value = 3
                mkSetup.side_effect = new

                self.Immigration._immigrate_larvae(simulation)
                self.assertEqual(mkNumber.call_args_list,
                                 [mk.call(self.Immigration)])
                for index, agent in enumerate(new):
                    self.assertEqual(mkSetup.call_args_list[index],
                                     mk.call(simulation.
                                             new_unique_id.return_value,
                                             keyword.immigrant,
                                             simulation,
                                             self.genotype))
                    self.assertEqual(simulation.
                                     new_unique_id.call_args_list[index],
                                     mk.call())
                    self.assertEqual(agent.activate.call_args_list,
                                     [mk.call()])
                self.assertEqual(len(mkSetup.call_args_list), 3)
                self.assertEqual(len(simulation.
                                     new_unique_id.call_args_list), 3)

    def test__immigrate_pupae(self):
        """test immigrate pupae into simulation"""

        simulation = mk.create_autospec(main_simulation.Simulation,
                                        spec_set=True)
        new = [mk.create_autospec(pupa.Pupa, spec_set=True)
               for _ in range(3)]

        with mk.patch.object(immigration.Immigration, '_number',
                             autospec=True) as mkNumber:
            with mk.patch.object(pupa.Pupa, 'setup',
                                 autospec=True) as mkSetup:
                mkNumber.return_value = 3
                mkSetup.side_effect = new

                self.Immigration._immigrate_pupae(simulation)
                self.assertEqual(mkNumber.call_args_list,
                                 [mk.call(self.Immigration)])
                for index, agent in enumerate(new):
                    self.assertEqual(mkSetup.call_args_list[index],
                                     mk.call(simulation.
                                             new_unique_id.return_value,
                                             keyword.immigrant,
                                             simulation,
                                             self.genotype))
                    self.assertEqual(simulation.
                                     new_unique_id.call_args_list[index],
                                     mk.call())
                    self.assertEqual(agent.activate.call_args_list,
                                     [mk.call()])
                self.assertEqual(len(mkSetup.call_args_list), 3)
                self.assertEqual(len(simulation.
                                     new_unique_id.call_args_list), 3)

    def test__immigrate_adults(self):
        """test immigrate adults into simulation"""

        simulation = mk.create_autospec(main_simulation.Simulation,
                                        spec_set=True)
        new = [mk.create_autospec(adult.Adult, spec_set=True)
               for _ in range(3)]

        with mk.patch.object(immigration.Immigration, '_number',
                             autospec=True) as mkNumber:
            with mk.patch.object(adult.Adult, 'setup',
                                 autospec=True) as mkSetup:
                mkNumber.return_value = 3
                mkSetup.side_effect = new

                self.Immigration._immigrate_adults(simulation)
                self.assertEqual(mkNumber.call_args_list,
                                 [mk.call(self.Immigration)])
                for index, agent in enumerate(new):
                    self.assertEqual(mkSetup.call_args_list[index],
                                     mk.call(simulation.
                                             new_unique_id.return_value,
                                             keyword.immigrant,
                                             simulation,
                                             self.genotype))
                    self.assertEqual(simulation.
                                     new_unique_id.call_args_list[index],
                                     mk.call())
                    self.assertEqual(agent.activate.call_args_list,
                                     [mk.call()])
                self.assertEqual(len(mkSetup.call_args_list), 3)
                self.assertEqual(len(simulation.
                                     new_unique_id.call_args_list), 3)

    def test__immigrate_pregnant(self):
        """test immigrate pregnant into simulation"""

        simulation = mk.create_autospec(main_simulation.Simulation,
                                        spec_set=True)
        new = [mk.create_autospec(adult.Adult, spec_set=True)
               for _ in range(3)]

        # Homo_r
        self.Immigration.genotype = keyword.homo_r
        with mk.patch.object(immigration.Immigration, '_number',
                             autospec=True) as mkNumber:
            with mk.patch.object(adult.Adult, 'setup',
                                 autospec=True) as mkSetup:
                with mk.patch.object(rnd, 'shuffle') as mkRND:
                    mkNumber.return_value = 3
                    mkSetup.side_effect = new

                    self.Immigration._immigrate_pregnant(simulation)
                    self.assertEqual(mkNumber.call_args_list,
                                     [mk.call(self.Immigration)])
                    for index, agent in enumerate(new):
                        self.assertEqual(mkSetup.call_args_list[index],
                                         mk.call(simulation.
                                                 new_unique_id.return_value,
                                                 keyword.immigrant,
                                                 simulation,
                                                 keyword.homo_r,
                                                 keyword.homo_r))
                        self.assertEqual(simulation.
                                         new_unique_id.call_args_list[index],
                                         mk.call())
                        self.assertEqual(mkRND.call_args_list[index],
                                         mk.call([keyword.homo_r,
                                                  keyword.homo_r]))
                        self.assertEqual(agent.activate.call_args_list,
                                         [mk.call()])
                        agent.reset_mock()
                    self.assertEqual(len(mkSetup.call_args_list), 3)
                    self.assertEqual(len(simulation.
                                         new_unique_id.call_args_list), 3)
                    self.assertEqual(len(mkRND.call_args_list), 3)
                    simulation.reset_mock()

        # Hetero
        self.Immigration.genotype = keyword.hetero
        with mk.patch.object(immigration.Immigration, '_number',
                             autospec=True) as mkNumber:
            with mk.patch.object(adult.Adult, 'setup',
                                 autospec=True) as mkSetup:
                with mk.patch.object(rnd, 'shuffle') as mkRND:
                    mkNumber.return_value = 3
                    mkSetup.side_effect = new

                    self.Immigration._immigrate_pregnant(simulation)
                    self.assertEqual(mkNumber.call_args_list,
                                     [mk.call(self.Immigration)])
                    for index, agent in enumerate(new):
                        self.assertEqual(mkSetup.call_args_list[index],
                                         mk.call(simulation.
                                                 new_unique_id.return_value,
                                                 keyword.immigrant,
                                                 simulation,
                                                 keyword.homo_r,
                                                 keyword.homo_s))
                        self.assertEqual(simulation.
                                         new_unique_id.call_args_list[index],
                                         mk.call())
                        self.assertEqual(mkRND.call_args_list[index],
                                         mk.call([keyword.homo_r,
                                                  keyword.homo_s]))
                        self.assertEqual(agent.activate.call_args_list,
                                         [mk.call()])
                        agent.reset_mock()
                    self.assertEqual(len(mkSetup.call_args_list), 3)
                    self.assertEqual(len(simulation.
                                         new_unique_id.call_args_list), 3)
                    self.assertEqual(len(mkRND.call_args_list), 3)
                    simulation.reset_mock()

        # Homo_s
        self.Immigration.genotype = keyword.homo_s
        with mk.patch.object(immigration.Immigration, '_number',
                             autospec=True) as mkNumber:
            with mk.patch.object(adult.Adult, 'setup',
                                 autospec=True) as mkSetup:
                with mk.patch.object(rnd, 'shuffle') as mkRND:
                    mkNumber.return_value = 3
                    mkSetup.side_effect = new

                    self.Immigration._immigrate_pregnant(simulation)
                    self.assertEqual(mkNumber.call_args_list,
                                     [mk.call(self.Immigration)])
                    for index, agent in enumerate(new):
                        self.assertEqual(mkSetup.call_args_list[index],
                                         mk.call(simulation.
                                                 new_unique_id.return_value,
                                                 keyword.immigrant,
                                                 simulation,
                                                 keyword.homo_s,
                                                 keyword.homo_s))
                        self.assertEqual(simulation.
                                         new_unique_id.call_args_list[index],
                                         mk.call())
                        self.assertEqual(mkRND.call_args_list[index],
                                         mk.call([keyword.homo_s,
                                                  keyword.homo_s]))
                        self.assertEqual(agent.activate.call_args_list,
                                         [mk.call()])
                        agent.reset_mock()
                    self.assertEqual(len(mkSetup.call_args_list), 3)
                    self.assertEqual(len(simulation.
                                         new_unique_id.call_args_list), 3)
                    self.assertEqual(len(mkRND.call_args_list), 3)
                    simulation.reset_mock()

    def test_immigration(self):
        """test run the immigration"""

        simulation = mk.create_autospec(main_simulation.Simulation,
                                        spec_set=True)

        with mk.patch.object(immigration.Immigration, '_immigrate_egg_masses',
                             autospec=True) as mkEggs:
            with mk.patch.object(immigration.Immigration, '_immigrate_larvae',
                                 autospec=True) as mkLarvae:
                with mk.patch.object(immigration.Immigration, '_immigrate_pupae',
                                     autospec=True) as mkPupae:
                    with mk.patch.object(immigration.Immigration,
                                         '_immigrate_adults',
                                         autospec=True) as mkAdults:
                        with mk.patch.object(immigration.Immigration,
                                             '_immigrate_pregnant',
                                             autospec=True) as mkPregnant:
                            # Not used agent_key
                            self.Immigration.immigration(simulation)
                            self.assertEqual(mkEggs.call_args_list, [])
                            self.assertEqual(mkLarvae.call_args_list, [])
                            self.assertEqual(mkPupae.call_args_list, [])
                            self.assertEqual(mkAdults.call_args_list, [])
                            self.assertEqual(mkPregnant.call_args_list, [])

                            # Eggs
                            self.Immigration.agent_key = keyword.egg_mass
                            self.Immigration.immigration(simulation)
                            self.assertEqual(mkEggs.call_args_list,
                                             [mk.call(self.Immigration,
                                                      simulation)])
                            self.assertEqual(mkLarvae.call_args_list, [])
                            self.assertEqual(mkPupae.call_args_list, [])
                            self.assertEqual(mkAdults.call_args_list, [])
                            self.assertEqual(mkPregnant.call_args_list, [])

                            mkEggs.reset_mock()
                            # Larvae
                            self.Immigration.agent_key = keyword.larva
                            self.Immigration.immigration(simulation)
                            self.assertEqual(mkEggs.call_args_list, [])
                            self.assertEqual(mkLarvae.call_args_list,
                                             [mk.call(self.Immigration,
                                                      simulation)])
                            self.assertEqual(mkPupae.call_args_list, [])
                            self.assertEqual(mkAdults.call_args_list, [])
                            self.assertEqual(mkPregnant.call_args_list, [])

                            mkLarvae.reset_mock()
                            # Pupae
                            self.Immigration.agent_key = keyword.pupa
                            self.Immigration.immigration(simulation)
                            self.assertEqual(mkEggs.call_args_list, [])
                            self.assertEqual(mkLarvae.call_args_list, [])
                            self.assertEqual(mkPupae.call_args_list,
                                             [mk.call(self.Immigration,
                                                      simulation)])
                            self.assertEqual(mkAdults.call_args_list, [])
                            self.assertEqual(mkPregnant.call_args_list, [])

                            mkPupae.reset_mock()
                            # Adults
                            self.Immigration.agent_key = keyword.adult
                            self.Immigration.immigration(simulation)
                            self.assertEqual(mkEggs.call_args_list, [])
                            self.assertEqual(mkLarvae.call_args_list, [])
                            self.assertEqual(mkPupae.call_args_list, [])
                            self.assertEqual(mkAdults.call_args_list,
                                             [mk.call(self.Immigration,
                                                      simulation)])
                            self.assertEqual(mkPregnant.call_args_list, [])

                            mkAdults.reset_mock()
                            # Pregnant
                            self.Immigration.agent_key = keyword.pregnant
                            self.Immigration.immigration(simulation)
                            self.assertEqual(mkEggs.call_args_list, [])
                            self.assertEqual(mkLarvae.call_args_list, [])
                            self.assertEqual(mkPupae.call_args_list, [])
                            self.assertEqual(mkAdults.call_args_list, [])
                            self.assertEqual(mkPregnant.call_args_list,
                                             [mk.call(self.Immigration,
                                                      simulation)])


class TestImmigrations(ut.TestCase):
    """test the Immigrations system class"""

    def setUp(self):
        """Setup the tests"""

        self.immigrations = [mk.create_autospec(immigration.Immigration,
                                                spec_set=True)
                             for _ in range(3)]

        self.Immigrations = immigration.Immigrations(self.immigrations)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Immigrations, collect.UserList)
        self.assertIsInstance(self.Immigrations, immigration.Immigrations)

        self.assertEqual(self.Immigrations,      self.immigrations)
        self.assertEqual(self.Immigrations.data, self.immigrations)

    def test_immigration(self):
        """test run immigration"""

        simulation = mk.create_autospec(main_simulation.Simulation,
                                        spec_set=True)

        self.Immigrations.immigration(simulation)
        for this in self.immigrations:
            self.assertEqual(this.immigration.call_args_list,
                             [mk.call(simulation)])

    def test_setup(self):
        """test setup the class"""

        setup_tuples = [(mk.MagicMock(spec=float),
                         mk.MagicMock(spec=str), mk.MagicMock(spec=str))
                        for _ in range(3)]

        self.Immigrations = immigration.Immigrations.setup(setup_tuples)
        self.assertIsInstance(self.Immigrations, immigration.Immigrations)
        for index, immigrate in enumerate(self.Immigrations):
            self.assertIsInstance(immigrate, immigration.Immigration)
            self.assertEqual(immigrate.lam,       setup_tuples[index][0])
            self.assertEqual(immigrate.genotype,  setup_tuples[index][1])
            self.assertEqual(immigrate.agent_key, setup_tuples[index][2])
        self.assertEqual(len(self.Immigrations), 3)
