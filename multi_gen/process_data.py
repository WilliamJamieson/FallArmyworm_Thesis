import datetime
import pickle

import dataclasses   as dclass
import pandas        as pd

import numpy as np

import source.hint as hint

import multi_gen.runs as runs

start_point     = runs.start_point
tables          = runs.tables
columns         = runs.columns
simulation_runs = runs.runs


@dclass.dataclass
class ProcessData(object):
    """
    Class to read data
    """
    base_name:  str
    dataframes: dict = dclass.field(default=dict)
    cut_frames: dict = dclass.field(default=dict)
    means:      dict = dclass.field(default=dict)
    medians:    dict = dclass.field(default=dict)
    stds:       dict = dclass.field(default=dict)

    def __post_init__(self):
        """read the data frames"""

        data_file = '{}.data'.format(self.base_name)

        with open(data_file, 'rb') as read_file:
            self.dataframes = pickle.load(read_file)

        self.cut_frames = self.cut_dataframes()
        self.percent_dataframes()

        self.means   = self.mean_dataframes()
        self.medians = self.median_dataframes()
        self.stds    = self.std_dataframes()

    @staticmethod
    def _cut_dataframe(dataframe: hint.dataframe) -> hint.dataframe:
        """
        Cut the dataframe to start at the new point

        Args:
            dataframe: dataframe to cut

        Returns:
            the cut dataframe
        """

        new = dataframe.copy()
        new = new.iloc[start_point:]
        new.reset_index(inplace=True, drop=True)

        return new

    def _cut_dataframes(self, dataframes: hint.dataframes) -> hint.dataframes:
        """
        Cut the dataframes in a given run

        Args:
            dataframes: all the dataframes for a given run

        Returns:
            the cut dataframes
        """

        new = {}
        for table_name, dataframe in dataframes.items():
            print('        {} Cutting table: {}'.
                  format(datetime.datetime.now(), table_name))
            new[table_name] = self._cut_dataframe(dataframe)

        return new

    def cut_dataframes(self) -> dict:
        """
        Cut all the runs to the new start point

        Returns:
            dictionary of cut runs
        """

        data = {}
        for run_num, dataframes in self.dataframes.items():
            print('    {} Cutting Run: {}'.
                  format(datetime.datetime.now(), run_num))
            data[run_num] = self._cut_dataframes(dataframes)

        return data

    @staticmethod
    def _percent_dataframe(dataframe: hint.dataframe) -> None:
        """
        Add percent resist column

        Args:
            dataframe: dataframe to process

        Effects:
            add percent column
        """

        def resist(row) -> float:
            """
            Percent resistant of row value

            Args:
                row: row of dataframe

            Returns:
                percent resistant
            """

            ss = row[columns[2]]
            sr = row[columns[1]]
            rr = row[columns[0]]

            total = 2*(ss + sr + rr)

            if total == 0:
                return np.nan
            else:
                r = 2*rr + sr

                return r / total

        dataframe[columns[3]] = dataframe.apply(lambda row: resist(row), axis=1)

    def _percent_dataframes(self, dataframes: hint.dataframes) -> None:
        """
        Add percent resist column to all dataframes in a run

        Args:
            dataframes: run's dataframes

        Effects:
            add percent columns
        """

        for table_name, dataframe in dataframes.items():
            print('        {} Calculating Percent for: {}'.
                  format(datetime.datetime.now(), table_name))
            self._percent_dataframe(dataframe)

    def percent_dataframes(self) -> None:
        """
        Add percent resist column to all cut dataframes

        Effects:
            add percent columns
        """

        for run_num, dataframes in self.cut_frames.items():
            print('    {} Calculating Percent for: {}'.
                  format(datetime.datetime.now(), run_num))
            self._percent_dataframes(dataframes)

    def _mean_dataframe(self, table_name: str) -> hint.dataframe:
        """
        Get the mean of the given table over all runs

        Args:
            table_name: name of the table to compute

        Returns:
            a mean dataframe table
        """

        data_list = []
        for data in self.cut_frames.values():
            data_list.append(data[table_name])

        concat     = pd.concat(data_list)
        row_concat = concat.groupby(concat.index)

        return row_concat.mean()

    def mean_dataframes(self) -> hint.dataframes:
        """
        Get the mean of all the different tables

        Returns:
            tables of mean values
        """

        means = {}
        for table_name in tables:
            print('    {} Mean for: {}'.
                  format(datetime.datetime.now(), table_name))
            means[table_name] = self._mean_dataframe(table_name)

        return means

    def _median_dataframe(self, table_name: str) -> hint.dataframe:
        """
        Get the median of the given table over all runs

        Args:
            table_name: name of the table to compute

        Returns:
            a median dataframe table
        """

        data_list = []
        for data in self.cut_frames.values():
            data_list.append(data[table_name])

        concat     = pd.concat(data_list)
        row_concat = concat.groupby(concat.index)

        return row_concat.median()

    def median_dataframes(self) -> hint.dataframes:
        """
        Get the median of all the different tables

        Returns:
            tables of median values
        """

        medians = {}
        for table_name in tables:
            print('    {} Median for: {}'.
                  format(datetime.datetime.now(), table_name))
            medians[table_name] = self._median_dataframe(table_name)

        return medians

    def _std_dataframe(self, table_name: str) -> hint.dataframe:
        """
        Get the std of the given table over all runs

        Args:
            table_name: name of the table to compute

        Returns:
            a std dataframe table
        """

        data_list = []
        for data in self.cut_frames.values():
            data_list.append(data[table_name])

        concat     = pd.concat(data_list)
        row_concat = concat.groupby(concat.index)

        return row_concat.std()

    def std_dataframes(self) -> hint.dataframes:
        """
        Get the std of all the different tables

        Returns:
            tables of std values
        """

        stds = {}
        for table_name in tables:
            print('    {} Stds for: {}'.
                  format(datetime.datetime.now(), table_name))
            stds[table_name] = self._std_dataframe(table_name)

        return stds

    @classmethod
    def process_data(cls, base_name: str) -> None:
        """
        Process the simulation data into summary tables

        Args:
            base_name:  simulation base name

        Effects:
            save the summary data
        """

        process = cls(base_name)

        pickle_name = '{}_summary.data'.format(base_name)
        data        = {
            runs.summaries[0]: process.means,
            runs.summaries[1]: process.medians,
            runs.summaries[2]: process.stds
        }

        with open(pickle_name, 'wb') as save_file:
            pickle.dump(data, save_file, protocol=pickle.HIGHEST_PROTOCOL)



for simulation_run in [runs.mix[4]]:
    print('{} Processing Simulation: {}'.
          format(datetime.datetime.now(), simulation_run))
    ProcessData.process_data(simulation_run)
