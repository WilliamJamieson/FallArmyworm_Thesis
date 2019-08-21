import unittest      as ut
import unittest.mock as mk

import collections as collect

import pandas as pd

import source.agents.agent as main_agent

import source.data.counter as counter


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
        self.assertIsInstance(self.Count, counter.Count)

        self.assertEqual(self.Count.attr,    self.attr)
        self.assertEqual(self.Count.removal, self.removal)

        self.assertEqual(self.Count.data_columns, self.data_columns)

        self.assertEqual(self.Count,      self.counts)
        self.assertEqual(self.Count.data, self.counts)

    def test_add(self):
        """test add agent to counter"""

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

    def test_record(self):
        """test record the counts"""

        self.Count.record()
        self.assertEqual(self.data_columns.record.call_args_list,
                         [mk.call(self.Count)])

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


class CountTest(counter.Count):
    """Class to add dynamic values for agent tests"""

    data_columns = mk.create_autospec(counter.DataColumns, spec_set=True)

            
class TestCounts(ut.TestCase):
    """test the Counts class"""

    def setUp(self):
        """Setup the tests"""

        self.counts = {mk.MagicMock(spec=str):
                           mk.create_autospec(CountTest, spec_set=True)
                       for _ in range(3)}

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

    def test_columns(self):
        """test create all the columns of data"""

        columns = {}
        for count in self.counts.values():
            count.data_columns = mk.create_autospec(counter.DataColumns,
                                                    spec_set=True)
            column = {}
            for _ in range(3):
                key   = mk.MagicMock(spec=str)
                value = mk.create_autospec(counter.DataColumn, spec_set=True)

                column[ key] = value
                columns[key] = value

            count.data_columns.columns.return_value = column

        self.assertEqual(self.Counts.columns(), columns)
        for count in self.Counts.values():
            self.assertEqual(count.data_columns.columns.call_args_list,
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

        attr    = mk.MagicMock(spec=str)
        values  = [mk.MagicMock(spec=str) for _ in range(3)]
        removal = mk.MagicMock(spec=bool)

        self.assertNotIn(attr, self.Counts)
        self.Counts.count(attr, values, removal)
        self.assertIn(attr, self.Counts)

        self.assertIsInstance(self.Counts[attr], counter.Count)
        self.assertEqual(self.Counts[attr].attr,    attr)
        self.assertEqual(self.Counts[attr].removal, removal)
        for key, value in self.Counts[attr].items():
            self.assertIn(key, values)
            self.assertEqual(value, 0)
        for value in values:
            self.assertIn(value, self.Counts[attr])
            self.assertEqual(self.Counts[attr][value], 0)

        self.assertIsInstance(self.Counts[attr].data_columns,
                              counter.DataColumns)
        self.assertEqual(self.Counts[attr].data_columns.attr, attr)
        for key, column in self.Counts[attr].data_columns.items():
            self.assertIn(key, values)
            self.assertIsInstance(column, counter.DataColumn)
            self.assertEqual(column.attr_value, key)
            self.assertEqual(column, [])
        for value in values:
            self.assertIn(value, self.Counts[attr].data_columns)
            self.assertIsInstance(self.Counts[attr].data_columns[value],
                                  counter.DataColumn)
            self.assertEqual(self.Counts[attr].data_columns[value].attr_value,
                             value)
            self.assertEqual(self.Counts[attr].data_columns[value], [])

    def test_empty(self):
        """test create an empty counts class"""

        attrs = {}
        for _ in range(3):
            values = [mk.MagicMock(spec=str) for _ in range(3)]
            removal = mk.MagicMock(spec=bool)
            attrs[mk.MagicMock(spec=str)] = (values, removal)

        self.Counts = counter.Counts.empty(attrs)
        self.assertIsInstance(self.Counts, counter.Counts)

        for attr, things in attrs.items():
            values, removal = things
            self.assertIsInstance(self.Counts[attr], counter.Count)
            self.assertEqual(self.Counts[attr].attr,    attr)
            self.assertEqual(self.Counts[attr].removal, removal)
            for key, value in self.Counts[attr].items():
                self.assertIn(key, values)
                self.assertEqual(value, 0)
            for value in values:
                self.assertIn(value, self.Counts[attr])
                self.assertEqual(self.Counts[attr][value], 0)

            self.assertIsInstance(self.Counts[attr].data_columns,
                                  counter.DataColumns)
            self.assertEqual(self.Counts[attr].data_columns.attr, attr)
            for key, column in self.Counts[attr].data_columns.items():
                self.assertIn(key, values)
                self.assertIsInstance(column, counter.DataColumn)
                self.assertEqual(column.attr_value, key)
                self.assertEqual(column, [])
            for value in values:
                self.assertIn(value, self.Counts[attr].data_columns)
                self.assertIsInstance(self.Counts[attr].data_columns[value],
                                      counter.DataColumn)
                self.assertEqual(self.Counts[attr].data_columns[value].
                                    attr_value,
                                 value)
                self.assertEqual(self.Counts[attr].data_columns[value], [])
