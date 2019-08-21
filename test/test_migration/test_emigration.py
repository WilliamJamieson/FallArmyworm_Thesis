import unittest      as ut
import unittest.mock as mk

import dataclasses  as dclass
import collections  as collect
import numpy.random as rnd
import scipy.stats  as stats

import source.keyword as keyword

import source.agents.agent as main_agent

import source.migration.emigration as emigration

import source.space.agents   as main_agents
import source.space.location as agent_location


class TestEmigration(ut.TestCase):
    """test the Emigration class"""

    def setUp(self):
        """Setup the tests"""

        self.mu    = mk.MagicMock(spec=float)
        self.sigma = mk.MagicMock(spec=float)

        self.agent_keys = [mk.MagicMock(spec=str) for _ in range(3)]

        self.Emigration = emigration.Emigration(self.mu,
                                                self.sigma,
                                                self.agent_keys)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Emigration, emigration.Emigration)

        self.assertEqual(self.Emigration.mu,         self.mu)
        self.assertEqual(self.Emigration.sigma,      self.sigma)
        self.assertEqual(self.Emigration.agent_keys, self.agent_keys)

        self.assertIsInstance(self.Emigration.location, agent_location.Location)
        self.assertEqual(self.Emigration.location, [0])

        self.assertTrue(dclass.is_dataclass(self.Emigration))
        
    def test_remove(self):
        """test get the probability of agent emigrating"""

        population = mk.MagicMock(spec=float)

        with mk.patch.object(stats.norm, 'cdf') as mkCDF:
            with mk.patch.object(rnd, 'random') as mkRND:
                mkRND.return_value.__le__.side_effect = [True, False]

                # Test if True
                self.assertTrue(self.Emigration._remove(population))
                self.assertEqual(mkRND.return_value.__le__.call_args_list,
                                 [mk.call(mkCDF.return_value)])
                self.assertEqual(mkRND.call_args_list,
                                 [mk.call()])
                self.assertEqual(mkCDF.call_args_list,
                                 [mk.call(population,
                                          loc=self.mu, scale=self.sigma)])

                mkRND.reset_mock()
                mkCDF.reset_mock()
                # Test if False
                self.assertFalse(self.Emigration._remove(population))
                self.assertEqual(mkRND.return_value.__le__.call_args_list,
                                 [mk.call(mkCDF.return_value)])
                self.assertEqual(mkRND.call_args_list,
                                 [mk.call()])
                self.assertEqual(mkCDF.call_args_list,
                                 [mk.call(population,
                                          loc=self.mu, scale=self.sigma)])

    def test__emigrate(self):
        """test run emigrate on agent"""

        agent      = mk.create_autospec(main_agent.Agent, spec_set=True)
        population = mk.MagicMock(spec=float)

        with mk.patch.object(emigration.Emigration, '_remove',
                             autospec=True) as mkRemove:
            mkRemove.side_effect = [False, True]

            # Test not remove
            self.assertEqual(self.Emigration._emigrate(agent, population),
                             population)
            self.assertEqual(population.__sub__.call_args_list, [])
            self.assertEqual(mkRemove.call_args_list,
                             [mk.call(self.Emigration, population)])
            self.assertEqual(agent.die.call_args_list, [])

            mkRemove.reset_mock()
            # Test not remove
            self.assertEqual(self.Emigration._emigrate(agent, population),
                             population.__sub__.return_value)
            self.assertEqual(population.__sub__.call_args_list,
                             [mk.call(1)])
            self.assertEqual(mkRemove.call_args_list,
                             [mk.call(self.Emigration, population)])
            self.assertEqual(agent.die.call_args_list,
                             [mk.call(keyword.emigrate)])

    def test__agents(self):
        """test create the agents"""

        agents = mk.create_autospec(main_agents.Agents, spec_set=True)
        agents.__getitem__.return_value = \
            mk.create_autospec(main_agents.AgentsBin, spec_set=True)

        population = []
        agent_bins = []
        for agent_key in self.agent_keys:
            pop       = [mk.create_autospec(main_agent.Agent, spec_set=True)
                         for _ in range(3)]
            agent_bin = main_agents.AgentBin(pop, mk.MagicMock(), agent_key)
            population.extend(agent_bin)
            agent_bins.append(agent_bin)

        agents.__getitem__.return_value.__getitem__.side_effect = agent_bins

        self.assertEqual(self.Emigration._agents(agents), population)
        for index, agent_key in enumerate(self.agent_keys):
            self.assertEqual(agents.__getitem__.return_value.
                                __getitem__.call_args_list[index],
                             mk.call(agent_key))
            self.assertEqual(agents.__getitem__.call_args_list[index],
                             mk.call(self.Emigration.location))
        self.assertEqual(len(agents.__getitem__.return_value.
                                __getitem__.call_args_list), 3)
        self.assertEqual(len(agents.__getitem__.call_args_list), 3)
        
    def test_emigration(self):
        """test run emigration"""

        agents = mk.create_autospec(main_agents.Agents, spec_set=True)

        population = [mk.create_autospec(main_agent.Agent, spec_set=True)
                      for _ in range(3)]
        pop        = [mk.MagicMock(spec=int) for _ in range(3)]

        with mk.patch.object(emigration.Emigration, '_agents',
                             autospec=True) as mkAgents:
            with mk.patch.object(emigration.Emigration, '_emigrate',
                                 autospec=True) as mkEmigrate:
                with mk.patch.object(emigration, 'len') as mkLen:
                    mkAgents.return_value  = population
                    mkEmigrate.side_effect = pop

                    self.Emigration.emigration(agents)
                    self.assertEqual(len(mkEmigrate.call_args_list), 3)
                    call = mkEmigrate.call_args_list.pop(0)
                    self.assertEqual(call,
                                     mk.call(self.Emigration,
                                             population[0], mkLen.return_value))
                    self.assertEqual(mkLen.call_args_list,
                                     [mk.call(population)])
                    self.assertEqual(mkAgents.call_args_list,
                                     [mk.call(self.Emigration, agents)])

                    for index, call in enumerate(mkEmigrate.call_args_list):
                        self.assertEqual(call,
                                         mk.call(self.Emigration,
                                                 population[index + 1],
                                                 pop[index]))
                    self.assertEqual(len(mkEmigrate.call_args_list), 2)


