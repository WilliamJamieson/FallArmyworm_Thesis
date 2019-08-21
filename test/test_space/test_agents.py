import unittest      as ut
import unittest.mock as mk

import collections as collect

import source.agents.agent as main_agent

import source.data.counter as counter

import source.space.agents   as agents
import source.space.location as agent_location


class AgentTest(main_agent.Agent):
    """Class to add dynamic values for tests"""

    agent_key = mk.MagicMock(spec=str)
    unique_id = mk.MagicMock(spec=str)
    location  = mk.create_autospec(agent_location.Location, spec_set=True)


class TestAgentBin(ut.TestCase):
    """test AgentBin class"""

    def setUp(self):
        """Setup the tests"""

        self.agents = []
        for _ in range(3):
            agent = mk.create_autospec(AgentTest, spec_set=True)
            self.agents.append(agent)

        self.counts    = mk.create_autospec(counter.Counts, spec_set=True)
        self.agent_key = mk.MagicMock(spec=str)

        self.AgentBin = agents.AgentBin(self.agents,
                                        self.counts,
                                        self.agent_key)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.AgentBin, collect.UserList)
        self.assertIsInstance(self.AgentBin, agents.AgentBin)

        self.assertEqual(self.AgentBin.counts,    self.counts)
        self.assertEqual(self.AgentBin.agent_key, self.agent_key)

        self.assertEqual(self.AgentBin,      self.agents)
        self.assertEqual(self.AgentBin.data, self.agents)

    def test_activate(self):
        """test activate an agent"""

        agent = mk.create_autospec(AgentTest, spec_set=True)

        self.assertNotIn(agent, self.AgentBin)
        self.AgentBin.activate(agent)
        self.assertIn(agent, self.AgentBin)
        self.assertEqual(self.AgentBin[-1], agent)
        self.assertEqual(self.counts.add.call_args_list,
                         [mk.call(agent)])

        self.assertNotEqual(self.AgentBin, self.agents)

    def test_deactivate(self):
        """test deactivate"""

        self.assertEqual(len(self.AgentBin), 3)
        for agent in self.agents:
            self.assertIn(agent, self.AgentBin)
            self.AgentBin.deactivate(agent)
            self.assertNotIn(agent, self.AgentBin)
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
        self.assertEqual(self.AgentBin, [])
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


