import unittest      as ut
import unittest.mock as mk

import collections as collect
import pandas      as pd

import source.keyword as keyword

import source.agents.agent as main_agent

import source.data.counter as counter

import source.space.agents      as agents
import source.space.environment as agent_environment
import source.space.location    as agent_location
import source.space.space       as agent_space


class AgentTest(main_agent.Agent):
    """Class to add dynamic values for tests"""

    agent_key = mk.MagicMock(spec=str)
    unique_id = mk.MagicMock(spec=str)
    location  = mk.create_autospec(agent_location.Location, spec_set=True)


class AgentBinTest(agents.AgentBin):
    """Class to add dynamic values for tests"""

    counts = mk.create_autospec(counter.Counts, spec_set=True)


class SpaceTest(agent_space.Space):
    """Class to add dynamic values for tests"""

    locations = [mk.create_autospec(agent_location.Location, spec_set=True)
                 for _ in range(3)]


class TestAgentBin(ut.TestCase):
    """test AgentBin class"""

    def setUp(self):
        """Setup the tests"""

        self.agents = {}
        for _ in range(3):
            unique_id = mk.MagicMock(spec=str)
            agent     = mk.create_autospec(AgentTest, spec_set=True)
            agent.unique_id = unique_id
            self.agents[unique_id] = agent

        self.counts    = mk.create_autospec(counter.Counts, spec_set=True)
        self.agent_key = mk.MagicMock(spec=str)

        self.AgentBin = agents.AgentBin(self.agents,
                                        self.counts,
                                        self.agent_key)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.AgentBin, collect.UserDict)
        self.assertIsInstance(self.AgentBin, agents.AgentBin)

        self.assertEqual(self.AgentBin.counts,    self.counts)
        self.assertEqual(self.AgentBin.agent_key, self.agent_key)

        self.assertEqual(self.AgentBin,      self.agents)
        self.assertEqual(self.AgentBin.data, self.agents)

    def test_agents(self):
        """test get the agents in system"""

        # Test calls
        with mk.patch.object(agents.AgentBin, 'values',
                             autospec=True) as mkValues:
            with mk.patch.object(agents, 'list') as mkList:
                self.assertEqual(self.AgentBin.agents,
                                 mkList.return_value)
                self.assertEqual(mkList.call_args_list,
                                 [mk.call(mkValues.return_value)])
                self.assertEqual(mkValues.call_args_list,
                                 [mk.call(self.AgentBin)])

        # Test practical
        self.assertEqual(self.AgentBin.agents, list(self.agents.values()))

    def test_activate(self):
        """test activate an agent"""


        agent     = mk.create_autospec(AgentTest, spec_set=True)
        unique_id = mk.MagicMock(spec=str)
        agent.unique_id = unique_id

        self.assertNotIn(unique_id, self.AgentBin)
        self.AgentBin.activate(agent)
        self.assertIn(unique_id, self.AgentBin)
        self.assertEqual(self.AgentBin[unique_id], agent)
        self.assertEqual(self.counts.add.call_args_list,
                         [mk.call(agent)])

        self.assertNotEqual(self.AgentBin, self.agents)

    def test_deactivate(self):
        """test deactivate"""

        self.assertEqual(len(self.AgentBin), 3)
        for unique_id, agent in self.agents.items():
            self.assertIn(unique_id, self.AgentBin)
            self.AgentBin.deactivate(agent)
            self.assertNotIn(unique_id, self.AgentBin)
            self.assertEqual(self.counts.sub.call_args_list,
                             [mk.call(agent)])
            self.counts.reset_mock()
        self.assertEqual(len(self.AgentBin), 0)

    def test_empty(self):
        """test create empty class"""

        attrs = {}
        for _ in range(3):
            values = [mk.MagicMock(spec=str) for _ in range(3)]
            removal = mk.MagicMock(spec=bool)
            attrs[mk.MagicMock(spec=str)] = (values, removal)

        self.AgentBin = agents.AgentBin.empty(self.agent_key, attrs)
        self.assertIsInstance(self.AgentBin, agents.AgentBin)
        self.assertEqual(self.AgentBin, {})
        self.assertEqual(self.AgentBin.agent_key, self.agent_key)

        self.assertIsInstance(self.AgentBin.counts, counter.Counts)
        for attr, things in attrs.items():
            values, removal = things
            self.assertIsInstance(self.AgentBin.counts[attr], counter.Count)
            self.assertEqual(self.AgentBin.counts[attr].attr,    attr)
            self.assertEqual(self.AgentBin.counts[attr].removal, removal)
            for key, value in self.AgentBin.counts[attr].items():
                self.assertIn(key, values)
                self.assertEqual(value, 0)
            for value in values:
                self.assertIn(value, self.AgentBin.counts[attr])
                self.assertEqual(self.AgentBin.counts[attr][value], 0)

            self.assertIsInstance(self.AgentBin.counts[attr].data_columns,
                                  counter.DataColumns)
            self.assertEqual(self.AgentBin.counts[attr].data_columns.attr, attr)
            for key, column in self.AgentBin.counts[attr].data_columns.items():
                self.assertIn(key, values)
                self.assertIsInstance(column, counter.DataColumn)
                self.assertEqual(column.attr_value, key)
                self.assertEqual(column, [])
            for value in values:
                self.assertIn(value, self.AgentBin.counts[attr].data_columns)
                self.assertIsInstance(self.AgentBin.counts[attr].
                                        data_columns[value],
                                      counter.DataColumn)
                self.assertEqual(self.AgentBin.counts[attr].data_columns[value].
                                 attr_value,
                                 value)
                self.assertEqual(self.AgentBin.counts[attr].data_columns[value],
                                 [])


