import unittest      as ut
import unittest.mock as mk

import collections as collect
import dataclasses as d_class

import pandas as pd

import source.keyword as keyword

import source.agents.agent as main_agent

import source.data.counter as counter


class CountTest(counter.Count):
    """Class to add dynamic values for agent tests"""

    data_columns = mk.create_autospec(counter.DataColumns, spec_set=True)


@d_class.dataclass
class InsectTest(main_agent.Agent):
    """calls to define a new agent"""

    death:    str
    genotype: str


class TestDataColumn(ut.TestCase):
    """test the DataColumn class"""

    def setUp(self):
        """Setup the tests"""

        self.data = [mk.MagicMock(spec=int) for _ in range(3)]

        self.attr_value = mk.MagicMock(spec=str)

        self.DataColumn = counter.DataColumn(self.data,
                                             self.attr_value)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.DataColumn, collect.UserList)
        self.assertIsInstance(self.DataColumn, counter.DataColumn)

        self.assertEqual(self.DataColumn.attr_value, self.attr_value)

        self.assertEqual(self.DataColumn,      self.data)
        self.assertEqual(self.DataColumn.data, self.data)

    def test_record(self):
        """test record a count"""

        count = mk.create_autospec(counter.Count, spec_set=True)

        with mk.patch.object(counter.DataColumn, 'append',
                             autospec=True) as mkAppend:
            self.DataColumn.record(count)
            self.assertEqual(mkAppend.call_args_list,
                             [mk.call(self.data,
                                      count.__getitem__.return_value)])
            self.assertEqual(count.__getitem__.call_args_list,
                             [mk.call(self.attr_value)])

        count.reset_mock()
        self.DataColumn.record(count)
        self.assertEqual(self.DataColumn[-1], count.__getitem__.return_value)
        self.assertNotEqual(self.data, self.DataColumn)

    def test_empty(self):
        """test create an empty data column"""

        self.DataColumn = counter.DataColumn.empty(self.attr_value)
        self.assertIsInstance(self.DataColumn, counter.DataColumn)
        self.assertEqual(self.DataColumn.attr_value, self.attr_value)
        self.assertEqual(self.DataColumn, [])


class TestDataColumns(ut.TestCase):
    """test DataColumns class"""

    def setUp(self):
        """Setup the tests"""

        self.data = {mk.MagicMock(spec=str):
                         mk.create_autospec(counter.DataColumn, spec_set=True)
                     for _ in range(3)}

        self.attr = mk.MagicMock(spec=str)

        self.DataColumns = counter.DataColumns(self.data,
                                               self.attr)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.DataColumns, collect.UserDict)
        self.assertIsInstance(self.DataColumns, counter.DataColumns)

        self.assertEqual(self.DataColumns.attr, self.attr)

        self.assertEqual(self.DataColumns,      self.data)
        self.assertEqual(self.DataColumns.data, self.data)

    def test_record(self):
        """test record all counts for attr"""

        count = mk.create_autospec(counter.Count, spec_set=True)

        self.DataColumns.record(count)
        for column in self.data.values():
            self.assertEqual(column.record.call_args_list,
                             [mk.call(count)])

    def test_refresh(self):
        """test refresh the data columns"""

        self.DataColumns.refresh()
        for column in self.data.values():
            self.assertEqual(column.clear.call_args_list,
                             [mk.call()])

    def test_columns(self):
        """test generate all the columns of data"""

        columns = self.DataColumns.columns()

        self.assertIsInstance(columns, dict)

        for key, value in self.data.items():
            column_key = '{}_{}'.format(self.attr, key)
            self.assertIn(column_key, columns)
            self.assertEqual(columns[column_key], value)
        self.assertEqual(len(columns), len(self.data))

    def test_empty(self):
        """test create an empty set of data columns"""

        attr_values = [mk.MagicMock(spec=str) for _ in range(3)]

        self.DataColumns = counter.DataColumns.empty(self.attr,
                                                     attr_values)
        self.assertIsInstance(self.DataColumns, counter.DataColumns)
        self.assertEqual(self.DataColumns.attr, self.attr)

        for key, value in self.DataColumns.items():
            self.assertIn(key, attr_values)
            self.assertIsInstance(value, counter.DataColumn)
            self.assertEqual(value.attr_value, key)
            self.assertEqual(value, [])
        for attr_value in attr_values:
            self.assertIn(attr_value, self.DataColumns)
            self.assertIsInstance(self.DataColumns[attr_value],
                                  counter.DataColumn)
            self.assertEqual(self.DataColumns[attr_value].attr_value,
                             attr_value)
            self.assertEqual(self.DataColumns[attr_value], [])


