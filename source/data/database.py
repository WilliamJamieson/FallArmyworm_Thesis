import dataclasses as dclass
import sqlalchemy  as sql

import source.hint as hint


@dclass.dataclass
class Database(object):
    """
    Class to handle saving data

    Variables:
        spacing:   number of steps between saves
        file_name: base name for the save file
        next_dump: next dump step
        prev_dump: last dump step
    """

    spacing:   int
    file_name: str = ':memory:'
    file_path: str = ''
    prev_dump: int = 0
    next_dump: int = 0

    def __post_init__(self):
        if self.next_dump == 0:
            self.next_dump = self.prev_dump + self.spacing

    def sql_file_name(self, simulation: hint.simulation) -> str:
        """
        Create the sql file name

        Args:
            simulation: the master simulation

        Returns:
            a sql filename for a connection
        """

        dialect = 'sqlite:///'
        time    = '{}/{}_to_{}_'.format(self.file_path,
                                        self.prev_dump,
                                        simulation.timestep)

        return '{}{}{}'.format(dialect, time, self.file_name)

    def _save(self, simulation: hint.simulation) -> None:
        """
        Save the data to a file

        Args:
            simulation: the master simulation

        Effects:
            save current data to a file
        """

        dataframes = simulation.agents.dataframes()
        file_name  = self.sql_file_name(simulation)
        engine     = sql.create_engine(file_name)

        for table_name, dataframe in dataframes.items():
            dataframe.to_sql(table_name, engine)

    def dump(self, simulation: hint.simulation) -> None:
        """
        Dump the data to a file

        Args:
            simulation: the master simulation

        Effects:
            save the current data and then refresh everything
        """

        self._save(simulation)
        simulation.agents.refresh()

        self.prev_dump = simulation.timestep
        self.next_dump = self.prev_dump + self.spacing

    def save(self, simulation: hint.simulation) -> None:
        """
        Save if correct time

        Args:
            simulation: the master simulation

        Effects:
            save the current data and then refresh everything if correct time
        """

        if simulation.timestep == self.next_dump:
            self.dump(simulation)

    @classmethod
    def setup(cls, data_tuple: hint.data_tuple) -> 'Database':
        """
        Setup the class

        Args:
            data_tuple: database arguments

        Returns:
            a setup class
        """

        return cls(*data_tuple)
