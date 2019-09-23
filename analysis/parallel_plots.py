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


start_point = 200

plot_width  = 1500
plot_height = 400

colors = palettes.Set1[3]

frequency_range = [62, 63, 64]


save_file = 'parallel_timeseries_decomp.html'
# source_name = 'long_sim_25_gen_no_im_bt_10_no_hetero.sqlite'
# source_name = 'parallel_sim_25_gen_no_bt_only_sus'
source_name = 'parallel_sim_50_gen_no_bt_only_sus'
source_path = '/home/william/Dropbox/Research/Parallel_FallArmyworm/' \
              'simulations/'
tables      = ['(0,)_egg',
               '(0,)_larva',
               '(0,)_pupa',
               '(0,)_female']

plt.output_file(save_file)


@dclass.dataclass
class ReadData(object):
    """
    Class to read data
    """

    base_name:   str
    base_path:   str
    table_names: list
    file_names:  dict = dclass.field(default=dict)

    def __post_init__(self):
        """Get the file names"""

        self.file_names = self.get_file_names()


    def get_file_list(self) -> list:
        """
        Get a list of all the files with base name

        Returns:
            list of all the files in base_path which use the base_name
        """

        files = os.listdir(self.base_path)
        files = [f for f in files if self.base_name in f]

        return files

    def get_run_file_lists(self) -> dict:
        """
        Get dictionary of file name lists by run tag

        Returns:
            the dictionary of names
        """

        files = self.get_file_list()

        file_dict = {}
        for file in files:
            end_tag    = file.split('_')[-1]
            end_number = int(end_tag.split('.')[0])

            if end_number in file_dict:
                file_dict[end_number].append(file)
            else:
                file_dict[end_number] = [file]

        return file_dict

    @staticmethod
    def _sort_file_names(files: list) -> list:
        """
        Sort the files in file list by number

        Args:
            files: list of files to sort for a run

        Returns:
            the files in order
        """

        file_dict = {}
        for file in files:
            f_num = int(file.split('_')[0])
            if f_num in file_dict:
                raise RuntimeError('bad run number found')
            else:
                file_dict[f_num] = file

        file_nums = list(file_dict.keys())
        file_nums.sort()

        return [file_dict[f_num] for f_num in file_nums]

    def get_sorted_file_lists(self) -> dict:
        """
        Get dictionary of file name lists by run tag with file lists in order

        Returns:
            the dictionary of names
        """

        files_dict = self.get_run_file_lists()

        return {run_num: self._sort_file_names(files)
                    for run_num, files in files_dict.items()}


    def get_file_names(self) -> dict:
        """
        Get dictionary of file name lists by run tag with file lists in order

        Returns:
            the dictionary of names in order by call
        """

        file_dict = self.get_sorted_file_lists()

        run_nums = list(file_dict.keys())
        run_nums.sort()

        return {run_num: file_dict[run_num] for run_num in run_nums}

    def sql_filename(self, file_name: str) -> str:
        """
        Return the sql filename for sql alchemy

        Args:
            file_name: name of the file

        Returns:
            argument for sql alchemy
        """

        dialect = 'sqlite:///'

        return '{}{}{}'.format(dialect, self.base_path, file_name)

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

    def dataframe(self, files:      list,
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

    def dataframes(self, files: list) -> hint.dataframes:
        """
        Get all of the dataframes that we wish to use

        Args:
            files: list of files to combine the read on

        Returns:
            dictionary of all the dataframes we want
        """

        dataframes = {}

        for table_name in self.table_names:
            dataframes[table_name] = self.dataframe(files, table_name)

        return dataframes

    def run_dataframes(self) -> dict:
        """
        Get a dictionary of all the run data in single dataframe format

        Returns:
            all the run data frames
        """

        data = {}
        for run_num, files in self.file_names.items():
            data[run_num] = self.dataframes(files)

        return data

    @staticmethod
    def cut_dataframe(dataframe: hint.dataframe,
                      start:     int) -> hint.dataframe:
        """
        Cut dataframe to start at new point

        Args:
            dataframe: dataframe to cut
            start:     new start point

        Returns:
            the cut dataframe
        """

        new = dataframe.copy()
        new = new.iloc[start:]
        new.reset_index(inplace=True, drop=True)
        new['index'] = range(len(new.index))

        return new

    def cut_single_dataframes(self, dataframes: hint.dataframes,
                                    start:      int) -> hint.dataframes:
        """
        Cut the read dataframes to the correct start point

        Args:
            dataframes: the collection of dataframes we process
            start:      the correct start point

        Returns:
            the dataframes to the right start point
        """

        new = {}
        for table_name, dataframe in dataframes.items():
            new[table_name] = self.cut_dataframe(dataframe, start)

        return new

    def cut_run_dataframes(self, start: int) -> dict:
        """
        Get cut all the dataframes at same start

        Args:
            start: the correct starting point

        Returns:
            all the data frames cut down
        """

        raw_data = self.run_dataframes()

        data = {}
        for run_num, dataframes in raw_data.items():
            data[run_num] = self.cut_single_dataframes(dataframes, start)

        return data

    def mean_dataframe(self, raw_data: dict) -> hint.dataframes:
        """
        Generate a mean dataframe for all of the data

        Args:
            raw_data: data by run for the system

        Returns:
            dataframes of all the mean data
        """

        means = {}
        for table_name in self.table_names:
            data_list = []
            for data in raw_data.values():
                data_list.append(data[table_name])

            concat     = pd.concat(data_list)
            row_concat = concat.groupby(concat.index)
            mean_data  = row_concat.mean()
            mean_data['index'] = range(len(mean_data.index))

            means[table_name] = mean_data

        return means

    def median_dataframe(self, raw_data: dict) -> hint.dataframes:
        """
        Generate a median dataframe for all of the data

        Args:
            raw_data: data by run for the system

        Returns:
            dataframes of all the median data
        """

        medians = {}
        for table_name in self.table_names:
            data_list = []
            for data in raw_data.values():
                data_list.append(data[table_name])

            concat      = pd.concat(data_list)
            row_concat  = concat.groupby(concat.index)
            median_data = row_concat.median()
            median_data['index'] = range(len(median_data.index))

            medians[table_name] = median_data

        return medians

    def std_dataframe(self, raw_data: dict) -> hint.dataframes:
        """
        Generate a std dataframe for all of the data

        Args:
            raw_data: data by run for the system

        Returns:
            dataframes of all the std data
        """

        stds = {}
        for table_name in self.table_names:
            data_list = []
            for data in raw_data.values():
                data_list.append(data[table_name])

            concat     = pd.concat(data_list)
            row_concat = concat.groupby(concat.index)
            std_data   = row_concat.std()
            std_data['index'] = range(len(std_data.index))

            stds[table_name] = std_data

        return stds

    def q_lower_dataframe(self, raw_data: dict) -> hint.dataframes:
        """
        Generate a q_lower dataframe for all of the data

        Args:
            raw_data: data by run for the system

        Returns:
            dataframes of all the q_lower data
        """

        q_lowers = {}
        for table_name in self.table_names:
            data_list = []
            for data in raw_data.values():
                data_list.append(data[table_name])

            concat       = pd.concat(data_list)
            row_concat   = concat.groupby(concat.index)
            q_lower_data = row_concat.quantile(2.5)
            q_lower_data['index'] = range(len(q_lower_data.index))

            q_lowers[table_name] = q_lower_data

        return q_lowers

    def q_upper_dataframe(self, raw_data: dict) -> hint.dataframes:
        """
        Generate a q_upper dataframe for all of the data

        Args:
            raw_data: data by run for the system

        Returns:
            dataframes of all the q_upper data
        """

        q_uppers = {}
        for table_name in self.table_names:
            data_list = []
            for data in raw_data.values():
                data_list.append(data[table_name])

            concat       = pd.concat(data_list)
            row_concat   = concat.groupby(concat.index)
            q_upper_data = row_concat.quantile(97.5)
            q_upper_data['index'] = range(len(q_upper_data.index))

            q_uppers[table_name] = q_upper_data

        return q_uppers

    def min_dataframe(self, raw_data: dict) -> hint.dataframes:
        """
        Generate a min dataframe for all of the data

        Args:
            raw_data: data by run for the system

        Returns:
            dataframes of all the min data
        """

        mins = {}
        for table_name in self.table_names:
            data_list = []
            for data in raw_data.values():
                data_list.append(data[table_name])

            concat     = pd.concat(data_list)
            row_concat = concat.groupby(concat.index)
            min_data   = row_concat.min()
            min_data['index'] = range(len(min_data.index))

            mins[table_name] = min_data

        return mins

    def max_dataframe(self, raw_data: dict) -> hint.dataframes:
        """
        Generate a max dataframe for all of the data

        Args:
            raw_data: data by run for the system

        Returns:
            dataframes of all the max data
        """

        maxs = {}
        for table_name in self.table_names:
            data_list = []
            for data in raw_data.values():
                data_list.append(data[table_name])

            concat     = pd.concat(data_list)
            row_concat = concat.groupby(concat.index)
            max_data   = row_concat.max()
            max_data['index'] = range(len(max_data.index))

            maxs[table_name] = max_data

        return maxs

    def process_dataframes(self, start: int) -> tuple:
        """
        Process all of the dataframes together

        Args:
            start: the correct starting point

        Returns:
            all the data frames cut down
        """

        data     = self.cut_run_dataframes(start)
        num_runs = len(data)

        data['mean']    = self.mean_dataframe(data)
        data['median']  = self.median_dataframe(data)
        # data['std']     = self.std_dataframe(data)
        # data['q_lower'] = self.q_lower_dataframe(data)
        # data['q_upper'] = self.q_upper_dataframe(data)
        # data['min']     = self.min_dataframe(data)
        # data['max']     = self.max_dataframe(data)

        return data, num_runs

    @staticmethod
    def _seasonal_decompose(dataframe: hint.dataframe,
                            frequency: int):
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

        return decomp

    def seasonal_decompose(self, dataframe: hint.dataframe) -> dict:
        """
        Decompose the data into all frequencies within the limit

        Args:
            dataframe: the dataframe to use

        Returns:
            dictionary of frequency to data
        """

        season = {}
        for frequency in frequency_range:
            season[frequency] = self._seasonal_decompose(dataframe, frequency)

        return season


reader                   = ReadData(source_name, source_path, tables)
run_data, number_of_runs = reader.process_dataframes(start_point)

mean    = run_data['mean']
median  = run_data['median']
# std     = run_data['std']
# q_lower = run_data['q_lower']
# min_val = run_data['min']
# max_val = run_data['max']

egg_mean    = mean[tables[0]]
larva_mean  = mean[tables[1]]
pupa_mean   = mean[tables[2]]
female_mean = mean[tables[3]]

egg_median    = median[tables[0]]
larva_median  = median[tables[1]]
pupa_median   = median[tables[2]]
female_median = median[tables[3]]


def periodogram_data(dataframe: hint.dataframe) -> hint.dataframes:
    """
    Create a periodogram of the data in the dataframe

    Args:
        dataframe: dataframe to create periodogram data

    Returns:
        periodogram dataframe
    """

    column_titles = ['genotype_resistant',
                     'genotype_heterozygous',
                     'genotype_susceptible']

    data_dict = {}
    for column_title in column_titles:
        periodogram_dict = {}
        frequency_data, power_data = signal.periodogram(dataframe[column_title])
        period_data = (1 / frequency_data[1:]).tolist()
        period_data.insert(0, np.inf)
        periodogram_dict['frequency'] = frequency_data
        periodogram_dict['power']     = power_data
        periodogram_dict['period']    = period_data

        periodogram_dataframe = pd.DataFrame.from_dict(periodogram_dict)
        periodogram_dataframe['genotype'] = column_title.split('_')[1]

        data_dict[column_title] = periodogram_dataframe

    return data_dict


egg_mean_periodogram    = periodogram_data(egg_mean)
larva_mean_periodogram  = periodogram_data(larva_mean)
pupa_mean_periodogram   = periodogram_data(pupa_mean)
female_mean_periodogram = periodogram_data(female_mean)

egg_median_periodogram    = periodogram_data(egg_median)
larva_median_periodogram  = periodogram_data(larva_median)
pupa_median_periodogram   = periodogram_data(pupa_median)
female_median_periodogram = periodogram_data(female_median)


egg_mean_decomp    = reader.seasonal_decompose(egg_mean)
larva_mean_decomp  = reader.seasonal_decompose(larva_mean)
pupa_mean_decomp   = reader.seasonal_decompose(pupa_mean)
female_mean_decomp = reader.seasonal_decompose(female_mean)

egg_median_decomp    = reader.seasonal_decompose(egg_median)
larva_median_decomp  = reader.seasonal_decompose(larva_median)
pupa_median_decomp   = reader.seasonal_decompose(pupa_median)
female_median_decomp = reader.seasonal_decompose(female_median)

egg_mean_source    = mdl.ColumnDataSource(egg_mean)
larva_mean_source  = mdl.ColumnDataSource(larva_mean)
pupa_mean_source   = mdl.ColumnDataSource(pupa_mean)
female_mean_source = mdl.ColumnDataSource(female_mean)

egg_median_source    = mdl.ColumnDataSource(egg_median)
larva_median_source  = mdl.ColumnDataSource(larva_median)
pupa_median_source   = mdl.ColumnDataSource(pupa_median)
female_median_source = mdl.ColumnDataSource(female_median)


def periodogram_data_source(periodogram_dataframe: dict) -> dict:
    """
    Convert the data into a data source for bokeh
    Args:
        periodogram_dataframe: the periodogram data

    Returns:
        dictionary of source data
    """

    data_sources = {}
    for column_name, data_source in periodogram_dataframe.items():
        data_sources[column_name] = mdl.ColumnDataSource(data_source)

    return data_sources


egg_mean_periodogram_sources    = periodogram_data_source(
    egg_mean_periodogram)
larva_mean_periodogram_sources  = periodogram_data_source(
    larva_mean_periodogram)
pupa_mean_periodogram_sources   = periodogram_data_source(
    pupa_mean_periodogram)
female_mean_periodogram_sources = periodogram_data_source(
    female_mean_periodogram)

egg_median_periodogram_sources    = periodogram_data_source(
    egg_median_periodogram)
larva_median_periodogram_sources  = periodogram_data_source(
    larva_median_periodogram)
pupa_median_periodogram_sources   = periodogram_data_source(
    pupa_median_periodogram)
female_median_periodogram_sources = periodogram_data_source(
    female_median_periodogram)


def seasonal_data_source(decomp_data: dict) -> dict:
    """
    Convert the decomp data into a data source for bokeh

    Args:
        decomp_data: the data source

    Returns:
        dictionary of tuples
    """

    data_sources = {}
    for frequency, data_source in decomp_data.items():
        data_sources[frequency] = (mdl.ColumnDataSource(data_source.trend),
                                   mdl.ColumnDataSource(data_source.seasonal),
                                   mdl.ColumnDataSource(data_source.resid))

    return data_sources


egg_mean_seasonal_sources    = seasonal_data_source(egg_mean_decomp)
larva_mean_seasonal_sources  = seasonal_data_source(larva_mean_decomp)
pupa_mean_seasonal_sources   = seasonal_data_source(pupa_mean_decomp)
female_mean_seasonal_sources = seasonal_data_source(female_mean_decomp)

egg_median_seasonal_sources    = seasonal_data_source(egg_median_decomp)
larva_median_seasonal_sources  = seasonal_data_source(larva_median_decomp)
pupa_median_seasonal_sources   = seasonal_data_source(pupa_median_decomp)
female_median_seasonal_sources = seasonal_data_source(female_median_decomp)


def periodogram_plotter(periodogram_mean_source, periodogram_median_source,
                        life_stage_title: str):
    """
    Create a set of periodograms
    Args:
        periodogram_mean_source:   mean data periodogram
        periodogram_median_source: median data periodogram
        life_stage_title:          name for life stage

    Returns:
        a plot system to show
    """

    mean_plot = plt.figure()
    mean_plot.title.text = '{} Mean Periodogram'.format(life_stage_title)
    mean_plot.yaxis.axis_label = 'Power Spectral Density'
    mean_plot.xaxis.axis_label = 'Frequency'
    mean_plot.line(x='frequency', y='power',
                   source=periodogram_mean_source['genotype_resistant'],
                   color=colors[0], legend='Resistant')
    mean_plot.line(x='frequency', y='power',
                   source=periodogram_mean_source['genotype_heterozygous'],
                   color=colors[1], legend='Heterozygous')
    mean_plot.line(x='frequency', y='power',
                   source=periodogram_mean_source['genotype_susceptible'],
                   color=colors[2], legend='Susceptible')
    mean_hover = tools.HoverTool()
    mean_hover.tooltips = [
        ('Frequency',        '@frequency'),
        ('Period',           '@period'),
        ('Spectral Density', '@power'),
        ('Genotype',         '@genotype')
    ]
    mean_plot.add_tools(mean_hover)

    median_plot = plt.figure()
    median_plot.title.text = '{} Median Periodogram'.format(life_stage_title)
    median_plot.yaxis.axis_label = 'Power Spectral Density'
    median_plot.xaxis.axis_label = 'Frequency'
    median_plot.line(x='frequency', y='power',
                     source=periodogram_median_source['genotype_resistant'],
                     color=colors[0], legend='Resistant')
    median_plot.line(x='frequency', y='power',
                     source=periodogram_median_source['genotype_heterozygous'],
                     color=colors[1], legend='Heterozygous')
    median_plot.line(x='frequency', y='power',
                     source=periodogram_median_source['genotype_susceptible'],
                     color=colors[2], legend='Susceptible')
    median_hover = tools.HoverTool()
    median_hover.tooltips = [
        ('Frequency', '@frequency'),
        ('Period', '@period'),
        ('Spectral Density', '@power'),
        ('Genotype', '@genotype')
    ]
    median_plot.add_tools(median_hover)

    mean_log_plot = plt.figure(y_axis_type='log')
    mean_log_plot.title.text = '{} Mean Log-Scale Periodogram'.\
        format(life_stage_title)
    mean_log_plot.yaxis.axis_label = 'log(Power Spectral Density)'
    mean_log_plot.xaxis.axis_label = 'Frequency'
    mean_log_plot.line(x='frequency', y='power',
                       source=periodogram_mean_source['genotype_resistant'],
                       color=colors[0], legend='Resistant')
    mean_log_plot.line(x='frequency', y='power',
                       source=periodogram_mean_source['genotype_heterozygous'],
                       color=colors[1], legend='Heterozygous')
    mean_log_plot.line(x='frequency', y='power',
                       source=periodogram_mean_source['genotype_susceptible'],
                       color=colors[2], legend='Susceptible')
    mean_log_hover = tools.HoverTool()
    mean_log_hover.tooltips = [
        ('Frequency', '@frequency'),
        ('Period', '@period'),
        ('Spectral Density', '@power'),
        ('Genotype', '@genotype')
    ]
    mean_log_plot.add_tools(mean_log_hover)

    median_log_plot = plt.figure(y_axis_type='log')
    median_log_plot.title.text = '{} Median Log-Scale Periodogram'. \
        format(life_stage_title)
    median_log_plot.yaxis.axis_label = 'log(Power Spectral Density)'
    median_log_plot.xaxis.axis_label = 'Frequency'
    median_log_plot.line(x='frequency', y='power',
                         source=periodogram_median_source['genotype_resistant'],
                         color=colors[0], legend='Resistant')
    median_log_plot.line(x='frequency', y='power',
                         source=periodogram_median_source['genotype_heterozygous'],
                         color=colors[1], legend='Heterozygous')
    median_log_plot.line(x='frequency', y='power',
                         source=periodogram_median_source['genotype_susceptible'],
                         color=colors[2], legend='Susceptible')
    median_log_hover = tools.HoverTool()
    median_log_hover.tooltips = [
        ('Frequency', '@frequency'),
        ('Period', '@period'),
        ('Spectral Density', '@power'),
        ('Genotype', '@genotype')
    ]
    median_log_plot.add_tools(median_log_hover)

    return lay.gridplot([[mean_plot,     median_plot],
                         [mean_log_plot, median_log_plot]],
                        toolbar_location='left')


larva_periodogram_title = mdl.Div(text='<h1>Larva Periodogram, '
                                         '{} runs</h1>'.format(number_of_runs))
larva_periodogram_plot = periodogram_plotter(larva_mean_periodogram_sources,
                                             larva_median_periodogram_sources,
                                             'Larva')


def seasonal_data_plotter(timeseries_mean_source,   decomp_mean_source: dict,
                          timeseries_median_source, decomp_median_source: dict,
                          life_stage_title: str):
    """
    Create a plot of the seasonal data via frequencies
    Args:
        timeseries_mean_source:   original series source for mean
        decomp_mean_source:       decomposition source   for mean
        timeseries_median_source: original series source for median
        decomp_median_source:     decomposition source   for median
        life_stage_title:         name for life stage

    Returns:
        a plotting object
    """

    frequencies    = list(decomp_mean_source.keys())
    base_frequency = frequencies.pop(0)

    first_line = []
    base_plot = plt.figure(plot_width=plot_width, plot_height=plot_height)
    base_plot.title.text = '{} Timeseries Mean Data, Seasonal Frequency: {}'.\
        format(life_stage_title, base_frequency)
    base_plot.yaxis.axis_label = 'Population'
    base_plot.xaxis.axis_label = 'time (days)'
    base_plot.line(x='index', y='genotype_resistant',
                   source=timeseries_mean_source,
                   color=colors[0], legend='Resistant')
    base_plot.line(x='index', y='genotype_heterozygous',
                   source=timeseries_mean_source,
                   color=colors[1], legend='Heterozygous')
    base_plot.line(x='index', y='genotype_susceptible',
                   source=timeseries_mean_source,
                   color=colors[2], legend='Susceptible')
    first_line.append(base_plot)

    trend_plot = plt.figure(plot_width=plot_width, plot_height=plot_height,
                            x_range=base_plot.x_range)
    trend_plot.title.text = '{} Trend Mean Data, Seasonal Frequency: {}'. \
        format(life_stage_title, base_frequency)
    trend_plot.yaxis.axis_label = 'Population'
    trend_plot.xaxis.axis_label = 'time (days)'
    trend_plot.line(x='index', y='genotype_resistant',
                    source=decomp_mean_source[base_frequency][0],
                    color=colors[0], legend='Resistant')
    trend_plot.line(x='index', y='genotype_heterozygous',
                    source=decomp_mean_source[base_frequency][0],
                    color=colors[1], legend='Heterozygous')
    trend_plot.line(x='index', y='genotype_susceptible',
                    source=decomp_mean_source[base_frequency][0],
                    color=colors[2], legend='Susceptible')
    first_line.append(trend_plot)

    seasonal_plot = plt.figure(plot_width=plot_width, plot_height=plot_height,
                               x_range=base_plot.x_range)
    seasonal_plot.title.text = '{} Seasonality Mean Data, ' \
                               'Seasonal Frequency: {}'. \
        format(life_stage_title, base_frequency)
    seasonal_plot.yaxis.axis_label = 'Population'
    seasonal_plot.xaxis.axis_label = 'time (days)'
    seasonal_plot.line(x='index', y='genotype_resistant',
                       source=decomp_mean_source[base_frequency][1],
                       color=colors[0], legend='Resistant')
    seasonal_plot.line(x='index', y='genotype_heterozygous',
                       source=decomp_mean_source[base_frequency][1],
                       color=colors[1], legend='Heterozygous')
    seasonal_plot.line(x='index', y='genotype_susceptible',
                       source=decomp_mean_source[base_frequency][1],
                       color=colors[2], legend='Susceptible')
    first_line.append(seasonal_plot)

    resid_plot = plt.figure(plot_width=plot_width, plot_height=plot_height,
                            x_range=base_plot.x_range)
    resid_plot.title.text = '{} Residual Mean Data, Seasonal Frequency: {}'. \
        format(life_stage_title, base_frequency)
    resid_plot.yaxis.axis_label = 'Population'
    resid_plot.xaxis.axis_label = 'time (days)'
    resid_plot.line(x='index', y='genotype_resistant',
                    source=decomp_mean_source[base_frequency][2],
                    color=colors[0], legend='Resistant')
    resid_plot.line(x='index', y='genotype_heterozygous',
                    source=decomp_mean_source[base_frequency][2],
                    color=colors[1], legend='Heterozygous')
    resid_plot.line(x='index', y='genotype_susceptible',
                    source=decomp_mean_source[base_frequency][2],
                    color=colors[2], legend='Susceptible')
    first_line.append(resid_plot)

    series_plot = plt.figure(plot_width=plot_width, plot_height=plot_height,
                             x_range=base_plot.x_range)
    series_plot.title.text = '{} Timeseries Median Data, ' \
                             'Seasonal Frequency: {}'. \
        format(life_stage_title, base_frequency)
    series_plot.yaxis.axis_label = 'Population'
    series_plot.xaxis.axis_label = 'time (days)'
    series_plot.line(x='index', y='genotype_resistant',
                     source=timeseries_median_source,
                     color=colors[0], legend='Resistant')
    series_plot.line(x='index', y='genotype_heterozygous',
                     source=timeseries_median_source,
                     color=colors[1], legend='Heterozygous')
    series_plot.line(x='index', y='genotype_susceptible',
                     source=timeseries_median_source,
                     color=colors[2], legend='Susceptible')
    first_line.append(series_plot)

    trend_plot = plt.figure(plot_width=plot_width, plot_height=plot_height,
                            x_range=base_plot.x_range)
    trend_plot.title.text = '{} Trend Median Data, Seasonal Frequency: {}'. \
        format(life_stage_title, base_frequency)
    trend_plot.yaxis.axis_label = 'Population'
    trend_plot.xaxis.axis_label = 'time (days)'
    trend_plot.line(x='index', y='genotype_resistant',
                    source=decomp_median_source[base_frequency][0],
                    color=colors[0], legend='Resistant')
    trend_plot.line(x='index', y='genotype_heterozygous',
                    source=decomp_median_source[base_frequency][0],
                    color=colors[1], legend='Heterozygous')
    trend_plot.line(x='index', y='genotype_susceptible',
                    source=decomp_median_source[base_frequency][0],
                    color=colors[2], legend='Susceptible')
    first_line.append(trend_plot)

    seasonal_plot = plt.figure(plot_width=plot_width, plot_height=plot_height,
                               x_range=base_plot.x_range)
    seasonal_plot.title.text = '{} Seasonality Median Data, ' \
                               'Seasonal Frequency: {}'. \
        format(life_stage_title, base_frequency)
    seasonal_plot.yaxis.axis_label = 'Population'
    seasonal_plot.xaxis.axis_label = 'time (days)'
    seasonal_plot.line(x='index', y='genotype_resistant',
                       source=decomp_median_source[base_frequency][1],
                       color=colors[0], legend='Resistant')
    seasonal_plot.line(x='index', y='genotype_heterozygous',
                       source=decomp_median_source[base_frequency][1],
                       color=colors[1], legend='Heterozygous')
    seasonal_plot.line(x='index', y='genotype_susceptible',
                       source=decomp_median_source[base_frequency][1],
                       color=colors[2], legend='Susceptible')
    first_line.append(seasonal_plot)

    resid_plot = plt.figure(plot_width=plot_width, plot_height=plot_height,
                            x_range=base_plot.x_range)
    resid_plot.title.text = '{} Residual Median Data, Seasonal Frequency: {}'. \
        format(life_stage_title, base_frequency)
    resid_plot.yaxis.axis_label = 'Population'
    resid_plot.xaxis.axis_label = 'time (days)'
    resid_plot.line(x='index', y='genotype_resistant',
                    source=decomp_median_source[base_frequency][2],
                    color=colors[0], legend='Resistant')
    resid_plot.line(x='index', y='genotype_heterozygous',
                    source=decomp_median_source[base_frequency][2],
                    color=colors[1], legend='Heterozygous')
    resid_plot.line(x='index', y='genotype_susceptible',
                    source=decomp_median_source[base_frequency][2],
                    color=colors[2], legend='Susceptible')
    first_line.append(resid_plot)

    grid_lines = [first_line]
    for frequency in frequencies:
        line_plots = []
        series_plot = plt.figure(plot_width=plot_width, plot_height=plot_height,
                                 x_range=base_plot.x_range)
        series_plot.title.text = '{} Timeseries Mean Data, ' \
                                 'Seasonal Frequency: {}'. \
            format(life_stage_title, frequency)
        series_plot.yaxis.axis_label = 'Population'
        series_plot.xaxis.axis_label = 'time (days)'
        series_plot.line(x='index', y='genotype_resistant',
                         source=timeseries_mean_source,
                         color=colors[0], legend='Resistant')
        series_plot.line(x='index', y='genotype_heterozygous',
                         source=timeseries_mean_source,
                         color=colors[1], legend='Heterozygous')
        series_plot.line(x='index', y='genotype_susceptible',
                         source=timeseries_mean_source,
                         color=colors[2], legend='Susceptible')
        line_plots.append(series_plot)

        trend_plot = plt.figure(plot_width=plot_width, plot_height=plot_height,
                                x_range=base_plot.x_range)
        trend_plot.title.text = '{} Trend Mean Data, Seasonal Frequency: {}'. \
            format(life_stage_title, frequency)
        trend_plot.yaxis.axis_label = 'Population'
        trend_plot.xaxis.axis_label = 'time (days)'
        trend_plot.line(x='index', y='genotype_resistant',
                        source=decomp_mean_source[frequency][0],
                        color=colors[0], legend='Resistant')
        trend_plot.line(x='index', y='genotype_heterozygous',
                        source=decomp_mean_source[frequency][0],
                        color=colors[1], legend='Heterozygous')
        trend_plot.line(x='index', y='genotype_susceptible',
                        source=decomp_mean_source[frequency][0],
                        color=colors[2], legend='Susceptible')
        line_plots.append(trend_plot)

        seasonal_plot = plt.figure(plot_width=plot_width,
                                   plot_height=plot_height,
                                   x_range=base_plot.x_range)
        seasonal_plot.title.text = '{} Seasonality Mean Data, ' \
                                   'Seasonal Frequency: {}'. \
            format(life_stage_title, frequency)
        seasonal_plot.yaxis.axis_label = 'Population'
        seasonal_plot.xaxis.axis_label = 'time (days)'
        seasonal_plot.line(x='index', y='genotype_resistant',
                           source=decomp_mean_source[frequency][1],
                           color=colors[0], legend='Resistant')
        seasonal_plot.line(x='index', y='genotype_heterozygous',
                           source=decomp_mean_source[frequency][1],
                           color=colors[1], legend='Heterozygous')
        seasonal_plot.line(x='index', y='genotype_susceptible',
                           source=decomp_mean_source[frequency][1],
                           color=colors[2], legend='Susceptible')
        line_plots.append(seasonal_plot)

        resid_plot = plt.figure(plot_width=plot_width, plot_height=plot_height,
                                x_range=base_plot.x_range)
        resid_plot.title.text = '{} Residual Mean Data, ' \
                                'Seasonal Frequency: {}'. \
            format(life_stage_title, frequency)
        resid_plot.yaxis.axis_label = 'Population'
        resid_plot.xaxis.axis_label = 'time (days)'
        resid_plot.line(x='index', y='genotype_resistant',
                        source=decomp_mean_source[frequency][2],
                        color=colors[0], legend='Resistant')
        resid_plot.line(x='index', y='genotype_heterozygous',
                        source=decomp_mean_source[frequency][2],
                        color=colors[1], legend='Heterozygous')
        resid_plot.line(x='index', y='genotype_susceptible',
                        source=decomp_mean_source[frequency][2],
                        color=colors[2], legend='Susceptible')
        line_plots.append(resid_plot)

        series_plot = plt.figure(plot_width=plot_width, plot_height=plot_height,
                                 x_range=base_plot.x_range)
        series_plot.title.text = '{} Timeseries Median Data, ' \
                                 'Seasonal Frequency: {}'. \
            format(life_stage_title, frequency)
        series_plot.yaxis.axis_label = 'Population'
        series_plot.xaxis.axis_label = 'time (days)'
        series_plot.line(x='index', y='genotype_resistant',
                         source=timeseries_median_source,
                         color=colors[0], legend='Resistant')
        series_plot.line(x='index', y='genotype_heterozygous',
                         source=timeseries_median_source,
                         color=colors[1], legend='Heterozygous')
        series_plot.line(x='index', y='genotype_susceptible',
                         source=timeseries_median_source,
                         color=colors[2], legend='Susceptible')
        line_plots.append(series_plot)

        trend_plot = plt.figure(plot_width=plot_width, plot_height=plot_height,
                                x_range=base_plot.x_range)
        trend_plot.title.text = '{} Trend Median Data, ' \
                                'Seasonal Frequency: {}'. \
            format(life_stage_title, frequency)
        trend_plot.yaxis.axis_label = 'Population'
        trend_plot.xaxis.axis_label = 'time (days)'
        trend_plot.line(x='index', y='genotype_resistant',
                        source=decomp_median_source[frequency][0],
                        color=colors[0], legend='Resistant')
        trend_plot.line(x='index', y='genotype_heterozygous',
                        source=decomp_median_source[frequency][0],
                        color=colors[1], legend='Heterozygous')
        trend_plot.line(x='index', y='genotype_susceptible',
                        source=decomp_median_source[frequency][0],
                        color=colors[2], legend='Susceptible')
        line_plots.append(trend_plot)

        seasonal_plot = plt.figure(plot_width=plot_width,
                                   plot_height=plot_height,
                                   x_range=base_plot.x_range)
        seasonal_plot.title.text = '{} Seasonality Median Data, ' \
                                   'Seasonal Frequency: {}'. \
            format(life_stage_title, frequency)
        seasonal_plot.yaxis.axis_label = 'Population'
        seasonal_plot.xaxis.axis_label = 'time (days)'
        seasonal_plot.line(x='index', y='genotype_resistant',
                           source=decomp_median_source[frequency][1],
                           color=colors[0], legend='Resistant')
        seasonal_plot.line(x='index', y='genotype_heterozygous',
                           source=decomp_median_source[frequency][1],
                           color=colors[1], legend='Heterozygous')
        seasonal_plot.line(x='index', y='genotype_susceptible',
                           source=decomp_median_source[frequency][1],
                           color=colors[2], legend='Susceptible')
        line_plots.append(seasonal_plot)

        resid_plot = plt.figure(plot_width=plot_width, plot_height=plot_height,
                                x_range=base_plot.x_range)
        resid_plot.title.text = '{} Residual Median Data, ' \
                                'Seasonal Frequency: {}'. \
            format(life_stage_title, frequency)
        resid_plot.yaxis.axis_label = 'Population'
        resid_plot.xaxis.axis_label = 'time (days)'
        resid_plot.line(x='index', y='genotype_resistant',
                        source=decomp_median_source[frequency][2],
                        color=colors[0], legend='Resistant')
        resid_plot.line(x='index', y='genotype_heterozygous',
                        source=decomp_median_source[frequency][2],
                        color=colors[1], legend='Heterozygous')
        resid_plot.line(x='index', y='genotype_susceptible',
                        source=decomp_median_source[frequency][2],
                        color=colors[2], legend='Susceptible')
        line_plots.append(resid_plot)

        grid_lines.append(line_plots)

    return lay.gridplot(grid_lines,
                        toolbar_location='left')


larva_seasonal_data_title = mdl.Div(text='<h1>Larva Seasonal Decomposition '
                                         'Timeseries Data, {} runs</h1>'.
                                    format(number_of_runs))
larva_seasonal_plot = seasonal_data_plotter(larva_mean_source,
                                            larva_mean_seasonal_sources,
                                            larva_median_source,
                                            larva_median_seasonal_sources,
                                            'Larva')

plt.show(lay.column(larva_periodogram_title,
                    larva_periodogram_plot,
                    larva_seasonal_data_title,
                    larva_seasonal_plot))