class TestBaseCount(ut.TestCase):
    """test BaseCount class"""

    def setUp(self):
        """Setup the tests"""

        self.counts = {mk.MagicMock(spec=str): mk.MagicMock(spec=int)
                       for _ in range(3)}

        self.attr = mk.MagicMock(spec=str)

        self.Count = counter.BaseCount(self.counts,
                                       self.attr)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Count, collect.UserDict)
        self.assertIsInstance(self.Count, counter.BaseCount)

        self.assertEqual(self.Count.attr, self.attr)

        self.assertEqual(self.Count,      self.counts)
        self.assertEqual(self.Count.data, self.counts)

    def test_add(self):
        """test add count"""

        agent = mk.create_autospec(main_agent.Agent, spec_set=True)

        self.assertIsNone(self.Count.add(agent))

    def test_sub(self):
        """test sub count"""

        agent = mk.create_autospec(main_agent.Agent, spec_set=True)

        self.assertIsNone(self.Count.sub(agent))

    def test_record(self):
        """test record counts"""

        self.assertIsNone(self.Count.record())

    def test_refresh(self):
        """test refresh counts"""

        self.assertIsNone(self.Count.refresh())

    def test_get_data_columns(self):
        """test get the data columns"""

        self.assertIsNone(self.Count.get_data_columns())


