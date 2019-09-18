import os

import bokeh.plotting     as plt
import bokeh.layouts      as lay
import bokeh.models       as mdl
import bokeh.palettes     as palettes
import bokeh.models.tools as tools

import scipy.signal             as signal
import statsmodels.tsa.seasonal as seasonal

import dataclasses   as dclass
import numpy         as np
import pandas        as pd
import sqlalchemy    as sql

import source.hint as hint


source_name = 'long_sim_25_gen_no_im_bt_10_no_hetero.sqlite'
# source_name = 'parallel_sim_25_gen_no_bt_only_sus_0.sqlite'
source_path = '/home/william/Dropbox/Research/Parallel_FallArmyworm/' \
              'simulations/'
tables      = ['(0,)_egg',
               '(0,)_larva',
               '(0,)_pupa',
               '(0,)_female']

save_file = 'timeseries_decomp.html'

frequency       = 28
sample_interval = 50
sample_length   = 10

plt.output_file(save_file)


@dclass.dataclass
class ReadData(object):
    """
    Class to read data
    """

    base_name:   str
    base_path:   str
    table_names: list
    file_names:  list = dclass.field(default=list)

    def __post_init__(self):
        """Get the file names"""

        self.file_names = self.get_file_names()

    def get_file_names(self) -> list:
        """
        Get list of files ending with base name

        Returns:
            list of file names
        """

        files = os.listdir(self.base_path)
        files = [f for f in files if f.endswith(self.base_name)]

        file_dict = {}
        for f in files:
            f_num = f.split('_')[0]
            if f_num in file_dict:
                raise RuntimeError('bad number found')
            else:
                file_dict[int(f_num)] = f

        file_nums = list(file_dict.keys())
        file_nums.sort()

        files = []
        for f_num in file_nums:
            files.append(file_dict[f_num])

        return files

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

    def dataframe(self, table_name: str) -> hint.dataframe:
        """
        Merge data into single dataframe

        Args:
            table_name: name of the sql table

        Returns:
            table merge across the files
        """

        dataframe0 = self.read(table_name, self.file_names[0])
        dataframes = [dataframe0]

        for file_name in self.file_names[1:]:
            dataframe1 = self.read(table_name, file_name)
            dataframe1 = dataframe1.iloc[1:]

            dataframes.append(dataframe1)

        dataframe = pd.concat(dataframes)
        dataframe.reset_index(inplace=True, drop=True)
        dataframe['index'] = range(len(dataframe.index))

        return dataframe

    def dataframes(self) -> hint.dataframes:
        """
        Get all of the dataframes that we wish to use

        Returns:
            dictionary of all the dataframes we want
        """

        dataframes = {}

        for table_name in self.table_names:
            dataframes[table_name] = self.dataframe(table_name)

        return dataframes

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

    def cut_dataframes(self, start: int) -> hint.dataframes:
        """
        Cut the read dataframes to the correct start point

        Args:
            start: the correct start point

        Returns:
            the dataframes to the right start point
        """

        dataframes = self.dataframes()

        new = {}
        for table_name, dataframe in dataframes.items():
            new[table_name] = self.cut_dataframe(dataframe, start)

        return new


reader = ReadData(source_name, source_path, tables)
data   = reader.cut_dataframes(200)

egg    = data[tables[0]]
larva  = data[tables[1]]
pupa   = data[tables[2]]
female = data[tables[3]]

egg_source    = mdl.ColumnDataSource(egg)
larva_source  = mdl.ColumnDataSource(larva)
pupa_source   = mdl.ColumnDataSource(pupa)
female_source = mdl.ColumnDataSource(female)

egg_resistant_freq, egg_resistant_power = \
    signal.periodogram(egg['genotype_resistant'])
egg_resistant_period = (1 / egg_resistant_freq[1:]).tolist()
egg_resistant_period.insert(0, np.inf)
egg_resistant_spec = \
    pd.DataFrame.from_dict({'frequency': egg_resistant_freq,
                            'power':     egg_resistant_power,
                            'period':    np.array(egg_resistant_period)})
egg_resistant_spec['genotype'] = 'Resistant'
egg_heterozygous_freq, egg_heterozygous_power = \
    signal.periodogram(egg['genotype_heterozygous'])
egg_heterozygous_period = (1 / egg_heterozygous_freq[1:]).tolist()
egg_heterozygous_period.insert(0, np.inf)
egg_heterozygous_spec = \
    pd.DataFrame.from_dict({'frequency': egg_heterozygous_freq,
                            'power':     egg_heterozygous_power,
                            'period':    np.array(egg_heterozygous_period)})
egg_heterozygous_spec['genotype'] = 'Heterozygous'
egg_susceptible_freq, egg_susceptible_power = \
    signal.periodogram(egg['genotype_susceptible'])
egg_susceptible_period = (1 / egg_susceptible_freq[1:]).tolist()
egg_susceptible_period.insert(0, np.inf)
egg_susceptible_spec = \
    pd.DataFrame.from_dict({'frequency': egg_susceptible_freq,
                            'power':     egg_susceptible_power,
                            'period':    np.array(egg_susceptible_period)})
egg_susceptible_spec['genotype'] = 'Susceptible'
egg_resistant_periodogram    = mdl.ColumnDataSource(egg_resistant_spec)
egg_heterozygous_periodogram = mdl.ColumnDataSource(egg_heterozygous_spec)
egg_susceptible_periodogram  = mdl.ColumnDataSource(egg_susceptible_spec)

larva_resistant_freq, larva_resistant_power = \
    signal.periodogram(larva['genotype_resistant'])
larva_resistant_period = (1 / larva_resistant_freq[1:]).tolist()
larva_resistant_period.insert(0, np.inf)
larva_resistant_spec = \
    pd.DataFrame.from_dict({'frequency': larva_resistant_freq,
                            'power':     larva_resistant_power,
                            'period':    np.array(larva_resistant_period)})
