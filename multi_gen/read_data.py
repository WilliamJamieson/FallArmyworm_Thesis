import datetime
import os
import pickle

import dataclasses   as dclass
import pandas        as pd
import sqlalchemy    as sql

import source.hint as hint

import multi_gen.runs as runs

tables          = runs.tables
columns         = runs.columns
simulation_runs = runs.runs


@dclass.dataclass
class ReadData(object):
    """
    Class to read data
    """

    base_name: str

    def _get_file_list(self) -> list:
        """
        Get list of all the files with base name

        Returns:
            list of all the files
        """

        files = os.listdir('./data/{}'.format(self.base_name))
        files = [f for f in files if self.base_name in f]
        files = [f for f in files if 'sqlite'       in f]

        print('    {} Number of files is {}'.
              format(datetime.datetime.now(),
                     len(files)))

        return files

    def _get_run_file_lists(self) -> dict:
        """
        Get a dictionary of run files
            key:   run number
            value: list of files

        Returns:
            run dictionary
        """

        files = self._get_file_list()

        file_dict = {}
        for f in files:
            end_tag    = f.split('_')[-1]
            end_number = int(end_tag.split('.')[0])

            if end_number in file_dict:
                file_dict[end_number].append(f)
            else:
                file_dict[end_number] = [f]

        print('        {} Number of runs is {}'.
              format(datetime.datetime.now(), len(file_dict)))

        return file_dict

    @staticmethod
    def _sort_files(files: list) -> list:
        """
        Sort a list of files in order of run for processing

        Args:
            files: list of files to sort

        Returns:
            list of file names sorted in order
        """

        file_dict = {}
        for f in files:
            f_num = int(f.split('_')[0])
            if f_num in file_dict:
                raise RuntimeError('Repeated run time frame')
            else:
                file_dict[f_num] = f

        f_nums = list(file_dict.keys())
        f_nums.sort()

        return [file_dict[f_num] for f_num in f_nums]

    def _get_run_files(self) -> dict:
        """
        Get a dictionary of file name lists by run tag that are sorted

        Returns:
            a sorted dictionary of names
        """

        files_dict = self._get_run_file_lists()

        return {run_num: self._sort_files(files)
                for run_num, files in files_dict.items()}

    def get_run_files(self) -> dict:
        """
        Get all the file names ordered

        Returns:
            dictionary of all the file names
        """

        print('    {} Getting files'.format(datetime.datetime.now()))

        file_dict = self._get_run_files()

        run_nums = list(file_dict.keys())
        run_nums.sort()

        return {run_num: file_dict[run_num] for run_num in run_nums}

    @staticmethod
    def get_low_runs(run_files: dict) -> list:
        """
        Get the list of runs that did not complete all the way

        Args:
            run_files: list of run files

        Returns:
            the list of runs that did not make it all the way
        """

        count_dict = {run_num: len(files)
                      for run_num, files in run_files.items()}

        run_length = max(count_dict.values())

        print('        {} Run length: {}'.
              format(datetime.datetime.now(), run_length))

        return [run_num for run_num in count_dict
                if count_dict[run_num] < run_length]

    def get_complete_runs(self) -> dict:
        """
        Getting complete files

        Returns:
            dictionary of all completed runs
        """

        run_files = self.get_run_files()
        failures  = self.get_low_runs(run_files)

        print('        {} Run failures {}'.
              format(datetime.datetime.now(), failures))

        return {run_num: files for run_num, files in run_files.items()
                if run_num not in failures}

    def _sql_filename(self, file_name: str) -> str:
        """
        Return the sql filename for sql alchemy

        Args:
            file_name: name of the file

        Returns:
            argument for sql alchemy
        """

        dialect = 'sqlite:///'

        return '{}data/{}/{}'.format(dialect, self.base_name, file_name)

    def _read(self, table_name: str,
                    file_name: str) -> hint.dataframe:
        """
        Read the table from the sql file
        Args:
            table_name: name of the sql table
            file_name:  name of the sql file

        Returns:
            a pandas dataframe
        """

        sql_filename = self._sql_filename(file_name)
        engine       = sql.create_engine(sql_filename)

        return pd.read_sql(table_name, engine)

    def _read_dataframe(self, files:      list,
                              table_name: str) -> hint.dataframe:
        """
        Merge data into single dataframe

        Args:
            files:      list of files to combine into single dataframe
            table_name: name of the sql table

        Returns:
            table merge across the files
        """

        dataframe0 = self._read(table_name, files[0])
        dataframes = [dataframe0]

        for file_name in files[1:]:
            dataframe1 = self._read(table_name, file_name)
            dataframe1 = dataframe1.iloc[1:]

            dataframes.append(dataframe1)

        dataframe = pd.concat(dataframes)
        dataframe.reset_index(inplace=True, drop=True)
        dataframe['index'] = range(len(dataframe.index))

        return dataframe

    def _read_dataframes(self, files: list) -> hint.dataframes:
        """
        Get all of the dataframes that we wish to use

        Args:
            files: list of files to combine the read on

        Returns:
            dictionary of all the dataframes we want
        """

        dataframes = {}

        for table_name in tables:
            print('                {} Reading table: {}'.
                  format(datetime.datetime.now(), table_name))
            dataframes[table_name] = self._read_dataframe(files, table_name)

        return dataframes

    def read(self) -> dict:
        """
        Read all of the complete run data

        Returns:
            dictionary of run data
        """

        run_files = self.get_complete_runs()

        data = {}
        for run_num, files in run_files.items():
            print('            {} Reading Run: {}'.
                  format(datetime.datetime.now(), run_num))
            data[run_num] = self._read_dataframes(files)

        return data

    def save(self) -> None:
        """
        Save the read data in python binary

        Effects:
            writes the read data to a python binary
        """

        pickle_name = '{}.data'.format(self.base_name)
        data        = self.read()

        with open(pickle_name, 'wb') as save_file:
            pickle.dump(data, save_file, protocol=pickle.HIGHEST_PROTOCOL)

    @classmethod
    def read_data(cls, base_name: str) -> None:
        """
        Read the simulation data to a binary file

        Args:
            base_name: simulation base name

        Effects:
            saves unified data to a file
        """

        read = cls(base_name)
        read.save()


for simulation_run in runs.mix[6:]:
    print('{} Processing Simulation: {}'.
          format(datetime.datetime.now(), simulation_run))
    ReadData.read_data(simulation_run)
