import unittest      as ut
import unittest.mock as mk

import dataclasses  as dclass
import itertools    as i_tools
import numpy.random as rnd
import pickle       as pk

import source.keyword as keyword

import source.schedule.schedule as schedule

import source.agents.adult    as adult
import source.agents.egg_mass as egg_mass
import source.agents.larva    as larva
import source.agents.pupa     as pupa

import source.data.database as database

import source.migration.emigration  as emigration
import source.migration.immigration as immigration

import source.simulation.behaviors  as behaviors
import source.simulation.models     as models
import source.simulation.simulation as simulation

import source.space.agents as agents
import source.space.graph  as main_graph
import source.space.space  as space


class GraphTest(main_graph.Graph):
    """Class to add dynamic values for tests"""

    adjacency = mk.create_autospec(main_graph.Adjacency, spec_seth=True)


class TestSimulation(ut.TestCase):
    """test the model Simulation class"""

    def setUp(self):
        """Setup the tests"""

        self.space     = mk.create_autospec(space.Space,          spec_set=True)
        self.agents    = mk.create_autospec(agents.Agents,        spec_set=True)
        self.schedule  = mk.create_autospec(schedule.Schedule,    spec_set=True)
        self.models    = mk.create_autospec(models.Models,        spec_set=True)
        self.behaviors = mk.create_autospec(behaviors.Behaviors,  spec_set=True)
        self.database  = mk.create_autospec(database.Database,    spec_set=True)

        self.emigration = mk.create_autospec(emigration.Emigrations,
                                             spec_set=True)
        self.immigration = mk.create_autospec(immigration.Immigrations,
                                              spec_set=True)

        self.timestep = mk.MagicMock(spec=int)

        self.Simulation = simulation.Simulation(self.space,
                                                self.agents,
                                                self.schedule,
                                                self.models,
                                                self.behaviors,
                                                self.database,
                                                self.emigration,
                                                self.immigration,
                                                self.timestep)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Simulation, simulation.Simulation)

        self.assertEqual(self.Simulation.space,       self.space)
        self.assertEqual(self.Simulation.agents,      self.agents)
        self.assertEqual(self.Simulation.schedule,    self.schedule)
        self.assertEqual(self.Simulation.models,      self.models)
        self.assertEqual(self.Simulation.behaviors,   self.behaviors)
        self.assertEqual(self.Simulation.database,    self.database)
        self.assertEqual(self.Simulation.emigration,  self.emigration)
        self.assertEqual(self.Simulation.immigration, self.immigration)
        self.assertEqual(self.Simulation.timestep,    self.timestep)

        # noinspection PyTypeChecker
        self.assertIsInstance(self.Simulation._id_count, i_tools.count)
        # noinspection PyTypeChecker
        self.assertEqual(next(self.Simulation._id_count),
                         next(i_tools.count()))

        self.assertTrue(dclass.is_dataclass(self.Simulation))

    def test_count_step(self):
        """test count a step"""

        self.assertEqual(self.Simulation.count_step(),
                         self.timestep.__add__.return_value)
        self.assertEqual(self.Simulation.timestep,
                         self.timestep.__add__.return_value)
        self.assertEqual(self.timestep.__add__.call_args_list,
                         [mk.call(1)])

    def test_new_unique_id(self):
        """test get a new unique_id"""

        for index in range(10):
            self.assertEqual(self.Simulation.new_unique_id(), index)

        self.assertEqual(next(self.Simulation._id_count), 10)

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

    def test_step(self):
        """test advance the model by one step"""

        master = mk.MagicMock()
        master.attach_mock(self.schedule.perform,        'perform')
        master.attach_mock(self.immigration.immigration, 'immigration')
        master.attach_mock(self.emigration.emigration,   'emigration')
        master.attach_mock(self.agents.record,           'record')
        master.attach_mock(self.database.save,           'save')

        self.Simulation.step()
        self.assertEqual(master.mock_calls,
                         [mk.call.perform(self.space, self.agents),
                          mk.call.immigration(self.Simulation),
                          mk.call.emigration(self.agents),
                          mk.call.record(),
                          mk.call.save(self.Simulation)])

    def test_save(self):
        """test save to file"""

        filename = mk.MagicMock(spec=str)

        with mk.patch('builtins.open', mk.mock_open()) as mkOpen:
            with mk.patch.object(pk, 'dump') as mkDump:
                self.Simulation.save(filename)
                self.assertEqual(mkDump.call_args_list,
                                 [mk.call(self.Simulation, mkOpen.return_value,
                                          protocol=pk.HIGHEST_PROTOCOL)])
                self.assertEqual(mkOpen.call_args_list,
                                 [mk.call(filename, 'wb')])

    def test_setup(self):
        """test setup the class"""

        graph = mk.create_autospec(GraphTest, spec_set=True)
        graph.adjacency = mk.create_autospec(main_graph.Adjacency,
                                             spec_set=True)
        self.space.__getitem__.return_value = graph

        nums = mk.MagicMock(spec=tuple)
        grid_generators = [mk.MagicMock(spec=tuple) for _ in range(3)]
        attrs = mk.MagicMock(spec=dict)
        data_tuple = mk.MagicMock(spec=tuple)
        bt_prop = mk.MagicMock(spec=float)
        step_tuples = [mk.MagicMock(spec=tuple) for _ in range(3)]
        emigration_tuples = [mk.MagicMock(spec=tuple) for _ in range(3)]
        immigration_tuples = [mk.MagicMock(spec=tuple) for _ in range(3)]
        args   = tuple([mk.MagicMock() for _ in range(3)])
        kwargs = {'test{}'.format(index): mk.MagicMock() for index in range(3)}

        cutoff = mk.MagicMock(spec=float)
        bt_prop.__mul__.return_value = cutoff

        init_plant  = mk.MagicMock(spec=callable)
        test_models = {keyword.init_plant: init_plant}

        with mk.patch.object(models.Models,
                             'setup') as mkModels:
            with mk.patch.object(behaviors.Behaviors,
                                 'setup') as mkBehaviors:
                with mk.patch.object(schedule.Schedule,
                                     'setup') as mkSchedule:
                    with mk.patch.object(database.Database,
                                         'setup') as mkDatabase:
                        with mk.patch.object(emigration.Emigrations,
                                             'setup') as mkEmigration:
                            with mk.patch.object(immigration.Immigrations,
                                                 'setup') as mkImmigration:
                                with mk.patch.object(space.Space,
                                                     'setup') as mkSpace:
                                    with mk.patch.object(agents.Agents,
                                                         'empty') as mkAgents:
                                        with mk.patch.object(simulation.
                                                                     Simulation,
                                                             'populate') \
                                                as mkPop:
                                            mkModels.return_value = test_models
                                            mkBehaviors.return_value = \
                                                self.behaviors
                                            mkSchedule.return_value = \
                                                self.schedule
                                            mkDatabase.return_value = \
                                                self.database
                                            mkEmigration.return_value = \
                                                self.emigration
                                            mkImmigration.return_value = \
                                                self.immigration
                                            mkSpace.return_value = self.space
                                            mkAgents.return_value = self.agents

                                            sim = \
                                                simulation.Simulation.\
                                                    setup(nums,
                                                          grid_generators,
                                                          attrs,
                                                          data_tuple,
                                                          bt_prop,
                                                          step_tuples,
                                                          emigration_tuples,
                                                          immigration_tuples,
                                                          *args, **kwargs)

        self.assertEqual(mkModels.call_args_list,
                         [mk.call(*args, **kwargs)])
        self.assertEqual(mkBehaviors.call_args_list,
                         [mk.call(**test_models)])
        self.assertEqual(mkSchedule.call_args_list,
                         [mk.call(step_tuples)])
        self.assertEqual(mkDatabase.call_args_list,
                         [mk.call(data_tuple)])
        self.assertEqual(mkEmigration.call_args_list,
                         [mk.call(emigration_tuples)])
        self.assertEqual(mkImmigration.call_args_list,
                         [mk.call(immigration_tuples)])
        self.assertEqual(mkSpace.call_args_list,
                         [mk.call(grid_generators)])
        self.assertEqual(mkAgents.call_args_list,
                         [mk.call(self.space,
                                  keyword.agent_keys,
                                  attrs, (cutoff, init_plant))])
        self.assertEqual(bt_prop.__mul__.call_args_list,
                         [mk.call(self.space.
                                    __getitem__.return_value.adjacency.num)])
        self.assertEqual(self.space.__getitem__.call_args_list,
                         [mk.call(keyword.bt_level)])
        self.assertEqual(mkPop.call_args_list,
                         [mk.call(nums)])
        self.assertEqual(self.agents.record.call_args_list,
                         [mk.call()])

        self.assertIsInstance(sim, simulation.Simulation)

        self.assertEqual(sim.space,       self.space)
        self.assertEqual(sim.agents,      self.agents)
        self.assertEqual(sim.schedule,    self.schedule)
        self.assertEqual(sim.models,      test_models)
        self.assertEqual(sim.behaviors,   self.behaviors)
        self.assertEqual(sim.database,    self.database)
        self.assertEqual(sim.emigration,  self.emigration)
        self.assertEqual(sim.immigration, self.immigration)
        self.assertEqual(sim.timestep,    0)
