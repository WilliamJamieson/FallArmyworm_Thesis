import datetime
import os
import pickle

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

source_name = os.path.basename(os.getcwd())
save_file   = '{}.html'.format(source_name)

sample_size = 100
freq_width  = 2

files_per_run = 40

egg    = '(0,)_egg'
larva  = '(0,)_larva'
pupa   = '(0,)_pupa'
female = '(0,)_female'
tables = [egg, larva, pupa, female]

mean     = 'mean'
median   = 'median'
std_dev  = 'std_dev'
q_lower  = 'q_lower'
q_upper  = 'q_upper'
t_min    = 't_min'
t_max    = 't_max'
freq     = 'freq'
power    = 'power'
period   = 'period'
primary  = 'primary'
genotype = 'genotype'
observed = 'observed'
trend    = 'trend'
season   = 'seasonal'
resid    = 'residual'

homo_r = 'genotype_resistant'
hetero = 'genotype_heterozygous'
homo_s = 'genotype_susceptible'

columns = [homo_r, hetero, homo_s]


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
    sample:      dict = dclass.field(default=dict)

    def __post_init__(self):
        """Setup the inner structure"""

        if not isinstance(self.file_names, dict):
            self.file_names = self.get_file_names()

        if not isinstance(self.dataframes, dict):
            self.dataframes = self.get_dataframes()

        if not isinstance(self.combined, dict):
            print('{} Combining all data'.format(datetime.datetime.now()))

            self.combined = self.get_combined_dataframes(self.dataframes)

        if not isinstance(self.sample, dict):
            print('{} Combining sample data'.format(datetime.datetime.now()))
            dataframes  = self.sample_dataframes()
            self.sample = self.get_combined_dataframes(dataframes)

        print('{} finished data read'.format(datetime.datetime.now()))

    @classmethod
    def setup(cls, base_name:   str,
                   cut_point:   int,
                   table_names: list) -> 'ReadData':
        """
        Read the data for system

        Args:
            base_name:   name of data files
            cut_point:   point to cut of head of series
            table_names: names of tables to read

        Returns:
            setup class
        """

        pickle_name = '{}.data'.format(base_name)

        if os.path.exists(pickle_name):
            print('{} Loading previous read from: {}'.
                  format(datetime.datetime.now(), pickle_name))
            with open(pickle_name, 'rb') as read_dump:
                return pickle.load(read_dump)
        else:
            new = cls(base_name, cut_point, table_names)
            new.save(pickle_name)

            return new


    def get_file_list(self) -> list:
        """
        Get list of all the files with base name

        Returns:
            list of all the files
        """

        files = os.listdir('.')
        files = [f for f in files if self.base_name in f]
        files = [f for f in files if 'sqlite'       in f]

        print('    {} Number of files is {}'.
              format(datetime.datetime.now(),
                     len(files)))

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

        print('    {} Number of runs is {}'.
              format(datetime.datetime.now(), len(file_dict)))

        for run_num, file_list in file_dict.items():
            if len(file_list) != files_per_run:
                raise TypeError('Run {} does not have enough files'.
                                format(run_num))


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

        print('{} Getting files'.format(datetime.datetime.now()))

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
            print('            {} Reading table: {}'.
                  format(datetime.datetime.now(), table_name))
            dataframes[table_name] = self.read_dataframe(files, table_name)

        return dataframes

    def all_dataframes(self) -> dict:
        """
        Get a dictionary of all the run data in single dataframe format

        Returns:
            all the run data frames
        """

        print('    {} Reading all of the raw data'.
              format(datetime.datetime.now()))

        data = {}
        for run_num, files in self.file_names.items():
            print('        {} Reading run: {}'.
                  format(datetime.datetime.now(), run_num))
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
            print('                {} Cutting table: {}'.
                  format(datetime.datetime.now(), table_name))
            new[table_name] = self.cut_dataframe(dataframe)

        return new


    def get_dataframes(self) -> dict:
        """
        Get cut all the dataframes at same start

        Returns:
            all the data frames cut down
        """

        print('{} Reading the run data'.format(datetime.datetime.now()))

        raw_data = self.all_dataframes()

        print('    {} Cutting raw data to actual data'.
              format(datetime.datetime.now()))

        data = {}
        for run_num, dataframes in raw_data.items():
            print('            {} Cutting run: {}'.
                  format(datetime.datetime.now(), run_num))
            data[run_num] = self.cut_single_dataframes(dataframes)

        return data

    def mean_dataframe(self, dataframes: hint.dataframes) -> hint.dataframes:
        """
        Generate a mean dataframe for all of the data

        Args:
            dataframes: the dataframes we will use

        Returns:
            dataframes of all the mean data
        """

        print('    {} Getting mean data'.format(datetime.datetime.now()))

        means = {}
        for table_name in self.table_names:
            data_list = []
            for data in dataframes.values():
                data_list.append(data[table_name])

            concat     = pd.concat(data_list)
            row_concat = concat.groupby(concat.index)
            mean_data  = row_concat.mean()
            mean_data['index'] = range(len(mean_data.index))

            means[table_name] = mean_data

        return means

    def median_dataframe(self, dataframes: hint.dataframes) -> hint.dataframes:
        """
        Generate a median dataframe for all of the data

        Args:
            dataframes: the dataframes we will use

        Returns:
            dataframes of all the median data
        """

        print('    {} Getting median data'.format(datetime.datetime.now()))

        medians = {}
        for table_name in self.table_names:
            data_list = []
            for data in dataframes.values():
                data_list.append(data[table_name])

            concat      = pd.concat(data_list)
            row_concat  = concat.groupby(concat.index)
            median_data = row_concat.median()
            median_data['index'] = range(len(median_data.index))

            medians[table_name] = median_data

        return medians

    def std_dataframe(self, dataframes: hint.dataframes) -> hint.dataframes:
        """
        Generate a std dataframe for all of the data

        Args:
            dataframes: the dataframes we will use

        Returns:
            dataframes of all the std data
        """

        print('    {} Getting standard deviation data'.
              format(datetime.datetime.now()))

        stds = {}
        for table_name in self.table_names:
            data_list = []
            for data in dataframes.values():
                data_list.append(data[table_name])

            concat     = pd.concat(data_list)
            row_concat = concat.groupby(concat.index)
            std_data   = row_concat.std()
            std_data['index'] = range(len(std_data.index))

            stds[table_name] = std_data

        return stds

    def q_lower_dataframe(self, dataframes: hint.dataframes) -> hint.dataframes:
        """
        Generate a q_lower dataframe for all of the data

        Args:
            dataframes: the dataframes we will use

        Returns:
            dataframes of all the q_lower data
        """

        print('    {} Getting lower quantile data'.
              format(datetime.datetime.now()))

        q_lowers = {}
        for table_name in self.table_names:
            data_list = []
            for data in dataframes.values():
                data_list.append(data[table_name])

            concat       = pd.concat(data_list)
            row_concat   = concat.groupby(concat.index)
            q_lower_data = row_concat.quantile(2.5)
            q_lower_data['index'] = range(len(q_lower_data.index))

            q_lowers[table_name] = q_lower_data

        return q_lowers

    def q_upper_dataframe(self, dataframes: hint.dataframes) -> hint.dataframes:
        """
        Generate a q_upper dataframe for all of the data

        Args:
            dataframes: the dataframes we will use

        Returns:
            dataframes of all the q_upper data
        """

        print('    {} Getting upper quantile data'.
              format(datetime.datetime.now()))

        q_uppers = {}
        for table_name in self.table_names:
            data_list = []
            for data in dataframes.values():
                data_list.append(data[table_name])

            concat       = pd.concat(data_list)
            row_concat   = concat.groupby(concat.index)
            q_upper_data = row_concat.quantile(97.5)
            q_upper_data['index'] = range(len(q_upper_data.index))

            q_uppers[table_name] = q_upper_data

        return q_uppers

    def min_dataframe(self, dataframes: hint.dataframes) -> hint.dataframes:
        """
        Generate a min dataframe for all of the data

        Args:
            dataframes: the dataframes we will use

        Returns:
            dataframes of all the min data
        """

        print('    {} Getting min data'.format(datetime.datetime.now()))

        mins = {}
        for table_name in self.table_names:
            data_list = []
            for data in dataframes.values():
                data_list.append(data[table_name])

            concat     = pd.concat(data_list)
            row_concat = concat.groupby(concat.index)
            min_data   = row_concat.min()
            min_data['index'] = range(len(min_data.index))

            mins[table_name] = min_data

        return mins

    def max_dataframe(self, dataframes: hint.dataframes) -> hint.dataframes:
        """
        Generate a max dataframe for all of the data

        Args:
            dataframes: the dataframes we will use

        Returns:
            dataframes of all the max data
        """

        print('    {} Getting max data'.format(datetime.datetime.now()))

        maxs = {}
        for table_name in self.table_names:
            data_list = []
            for data in dataframes.values():
                data_list.append(data[table_name])

            concat     = pd.concat(data_list)
            row_concat = concat.groupby(concat.index)
            max_data   = row_concat.max()
            max_data['index'] = range(len(max_data.index))

            maxs[table_name] = max_data

        return maxs

    def get_combined_dataframes(self, dataframes: hint.dataframes) -> dict:
        """
        Combine all of the dataframes together

        Returns:
            all the data frames cut down
        """

        data = {
            mean:    self.mean_dataframe(dataframes),
            median:  self.median_dataframe(dataframes),
            # std_dev: self.std_dataframe(),
            # q_lower: self.q_lower_dataframe(),
            # q_upper: self.q_upper_dataframe(),
            # t_min:     self.min_dataframe(),
            # t_max:     self.max_dataframe()
        }

        return data

    def sample_dataframes(self) -> dict:
        """
        Sample a subset of the dataframes

        Returns:
            a set of dataframes as a subset
        """

        r_nums = list(self.dataframes.keys())
        s_nums = np.random.choice(r_nums, sample_size,
                                          replace=False)
        s_nums.sort()

        return {s_num: self.dataframes[s_num]
                for s_num in s_nums}

    def save(self, pickle_name: str) -> None:
        """
        Save the read data as single file

        Args:
            pickle_name: name of pickle file to save to

        Effects:
            writes data to single file
        """

        print('{} Saving data reads to file'.format(datetime.datetime.now()))

        with open(pickle_name, 'wb') as read_dump:
            pickle.dump(self, read_dump, protocol=pickle.HIGHEST_PROTOCOL)


