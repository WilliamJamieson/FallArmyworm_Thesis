import unittest      as ut
import unittest.mock as mk

import dataclasses as dclass
import sqlalchemy  as sql
import pandas      as pd

import source.data.database as database

import source.simulation.simulation as main_simulation

import source.space.agents as main_agents


class SimulationTest(main_simulation.Simulation):
    """Class to add dynamic values for tests"""

    agents   = mk.create_autospec(main_agents.Agents, spec_set=True)
    timestep = mk.MagicMock(spec=int)


class TestDatabase(ut.TestCase):
    """test the Database system class"""

    def setUp(self):
        """Setup the tests"""

        self.spacing   = mk.MagicMock(spec=int)
        self.file_name = mk.MagicMock(spec=str)
        self.prev_dump = mk.MagicMock(spec= int)

        self.Database = database.Database(self.spacing,
                                          self.file_name,
                                          self.prev_dump)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Database, database.Database)

        self.assertEqual(self.Database.spacing,   self.spacing)
        self.assertEqual(self.Database.file_name, self.file_name)
        self.assertEqual(self.Database.prev_dump, self.prev_dump)

        self.assertEqual(self.Database.next_dump,
                         self.prev_dump.__add__.return_value)
        self.assertEqual(self.prev_dump.__add__.call_args_list,
                         [mk.call(self.spacing)])

        self.assertTrue(dclass.is_dataclass(self.Database))

        # Test default
        self.Database = database.Database(self.spacing)

        self.assertIsInstance(self.Database, database.Database)

        self.assertEqual(self.Database.spacing,   self.spacing)
        self.assertEqual(self.Database.file_name, ':memory:')
        self.assertEqual(self.Database.prev_dump, 0)

        self.assertEqual(self.Database.next_dump,
                         self.spacing.__radd__.return_value)
        self.assertEqual(self.spacing.__radd__.call_args_list,
                         [mk.call(0)])

        self.assertTrue(dclass.is_dataclass(self.Database))

    def test_sql_file_name(self):
        """test get the file_name for sql engine"""

        simulation = mk.create_autospec(SimulationTest, spec_set=True)

        dialect = 'sqlite:///'
        time    = str(self.prev_dump) + '_to_' + str(simulation.timestep) + '_'

        self.assertEqual(self.Database.sql_file_name(simulation),
                         dialect + time + str(self.file_name))

    def test__save(self):
        """test save data to file"""

        simulation = mk.create_autospec(SimulationTest, spec_set=True)
        simulation.agents = mk.create_autospec(main_agents.Agents,
                                               spec_set=True)
        dataframes = {mk.MagicMock(spec=str): mk.create_autospec(pd.DataFrame,
                                                                 spec_set=True)
                      for _ in range(3)}
        simulation.agents.dataframes.return_value = dataframes

        with mk.patch.object(database.Database, 'sql_file_name',
                             autospec=True) as mkName:
            with mk.patch.object(sql, 'create_engine') as mkSQL:
                self.Database._save(simulation)
                for table_name, dataframe in dataframes.items():
                    self.assertEqual(dataframe.to_sql.call_args_list,
                                     [mk.call(table_name, mkSQL.return_value)])
                self.assertEqual(mkSQL.call_args_list,
                                 [mk.call(mkName.return_value)])
                self.assertEqual(mkName.call_args_list,
                                 [mk.call(self.Database, simulation)])
                self.assertEqual(simulation.agents.dataframes.call_args_list,
                                 [mk.call()])

    def test_dump(self):
        """test dump the data"""

        simulation = mk.create_autospec(SimulationTest, spec_set=True)
        simulation.agents = mk.create_autospec(main_agents.Agents,
                                               spec_set=True)

        with mk.patch.object(database.Database, '_save') as mkSave:
            master = mk.MagicMock()
            master.attach_mock(mkSave,            'save')
            master.attach_mock(simulation.agents, 'agents')

            self.Database.dump(simulation)
            self.assertEqual(master.mock_calls,
                             [mk.call.save(simulation),
                              mk.call.agents.refresh()])

            self.assertEqual(self.Database.prev_dump, simulation.timestep)
            self.assertEqual(self.Database.next_dump,
                             simulation.timestep.__add__.return_value)
            self.assertEqual(simulation.timestep.__add__.call_args_list,
                             [mk.call(self.spacing)])

    def test_save(self):
        """test save the simulation"""

        simulation = mk.create_autospec(SimulationTest, spec_set=True)

        with mk.patch.object(database.Database, 'dump',
                             autospec=True) as mkDump:
            simulation.timestep.__eq__.side_effect = [False, True]

            # Test no save
            self.Database.save(simulation)
            self.assertEqual(mkDump.call_args_list, [])
            self.assertEqual(simulation.timestep.__eq__.call_args_list,
                             [mk.call(self.Database.next_dump)])

            simulation.timestep.__eq__.reset_mock()
            # Test save
            self.Database.save(simulation)
            self.assertEqual(mkDump.call_args_list,
                             [mk.call(self.Database, simulation)])
            self.assertEqual(simulation.timestep.__eq__.call_args_list,
                             [mk.call(self.Database.next_dump)])
            
    def test_setup(self):
        """test save the class"""

        # Just spacing
        data_tuple = (self.spacing,)
        self.Database = database.Database.setup(data_tuple)
        self.assertIsInstance(self.Database, database.Database)
        self.assertEqual(self.Database.spacing,   self.spacing)
        self.assertEqual(self.Database.file_name, ':memory:')
        self.assertEqual(self.Database.prev_dump, 0)
        self.assertEqual(self.Database.next_dump,
                         self.spacing.__radd__.return_value)
        self.assertEqual(self.spacing.__radd__.call_args_list,
                         [mk.call(0)])

        self.spacing.reset_mock()
        # Spacing and file name
        data_tuple = (self.spacing, self.file_name)
        self.Database = database.Database.setup(data_tuple)
        self.assertIsInstance(self.Database, database.Database)
        self.assertEqual(self.Database.spacing,   self.spacing)
        self.assertEqual(self.Database.file_name, self.file_name)
        self.assertEqual(self.Database.prev_dump, 0)
        self.assertEqual(self.Database.next_dump,
                         self.spacing.__radd__.return_value)
        self.assertEqual(self.spacing.__radd__.call_args_list,
                         [mk.call(0)])