class TestEmigrations(ut.TestCase):
    """test Emigrations class"""

    def setUp(self):
        """Setup the tests"""

        self.emigrations = [mk.create_autospec(emigration.Emigration,
                                               spec_set=True)
                            for _ in range(3)]

        self.Emigrations = emigration.Emigrations(self.emigrations)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Emigrations, collect.UserList)
        self.assertIsInstance(self.Emigrations, emigration.Emigrations)

        self.assertEqual(self.Emigrations,      self.emigrations)
        self.assertEqual(self.Emigrations.data, self.emigrations)

    def test_emigration(self):
        """test run emigration"""

        agents = mk.create_autospec(main_agents.Agents, spec_set=True)

        self.Emigrations.emigration(agents)
        for this in self.emigrations:
            self.assertEqual(this.emigration.call_args_list,
                             [mk.call(agents)])

    def test_setup(self):
        """test setup the class"""

        setup_tuples = [(mk.MagicMock(spec=float), mk.MagicMock(spec=float),
                         [mk.MagicMock(spec=str) for _ in range(3)])
                        for _ in range(3)]

        self.Emigrations = emigration.Emigrations.setup(setup_tuples)
        self.assertIsInstance(self.Emigrations, emigration.Emigrations)

        for index, emigrate in enumerate(self.Emigrations):
            self.assertIsInstance(emigrate, emigration.Emigration)
            self.assertEqual(emigrate.mu,         setup_tuples[index][0])
            self.assertEqual(emigrate.sigma,      setup_tuples[index][1])
            self.assertEqual(emigrate.agent_keys, setup_tuples[index][2])

            self.assertIsInstance(emigrate.location, agent_location.Location)
            self.assertEqual(emigrate.location, [0])
        self.assertEqual(len(self.Emigrations), 3)
