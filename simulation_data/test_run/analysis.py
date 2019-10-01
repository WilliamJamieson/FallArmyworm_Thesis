import os

import bokeh.plotting     as plt
import bokeh.layouts      as lay
import bokeh.models       as mdl
import bokeh.palettes     as palettes
import bokeh.models.tools as tools

import numpy                    as np
import scipy.signal             as signal
import statsmodels.tsa.seasonal as seasonal

import dataclasses   as dclass
import pandas        as pd
import sqlalchemy    as sql

import source.hint as hint


start_point = 0

plot_width  = 1500
plot_height = 400

colors = palettes.Set1[3]

frequency_range = [62, 63, 64]

save_file   = 'test_run.html'
source_name = 'test_run'

egg    = '(0,)_egg'
larva  = '(0,)_larva'
pupa   = '(0,)_pupa'
female = '(0,)_female'
tables = [egg, larva, pupa, female]

mean    = 'mean'
median  = 'median'
std_dev = 'std_dev'
q_lower = 'q_lower'
q_upper = 'q_upper'
t_min   = 't_min'
t_max   = 't_max'


plt.output_file(save_file)


@dclass.dataclass
class ReadData(object):
    """
    Class to read data
    """

    base_name:   str
    cut_point:   int
    table_names: list
    file_names:  dict = dclass.field(default=dict)
    dataframes:  dict = dclass.field(default=dict)
    combined:    dict = dclass.field(default=dict)

    def __post_init__(self):
        """Setup the inner structure"""

        self.file_names = self.get_file_names()
        self.dataframes = self.get_dataframes()

        self.combined = self.get_combined_dataframes()

    def get_file_list(self) -> list:
        """
        Get list of all the files with base name

        Returns:
            list of all the files
        """

        files = os.listdir('.')
        files = [f for f in files if self.base_name in f]
        files = [f for f in files if 'sqlite'       in f]

        return files

    def get_run_file_lists(self) -> dict:
        """
        Get a dictionary of run files
            key:   run number
            value: list of files

        Returns:
            run dictionary
        """

        files = self.get_file_list()

        file_dict = {}
        for f in files:
            end_tag    = f.split('_')[-1]
            end_number = int(end_tag.split('.')[0])

            if end_number in file_dict:
                file_dict[end_number].append(f)
            else:
                file_dict[end_number] = [f]

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

    def get_run_files(self) -> dict:
        """
        Get a dictionary of file name lists by run tag that are sorted

        Returns:
            a sorted dictionary of names
        """

        files_dict = self.get_run_file_lists()

        return {run_num: self._sort_files(files)
                    for run_num, files in files_dict.items()}

    def get_file_names(self) -> dict:
        """
        Get all the file names ordered

        Returns:
            dictionary of all the file names
        """

        file_dict = self.get_run_files()

        run_nums = list(file_dict.keys())
        run_nums.sort()

        return {run_num: file_dict[run_num] for run_num in run_nums}

    @staticmethod
    def sql_filename(file_name: str) -> str:
        """
        Return the sql filename for sql alchemy

        Args:
            file_name: name of the file

        Returns:
            argument for sql alchemy
        """

        dialect = 'sqlite:///'

        return '{}{}'.format(dialect, file_name)

    def read(self, table_name: str,
                   file_name: str) -> hint.dataframe:
        """
        Read the table from the sql file
        Args:
            table_name: name of the sql table
            file_name:  name of the sql file

        Returns:
            a pandas dataframe
        """

        sql_filename = self.sql_filename(file_name)
        engine       = sql.create_engine(sql_filename)

        return pd.read_sql(table_name, engine)

    def read_dataframe(self, files:      list,
                             table_name: str) -> hint.dataframe:
        """
        Merge data into single dataframe

        Args:
            files:      list of files to combine into single dataframe
            table_name: name of the sql table

        Returns:
            table merge across the files
        """

        dataframe0 = self.read(table_name, files[0])
        dataframes = [dataframe0]

        for file_name in files[1:]:
            dataframe1 = self.read(table_name, file_name)
            dataframe1 = dataframe1.iloc[1:]

            dataframes.append(dataframe1)

        dataframe = pd.concat(dataframes)
        dataframe.reset_index(inplace=True, drop=True)
        dataframe['index'] = range(len(dataframe.index))

        return dataframe

    def read_dataframes(self, files: list) -> hint.dataframes:
        """
        Get all of the dataframes that we wish to use

        Args:
            files: list of files to combine the read on

        Returns:
            dictionary of all the dataframes we want
        """

        dataframes = {}

        for table_name in self.table_names:
            dataframes[table_name] = self.read_dataframe(files, table_name)

        return dataframes

    def all_dataframes(self) -> dict:
        """
        Get a dictionary of all the run data in single dataframe format

        Returns:
            all the run data frames
        """

        data = {}
        for run_num, files in self.file_names.items():
            data[run_num] = self.read_dataframes(files)

        return data

    def cut_dataframe(self, dataframe: hint.dataframe) -> hint.dataframe:
        """
        Cut dataframe to start at new point

        Args:
            dataframe: dataframe to cut

        Returns:
            the cut dataframe
        """

        new = dataframe.copy()
        new = new.iloc[self.cut_point:]
        new.reset_index(inplace=True, drop=True)
        new['index'] = range(len(new.index))

        return new

    def cut_single_dataframes(self, dataframes: hint.dataframes)\
            -> hint.dataframes:
        """
        Cut the read dataframes to the correct start point

        Args:
            dataframes: the collection of dataframes we process

        Returns:
            the dataframes to the right start point
        """

        new = {}
        for table_name, dataframe in dataframes.items():
            new[table_name] = self.cut_dataframe(dataframe)

        return new


    def get_dataframes(self) -> dict:
        """
        Get cut all the dataframes at same start

        Returns:
            all the data frames cut down
        """

        raw_data = self.all_dataframes()

        data = {}
        for run_num, dataframes in raw_data.items():
            data[run_num] = self.cut_single_dataframes(dataframes)

        return data

    def mean_dataframe(self) -> hint.dataframes:
        """
        Generate a mean dataframe for all of the data

        Returns:
            dataframes of all the mean data
        """

        means = {}
        for table_name in self.table_names:
            data_list = []
            for data in self.dataframes.values():
                data_list.append(data[table_name])

            concat     = pd.concat(data_list)
            row_concat = concat.groupby(concat.index)
            mean_data  = row_concat.mean()
            mean_data['index'] = range(len(mean_data.index))

            means[table_name] = mean_data

        return means

    def median_dataframe(self) -> hint.dataframes:
        """
        Generate a median dataframe for all of the data

        Returns:
            dataframes of all the median data
        """

        medians = {}
        for table_name in self.table_names:
            data_list = []
            for data in self.dataframes.values():
                data_list.append(data[table_name])

            concat      = pd.concat(data_list)
            row_concat  = concat.groupby(concat.index)
            median_data = row_concat.median()
            median_data['index'] = range(len(median_data.index))

            medians[table_name] = median_data

        return medians

    def std_dataframe(self) -> hint.dataframes:
        """
        Generate a std dataframe for all of the data

        Returns:
            dataframes of all the std data
        """

        stds = {}
        for table_name in self.table_names:
            data_list = []
            for data in self.dataframes.values():
                data_list.append(data[table_name])

            concat     = pd.concat(data_list)
            row_concat = concat.groupby(concat.index)
            std_data   = row_concat.std()
            std_data['index'] = range(len(std_data.index))

            stds[table_name] = std_data

        return stds

    def q_lower_dataframe(self) -> hint.dataframes:
        """
        Generate a q_lower dataframe for all of the data

        Returns:
            dataframes of all the q_lower data
        """

        q_lowers = {}
        for table_name in self.table_names:
            data_list = []
            for data in self.dataframes.values():
                data_list.append(data[table_name])

            concat       = pd.concat(data_list)
            row_concat   = concat.groupby(concat.index)
            q_lower_data = row_concat.quantile(2.5)
            q_lower_data['index'] = range(len(q_lower_data.index))

            q_lowers[table_name] = q_lower_data

        return q_lowers

    def q_upper_dataframe(self) -> hint.dataframes:
        """
        Generate a q_upper dataframe for all of the data

        Returns:
            dataframes of all the q_upper data
        """

        q_uppers = {}
        for table_name in self.table_names:
            data_list = []
            for data in self.dataframes.values():
                data_list.append(data[table_name])

            concat       = pd.concat(data_list)
            row_concat   = concat.groupby(concat.index)
            q_upper_data = row_concat.quantile(97.5)
            q_upper_data['index'] = range(len(q_upper_data.index))

            q_uppers[table_name] = q_upper_data

        return q_uppers

    def min_dataframe(self) -> hint.dataframes:
        """
        Generate a min dataframe for all of the data

        Returns:
            dataframes of all the min data
        """

        mins = {}
        for table_name in self.table_names:
            data_list = []
            for data in self.dataframes.values():
                data_list.append(data[table_name])

            concat     = pd.concat(data_list)
            row_concat = concat.groupby(concat.index)
            min_data   = row_concat.min()
            min_data['index'] = range(len(min_data.index))

            mins[table_name] = min_data

        return mins

    def max_dataframe(self) -> hint.dataframes:
        """
        Generate a max dataframe for all of the data

        Returns:
            dataframes of all the max data
        """

        maxs = {}
        for table_name in self.table_names:
            data_list = []
            for data in self.dataframes.values():
                data_list.append(data[table_name])

            concat     = pd.concat(data_list)
            row_concat = concat.groupby(concat.index)
            max_data   = row_concat.max()
            max_data['index'] = range(len(max_data.index))

            maxs[table_name] = max_data

        return maxs

    def get_combined_dataframes(self) -> dict:
        """
        Combine all of the dataframes together

        Returns:
            all the data frames cut down
        """

        dataframes = {
            mean:    self.mean_dataframe(),
            median:  self.median_dataframe(),
            # std_dev: self.std_dataframe(),
            # q_lower: self.q_lower_dataframe(),
            # q_upper: self.q_upper_dataframe(),
            # t_min:     self.min_dataframe(),
            # t_max:     self.max_dataframe()
        }

        return dataframes


reader = ReadData(source_name, start_point, tables)
egg_data = reader.dataframes[0][egg]