larva_resistant_spec['genotype'] = 'Resistant'
larva_heterozygous_freq, larva_heterozygous_power = \
    signal.periodogram(larva['genotype_heterozygous'])
larva_heterozygous_period = (1 / larva_heterozygous_freq[1:]).tolist()
larva_heterozygous_period.insert(0, np.inf)
larva_heterozygous_spec = \
    pd.DataFrame.from_dict({'frequency': larva_heterozygous_freq,
                            'power':     larva_heterozygous_power,
                            'period':    np.array(larva_heterozygous_period)})
larva_heterozygous_spec['genotype'] = 'Heterozygous'
larva_susceptible_freq, larva_susceptible_power = \
    signal.periodogram(larva['genotype_susceptible'])
larva_susceptible_period = (1 / larva_susceptible_freq[1:]).tolist()
larva_susceptible_period.insert(0, np.inf)
larva_susceptible_spec = \
    pd.DataFrame.from_dict({'frequency': larva_susceptible_freq,
                            'power':     larva_susceptible_power,
                            'period':    np.array(larva_susceptible_period)})
larva_susceptible_spec['genotype'] = 'Susceptible'
larva_resistant_periodogram    = mdl.ColumnDataSource(larva_resistant_spec)
larva_heterozygous_periodogram = mdl.ColumnDataSource(larva_heterozygous_spec)
larva_susceptible_periodogram  = mdl.ColumnDataSource(larva_susceptible_spec)

pupa_resistant_freq, pupa_resistant_power = \
    signal.periodogram(pupa['genotype_resistant'])
pupa_resistant_period = (1 / pupa_resistant_freq[1:]).tolist()
pupa_resistant_period.insert(0, np.inf)
pupa_resistant_spec = \
    pd.DataFrame.from_dict({'frequency': pupa_resistant_freq,
                            'power':     pupa_resistant_power,
                            'period':    np.array(pupa_resistant_period)})
pupa_resistant_spec['genotype'] = 'Resistant'
pupa_heterozygous_freq, pupa_heterozygous_power = \
    signal.periodogram(pupa['genotype_heterozygous'])
pupa_heterozygous_period = (1 / pupa_heterozygous_freq[1:]).tolist()
pupa_heterozygous_period.insert(0, np.inf)
pupa_heterozygous_spec = \
    pd.DataFrame.from_dict({'frequency': pupa_heterozygous_freq,
                            'power':     pupa_heterozygous_power,
                            'period':    np.array(pupa_heterozygous_period)})
pupa_heterozygous_spec['genotype'] = 'Heterozygous'
pupa_susceptible_freq, pupa_susceptible_power = \
    signal.periodogram(pupa['genotype_susceptible'])
pupa_susceptible_period = (1 / pupa_susceptible_freq[1:]).tolist()
pupa_susceptible_period.insert(0, np.inf)
pupa_susceptible_spec = \
    pd.DataFrame.from_dict({'frequency': pupa_susceptible_freq,
                            'power':     pupa_susceptible_power,
                            'period':    np.array(pupa_susceptible_period)})
pupa_susceptible_spec['genotype'] = 'Susceptible'
pupa_resistant_periodogram    = mdl.ColumnDataSource(pupa_resistant_spec)
pupa_heterozygous_periodogram = mdl.ColumnDataSource(pupa_heterozygous_spec)
pupa_susceptible_periodogram  = mdl.ColumnDataSource(pupa_susceptible_spec)

female_resistant_freq, female_resistant_power = \
    signal.periodogram(female['genotype_resistant'])
female_resistant_period = (1 / female_resistant_freq[1:]).tolist()
female_resistant_period.insert(0, np.inf)
female_resistant_spec = \
    pd.DataFrame.from_dict({'frequency': female_resistant_freq,
                            'power':     female_resistant_power,
                            'period':    np.array(female_resistant_period)})
female_resistant_spec['genotype'] = 'Resistant'
female_heterozygous_freq, female_heterozygous_power = \
    signal.periodogram(female['genotype_heterozygous'])
female_heterozygous_period = (1 / female_heterozygous_freq[1:]).tolist()
female_heterozygous_period.insert(0, np.inf)
female_heterozygous_spec = \
    pd.DataFrame.from_dict({'frequency': female_heterozygous_freq,
                            'power':     female_heterozygous_power,
                            'period':    np.array(female_heterozygous_period)})
female_heterozygous_spec['genotype'] = 'Heterozygous'
female_susceptible_freq, female_susceptible_power = \
    signal.periodogram(female['genotype_susceptible'])
female_susceptible_period = (1 / female_susceptible_freq[1:]).tolist()
female_susceptible_period.insert(0, np.inf)
female_susceptible_spec = \
    pd.DataFrame.from_dict({'frequency': female_susceptible_freq,
                            'power':     female_susceptible_power,
                            'period':    np.array(female_susceptible_period)})
female_susceptible_spec['genotype'] = 'Susceptible'
female_resistant_periodogram    = mdl.ColumnDataSource(female_resistant_spec)
female_heterozygous_periodogram = mdl.ColumnDataSource(female_heterozygous_spec)
female_susceptible_periodogram  = mdl.ColumnDataSource(female_susceptible_spec)

egg_decomp    = seasonal.seasonal_decompose(egg,
                                            model='additive', freq=frequency)
egg_decomp.trend[   'index'] = range(len(egg_decomp.trend))
egg_decomp.seasonal['index'] = range(len(egg_decomp.seasonal))
egg_decomp.resid[   'index'] = range(len(egg_decomp.resid))
larva_decomp  = seasonal.seasonal_decompose(larva,
                                            model='additive', freq=frequency)
larva_decomp.trend[   'index'] = range(len(larva_decomp.trend))
larva_decomp.seasonal['index'] = range(len(larva_decomp.seasonal))
larva_decomp.resid[   'index'] = range(len(larva_decomp.resid))
pupa_decomp   = seasonal.seasonal_decompose(pupa,
                                            model='additive', freq=frequency)