@dclass.dataclass
class ProcessData(object):
    """
    Process read data
    """

    data: ReadData

    periodograms: dict = dclass.field(default=dict)
    decompose:    dict = dclass.field(default=dict)

    sample_periodograms: dict = dclass.field(default=dict)
    sample_decompose:    dict = dclass.field(default=dict)

    def __post_init__(self):
        """Setup the other stuff"""


        print('{} Processing Combined Data'.format(datetime.datetime.now()))
        if not isinstance(self.periodograms, dict):
            self.periodograms = self.get_periodograms(self.data.combined)
        if not isinstance(self.decompose, dict):
            self.decompose    = self.get_seasonal_decompose(self.data.combined,
                                                            self.periodograms)

        print('{} Processing Sample Data'.format(datetime.datetime.now()))
        if not isinstance(self.sample_periodograms, dict):
            self.sample_periodograms = self.get_periodograms(self.data.sample)
        if not isinstance(self.sample_decompose, dict):
            self.sample_decompose \
                = self.get_seasonal_decompose(self.data.sample,
                                              self.sample_periodograms)

        print('{} Finished data processing'.format(datetime.datetime.now()))

    @staticmethod
    def make_periodogram(dataframe: hint.dataframe) -> dict:
        """
        Create a periodogram of the dataframe

        Args:
            dataframe: dataframe to create data on

        Returns:
            periodogram dataframes
        """

        data_dict = {}
        for column in columns:
            print('                {} Creating the {} periodogram'.
                  format(datetime.datetime.now(), column))
            periodogram_dict = {}
            frequency_data, power_data = signal.periodogram(dataframe[column])

            period_data = (1 / frequency_data[1:]).tolist()
            period_data.insert(0, np.inf)

            primary_index = np.argmax(power_data)
            primary_data  = period_data[primary_index]
            print('                    {} found frequency: {}'.
                  format(datetime.datetime.now(), primary_data))

            periodogram_dict[freq]     = frequency_data
            periodogram_dict[power]    = power_data
            periodogram_dict[period]   = period_data
            periodogram_dict[primary]  = primary_data
            periodogram_dict[genotype] = column.split('_')[1]

            data_dict[column] = periodogram_dict

        return data_dict

    def find_periodogram(self, dataframes: hint.dataframes) -> dict:
        """
        Create the periodograms for the given dataframes

        Args:
            dataframes: the dataframes for a given combined type

        Returns:
            periodograms
        """

        periodograms = {}
        for table_name, dataframe in dataframes.items():
            print('            {} Creating periodograms for table: {}'.
                  format(datetime.datetime.now(), table_name))
            periodograms[table_name] = self.make_periodogram(dataframe)

        return periodograms

    def get_periodograms(self, dataframes: dict) -> dict:
        """
        Create the combined periodograms

        Args:
            dataframes: dataframes for combined data

        Returns:
            dictionary of periodograms
        """

        print('    {} Creating Periodograms'.format(datetime.datetime.now()))

        periodograms = {}
        for label, dataframe in dataframes.items():
            print('        {} Creating {} series periodograms'.
                  format(datetime.datetime.now(), label))
            periodograms[label] = self.find_periodogram(dataframe)

        return periodograms

    @staticmethod
    def seasonal_decompose(dataframe: hint.dataframe,
                           frequency: int) -> dict:
        """
        Decompose the data at the given seasonal frequency
        Args:
            dataframe: dataframe to use
            frequency: seasonal frequency

        Returns:
            seasonal decomposition object
        """

        decomp = seasonal.seasonal_decompose(dataframe,
                                             model='additive',
                                             freq=frequency)
        decomp.trend[   'index'] = range(len(decomp.trend))
        decomp.seasonal['index'] = range(len(decomp.seasonal))
        decomp.resid[   'index'] = range(len(decomp.resid))

        decomp_dict = {
            observed: decomp.observed,
            trend:    decomp.trend,
            season:   decomp.seasonal,
            resid:    decomp.resid,
            freq:     frequency
        }

        return decomp_dict

    def find_seasonal_decompose(self, dataframes:   dict,
                                      periodograms: dict) -> dict:
        """
        Find the seasonal decompose of the dataframe with label, title

        Args:
            dataframes:   dataframes for combined data
            periodograms: periodogram data for combined

        Returns:
            dictionary of decomposition
        """

        decomp = {}
        for column in columns:
            print('               {} Decomposing column {}'.
                  format(datetime.datetime.now(),
                         column))
            data        = dataframes[column]
            decomp_dict = {}
            main_freq_float = periodograms[column][primary]
            if main_freq_float != np.inf:
                main_freq   = int(main_freq_float)
                print('                  {} using frequency {}'.
                      format(datetime.datetime.now(),
                             main_freq))
                decomp_dict[main_freq] = self.seasonal_decompose(data,
                                                                 main_freq)

                for index in range(1, freq_width + 1):
                    frequency = main_freq + index
                    print('                  {} using frequency {}'.
                          format(datetime.datetime.now(),
                                 frequency))
                    decomp_dict[frequency] = self.seasonal_decompose(data,
                                                                     frequency)
                    frequency = main_freq - index
                    if frequency >= 0:
                        print('                  {} using frequency {}'.
                              format(datetime.datetime.now(),
                                     frequency))
                        decomp_dict[frequency] = \
                            self.seasonal_decompose(data, frequency)
                decomp[column] = decomp_dict
            else:
                print('                  {} no decomposition infinite '
                      'frequency'. format(datetime.datetime.now()))

        return decomp

    def get_seasonal_decompose(self, dataframes:   dict,
                                     periodograms: dict) -> dict:
        """
        Get all of the seasonal decomposes

        Args:
            dataframes:   dataframes for combined data
            periodograms: periodogram data for combined

        Returns:
            all the decompositions
        """

        print('    {} Getting Seasonal Decompositions'.
              format(datetime.datetime.now()))

        decomp = {}
        for label, dataframe in dataframes.items():
            print('        {} Decomposing {} data'.
                  format(datetime.datetime.now(),
                         label))
            decomp_combined = {}
            for table_title, table_data in dataframe.items():
                print('           {} Decomposing {} table'.
                      format(datetime.datetime.now(),
                             table_title))
                periodogram_data = periodograms[label][table_title]
                decomp_combined[table_title] = \
                    self.find_seasonal_decompose(table_data, periodogram_data)

            decomp[label] = decomp_combined

        return decomp



start_time = datetime.datetime.now()
reader  = ReadData.setup(source_name, start_point, tables)
process = ProcessData(reader)
end_time = datetime.datetime.now()
elapsed_time = end_time - start_time

print('Analysis elapsed time: {}'.format(elapsed_time))