class TestCount(ut.TestCase):
    """test Count class"""

    def setUp(self):
        """Setup the tests"""

        self.counts = {mk.MagicMock(spec=str): mk.MagicMock(spec=int)
                       for _ in range(3)}

        self.attr    = mk.MagicMock(spec=str)
        self.removal = mk.MagicMock(spec=bool)

        self.data_columns = mk.create_autospec(counter.DataColumns,
                                               spec_set=True)

        self.Count = counter.Count(self.counts,
                                   self.attr,
                                   self.removal,
                                   self.data_columns)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Count, collect.UserDict)
        self.assertIsInstance(self.Count, counter.BaseCount)
        self.assertIsInstance(self.Count, counter.Count)

        self.assertEqual(self.Count.attr,    self.attr)
        self.assertEqual(self.Count.removal, self.removal)

        self.assertEqual(self.Count.data_columns, self.data_columns)

        self.assertEqual(self.Count,      self.counts)
        self.assertEqual(self.Count.data, self.counts)

    def test_add(self):
        """test add agent to counter"""

        # Call test
        agent = mk.create_autospec(main_agent.Agent, spec_set=True)

        with mk.patch.object(counter, 'getattr') as mkGet:
            # Removal is True
            self.Count.removal = True
            self.Count.add(agent)
            self.assertEqual(mkGet.call_args_list, [])
            for key, value in self.Count.items():
                self.assertEqual(self.counts[key], value)

            # Removal is False
            self.Count.removal = False
            for value in self.counts.keys():
                mkGet.return_value = value
                self.Count.add(agent)
                self.assertEqual(mkGet.call_args_list,
                                 [mk.call(agent, self.attr)])
                mkGet.reset_mock()

                self.assertNotEqual(self.Count[value], self.counts[value])
                self.assertEqual(self.Count[value],
                                 self.counts[value].__add__.return_value)
                self.assertEqual(self.counts[value].__add__.call_args_list,
                                 [mk.call(1)])
            for value in self.counts.keys():
                self.assertEqual(self.Count[value],
                                 self.counts[value].__add__.return_value)

        # Practical test
        # noinspection PyTypeChecker
        agent = main_agent.Agent('test', 'test0', None, [0], True)
        # noinspection PyTypeChecker
        count = counter.Count.empty('alive', [True, False], False)
        self.assertEqual(count[True], 0)
        count.add(agent)
        self.assertEqual(count[True], 1)
        # noinspection PyTypeChecker
        agent = main_agent.Agent('test', 'test0', None, [0], False)
        self.assertEqual(count[False], 0)
        count.add(agent)
        self.assertEqual(count[False], 1)
        # noinspection PyTypeChecker
        agent = main_agent.Agent('test', 'test0', None, [0], True)
        # noinspection PyTypeChecker
        count = counter.Count.empty('alive', [True, False], True)
        self.assertEqual(count[True], 0)
        count.add(agent)
        self.assertEqual(count[True], 0)
        # noinspection PyTypeChecker
        agent = main_agent.Agent('test', 'test0', None, [0], False)
        self.assertEqual(count[False], 0)
        count.add(agent)
        self.assertEqual(count[False], 0)

    def test_sub(self):
        """test sub agent to counter"""

        agent = mk.create_autospec(main_agent.Agent, spec_set=True)

        with mk.patch.object(counter, 'getattr') as mkGet:
            # Removal is True
            self.Count.removal = True
            #   Test remove non-present
            self.Count.sub(agent)
            self.assertEqual(mkGet.call_args_list,
                             [mk.call(agent, self.attr)])
            mkGet.reset_mock()
            self.assertEqual(self.Count, self.counts)
            #   Test remove present
            for value in self.counts.keys():
                mkGet.return_value = value
                self.Count.sub(agent)
                self.assertEqual(mkGet.call_args_list,
                                 [mk.call(agent, self.attr)])
                mkGet.reset_mock()

                self.assertNotEqual(self.Count[value], self.counts[value])
                self.assertEqual(self.Count[value],
                                 self.counts[value].__add__.return_value)
                self.assertEqual(self.counts[value].__add__.call_args_list,
                                 [mk.call(1)])
            for value in self.counts.keys():
                self.assertEqual(self.Count[value],
                                 self.counts[value].__add__.return_value)

            self.Count = counter.Count(self.counts,
                                       self.attr,
                                       self.removal,
                                       self.data_columns)
            # Removal is False
            self.Count.removal = False
            for value in self.counts.keys():
                mkGet.return_value = value
                self.Count.sub(agent)
                self.assertEqual(mkGet.call_args_list,
                                 [mk.call(agent, self.attr)])
                mkGet.reset_mock()

                self.assertNotEqual(self.Count[value], self.counts[value])
                self.assertEqual(self.Count[value],
                                 self.counts[value].__sub__.return_value)
                self.assertEqual(self.counts[value].__sub__.call_args_list,
                                 [mk.call(1)])
            for value in self.counts.keys():
                self.assertEqual(self.Count[value],
                                 self.counts[value].__sub__.return_value)

        # Practical test
        # noinspection PyTypeChecker
        agent = main_agent.Agent('test', 'test0', None, [0], True)
        # noinspection PyTypeChecker
        count = counter.Count.empty('alive', [True, False], False)
        self.assertEqual(count[True], 0)
        count.sub(agent)
        self.assertEqual(count[True], -1)
        # noinspection PyTypeChecker
        agent = main_agent.Agent('test', 'test0', None, [0], False)
        self.assertEqual(count[False], 0)
        count.sub(agent)
        self.assertEqual(count[False], -1)
        # noinspection PyTypeChecker
        agent = main_agent.Agent('test', 'test0', None, [0], True)
        # noinspection PyTypeChecker
        count = counter.Count.empty('alive', [True, False], True)
        self.assertEqual(count[True], 0)
        count.sub(agent)
        self.assertEqual(count[True], 1)
        # noinspection PyTypeChecker
        agent = main_agent.Agent('test', 'test0', None, [0], False)
        self.assertEqual(count[False], 0)
        count.sub(agent)
        self.assertEqual(count[False], 1)

    def test__reset(self):
        """test reset the count"""

        self.assertEqual(self.Count, self.counts)
        self.Count._reset()
        self.assertNotEqual(self.Count, self.counts)

        for key in self.counts:
            self.assertIn(key, self.Count)
            self.assertEqual(self.Count[key], 0)

    def test_record(self):
        """test record the counts"""

        with mk.patch.object(counter.Count, '_reset', autospec=True) as mkReset:
            # Removal is False
            self.Count.removal = False
            self.Count.record()
            self.assertEqual(self.data_columns.record.call_args_list,
                             [mk.call(self.Count)])
            self.assertEqual(mkReset.call_args_list, [])

            self.data_columns.reset_mock()
            # Removal is true
            self.Count.removal = True
            self.Count.record()
            self.assertEqual(self.data_columns.record.call_args_list,
                             [mk.call(self.Count)])
            self.assertEqual(mkReset.call_args_list,
                             [mk.call(self.Count)])

    def test_refresh(self):
        """test refresh the stored values"""

        master = mk.MagicMock()
        master.attach_mock(self.data_columns, 'columns')

        self.Count.refresh()
        self.assertEqual(master.mock_calls,
                         [mk.call.columns.refresh(),
                          mk.call.columns.record(self.Count)])

    def test_get_data_columns(self):
        """test get the data columns"""

        self.assertEqual(self.Count.get_data_columns(),
                         self.data_columns.columns.return_value)
        self.assertEqual(self.data_columns.columns.call_args_list,
                         [mk.call()])

    def test_empty(self):
        """test create empty class"""

        values = [mk.MagicMock(spec=str) for _ in range(3)]

        self.Count = counter.Count.empty(self.attr, values, self.removal)
        self.assertIsInstance(self.Count, counter.Count)
        self.assertEqual(self.Count.attr,    self.attr)
        self.assertEqual(self.Count.removal, self.removal)
        for key, value in self.Count.items():
            self.assertIn(key, values)
            self.assertEqual(value, 0)
        for value in values:
            self.assertIn(value, self.Count)
            self.assertEqual(self.Count[value], 0)

        self.assertIsInstance(self.Count.data_columns, counter.DataColumns)
        self.assertEqual(self.Count.data_columns.attr, self.attr)
        for key, column in self.Count.data_columns.items():
            self.assertIn(key, values)
            self.assertIsInstance(column, counter.DataColumn)
            self.assertEqual(column.attr_value, key)
            self.assertEqual(column, [])
        for value in values:
            self.assertIn(value, self.Count.data_columns)
            self.assertIsInstance(self.Count.data_columns[value],
                                  counter.DataColumn)
            self.assertEqual(self.Count.data_columns[value].attr_value, value)
            self.assertEqual(self.Count.data_columns[value], [])
            
            