pupa_decomp.trend[   'index'] = range(len(pupa_decomp.trend))
pupa_decomp.seasonal['index'] = range(len(pupa_decomp.seasonal))
pupa_decomp.resid[   'index'] = range(len(pupa_decomp.resid))
female_decomp = seasonal.seasonal_decompose(female,
                                            model='additive', freq=frequency)
female_decomp.trend[   'index'] = range(len(female_decomp.trend))
female_decomp.seasonal['index'] = range(len(female_decomp.seasonal))
female_decomp.resid[   'index'] = range(len(female_decomp.resid))


egg_trend_source    = mdl.ColumnDataSource(egg_decomp.trend)
larva_trend_source  = mdl.ColumnDataSource(larva_decomp.trend)
pupa_trend_source   = mdl.ColumnDataSource(pupa_decomp.trend)
female_trend_source = mdl.ColumnDataSource(female_decomp.trend)

egg_seasonal_source    = mdl.ColumnDataSource(egg_decomp.seasonal)
larva_seasonal_source  = mdl.ColumnDataSource(larva_decomp.seasonal)
pupa_seasonal_source   = mdl.ColumnDataSource(pupa_decomp.seasonal)
female_seasonal_source = mdl.ColumnDataSource(female_decomp.seasonal)

egg_resid_source    = mdl.ColumnDataSource(egg_decomp.resid)
larva_resid_source  = mdl.ColumnDataSource(larva_decomp.resid)
pupa_resid_source   = mdl.ColumnDataSource(pupa_decomp.resid)
female_resid_source = mdl.ColumnDataSource(female_decomp.resid)

egg_sample    = egg.   iloc[::sample_interval, :].copy()
larva_sample  = larva. iloc[::sample_interval, :].copy()
pupa_sample   = pupa.  iloc[::sample_interval, :].copy()
female_sample = female.iloc[::sample_interval, :].copy()

egg_sample[   'index'] = range(len(egg_sample))
larva_sample[ 'index'] = range(len(larva_sample))
pupa_sample[  'index'] = range(len(pupa_sample))
female_sample['index'] = range(len(female_sample))

egg_samples    = pd.DataFrame()
larva_samples  = pd.DataFrame()
pupa_samples   = pd.DataFrame()
female_samples = pd.DataFrame()

egg_samples[   'index'] = egg_sample[   'index']
larva_samples[ 'index'] = larva_sample[ 'index']
pupa_samples[  'index'] = pupa_sample[  'index']
female_samples['index'] = female_sample['index']

egg_samples.   reset_index(inplace=True, drop=True)
larva_samples. reset_index(inplace=True, drop=True)
pupa_samples.  reset_index(inplace=True, drop=True)
female_samples.reset_index(inplace=True, drop=True)

column_titles = ['genotype_resistant',
                 'genotype_heterozygous',
                 'genotype_susceptible']
for index in range(sample_length + 1):
    egg_data    = egg.   iloc[index::sample_interval, :].copy()
    larva_data  = larva. iloc[index::sample_interval, :].copy()
    pupa_data   = pupa.  iloc[index::sample_interval, :].copy()
    female_data = female.iloc[index::sample_interval, :].copy()

    egg_data.reset_index(inplace=True, drop=True)
    larva_data.reset_index(inplace=True, drop=True)
    pupa_data.reset_index(inplace=True, drop=True)
    female_data.reset_index(inplace=True, drop=True)


    for genotype_title in column_titles:
        column_title = '{}_{}'.format(genotype_title, index)

        egg_samples[   column_title] = egg_data[   genotype_title]
        larva_samples[ column_title] = larva_data[ genotype_title]
        pupa_samples[  column_title] = pupa_data[  genotype_title]
        female_samples[column_title] = female_data[genotype_title]


def data_mean(row, geno_title):
    data_list = []

    for s_index in range(sample_length + 1):
        col_title = '{}_{}'.format(geno_title, index)
        data_list.append(row[col_title])

    return np.mean(data_list)


def data_median(row, geno_title):
    data_list = []

    for s_index in range(sample_length + 1):
        col_title = '{}_{}'.format(geno_title, index)
        data_list.append(row[col_title])

    return np.median(data_list)


def data_min(row, geno_title):
    data_list = []

    for s_index in range(sample_length + 1):
        col_title = '{}_{}'.format(geno_title, index)
        data_list.append(row[col_title])

    return np.min(data_list)


def data_max(row, geno_title):
    data_list = []

    for s_index in range(sample_length + 1):
        col_title = '{}_{}'.format(geno_title, index)
        data_list.append(row[col_title])

    return np.max(data_list)


for genotype_title in column_titles:
    column_title = '{}_{}'.format(genotype_title, 'mean')
    egg_samples[column_title] =\
        egg_samples.apply(lambda row: data_mean(row, genotype_title), axis=1)
    larva_samples[column_title] = \
        larva_samples.apply(lambda row: data_mean(row, genotype_title), axis=1)
    pupa_samples[column_title] = \
        pupa_samples.apply(lambda row: data_mean(row, genotype_title), axis=1)
    female_samples[column_title] = \
        female_samples.apply(lambda row: data_mean(row, genotype_title), axis=1)

    column_title = '{}_{}'.format(genotype_title, 'median')
    egg_samples[column_title] = \
        egg_samples.apply(lambda row: data_median(row, genotype_title),
                          axis=1)
    larva_samples[column_title] = \
        larva_samples.apply(lambda row: data_median(row, genotype_title),
                            axis=1)
    pupa_samples[column_title] = \
        pupa_samples.apply(lambda row: data_median(row, genotype_title),
                           axis=1)
    female_samples[column_title] = \
        female_samples.apply(lambda row: data_median(row, genotype_title),
                             axis=1)

    column_title = '{}_{}'.format(genotype_title, 'min')
    egg_samples[column_title] = \
        egg_samples.apply(lambda row: data_min(row, genotype_title),
                          axis=1)
    larva_samples[column_title] = \
        larva_samples.apply(lambda row: data_min(row, genotype_title),
                            axis=1)
    pupa_samples[column_title] = \
        pupa_samples.apply(lambda row: data_min(row, genotype_title),
                           axis=1)
    female_samples[column_title] = \
        female_samples.apply(lambda row: data_min(row, genotype_title),
                             axis=1)

    column_title = '{}_{}'.format(genotype_title, 'max')
    egg_samples[column_title] = \
        egg_samples.apply(lambda row: data_max(row, genotype_title),
                          axis=1)
    larva_samples[column_title] = \
        larva_samples.apply(lambda row: data_max(row, genotype_title),
                            axis=1)
    pupa_samples[column_title] = \
        pupa_samples.apply(lambda row: data_max(row, genotype_title),
                           axis=1)
    female_samples[column_title] = \
        female_samples.apply(lambda row: data_max(row, genotype_title),
                             axis=1)