class TestAgentsBin(ut.TestCase):
    """test AgentsBin class"""

    def setUp(self):
        """Setup the tests"""

        self.agents = {}
        self.agent_list = []
        for _ in range(3):
            agent = mk.create_autospec(AgentTest, spec_set=True)
            self.agents[agent.agent_key] = mk.create_autospec(AgentBinTest,
                                                              spec_set=True)
            self.agent_list.append(agent)

        self.location_key = mk.MagicMock(spec=tuple)
        self.environment  = mk.create_autospec(agent_environment.Environment,
                                               spec_set=True)

        self.AgentsBin = agents.AgentsBin(self.agents,
                                          self.location_key,
                                          self.environment)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.AgentsBin, collect.UserDict)
        self.assertIsInstance(self.AgentsBin, agents.AgentsBin)

        self.assertEqual(self.AgentsBin.location_key, self.location_key)
        self.assertEqual(self.AgentsBin.environment,  self.environment)

        self.assertEqual(self.AgentsBin,      self.agents)
        self.assertEqual(self.AgentsBin.data, self.agents)

    def test_activate(self):
        """test activate an agent"""

        for agent in self.agent_list:
            self.AgentsBin.activate(agent)
            self.assertEqual(self.agents[agent.agent_key].activate.
                                call_args_list,
                             [mk.call(agent)])
            self.agents[agent.agent_key].reset_mock()
            for agent_bin in self.agents.values():
                self.assertEqual(agent_bin.activate.call_args_list, [])
            self.assertEqual(len(self.agents), 3)
        self.assertEqual(len(self.agent_list), 3)

    def test_deactivate(self):
        """test deactivate an agent"""

        for agent in self.agent_list:
            self.AgentsBin.deactivate(agent)
            self.assertEqual(self.agents[agent.agent_key].deactivate.
                             call_args_list,
                             [mk.call(agent)])
            self.agents[agent.agent_key].reset_mock()
            for agent_bin in self.agents.values():
                self.assertEqual(agent_bin.deactivate.call_args_list, [])
            self.assertEqual(len(self.agents), 3)
        self.assertEqual(len(self.agent_list), 3)

    def test_record(self):
        """test record the counts"""

        for agent_bin in self.agents.values():
            agent_bin.counts = mk.create_autospec(counter.Counts, spec_set=True)

        self.AgentsBin.record()
        for agent_bin in self.AgentsBin.values():
            self.assertEqual(agent_bin.counts.record.call_args_list,
                             [mk.call()])

    def test_refresh(self):
        """test refresh the stored data"""

        for agent_bin in self.agents.values():
            agent_bin.counts = mk.create_autospec(counter.Counts, spec_set=True)

        self.AgentsBin.refresh()
        for agent_bin in self.AgentsBin.values():
            self.assertEqual(agent_bin.counts.refresh.call_args_list,
                             [mk.call()])

    def test_dataframes(self):
        """test create a dictionary of dataframes"""

        # Test no empty
        dataframes = {}
        for agent_key, agent_bin in self.agents.items():
            key = '{}_{}'.format(self.location_key, agent_key)
            agent_bin.counts = mk.create_autospec(counter.Counts, spec_set=True)
            dataframe        = mk.create_autospec(pd.DataFrame, spec_set=True)
            dataframe.empty  = False
            agent_bin.counts.dataframe.return_value = dataframe
            dataframes[key] = dataframe
        self.assertEqual(len(dataframes), 3)

        self.assertEqual(self.AgentsBin.dataframes(), dataframes)
        for agent_bin in self.AgentsBin.values():
            self.assertEqual(agent_bin.counts.dataframe.call_args_list,
                             [mk.call()])

        # Test empty
        dataframes = {}
        for agent_key, agent_bin in self.agents.items():
            key = '{}_{}'.format(self.location_key, agent_key)
            agent_bin.counts = mk.create_autospec(counter.Counts, spec_set=True)
            dataframe        = mk.create_autospec(pd.DataFrame, spec_set=True)
            dataframe.empty  = True
            agent_bin.counts.dataframe.return_value = dataframe
            dataframes[key] = dataframe
        self.assertEqual(len(dataframes), 3)

        self.assertEqual(self.AgentsBin.dataframes(), {})
        for agent_bin in self.AgentsBin.values():
            self.assertEqual(agent_bin.counts.dataframe.call_args_list,
                             [mk.call()])

    def test_make_environment(self):
        """test make the environment"""

        location = mk.create_autospec(agent_location.Location, spec_set=True)
        location.depth.__eq__.side_effect = [False, True, True]

        location.__getitem__.return_value.__lt__.side_effect = [True, False]

        cutoff      = mk.MagicMock(spec=float)
        init_plant  = mk.MagicMock(spec=callable)
        environment = (cutoff, init_plant)

        # Test incorrect depth
        environ = self.AgentsBin.make_environment(location, environment)
        self.assertIsInstance(environ, agent_environment.Environment)
        self.assertEqual(environ.bt,    None)
        self.assertEqual(environ.plant, None)
        self.assertEqual(location.depth.__eq__.call_args_list,
                         [mk.call(keyword.bt_depth)])

        location.reset_mock()
        # Test correct depth, bt
        environ = self.AgentsBin.make_environment(location, environment)
        self.assertIsInstance(environ, agent_environment.Environment)
        self.assertEqual(environ.bt,    keyword.bt)
        self.assertEqual(environ.plant,
                         init_plant.return_value)
        self.assertEqual(init_plant.call_args_list,
                         [mk.call(keyword.bt)])
        self.assertEqual(location.depth.__eq__.call_args_list,
                         [mk.call(keyword.bt_depth)])
        self.assertEqual(location.__getitem__.return_value.
                            __lt__.call_args_list,
                         [mk.call(cutoff)])
        self.assertEqual(location.__getitem__.call_args_list,
                         [mk.call(-1)])

        location.reset_mock()
        init_plant.reset_mock()
        # Test correct depth, not_bt
        environ = self.AgentsBin.make_environment(location, environment)
        self.assertIsInstance(environ, agent_environment.Environment)
        self.assertEqual(environ.bt,    keyword.not_bt)
        self.assertEqual(environ.plant,
                         init_plant.return_value)
        self.assertEqual(init_plant.call_args_list,
                         [mk.call(keyword.not_bt)])
        self.assertEqual(location.depth.__eq__.call_args_list,
                         [mk.call(keyword.bt_depth)])
        self.assertEqual(location.__getitem__.return_value.
                         __lt__.call_args_list,
                         [mk.call(cutoff)])
        self.assertEqual(location.__getitem__.call_args_list,
                         [mk.call(-1)])

    def test_make_bins(self):
        """test make the bins"""

        agent_keys = []
        attrs      = {}
        for _ in range(3):
            attr = {}
            for _ in range(3):
                values = [mk.MagicMock(spec=str) for _ in range(3)]
                removal = mk.MagicMock(spec=bool)
                attr[mk.MagicMock(spec=str)] = (values, removal)

            agent_key = mk.MagicMock(spec=str)
            agent_keys.append(agent_key)
            attrs[agent_key] = attr

        # with attrs
        agent_bins = self.AgentsBin.make_bins(agent_keys, attrs)
        for agent_key in agent_keys:
            self.assertIn(agent_key, agent_bins)
            self.assertIsInstance(agent_bins[agent_key], agents.AgentBin)
            self.assertEqual(agent_bins[agent_key], {})
            self.assertEqual(agent_bins[agent_key].agent_key, agent_key)
            self.assertIsInstance(agent_bins[agent_key].counts,
                                  counter.Counts)
            for attr, things in attrs[agent_key].items():
                values, removal = things
                self.assertIsInstance(agent_bins[agent_key].counts[attr],
                                      counter.Count)
                self.assertEqual(agent_bins[agent_key].counts[attr].attr, attr)
                self.assertEqual(agent_bins[agent_key].counts[attr].removal,
                                 removal)
                for key, value in agent_bins[agent_key].counts[attr].items():
                    self.assertIn(key, values)
                    self.assertEqual(value, 0)
                for value in values:
                    self.assertIn(value, agent_bins[agent_key].counts[attr])
                    self.assertEqual(agent_bins[agent_key].counts[attr][value],
                                     0)
                self.assertEqual(len(agent_bins[agent_key].counts[attr]), 3)
                self.assertIsInstance(agent_bins[agent_key].
                                        counts[attr].data_columns,
                                      counter.DataColumns)
                self.assertEqual(agent_bins[agent_key].
                                    counts[attr].data_columns.attr, attr)
                for key, column in agent_bins[agent_key].counts[attr].\
                        data_columns.items():
                    self.assertIn(key, values)
                    self.assertIsInstance(column, counter.DataColumn)
                    self.assertEqual(column.attr_value, key)
                    self.assertEqual(column, [])
                for value in values:
                    self.assertIn(value,
                                  agent_bins[agent_key].counts[attr].
                                    data_columns)
                    self.assertIsInstance(agent_bins[agent_key].counts[attr].
                                            data_columns[value],
                                          counter.DataColumn)
                    self.assertEqual(agent_bins[agent_key].counts[attr].
                                         data_columns[value].attr_value,
                                     value)
                    self.assertEqual(agent_bins[agent_key].counts[attr].
                                     data_columns[value], [])
                self.assertEqual(len(agent_bins[agent_key].counts[attr].
                                        data_columns), 3)
            self.assertEqual(len(agent_bins[agent_key].counts), 3)
        self.assertEqual(len(agent_bins), 3)

        # no attrs
        agent_bins = self.AgentsBin.make_bins(agent_keys, {})
        for agent_key in agent_keys:
            self.assertIsInstance(agent_bins[agent_key], agents.AgentBin)
            self.assertEqual(agent_bins[agent_key], {})
            self.assertEqual(agent_bins[agent_key].agent_key, agent_key)
            self.assertIsInstance(agent_bins[agent_key].counts, counter.Counts)
            self.assertEqual(agent_bins[agent_key].counts, {})
        self.assertEqual(len(agent_bins), 3)

    def test_get_attrs(self):
        """test get the correct attrs system"""

        location = mk.create_autospec(agent_location.Location, spec_set=True)

        attrs = mk.MagicMock(spec=dict)
        attrs.__contains__.side_effect = [False, True]

        # Test incorrect level
        self.assertEqual(self.AgentsBin.get_attrs(location, attrs), {})
        self.assertEqual(attrs.__contains__.call_args_list,
                         [mk.call(location.level)])

        attrs.reset_mock()
        # Test incorrect level
        self.assertEqual(self.AgentsBin.get_attrs(location, attrs),
                         attrs.__getitem__.return_value)
        self.assertEqual(attrs.__getitem__.call_args_list,
                         [mk.call(location.level)])
        self.assertEqual(attrs.__contains__.call_args_list,
                         [mk.call(location.level)])
        
    def test_empty(self):
        """test create an empty class"""

        agent_keys  = mk.MagicMock(spec=list)
        location    = mk.create_autospec(agent_location.Location, spec_set=True)
        attrs       = mk.MagicMock(spec=dict)
        environment = mk.MagicMock(spec=tuple)

        with mk.patch.object(agents.AgentsBin, 'get_attrs',
                             autospec=True) as mkAttrs:
            with mk.patch.object(agents.AgentsBin, 'make_bins',
                                 autospec=True) as mkBins:
                with mk.patch.object(agents.AgentsBin, 'make_environment',
                                     autospec=True) as mkEnvironment:
                    mkBins.return_value        = self.agents
                    mkEnvironment.return_value = self.environment

                    self.AgentsBin = agents.AgentsBin.empty(agent_keys,
                                                            location,
                                                            attrs,
                                                            environment)
                    self.assertIsInstance(self.AgentsBin, agents.AgentsBin)
                    self.assertEqual(self.AgentsBin.location_key,
                                     location.location_key)
                    self.assertEqual(self.AgentsBin.environment,
                                     self.environment)
                    self.assertEqual(self.AgentsBin,      self.agents)
                    self.assertEqual(self.AgentsBin.data, self.agents)

                    self.assertEqual(mkEnvironment.call_args_list,
                                     [mk.call(location, environment)])
                    self.assertEqual(mkBins.call_args_list,
                                     [mk.call(agent_keys,
                                              mkAttrs.return_value)])
                    self.assertEqual(mkAttrs.call_args_list,
                                     [mk.call(location, attrs)])