class AgentBinTest(agents.AgentBin):
    """Class to add dynamic values for agent_bin tests"""

    counts = mk.create_autospec(counter.Counts, spec_set=True)


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
        self.environment  = mk.MagicMock(spec=dict)

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
            
    def test_dataframes(self):
        """test create a dictionary of dataframes"""

        dataframes = {}
        for agent_key, agent_bin in self.agents.items():
            key = '{}_{}'.format(self.location_key, agent_key)
            agent_bin.counts = mk.create_autospec(counter.Counts, spec_set=True)
            dataframe = mk.MagicMock()
            agent_bin.counts.dataframe.return_value = dataframe
            dataframes[key] = dataframe
        self.assertEqual(len(dataframes), 3)

        self.assertEqual(self.AgentsBin.dataframes(), dataframes)
        for agent_bin in self.AgentsBin.values():
            self.assertEqual(agent_bin.counts.dataframe.call_args_list,
                             [mk.call()])

    def test_empty(self):
        """test create an empty class"""

        agent_keys = []
        attrs      = {}
        for _ in range(3):
            attr = {}
            for _ in range(3):
                values = [mk.MagicMock(spec=str) for _ in range(3)]
                removal = mk.MagicMock(spec=bool)
                attr[mk.MagicMock(spec=str)] = (values, removal)
                
            agent_key = mk.MagicMock(spec=int)
            agent_keys.append(agent_key)
            attrs[agent_key] = attr

        # Has attrs for agent keys
        self.AgentsBin = agents.AgentsBin.empty(agent_keys,
                                                self.location_key,
                                                attrs)
        self.assertIsInstance(self.AgentsBin, agents.AgentsBin)
        self.assertEqual(self.AgentsBin.location_key, self.location_key)
        self.assertEqual(self.AgentsBin.environment,  {})

        for agent_key in agent_keys:
            self.assertIsInstance(self.AgentsBin[agent_key], agents.AgentBin)
            self.assertEqual(self.AgentsBin[agent_key], [])
            self.assertEqual(self.AgentsBin[agent_key].agent_key, agent_key)
            self.assertIsInstance(self.AgentsBin[agent_key].counts,
                                  counter.Counts)
            for attr, things in attrs[agent_key].items():
                values, removal = things
                self.assertIsInstance(self.AgentsBin[agent_key].counts[attr],
                                      counter.Count)
                self.assertEqual(self.AgentsBin[agent_key].counts[attr].attr,
                                 attr)
                self.assertEqual(self.AgentsBin[agent_key].counts[attr].removal,
                                 removal)
                for key, value in \
                        self.AgentsBin[agent_key].counts[attr].items():
                    self.assertIn(key, values)
                    self.assertEqual(value, 0)
                for value in values:
                    self.assertIn(value, self.AgentsBin[agent_key].counts[attr])
                    self.assertEqual(self.AgentsBin[agent_key].
                                        counts[attr][value],
                                     0)
                self.assertIsInstance(self.AgentsBin[agent_key].
                                        counts[attr].data_columns,
                                      counter.DataColumns)
                self.assertEqual(self.AgentsBin[agent_key].counts[attr].
                                    data_columns.attr,
                                 attr)
                for key, column in self.AgentsBin[agent_key].counts[attr].\
                        data_columns.items():
                    self.assertIn(key, values)
                    self.assertIsInstance(column, counter.DataColumn)
                    self.assertEqual(column.attr_value, key)
                    self.assertEqual(column, [])
                for value in values:
                    self.assertIn(value,
                                  self.AgentsBin[agent_key].counts[attr].
                                    data_columns)
                    self.assertIsInstance(self.AgentsBin[agent_key].
                                            counts[attr].data_columns[value],
                                          counter.DataColumn)
                    self.assertEqual(self.AgentsBin[agent_key].counts[attr].
                                        data_columns[value].attr_value,
                                     value)
                    self.assertEqual(self.AgentsBin[agent_key].counts[attr].
                                        data_columns[value],
                                     [])

        # No attrs
        self.AgentsBin = agents.AgentsBin.empty(agent_keys,
                                                self.location_key,
                                                {})
        self.assertIsInstance(self.AgentsBin, agents.AgentsBin)
        self.assertEqual(self.AgentsBin.location_key, self.location_key)
        self.assertEqual(self.AgentsBin.environment,  {})

        for agent_key in agent_keys:
            self.assertIsInstance(self.AgentsBin[agent_key], agents.AgentBin)
            self.assertEqual(self.AgentsBin[agent_key], [])
            self.assertEqual(self.AgentsBin[agent_key].agent_key, agent_key)
            self.assertIsInstance(self.AgentsBin[agent_key].counts,
                                  counter.Counts)
            self.assertEqual(self.AgentsBin[agent_key].counts, {})


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
                         self.master.__getitem__.return_value)
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
                
    def test_empty(self):
        """test create an empty agents system"""

        locations  = [mk.create_autospec(agent_location.Location, spec_set=True)
                      for _ in range(3)]
        agent_keys = [mk.MagicMock(spec=str)   for _ in range(3)]

        attrs = {}
        for location in locations:
            location_key = location.location_key
            agent_attrs = {}
            for agent_key in agent_keys:
                attr = {}
                for _ in range(3):
                    values = [mk.MagicMock(spec=str) for _ in range(3)]
                    removal = mk.MagicMock(spec=bool)

                    attr[mk.MagicMock(spec=str)] = (values, removal)
                agent_attrs[agent_key] = attr
            attrs[location_key] = agent_attrs

        # Has attrs for location keys
        self.Agents = agents.Agents.empty(locations,
                                          agent_keys,
                                          attrs)
        self.assertIsInstance(self.Agents, agents.Agents)

        for location in locations:
            location_key = location.location_key
            self.assertIsInstance(self.Agents[location_key], agents.AgentsBin)
            self.assertEqual(self.Agents[location_key].location_key,
                             location_key)
            self.assertEqual(self.Agents[location_key].environment,  {})

            for agent_key in agent_keys:
                self.assertIsInstance(self.Agents[location_key][agent_key],
                                      agents.AgentBin)
                self.assertEqual(self.Agents[location_key][agent_key], [])
                self.assertEqual(self.Agents[location_key][agent_key].agent_key,
                                 agent_key)
                self.assertIsInstance(self.Agents[location_key][agent_key].
                                        counts,
                                      counter.Counts)
                for attr, things in attrs[location_key][agent_key].items():
                    values, removal = things
                    self.assertIsInstance(self.Agents[location_key][agent_key].
                                            counts[attr],
                                          counter.Count)
                    self.assertEqual(self.Agents[location_key][agent_key].
                                        counts[attr].attr,
                                     attr)
                    self.assertEqual(self.Agents[location_key][agent_key].
                                     counts[attr].removal,
                                     removal)
                    for key, value in self.Agents[location_key][agent_key].\
                            counts[attr].items():
                        self.assertIn(key, values)
                        self.assertEqual(value, 0)
                    for value in values:
                        self.assertIn(value,
                                      self.Agents[location_key][agent_key].
                                        counts[attr])
                        self.assertEqual(self.Agents[location_key][agent_key].
                                            counts[attr][value],
                                         0)
                    self.assertIsInstance(self.Agents[location_key][agent_key].
                                            counts[attr].data_columns,
                                          counter.DataColumns)
                    self.assertEqual(self.Agents[location_key][agent_key].
                                        counts[attr].data_columns.attr,
                                     attr)
                    for key, column in self.Agents[location_key][agent_key].\
                            counts[attr].data_columns.items():
                        self.assertIn(key, values)
                        self.assertIsInstance(column, counter.DataColumn)
                        self.assertEqual(column.attr_value, key)
                        self.assertEqual(column, [])
                    for value in values:
                        self.assertIn(value,
                                      self.Agents[location_key][agent_key].
                                        counts[attr].data_columns)
                        self.assertIsInstance(self.Agents[location_key]
                                                [agent_key].counts[attr].
                                                data_columns[value],
                                              counter.DataColumn)
                        self.assertEqual(self.Agents[location_key][agent_key].
                                            counts[attr].data_columns[value].
                                            attr_value,
                                         value)
                        self.assertEqual(self.Agents[location_key][agent_key].
                                            counts[attr].data_columns[value],
                                         [])
        # No attrs
        self.Agents = agents.Agents.empty(locations,
                                          agent_keys,
                                          {})
        self.assertIsInstance(self.Agents, agents.Agents)

        for location in locations:
            location_key = location.location_key
            self.assertIsInstance(self.Agents[location_key], agents.AgentsBin)
            self.assertEqual(self.Agents[location_key].location_key,
                             location_key)
            self.assertEqual(self.Agents[location_key].environment,  {})

            for agent_key in agent_keys:
                self.assertIsInstance(self.Agents[location_key][agent_key],
                                      agents.AgentBin)
                self.assertEqual(self.Agents[location_key][agent_key], [])
                self.assertEqual(self.Agents[location_key][agent_key].agent_key,
                                 agent_key)
                self.assertIsInstance(self.Agents[location_key][agent_key].
                                      counts,
                                      counter.Counts)
                self.assertEqual(self.Agents[location_key][agent_key].counts,
                                 {})