egg_sample_source    = mdl.ColumnDataSource(egg_sample)
larva_sample_source  = mdl.ColumnDataSource(larva_sample)
pupa_sample_source   = mdl.ColumnDataSource(pupa_sample)
female_sample_source = mdl.ColumnDataSource(female_sample)

egg_samples_source    = mdl.ColumnDataSource(egg_samples)
larva_samples_source  = mdl.ColumnDataSource(larva_samples)
pupa_samples_source   = mdl.ColumnDataSource(pupa_samples)
female_samples_source = mdl.ColumnDataSource(female_samples)

colors = palettes.Set1[3]

egg_plot = plt.figure(plot_width=1500, plot_height=400)
egg_plot.title.text = 'Egg Time Series data'
egg_plot.yaxis.axis_label = 'Population'
egg_plot.xaxis.axis_label = 'time (days)'
egg_plot.line(x='index', y='genotype_resistant',
              source=egg_source,
              color=colors[0], legend='Resistant')
egg_plot.line(x='index', y='genotype_heterozygous',
              source=egg_source,
              color=colors[1], legend='Heterozygous')
egg_plot.line(x='index', y='genotype_susceptible',
              source=egg_source,
              color=colors[2], legend='Susceptible')

larva_plot = plt.figure(plot_width=1500, plot_height=400,
                        x_range=egg_plot.x_range)
larva_plot.title.text = 'Larva Time Series data'
larva_plot.yaxis.axis_label = 'Population'
larva_plot.xaxis.axis_label = 'time (days)'
larva_plot.line(x='index', y='genotype_resistant',
                source=larva_source,
                color=colors[0], legend='Resistant')
larva_plot.line(x='index', y='genotype_heterozygous',
                source=larva_source,
                color=colors[1], legend='Heterozygous')
larva_plot.line(x='index', y='genotype_susceptible',
                source=larva_source,
                color=colors[2], legend='Susceptible')

pupa_plot = plt.figure(plot_width=1500, plot_height=400,
                        x_range=egg_plot.x_range)
pupa_plot.title.text = 'Pupa Time Series data'
pupa_plot.yaxis.axis_label = 'Population'
pupa_plot.xaxis.axis_label = 'time (days)'
pupa_plot.line(x='index', y='genotype_resistant',
               source=pupa_source,
                color=colors[0], legend='Resistant')
pupa_plot.line(x='index', y='genotype_heterozygous',
               source=pupa_source,
                color=colors[1], legend='Heterozygous')
pupa_plot.line(x='index', y='genotype_susceptible',
               source=pupa_source,
                color=colors[2], legend='Susceptible')

female_plot = plt.figure(plot_width=1500, plot_height=400,
                         x_range=egg_plot.x_range)
female_plot.title.text = 'Female Time Series data'
female_plot.yaxis.axis_label = 'Population'
female_plot.xaxis.axis_label = 'time (days)'
female_plot.line(x='index', y='genotype_resistant',
                 source=female_source,
                 color=colors[0], legend='Resistant')
female_plot.line(x='index', y='genotype_heterozygous',
                 source=female_source,
                 color=colors[1], legend='Heterozygous')
female_plot.line(x='index', y='genotype_susceptible',
                 source=female_source,
                 color=colors[2], legend='Susceptible')

egg_trend = plt.figure(plot_width=1500, plot_height=400,
                       x_range=egg_plot.x_range)
egg_trend.title.text = 'Egg Trend Data'
egg_trend.yaxis.axis_label = 'Trend'
egg_trend.xaxis.axis_label = 'time (days)'
egg_trend.line(x='index', y='genotype_resistant',
               source=egg_trend_source,
               color=colors[0], legend='Resistant')
egg_trend.line(x='index', y='genotype_heterozygous',
               source=egg_trend_source,
               color=colors[1], legend='Heterozygous')
egg_trend.line(x='index', y='genotype_susceptible',
               source=egg_trend_source,
               color=colors[2], legend='Susceptible')

larva_trend = plt.figure(plot_width=1500, plot_height=400,
                         x_range=egg_plot.x_range)
larva_trend.title.text = 'Larva Trend Data'
larva_trend.yaxis.axis_label = 'Trend'
larva_trend.xaxis.axis_label = 'time (days)'
larva_trend.line(x='index', y='genotype_resistant',
                 source=larva_trend_source,
                 color=colors[0], legend='Resistant')
larva_trend.line(x='index', y='genotype_heterozygous',
                 source=larva_trend_source,
                 color=colors[1], legend='Heterozygous')
larva_trend.line(x='index', y='genotype_susceptible',
                 source=larva_trend_source,
                 color=colors[2], legend='Susceptible')

pupa_trend = plt.figure(plot_width=1500, plot_height=400,
                        x_range=egg_plot.x_range)