class TestAgents(ut.TestCase):
    """test the Agents class"""

    def setUp(self):
        """Setup the tests"""

        self.master = mk.create_autospec(agents.AgentsBin, spec_set=True)
        self.agents = {mk.MagicMock(spec=tuple):
                           mk.create_autospec(agents.AgentsBin, spec_set=True)
                       for _ in range(3)}
        self.agents[(0,)] = self.master

        self.Agents = agents.Agents(self.agents)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Agents, collect.UserDict)
        self.assertIsInstance(self.Agents, agents.Agents)

        self.assertEqual(self.Agents,      self.agents)
        self.assertEqual(self.Agents.data, self.agents)

        self.assertEqual(len(self.Agents), 4)

    def test_agents(self):
        """test get the master agents location"""

        agent_key = mk.MagicMock(spec=str)

        self.master.__getitem__.return_value = \
            mk.create_autospec(AgentBinTest, spec_set=True)

        self.assertEqual(self.Agents.agents(agent_key),
                         self.master.__getitem__.return_value.agents)
        self.assertEqual(self.master.__getitem__.call_args_list,
                         [mk.call(agent_key)])

    def test_activate(self):
        """test activate an agent"""

        location = agent_location.Location([0,
                                            mk.MagicMock(spec=int),
                                            mk.MagicMock(spec=int)])

        location_keys = [(0,)]
        for index in range(2, 4):
            key = location[:index].location_key
            self.Agents[key] = mk.create_autospec(agents.AgentsBin,
                                                  spec_set=True)
            location_keys.append(key)
        self.assertEqual(len(self.Agents), 6)

        agent = mk.create_autospec(AgentTest, spec_set=True)
        agent.location = location

        self.Agents.activate(agent)
        for location_key in self.Agents.keys():
            if location_key in location_keys:
                self.assertEqual(self.Agents[location_key].
                                    activate.call_args_list,
                                 [mk.call(agent)])
            else:
                self.assertEqual(self.Agents[location_key].
                                    activate.call_args_list,
                                 [])

    def test_deactivate(self):
        """test deactivate an agent"""

        location = agent_location.Location([0,
                                            mk.MagicMock(spec=int),
                                            mk.MagicMock(spec=int)])

        location_keys = [(0,)]
        for index in range(2, 4):
            key = location[:index].location_key
            self.Agents[key] = mk.create_autospec(agents.AgentsBin,
                                                  spec_set=True)
            location_keys.append(key)
        self.assertEqual(len(self.Agents), 6)

        agent = mk.create_autospec(AgentTest, spec_set=True)
        agent.location = location

        self.Agents.deactivate(agent)
        for location_key in self.Agents.keys():
            if location_key in location_keys:
                self.assertEqual(self.Agents[location_key].
                                 deactivate.call_args_list,
                                 [mk.call(agent)])
            else:
                self.assertEqual(self.Agents[location_key].
                                 deactivate.call_args_list,
                                 [])

    def test_record(self):
        """test record all the counts"""

        self.Agents.record()
        for agent_bin in self.agents.values():
            self.assertEqual(agent_bin.record.call_args_list,
                             [mk.call()])

    def test_refresh(self):
        """test refresh all the storage"""

        self.Agents.refresh()
        for agent_bin in self.agents.values():
            self.assertEqual(agent_bin.refresh.call_args_list,
                             [mk.call()])

    def test_dataframes(self):
        """test generate a dict of all dataframes"""

        dataframes = {}
        for agent_bin in self.agents.values():
            data_dict = {mk.MagicMock(spec=str): mk.MagicMock()
                         for _ in range(3)}
            dataframes.update(data_dict)
            agent_bin.dataframes.return_value = data_dict

        self.assertEqual(len(dataframes), 12)

        self.assertEqual(self.Agents.dataframes(), dataframes)
        for agent_bin in self.agents.values():
            self.assertEqual(agent_bin.dataframes.call_args_list,
                             [mk.call()])

    def test_empty(self):
        """test create an empty agents system"""

        locations  = [mk.create_autospec(agent_location.Location, spec_set=True)
                      for _ in range(3)]
        space = mk.create_autospec(SpaceTest, spec_set=True)
        space.locations = locations

        agent_keys  = mk.MagicMock(spec=list)
        attrs       = mk.MagicMock(spec=dict)
        environment = mk.MagicMock(spec=tuple)

        agent_bins = [mk.create_autospec(agents.AgentsBin, spec_set=True)
                      for _ in range(3)]

        with mk.patch.object(agents.AgentsBin, 'empty',
                             autospec=True) as mkEmpty:
            mkEmpty.side_effect = agent_bins

            self.Agents = agents.Agents.empty(space, agent_keys,
                                              attrs, environment)
            self.assertIsInstance(self.Agents, agents.Agents)

            for index, location in enumerate(locations):
                location_key = location.location_key
                self.assertIn(location_key, self.Agents)
                self.assertEqual(self.Agents[location_key], agent_bins[index])
                self.assertEqual(mkEmpty.call_args_list[index],
                                 mk.call(agent_keys, location,
                                         attrs, environment))
            for index, things in enumerate(self.Agents.items()):
                location_key, agent_bin = things
                self.assertEqual(location_key, locations[index].location_key)
                self.assertEqual(agent_bin, agent_bins[index])
                self.assertEqual(mkEmpty.call_args_list[index],
                                 mk.call(agent_keys, locations[index],
                                         attrs, environment))
            self.assertEqual(len(self.Agents), 3)