class TestCountFilter(ut.TestCase):
    """test CountFilter class"""

    def setUp(self):
        """Setup the tests"""

        self.counts = {}
        for _ in range(3):
            self.counts[mk.MagicMock(spec=str)] = \
                mk.create_autospec(CountTest, spec_set=True)
            self.counts[mk.MagicMock(spec=str)] = \
                mk.create_autospec(counter.CountFilter, spec_set=True)

        self.attr = mk.MagicMock(spec=str)

        self.Count = counter.CountFilter(self.counts,
                                         self.attr)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Count, collect.UserDict)
        self.assertIsInstance(self.Count, counter.BaseCount)
        self.assertIsInstance(self.Count, counter.CountFilter)

        self.assertEqual(self.Count.attr, self.attr)

        self.assertEqual(self.Count,      self.counts)
        self.assertEqual(self.Count.data, self.counts)

    def test_add(self):
        """test add agent to counter"""

        # Call test
        agent = mk.create_autospec(main_agent.Agent, spec_set=True)

        with mk.patch.object(counter, 'getattr') as mkGet:
            for value in self.counts.keys():
                mkGet.return_value = value
                self.Count.add(agent)
                self.assertEqual(mkGet.call_args_list,
                                 [mk.call(agent, self.attr)])
                mkGet.reset_mock()

                self.assertEqual(self.Count[value].add.call_args_list,
                                 [mk.call(agent)])
                self.Count[value].reset_mock()
            for value in self.counts.keys():
                self.assertEqual(self.Count[value].add.call_args_list, [])

        # Practical test
        # noinspection PyTypeChecker
        agent_sur_homo_r = InsectTest('test', 'test0', None, None, True,
                                      keyword.survival, keyword.homo_r)
        # noinspection PyTypeChecker
        agent_sur_hetero = InsectTest('test', 'test0', None, None, True,
                                      keyword.survival, keyword.hetero)
        # noinspection PyTypeChecker
        agent_sur_homo_s = InsectTest('test', 'test0', None, None, True,
                                      keyword.survival, keyword.homo_s)
        # noinspection PyTypeChecker
        agent_can_homo_r = InsectTest('test', 'test0', None, None, True,
                                      keyword.cannibalism, keyword.homo_r)
        # noinspection PyTypeChecker
        agent_can_hetero = InsectTest('test', 'test0', None, None, True,
                                      keyword.cannibalism, keyword.hetero)
        # noinspection PyTypeChecker
        agent_can_homo_s = InsectTest('test', 'test0', None, None, True,
                                      keyword.cannibalism, keyword.homo_s)
        attrs = {keyword.genotype: (keyword.genotype_keys, False)}
        count = counter.CountFilter.empty('death',
                                          keyword.death_keys,
                                          attrs)
        count.add(agent_sur_homo_r)
        count.add(agent_sur_hetero)
        count.add(agent_sur_homo_s)
        count.add(agent_can_homo_r)
        count.add(agent_can_hetero)
        count.add(agent_can_homo_s)
        count.record()

        count_data = count.get_data_columns()

        actual_deaths = [keyword.cannibalism, keyword.survival]
        other_deaths  = [key for key in keyword.death_keys
                         if key not in actual_deaths]

        for death_key in actual_deaths:
            for genotype_key in keyword.genotype_keys:
                key = '{}_{}_{}_{}'.format('death', death_key,
                                           'genotype', genotype_key)
                self.assertIn(key, count_data)
                self.assertEqual(count_data[key], [1])

        for death_key in other_deaths:
            for genotype_key in keyword.genotype_keys:
                key = '{}_{}_{}_{}'.format('death', death_key,
                                           'genotype', genotype_key)
                self.assertIn(key, count_data)
                self.assertEqual(count_data[key], [0])

    def test_sub(self):
        """test sub agent to counter"""

        # Call test
        agent = mk.create_autospec(main_agent.Agent, spec_set=True)

        with mk.patch.object(counter, 'getattr') as mkGet:
            for value in self.counts.keys():
                mkGet.return_value = value
                self.Count.sub(agent)
                self.assertEqual(mkGet.call_args_list,
                                 [mk.call(agent, self.attr)])
                mkGet.reset_mock()

                self.assertEqual(self.Count[value].sub.call_args_list,
                                 [mk.call(agent)])
                self.Count[value].reset_mock()
            for value in self.counts.keys():
                self.assertEqual(self.Count[value].sub.call_args_list, [])

        # Practical test
        # noinspection PyTypeChecker
        agent_sur_homo_r = InsectTest('test', 'test0', None, None, True,
                                      keyword.survival, keyword.homo_r)
        # noinspection PyTypeChecker
        agent_sur_hetero = InsectTest('test', 'test0', None, None, True,
                                      keyword.survival, keyword.hetero)
        # noinspection PyTypeChecker
        agent_sur_homo_s = InsectTest('test', 'test0', None, None, True,
                                      keyword.survival, keyword.homo_s)
        # noinspection PyTypeChecker
        agent_can_homo_r = InsectTest('test', 'test0', None, None, True,
                                      keyword.cannibalism, keyword.homo_r)
        # noinspection PyTypeChecker
        agent_can_hetero = InsectTest('test', 'test0', None, None, True,
                                      keyword.cannibalism, keyword.hetero)
        # noinspection PyTypeChecker
        agent_can_homo_s = InsectTest('test', 'test0', None, None, True,
                                      keyword.cannibalism, keyword.homo_s)
        attrs = {keyword.genotype: (keyword.genotype_keys, False)}
        count = counter.CountFilter.empty('death',
                                          keyword.death_keys,
                                          attrs)
        count.sub(agent_sur_homo_r)
        count.sub(agent_sur_hetero)
        count.sub(agent_sur_homo_s)
        count.sub(agent_can_homo_r)
        count.sub(agent_can_hetero)
        count.sub(agent_can_homo_s)
        count.record()

        count_data = count.get_data_columns()

        actual_deaths = [keyword.cannibalism, keyword.survival]
        other_deaths  = [key for key in keyword.death_keys
                         if key not in actual_deaths]

        for death_key in actual_deaths:
            for genotype_key in keyword.genotype_keys:
                key = '{}_{}_{}_{}'.format('death', death_key,
                                           'genotype', genotype_key)
                self.assertIn(key, count_data)
                self.assertEqual(count_data[key], [-1])

        for death_key in other_deaths:
            for genotype_key in keyword.genotype_keys:
                key = '{}_{}_{}_{}'.format('death', death_key,
                                           'genotype', genotype_key)
                self.assertIn(key, count_data)
                self.assertEqual(count_data[key], [0])

    def test_record(self):
        """test record data"""

        self.Count.record()
        for count in self.counts.values():
            self.assertEqual(count.record.call_args_list,
                             [mk.call()])

    def test_refresh(self):
        """test refresh data"""

        self.Count.refresh()
        for count in self.counts.values():
            self.assertEqual(count.refresh.call_args_list,
                             [mk.call()])

    def test_get_data_columns(self):
        """test get the data columns"""

        data_columns = {}
        for attr_value, count in self.counts.items():
            data_column = {mk.MagicMock(spec=str):
                               mk.create_autospec(counter.DataColumn,
                                                  spec_set=True)
                           for _ in range(3)}
            count.get_data_columns.return_value = data_column

            for key, value in data_column.items():
                data_key = '{}_{}_{}'.format(self.attr, attr_value, key)
                data_columns[data_key] = value

        self.assertEqual(self.Count.get_data_columns(), data_columns)
        for count in self.Count.values():
            self.assertEqual(count.get_data_columns.call_args_list,
                             [mk.call()])
            
    def test_empty(self):
        """test build an empty class"""

        values = [mk.MagicMock(spec=str) for _ in range(3)]

        # Single layer of filtering
        attr  = mk.MagicMock(spec=str)
        attrs = {attr:
                     ([mk.MagicMock(spec=str) for _ in range(3)],
                      mk.MagicMock(spec=bool))}
        attr_data = attrs[attr]

        self.Count = counter.CountFilter.empty(self.attr,
                                               values,
                                               attrs)
        self.assertIsInstance(self.Count, counter.CountFilter)
        self.assertEqual(self.Count.attr, self.attr)
        for value_key, count in self.Count.items():
            self.assertIn(value_key, values)
            self.assertIsInstance(count, counter.Count)
            self.assertEqual(count.attr,    attr)
            self.assertEqual(count.removal, attr_data[1])

            for key, value in count.items():
                self.assertIn(key, attr_data[0])
                self.assertEqual(value, 0)
            for key in attr_data[0]:
                self.assertIn(key, count)
                self.assertEqual(count[key], 0)

            self.assertIsInstance(count.data_columns, counter.DataColumns)
            self.assertEqual(count.data_columns.attr, attr)
            for key, column in count.data_columns.items():
                self.assertIn(key, attr_data[0])
                self.assertIsInstance(column, counter.DataColumn)
                self.assertEqual(column.attr_value, key)
                self.assertEqual(column, [])
            for value in attr_data[0]:
                self.assertIn(value, count.data_columns)
                self.assertIsInstance(count.data_columns[value],
                                      counter.DataColumn)
                self.assertEqual(count.data_columns[value].attr_value, value)
                self.assertEqual(count.data_columns[value], [])

        self.assertEqual(len(self.Count), 3)
        for value_key in values:
            self.assertIn(value_key, self.Count)
            count = self.Count[value_key]
            self.assertIsInstance(count, counter.Count)
            self.assertEqual(count.attr,    attr)
            self.assertEqual(count.removal, attr_data[1])

            for key, value in count.items():
                self.assertIn(key, attr_data[0])
                self.assertEqual(value, 0)
            for key in attr_data[0]:
                self.assertIn(key, count)
                self.assertEqual(count[key], 0)

            self.assertIsInstance(count.data_columns, counter.DataColumns)
            self.assertEqual(count.data_columns.attr, attr)
            for key, column in count.data_columns.items():
                self.assertIn(key, attr_data[0])
                self.assertIsInstance(column, counter.DataColumn)
                self.assertEqual(column.attr_value, key)
                self.assertEqual(column, [])
            for value in attr_data[0]:
                self.assertIn(value, count.data_columns)
                self.assertIsInstance(count.data_columns[value],
                                      counter.DataColumn)
                self.assertEqual(count.data_columns[value].attr_value, value)
                self.assertEqual(count.data_columns[value], [])

        # Two layers of filtering
        attrs = {mk.MagicMock(spec=str):
                     ([mk.MagicMock(spec=str) for _ in range(3)],
                      mk.MagicMock(spec=bool))
                 for _ in range(2)}
        attr_list = list(attrs.keys())
        attr_data_list = [attrs[key] for key in attr_list]

        self.Count = counter.CountFilter.empty(self.attr,
                                               values,
                                               attrs)
        self.assertIsInstance(self.Count, counter.CountFilter)
        self.assertEqual(self.Count.attr, self.attr)
        for value_key0, count0 in self.Count.items():
            attr0      = attr_list[0]
            attr_data0 = attr_data_list[0]
            self.assertIn(value_key0, values)
            self.assertIsInstance(count0, counter.CountFilter)
            self.assertEqual(count0.attr, attr0)
            for value_key1, count1 in count0.items():
                self.assertIn(value_key1, attr_data0[0])
                self.assertIsInstance(count1, counter.Count)
                attr1      = attr_list[1]
                attr_data1 = attr_data_list[1]
                self.assertEqual(count1.attr,    attr1)
                self.assertEqual(count1.removal, attr_data1[1])

                for key, value in count1.items():
                    self.assertIn(key, attr_data1[0])
                    self.assertEqual(value, 0)
                for key in attr_data1[0]:
                    self.assertIn(key, count1)
                    self.assertEqual(count1[key], 0)

                self.assertIsInstance(count1.data_columns, counter.DataColumns)
                self.assertEqual(count1.data_columns.attr, attr1)
                for key, column in count1.data_columns.items():
                    self.assertIn(key, attr_data1[0])
                    self.assertIsInstance(column, counter.DataColumn)
                    self.assertEqual(column.attr_value, key)
                    self.assertEqual(column, [])
                for value in attr_data1[0]:
                    self.assertIn(value, count1.data_columns)
                    self.assertIsInstance(count1.data_columns[value],
                                          counter.DataColumn)
                    self.assertEqual(count1.data_columns[value].attr_value,
                                     value)
                    self.assertEqual(count1.data_columns[value], [])

        self.assertEqual(len(self.Count), 3)
        for value_key in values:
            self.assertIn(value_key, self.Count)
            count0     = self.Count[value_key]
            attr0      = attr_list[0]
            attr_data0 = attr_data_list[0]
            self.assertIsInstance(count0, counter.CountFilter)
            self.assertEqual(count0.attr, attr0)
            for value_key1, count1 in count0.items():
                self.assertIn(value_key1, attr_data0[0])
                self.assertIsInstance(count1, counter.Count)
                attr1      = attr_list[1]
                attr_data1 = attr_data_list[1]
                self.assertEqual(count1.attr,    attr1)
                self.assertEqual(count1.removal, attr_data1[1])

                for key, value in count1.items():
                    self.assertIn(key, attr_data1[0])
                    self.assertEqual(value, 0)
                for key in attr_data1[0]:
                    self.assertIn(key, count1)
                    self.assertEqual(count1[key], 0)

                self.assertIsInstance(count1.data_columns, counter.DataColumns)
                self.assertEqual(count1.data_columns.attr, attr1)
                for key, column in count1.data_columns.items():
                    self.assertIn(key, attr_data1[0])
                    self.assertIsInstance(column, counter.DataColumn)
                    self.assertEqual(column.attr_value, key)
                    self.assertEqual(column, [])
                for value in attr_data1[0]:
                    self.assertIn(value, count1.data_columns)
                    self.assertIsInstance(count1.data_columns[value],
                                          counter.DataColumn)
                    self.assertEqual(count1.data_columns[value].attr_value,
                                     value)
                    self.assertEqual(count1.data_columns[value], [])