pupa_trend.title.text = 'Pupa Trend Data'
pupa_trend.yaxis.axis_label = 'Trend'
pupa_trend.xaxis.axis_label = 'time (days)'
pupa_trend.line(x='index', y='genotype_resistant',
                source=pupa_trend_source,
                color=colors[0], legend='Resistant')
pupa_trend.line(x='index', y='genotype_heterozygous',
                source=pupa_trend_source,
                color=colors[1], legend='Heterozygous')
pupa_trend.line(x='index', y='genotype_susceptible',
                source=pupa_trend_source,
                color=colors[2], legend='Susceptible')

female_trend = plt.figure(plot_width=1500, plot_height=400,
                          x_range=egg_plot.x_range)
female_trend.title.text = 'Female Trend Data'
female_trend.yaxis.axis_label = 'Trend'
female_trend.xaxis.axis_label = 'time (days)'
female_trend.line(x='index', y='genotype_resistant',
                  source=female_trend_source,
                  color=colors[0], legend='Resistant')
female_trend.line(x='index', y='genotype_heterozygous',
                  source=female_trend_source,
                  color=colors[1], legend='Heterozygous')
female_trend.line(x='index', y='genotype_susceptible',
                  source=female_trend_source,
                  color=colors[2], legend='Susceptible')

egg_seasonal = plt.figure(plot_width=1500, plot_height=400,
                          x_range=egg_plot.x_range)
egg_seasonal.title.text = 'Egg Seasonal Data'
egg_seasonal.yaxis.axis_label = 'Seasonal'
egg_seasonal.xaxis.axis_label = 'time (days)'
egg_seasonal.line(x='index', y='genotype_resistant',
                  source=egg_seasonal_source,
                  color=colors[0], legend='Resistant')
egg_seasonal.line(x='index', y='genotype_heterozygous',
                  source=egg_seasonal_source,
                  color=colors[1], legend='Heterozygous')
egg_seasonal.line(x='index', y='genotype_susceptible',
                  source=egg_seasonal_source,
                  color=colors[2], legend='Susceptible')

larva_seasonal = plt.figure(plot_width=1500, plot_height=400,
                            x_range=egg_plot.x_range)
larva_seasonal.title.text = 'Larva Seasonal Data'
larva_seasonal.yaxis.axis_label = 'Seasonal'
larva_seasonal.xaxis.axis_label = 'time (days)'
larva_seasonal.line(x='index', y='genotype_resistant',
                    source=larva_seasonal_source,
                    color=colors[0], legend='Resistant')
larva_seasonal.line(x='index', y='genotype_heterozygous',
                    source=larva_seasonal_source,
                    color=colors[1], legend='Heterozygous')
larva_seasonal.line(x='index', y='genotype_susceptible',
                    source=larva_seasonal_source,
                    color=colors[2], legend='Susceptible')

pupa_seasonal = plt.figure(plot_width=1500, plot_height=400,
                           x_range=egg_plot.x_range)
pupa_seasonal.title.text = 'Pupa Seasonal Data'
pupa_seasonal.yaxis.axis_label = 'Seasonal'
pupa_seasonal.xaxis.axis_label = 'time (days)'
pupa_seasonal.line(x='index', y='genotype_resistant',
                   source=pupa_seasonal_source,
                   color=colors[0], legend='Resistant')
pupa_seasonal.line(x='index', y='genotype_heterozygous',
                   source=pupa_seasonal_source,
                   color=colors[1], legend='Heterozygous')
pupa_seasonal.line(x='index', y='genotype_susceptible',
                   source=pupa_seasonal_source,
                   color=colors[2], legend='Susceptible')

female_seasonal = plt.figure(plot_width=1500, plot_height=400,
                             x_range=egg_plot.x_range)
female_seasonal.title.text = 'Female Seasonal Data'
female_seasonal.yaxis.axis_label = 'Seasonal'
female_seasonal.xaxis.axis_label = 'time (days)'
female_seasonal.line(x='index', y='genotype_resistant',
                     source=female_seasonal_source,
                     color=colors[0], legend='Resistant')
female_seasonal.line(x='index', y='genotype_heterozygous',
                     source=female_seasonal_source,
                     color=colors[1], legend='Heterozygous')
female_seasonal.line(x='index', y='genotype_susceptible',
                     source=female_seasonal_source,
                     color=colors[2], legend='Susceptible')

egg_resid = plt.figure(plot_width=1500, plot_height=400,
                       x_range=egg_plot.x_range)
egg_resid.title.text = 'Egg Residual Data'
egg_resid.yaxis.axis_label = 'Trend'
egg_resid.xaxis.axis_label = 'time (days)'
egg_resid.line(x='index', y='genotype_resistant',
               source=egg_resid_source,
               color=colors[0], legend='Resistant')
egg_resid.line(x='index', y='genotype_heterozygous',
               source=egg_resid_source,
               color=colors[1], legend='Heterozygous')
egg_resid.line(x='index', y='genotype_susceptible',
               source=egg_resid_source,
               color=colors[2], legend='Susceptible')

larva_resid = plt.figure(plot_width=1500, plot_height=400,
                         x_range=egg_plot.x_range)
larva_resid.title.text = 'Larva Residual Data'
larva_resid.yaxis.axis_label = 'Trend'
larva_resid.xaxis.axis_label = 'time (days)'
larva_resid.line(x='index', y='genotype_resistant',
                 source=larva_resid_source,
                 color=colors[0], legend='Resistant')
larva_resid.line(x='index', y='genotype_heterozygous',
                 source=larva_resid_source,
                 color=colors[1], legend='Heterozygous')
larva_resid.line(x='index', y='genotype_susceptible',
                 source=larva_resid_source,
                 color=colors[2], legend='Susceptible')

pupa_resid = plt.figure(plot_width=1500, plot_height=400,
                        x_range=egg_plot.x_range)
