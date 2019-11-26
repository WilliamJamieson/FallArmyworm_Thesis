import datetime
import pickle

import bokeh.plotting     as plt
import bokeh.layouts      as lay
import bokeh.models       as mdl
import bokeh.palettes     as palettes

import dataclasses   as dclass
import pandas        as pd

import numpy as np

import source.hint as hint

import multi_gen.runs as runs

start_point     = runs.start_point
tables          = runs.tables
columns         = runs.columns
simulation_runs = runs.runs

plot_width  = 800
plot_height = 500

colors    = palettes.Colorblind[8]
save_file = 'error_plots.html'

plt.output_file(save_file)


line_width       = 3.5
point_size       = 10
point_size_stoch = 8

axis_line_width     = 2
grid_line_width     = 2
title_font_size     = '16pt'
legend_font_size    = '12pt'
axis_font_size      = '12pt'
axis_tick_font_size = '10pt'


@dclass.dataclass
class ProcessData(object):
    """
    Class to read data
    """
    base_name:  str
    dataframes: dict = dclass.field(default=dict)
    cut_frames: dict = dclass.field(default=dict)

    def __post_init__(self):
        """read the data frames"""

        data_file = '{}.data'.format(self.base_name)

        with open(data_file, 'rb') as read_file:
            self.dataframes = pickle.load(read_file)

        self.cut_frames = self.cut_dataframes()
        # self.percent_dataframes()

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

    def _mean_dataframe(self, sims:       list,
                              table_name: str) -> hint.dataframe:
        """
        Get the mean of the given table over all runs

        Args:
            sims:       list of simulations to combine
            table_name: name of the table to compute

        Returns:
            a mean dataframe table
        """

        data_list = []
        for sim in sims:
            data = self.cut_frames[sim]
            data_list.append(data[table_name])

        concat     = pd.concat(data_list)
        row_concat = concat.groupby(concat.index)

        return row_concat.mean()

    def mean_dataframes(self, sims: list) -> hint.dataframes:
        """
        Get the mean of all the different tables

        Args:
            sims: list of simulations to compute the mean over

        Returns:
            tables of mean values
        """

        means = {}
        for table_name in tables:
            print('    {} Mean for: {}'.
                  format(datetime.datetime.now(), table_name))
            means[table_name] = self._mean_dataframe(sims, table_name)

        return means

    def all_sims(self) -> dict:
        """
        Get all the sets of sims to average over

        Returns:
            dictionary of lists of sims
        """

        sims = list(self.cut_frames.keys())

        return {
            1:          sims[:1],
            2:          sims[:2],
            4:          sims[:4],
            8:          sims[:8],
            16:         sims[:16],
            32:         sims[:32],
            64:         sims[:64],
            128:        sims[:128],
            len(sims):  sims
        }

    def means(self) -> dict:
        """
        Calculate all of the means

        Returns:
            dictionary of all mean tables
        """

        all_sims = self.all_sims()

        means = {}
        for num, sims in all_sims.items():
            means[num] = self.mean_dataframes(sims)

        return means

    @staticmethod
    def _diffs(means_0: hint.dataframes,
               means_1: hint.dataframes) -> dict:
        """
        Find the squared difference
        Args:
            means_0: data set 0
            means_1: data set 1

        Returns:
            dictionary of square diff
        """

        diffs = {}

        for table_name, mean_0 in means_0.items():
            mean_1 = means_1[table_name]

            diff = mean_0 - mean_1
            diff = diff.pow(2)
            diff = diff.pow(0.5)

            diffs[table_name] = diff

        return diffs


    def diffs(self) -> dict:
        """
        Compute the differences pairwise

        Returns:
            difference dictionary
        """

        means = self.means()
        sims  = list(means.keys())

        diffs = {}
        for index in range(len(means) - 1):
            sim_0 = sims[index]
            sim_1 = sims[index + 1]

            means_0 = means[sim_0]
            means_1 = means[sim_1]

            diffs[sim_0] = self._diffs(means_0,
                                       means_1)

        return diffs

    @staticmethod
    def _integral(diffs: hint.dataframes,
                  total: hint.dataframes) -> dict:
        """
        Find the root of the column sums
        Args:
            diffs: difference data
            total: the final data

        Returns:
            dict of data points
        """

        values = {}
        for table_name, diff in diffs.items():
            actual   = total[table_name].sum()
            integral = diff.sum()
            values[table_name] = integral.div(actual)

        return values

    def integral(self) -> dict:
        """
        Find integral of all the data

        Returns:
            dict of data points
        """

        difference = self.diffs()
        sims       = list(difference.keys())
        total      = self.mean_dataframes(sims)

        integral = {}
        for num, diffs in difference.items():
            integral[num] = self._integral(diffs, total)

        return integral

    def series(self) -> dict:
        """
        Create a series of data points

        Returns:
            dictionary of data series
        """

        integral = self.integral()
        sims = list(integral.keys())

        data = {}
        for table_name in runs.tables:
            data_columns = {}
            for column in runs.columns:
                data_sim = {}
                for sim in sims:
                    data_sim[sim] = integral[sim][table_name][column]
                data_columns[column] = data_sim
            data[table_name] = data_columns

        return data

    @staticmethod
    def _plot(error: dict,
              title: str):
        """
        Create an error plot

        Args:
            error: error dictionary
            title: title of plot

        Returns:
            plot structure
        """
        reg_plot            = plt.figure(plot_height=plot_height,
                                         plot_width=plot_width)
        reg_plot.title.text = title
        reg_plot.xaxis.axis_label = 'trials'
        reg_plot.yaxis.axis_label = 'Mean Relative Error'

        reg_plot.line(list(error.keys()), list(error.values()),
                      line_width=line_width,
                      color=colors[0])

        reg_plot.title.text_font_size = title_font_size
        reg_plot.yaxis.axis_line_width = axis_line_width
        reg_plot.xaxis.axis_line_width = axis_line_width
        reg_plot.yaxis.axis_label_text_font_size = axis_font_size
        reg_plot.xaxis.axis_label_text_font_size = axis_font_size
        reg_plot.yaxis.major_label_text_font_size = axis_tick_font_size
        reg_plot.xaxis.major_label_text_font_size = axis_tick_font_size
        reg_plot.ygrid.grid_line_width = grid_line_width
        reg_plot.xgrid.grid_line_width = grid_line_width

        return reg_plot

    def plot_columns(self, errors: dict,
                           title:  str) -> dict:
        """
        Plot all of the columns of data

        Args:
            errors: dictionary of error data
            title:  title of table

        Returns:
            dictionary of plots
        """

        plots = {}
        for column, error in errors.items():
            plot_title = '{} {}'.format(title, column)
            plots[column] = self._plot(error, plot_title)

        return plots

    def plot(self) -> dict:
        """
        Create all of the plots

        Returns:
            all of the error plots
        """

        series = self.series()

        plots = {}
        for table_name, errors in series.items():
            title = table_name.split('_')[1]
            plots[table_name] = self.plot_columns(errors,
                                                  title)

        return plots