class TestCounts(ut.TestCase):
    """test the Counts class"""

    def setUp(self):
        """Setup the tests"""

        self.counts = {}
        for _ in range(3):
            self.counts[mk.MagicMock(spec=str)] = \
                mk.create_autospec(CountTest, spec_set=True)
            self.counts[mk.MagicMock(spec=str)] = \
                mk.create_autospec(counter.CountFilter, spec_set=True)

        self.Counts = counter.Counts(self.counts)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Counts, collect.UserDict)
        self.assertIsInstance(self.Counts, counter.Counts)

        self.assertEqual(self.Counts,      self.counts)
        self.assertEqual(self.Counts.data, self.counts)

    def test_add(self):
        """test add to counts of all things"""

        agent = mk.create_autospec(main_agent.Agent, spec_set=True)

        self.Counts.add(agent)
        for count in self.counts.values():
            self.assertEqual(count.add.call_args_list,
                             [mk.call(agent)])

    def test_sub(self):
        """test sub from counts of all things"""

        agent = mk.create_autospec(main_agent.Agent, spec_set=True)

        self.Counts.sub(agent)
        for count in self.counts.values():
            self.assertEqual(count.sub.call_args_list,
                             [mk.call(agent)])

    def test_record(self):
        """test record the counts"""

        self.Counts.record()
        for count in self.counts.values():
            self.assertEqual(count.record.call_args_list,
                             [mk.call()])

    def test_refresh(self):
        """test refresh the stored data"""

        self.Counts.refresh()
        for count in self.counts.values():
            self.assertEqual(count.refresh.call_args_list,
                             [mk.call()])

    def test_columns(self):
        """test create all the columns of data"""

        columns = {}
        for count in self.counts.values():
            column = {}
            for _ in range(3):
                key   = mk.MagicMock(spec=str)
                value = mk.create_autospec(counter.DataColumn, spec_set=True)

                column[ key] = value
                columns[key] = value

            count.get_data_columns.return_value = column

        self.assertEqual(self.Counts.columns(), columns)
        for count in self.Counts.values():
            self.assertEqual(count.get_data_columns.call_args_list,
                             [mk.call()])

    def test_dataframe(self):
        """test create a dataframe of the data"""

        with mk.patch.object(counter.Counts, 'columns',
                             autospec=True) as mkColumns:
            with mk.patch.object(pd.DataFrame, 'from_dict',
                                 autospec=True) as mkDataFrame:
                self.assertEqual(self.Counts.dataframe(),
                                 mkDataFrame.return_value)
                self.assertEqual(mkDataFrame.call_args_list,
                                 [mk.call(mkColumns.return_value)])
                self.assertEqual(mkColumns.call_args_list,
                                 [mk.call(self.Counts)])

    def test_count(self):
        """test add a count to system"""

        attr_key = mk.MagicMock(spec=str)
        attr     = mk.MagicMock(spec=str)
        values   = [mk.MagicMock(spec=str) for _ in range(3)]

        # Add standard
        removal = mk.MagicMock(spec=bool)
        self.assertNotIn(attr_key, self.Counts)

        with mk.patch.object(counter.Count, 'empty', autospec=True) as mkEmpty:
            self.Counts.count(attr_key, attr, values, removal)
            self.assertIn(attr_key, self.Counts)
            self.assertEqual(self.Counts[attr_key],
                             mkEmpty.return_value)
            self.assertEqual(mkEmpty.call_args_list,
                             [mk.call(attr, values, removal)])

        del self.Counts[attr_key]

        # Add default
        self.assertNotIn(attr_key, self.Counts)

        with mk.patch.object(counter.Count, 'empty', autospec=True) as mkEmpty:
            self.Counts.count(attr_key, attr, values, {})
            self.assertIn(attr_key, self.Counts)
            self.assertEqual(self.Counts[attr_key],
                             mkEmpty.return_value)
            self.assertEqual(mkEmpty.call_args_list,
                             [mk.call(attr, values, False)])

        del self.Counts[attr_key]

        # Add filter stack
        attrs = {mk.MagicMock(spec=str): mk.MagicMock(spec=tuple)}
        self.assertNotIn(attr_key, self.Counts)

        with mk.patch.object(counter.CountFilter, 'empty',
                             autospec=True) as mkEmpty:
            self.Counts.count(attr_key, attr, values, attrs)
            self.assertIn(attr_key, self.Counts)
            self.assertEqual(self.Counts[attr_key],
                             mkEmpty.return_value)
            self.assertEqual(mkEmpty.call_args_list,
                             [mk.call(attr, values, attrs)])


    def test_empty(self):
        """test create an empty counts class"""

        attrs = {}
        for _ in range(3):
            attr   = mk.MagicMock(spec=str)
            values = [mk.MagicMock(spec=str) for _ in range(3)]
            removal = mk.MagicMock(spec=bool)
            attrs[mk.MagicMock(spec=str)] = (attr, values, removal)

        attr_keys = list(attrs.keys())

        with mk.patch.object(counter.Counts, 'count', autospec=True) as mkCount:
            self.Counts = counter.Counts.empty(attrs)
            self.assertIsInstance(self.Counts, counter.Counts)
            self.assertEqual(self.Counts, {})

            for index, this in enumerate(attrs.items()):
                attr_key, attr_filter = this
                self.assertEqual(mkCount.call_args_list[index],
                                 mk.call(self.Counts, attr_key, *attr_filter))
            for index, call in enumerate(mkCount.call_args_list):
                self.assertEqual(call,
                                 mk.call(self.Counts, attr_keys[index],
                                         *attrs[attr_keys[index]]))
            self.assertEqual(len(mkCount.call_args_list), 3)