pupa_resid.title.text = 'Pupa Residual Data'
pupa_resid.yaxis.axis_label = 'Trend'
pupa_resid.xaxis.axis_label = 'time (days)'
pupa_resid.line(x='index', y='genotype_resistant',
                source=pupa_resid_source,
                color=colors[0], legend='Resistant')
pupa_resid.line(x='index', y='genotype_heterozygous',
                source=pupa_resid_source,
                color=colors[1], legend='Heterozygous')
pupa_resid.line(x='index', y='genotype_susceptible',
                source=pupa_resid_source,
                color=colors[2], legend='Susceptible')

female_resid = plt.figure(plot_width=1500, plot_height=400,
                          x_range=egg_plot.x_range)
female_resid.title.text = 'Female Residual Data'
female_resid.yaxis.axis_label = 'Trend'
female_resid.xaxis.axis_label = 'time (days)'
female_resid.line(x='index', y='genotype_resistant',
                  source=female_resid_source,
                  color=colors[0], legend='Resistant')
female_resid.line(x='index', y='genotype_heterozygous',
                  source=female_resid_source,
                  color=colors[1], legend='Heterozygous')
female_resid.line(x='index', y='genotype_susceptible',
                  source=female_resid_source,
                  color=colors[2], legend='Susceptible')

series_plot = lay.gridplot([[egg_plot,    egg_trend,    egg_seasonal,
                             egg_resid],
                            [larva_plot,  larva_trend,  larva_seasonal,
                             larva_resid],
                            [pupa_plot,   pupa_trend,   pupa_seasonal,
                             pupa_resid],
                            [female_plot, female_trend, female_seasonal,
                             female_resid]],
                           toolbar_location='left')

egg_periodogram = plt.figure()
egg_periodogram.title.text = 'Egg Periodogram'
egg_periodogram.yaxis.axis_label = 'Power Spectral Density'
egg_periodogram.xaxis.axis_label = 'Frequency'
egg_periodogram.line(x='frequency', y='power',
                     source=egg_resistant_periodogram,
                     color=colors[0], legend='Resistant')
egg_periodogram.line(x='frequency', y='power',
                     source=egg_heterozygous_periodogram,
                     color=colors[1], legend='Heterozygous')
egg_periodogram.line(x='frequency', y='power',
                     source=egg_susceptible_periodogram,
                     color=colors[2], legend='Susceptible')
egg_hover = tools.HoverTool()
egg_hover.tooltips = [
    ('Frequency',        '@frequency'),
    ('Period',           '@period'),
    ('Spectral Density', '@power'),
    ('Genotype',         '@genotype')
]
egg_periodogram.add_tools(egg_hover)

larva_periodogram = plt.figure()
larva_periodogram.title.text = 'Larva Periodogram'
larva_periodogram.yaxis.axis_label = 'Power Spectral Density'
larva_periodogram.xaxis.axis_label = 'Frequency'
larva_periodogram.line(x='frequency', y='power',
                       source=larva_resistant_periodogram,
                       color=colors[0], legend='Resistant')
larva_periodogram.line(x='frequency', y='power',
                       source=larva_heterozygous_periodogram,
                       color=colors[1], legend='Heterozygous')
larva_periodogram.line(x='frequency', y='power',
                       source=larva_susceptible_periodogram,
                       color=colors[2], legend='Susceptible')
larva_hover = tools.HoverTool()
larva_hover.tooltips = [
    ('Frequency',        '@frequency'),
    ('Period',           '@period'),
    ('Spectral Density', '@power'),
    ('Genotype',         '@genotype')
]
larva_periodogram.add_tools(larva_hover)

pupa_periodogram = plt.figure()
pupa_periodogram.title.text = 'Pupa Periodogram'
pupa_periodogram.yaxis.axis_label = 'Power Spectral Density'
pupa_periodogram.xaxis.axis_label = 'Frequency'
pupa_periodogram.line(x='frequency', y='power',
                      source=pupa_resistant_periodogram,
                      color=colors[0], legend='Resistant')
pupa_periodogram.line(x='frequency', y='power',
                      source=pupa_heterozygous_periodogram,
                      color=colors[1], legend='Heterozygous')
pupa_periodogram.line(x='frequency', y='power',
                      source=pupa_susceptible_periodogram,
                      color=colors[2], legend='Susceptible')
pupa_hover = tools.HoverTool()
pupa_hover.tooltips = [
    ('Frequency',        '@frequency'),
    ('Period',           '@period'),
    ('Spectral Density', '@power'),
    ('Genotype',         '@genotype')
]
pupa_periodogram.add_tools(pupa_hover)

female_periodogram = plt.figure()
female_periodogram.title.text = 'Female Periodogram'
female_periodogram.yaxis.axis_label = 'Power Spectral Density'
female_periodogram.xaxis.axis_label = 'Frequency'
female_periodogram.line(x='frequency', y='power',
                        source=female_resistant_periodogram,
                        color=colors[0], legend='Resistant')
female_periodogram.line(x='frequency', y='power',
                        source=female_heterozygous_periodogram,
                        color=colors[1], legend='Heterozygous')
female_periodogram.line(x='frequency', y='power',
                        source=female_susceptible_periodogram,
                        color=colors[2], legend='Susceptible')
female_hover = tools.HoverTool()
female_hover.tooltips = [
    ('Frequency',        '@frequency'),
    ('Period',           '@period'),
    ('Frequency',        '@frequency'),
    ('Spectral Density', '@power'),
    ('Genotype',         '@genotype')
]
female_periodogram.add_tools(female_hover)

egg_log_periodogram = plt.figure(y_axis_type='log')
egg_log_periodogram.title.text = 'Egg Log-Scale Periodogram'
egg_log_periodogram.yaxis.axis_label = 'Power Spectral Density'
egg_log_periodogram.xaxis.axis_label = 'Frequency'
egg_log_periodogram.line(x='frequency', y='power',
                         source=egg_resistant_periodogram,
                         color=colors[0], legend='Resistant')
