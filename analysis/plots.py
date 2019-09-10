import os

import bokeh.plotting     as plt
import bokeh.layouts      as lay
import bokeh.models       as mdl
import bokeh.palettes     as palettes

import statsmodels.tsa.seasonal as seasonal

import dataclasses   as dclass
import pandas        as pd
import sqlalchemy    as sql


import source.hint as hint


source_name = 'long_sim_25_gen_no_im_bt_10_no_hetero.sqlite'
source_path = '/home/william/Dropbox/Research/Parallel_FallArmyworm/' \
              'simulations/'
tables      = ['(0,)_egg',
               '(0,)_larva',
               '(0,)_pupa',
               '(0,)_female']

save_file = 'timeseries_decomp.html'

frequency = 45

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

main_title = mdl.Div(text='<h1>Time Series Decomposition, '
                          'Generation Time {} Days</h1>'.format(frequency))
plt.show(lay.column(main_title,
                    series_plot))