egg_log_periodogram.line(x='frequency', y='power',
                         source=egg_heterozygous_periodogram,
                         color=colors[1], legend='Heterozygous')
egg_log_periodogram.line(x='frequency', y='power',
                         source=egg_susceptible_periodogram,
                         color=colors[2], legend='Susceptible')
egg_log_hover = tools.HoverTool()
egg_log_hover.tooltips = [
    ('Frequency',        '@frequency'),
    ('Period',           '@period'),
    ('Spectral Density', '@power'),
    ('Genotype',         '@genotype')
]
egg_log_periodogram.add_tools(egg_log_hover)

larva_log_periodogram = plt.figure(y_axis_type='log')
larva_log_periodogram.title.text = 'Larva Log-Scale Periodogram'
larva_log_periodogram.yaxis.axis_label = 'Power Spectral Density'
larva_log_periodogram.xaxis.axis_label = 'Frequency'
larva_log_periodogram.line(x='frequency', y='power',
                           source=larva_resistant_periodogram,
                           color=colors[0], legend='Resistant')
larva_log_periodogram.line(x='frequency', y='power',
                           source=larva_heterozygous_periodogram,
                           color=colors[1], legend='Heterozygous')
larva_log_periodogram.line(x='frequency', y='power',
                           source=larva_susceptible_periodogram,
                           color=colors[2], legend='Susceptible')
larva_log_hover = tools.HoverTool()
larva_log_hover.tooltips = [
    ('Frequency',        '@frequency'),
    ('Period',           '@period'),
    ('Spectral Density', '@power'),
    ('Genotype',         '@genotype')
]
larva_log_periodogram.add_tools(larva_log_hover)

pupa_log_periodogram = plt.figure(y_axis_type='log')
pupa_log_periodogram.title.text = 'Pupa Log-Scale Periodogram'
pupa_log_periodogram.yaxis.axis_label = 'Power Spectral Density'
pupa_log_periodogram.xaxis.axis_label = 'Frequency'
pupa_log_periodogram.line(x='frequency', y='power',
                          source=pupa_resistant_periodogram,
                          color=colors[0], legend='Resistant')
pupa_log_periodogram.line(x='frequency', y='power',
                          source=pupa_heterozygous_periodogram,
                          color=colors[1], legend='Heterozygous')
pupa_log_periodogram.line(x='frequency', y='power',
                          source=pupa_susceptible_periodogram,
                          color=colors[2], legend='Susceptible')
pupa_log_hover = tools.HoverTool()
pupa_log_hover.tooltips = [
    ('Frequency',        '@frequency'),
    ('Period',           '@period'),
    ('Spectral Density', '@power'),
    ('Genotype',         '@genotype')
]
pupa_log_periodogram.add_tools(pupa_log_hover)

female_log_periodogram = plt.figure(y_axis_type='log')
female_log_periodogram.title.text = 'Female Log-Scale Periodogram'
female_log_periodogram.yaxis.axis_label = 'Power Spectral Density'
female_log_periodogram.xaxis.axis_label = 'Frequency'
female_log_periodogram.line(x='frequency', y='power',
                            source=female_resistant_periodogram,
                            color=colors[0], legend='Resistant')
female_log_periodogram.line(x='frequency', y='power',
                            source=female_heterozygous_periodogram,
                            color=colors[1], legend='Heterozygous')
female_log_periodogram.line(x='frequency', y='power',
                            source=female_susceptible_periodogram,
                            color=colors[2], legend='Susceptible')
female_log_hover = tools.HoverTool()
female_log_hover.tooltips = [
    ('Frequency',        '@frequency'),
    ('Period',           '@period'),
    ('Spectral Density', '@power'),
    ('Genotype',         '@genotype')
]
female_log_periodogram.add_tools(female_log_hover)

periodograms = lay.gridplot([[egg_periodogram,
                              larva_periodogram,
                              pupa_periodogram,
                              female_periodogram],
                            [egg_log_periodogram,
                             larva_log_periodogram,
                             pupa_log_periodogram,
                             female_log_periodogram]])

egg_sample_plot = plt.figure(plot_width=1500, plot_height=400)
egg_sample_plot.title.text = 'Egg Sample data'
egg_sample_plot.yaxis.axis_label = 'Population'
egg_sample_plot.xaxis.axis_label = 'time (every {} days)'.\
    format(sample_interval)
egg_sample_plot.line(x='index', y='genotype_resistant',
                     source=egg_sample_source,
                     color=colors[0], legend='Resistant')
egg_sample_plot.line(x='index', y='genotype_heterozygous',
                     source=egg_sample_source,
                     color=colors[1], legend='Heterozygous')
egg_sample_plot.line(x='index', y='genotype_susceptible',
                     source=egg_sample_source,
                     color=colors[2], legend='Susceptible')

larva_sample_plot = plt.figure(plot_width=1500, plot_height=400,
                               x_range=egg_sample_plot.x_range)
larva_sample_plot.title.text = 'Larva Sample data'
larva_sample_plot.yaxis.axis_label = 'Population'
larva_sample_plot.xaxis.axis_label = 'time (every {} days)'. \
    format(sample_interval)
larva_sample_plot.line(x='index', y='genotype_resistant',
                       source=larva_sample_source,
                       color=colors[0], legend='Resistant')
larva_sample_plot.line(x='index', y='genotype_heterozygous',
                       source=larva_sample_source,
                       color=colors[1], legend='Heterozygous')
larva_sample_plot.line(x='index', y='genotype_susceptible',
                       source=larva_sample_source,
                       color=colors[2], legend='Susceptible')

pupa_sample_plot = plt.figure(plot_width=1500, plot_height=400,
                              x_range=egg_sample_plot.x_range)
pupa_sample_plot.title.text = 'Pupa Sample data'
pupa_sample_plot.yaxis.axis_label = 'Population'
pupa_sample_plot.xaxis.axis_label = 'time (every {} days)'. \
    format(sample_interval)
pupa_sample_plot.line(x='index', y='genotype_resistant',
                      source=pupa_sample_source,
                      color=colors[0], legend='Resistant')
pupa_sample_plot.line(x='index', y='genotype_heterozygous',
                      source=pupa_sample_source,
                      color=colors[1], legend='Heterozygous')
pupa_sample_plot.line(x='index', y='genotype_susceptible',
                      source=pupa_sample_source,
                      color=colors[2], legend='Susceptible')

female_sample_plot = plt.figure(plot_width=1500, plot_height=400,
                                x_range=egg_sample_plot.x_range)
female_sample_plot.title.text = 'Female Sample data'
female_sample_plot.yaxis.axis_label = 'Population'
female_sample_plot.xaxis.axis_label = 'time (every {} days)'. \
    format(sample_interval)
female_sample_plot.line(x='index', y='genotype_resistant',
                        source=female_sample_source,
                        color=colors[0], legend='Resistant')
female_sample_plot.line(x='index', y='genotype_heterozygous',
                        source=female_sample_source,
                        color=colors[1], legend='Heterozygous')
female_sample_plot.line(x='index', y='genotype_susceptible',
                        source=female_sample_source,
                        color=colors[2], legend='Susceptible')

sample_plot = lay.gridplot([[egg_sample_plot],
                            [larva_sample_plot],
                            [pupa_sample_plot],
                            [female_sample_plot]],
                           toolbar_location='left')

# egg_samples_plot_mean = plt.figure(plot_width=1500, plot_height=400)
# egg_samples_plot_mean.title.text = 'Egg Sample data'
# egg_samples_plot_mean.yaxis.axis_label = 'Population'
# egg_samples_plot_mean.xaxis.axis_label = 'time (every {} days)'. \
#     format(sample_interval)
# egg_samples_plot_mean.line(x='index', y='genotype_resistant',
#                      source=egg_samples_source,
#                      color=colors[0], legend='Resistant')
# egg_samples_plot_mean.line(x='index', y='genotype_heterozygous',
#                      source=egg_samples_source,
#                      color=colors[1], legend='Heterozygous')
# egg_samples_plot_mean.line(x='index', y='genotype_susceptible',
#                      source=egg_samples_source,
#                      color=colors[2], legend='Susceptible')
#
# larva_samples_plot_mean = plt.figure(plot_width=1500, plot_height=400,
#                                x_range=egg_samples_plot_mean.x_range)
# larva_samples_plot_mean.title.text = 'Larva Sample data'
# larva_samples_plot_mean.yaxis.axis_label = 'Population'
# larva_samples_plot_mean.xaxis.axis_label = 'time (every {} days)'. \
#     format(sample_interval)
# larva_samples_plot_mean.line(x='index', y='genotype_resistant',
#                        source=larva_samples_source,
#                        color=colors[0], legend='Resistant')
# larva_samples_plot_mean.line(x='index', y='genotype_heterozygous',
#                        source=larva_samples_source,
#                        color=colors[1], legend='Heterozygous')
# larva_samples_plot_mean.line(x='index', y='genotype_susceptible',
#                        source=larva_samples_source,
#                        color=colors[2], legend='Susceptible')
#
# pupa_samples_plot_mean = plt.figure(plot_width=1500, plot_height=400,
#                               x_range=egg_samples_plot_mean.x_range)
# pupa_samples_plot_mean.title.text = 'Pupa Sample data'
# pupa_samples_plot_mean.yaxis.axis_label = 'Population'
# pupa_samples_plot_mean.xaxis.axis_label = 'time (every {} days)'. \
#     format(sample_interval)
# pupa_samples_plot_mean.line(x='index', y='genotype_resistant',
#                       source=pupa_samples_source,
#                       color=colors[0], legend='Resistant')
# pupa_samples_plot_mean.line(x='index', y='genotype_heterozygous',
#                       source=pupa_samples_source,
#                       color=colors[1], legend='Heterozygous')
# pupa_samples_plot_mean.line(x='index', y='genotype_susceptible',
#                       source=pupa_samples_source,
#                       color=colors[2], legend='Susceptible')
#
# female_samples_plot_mean = plt.figure(plot_width=1500, plot_height=400,
#                                 x_range=egg_samples_plot_mean.x_range)
# female_samples_plot_mean.title.text = 'Female Sample data'
# female_samples_plot_mean.yaxis.axis_label = 'Population'
# female_samples_plot_mean.xaxis.axis_label = 'time (every {} days)'. \
#     format(sample_interval)
# female_samples_plot_mean.line(x='index', y='genotype_resistant_mean',
#                         source=female_samples_source,
#                         color=colors[0], legend='Resistant')
# female_samples_plot_mean.line(x='index', y='genotype_heterozygous_mean',
#                         source=female_samples_source,
#                         color=colors[1], legend='Heterozygous')
# female_samples_plot_mean.line(x='index', y='genotype_susceptible_mean',
#                         source=female_samples_source,
#                         color=colors[2], legend='Susceptible')
#
# samples_plot_mean = lay.gridplot([[egg_samples_plot_mean],
#                             [larva_samples_plot_mean],
#                             [pupa_samples_plot_mean],
#                             [female_samples_plot_mean]],
#                            toolbar_location='left')

timeseries_title = mdl.Div(text='<h1>Time Series Decomposition, '
                                'Generation Time {} Days</h1>'.
                           format(frequency))
periodogram_title = mdl.Div(text='<h1>Time Series Periodograms</h1>')
sample_title = mdl.Div(text='<h1>Time Series Sampling, '
                                'Sample Interval {} Days</h1>'.
                           format(sample_interval))

plt.show(lay.column(timeseries_title,
                    series_plot,
                    periodogram_title,
                    periodograms,
                    sample_title,
                    sample_plot))
