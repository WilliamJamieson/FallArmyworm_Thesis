import datetime
import pickle

import bokeh.plotting     as plt
import bokeh.layouts      as lay
import bokeh.models       as mdl
import bokeh.palettes     as palettes
import bokeh.models.tools as tools

import dataclasses   as dclass
import pandas        as pd

import numpy                    as np
import statsmodels.tsa.seasonal as seasonal

import source.hint as hint

import multi_gen.runs as runs

simulation_runs = runs.runs

plot_width  = 2000
plot_height = 500

colors    = palettes.Colorblind[8]
save_file = 'seasonal_plots.html'

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
class Seasonal(object):
    """
    Class to read data
    """
    base_name:  str
    frequency:  int
    dataframes: dict = dclass.field(default=dict)

    def __post_init__(self):
        """read the data frames"""

        data_file = '{}_summary.data'.format(self.base_name)

        with open(data_file, 'rb') as read_file:
            self.dataframes = pickle.load(read_file)

    def _make_seasonal(self, dataframe: hint.dataframe) -> dict:
        """
        Create a seasonal decomposition from a data table

        Args:
            dataframe: the data source

        Returns:
            dictionary of seasonal data
        """

        decomp = seasonal.seasonal_decompose(dataframe,
                                             model='additive',
                                             freq=self.frequency)

        return {
            runs.observed: decomp.observed,
            runs.trend:    decomp.trend,
            runs.season:   decomp.seasonal,
            runs.resid:    decomp.resid
        }

    def make_seasonal(self, dataframes: hint.dataframes) -> dict:
        """
        Create seasonal decomposition for a collection of dataframes

        Args:
            dataframes:  the dataframes

        Returns:
            all of the seasonal decomposes
        """

        decomp = {}
        for table_name, dataframe in dataframes.items():
            print('        {} Creating {} table decomposition'.
                  format(datetime.datetime.now(), table_name))
            decomp[table_name] = self._make_seasonal(dataframe)

        return decomp

    def seasonal(self) -> dict:
        """
        Create all the seasonal decompositions

        Returns:
            dictionary of all seasonal decompositions
        """

        decomp = {}
        for label, dataframes in self.dataframes.items():
            print('    {} Creating {} decomposition'.
                  format(datetime.datetime.now(), label))
            decomp[label] = self.make_seasonal(dataframes)

        return decomp

    @classmethod
    def create(cls, base_name: str,
                    frequency: int) -> dict:
        """
        Create all the seasonal decompositions

        Args:
            base_name: name of the simulation
            frequency: of seasons

        Returns:
            dictionary of decomposition data
        """

        decomp = cls(base_name, frequency)

        return decomp.seasonal()


@dclass.dataclass
class PlotData(object):
    """
    Class to plot seasonal decompositions
    """

    seasonal: dict

    @staticmethod
    def _plot_seasonal(dataframe: hint.dataframe,
                       columns:   list,
                       title:     str):
        """
        Plot a seasonal dataframe

        Args:
            dataframe: dataframe to plot
            columns:   list of columns to plot
            title:     title of plot

        Returns:
            a plot
        """

        reg_plot            = plt.figure(plot_height=plot_height,
                                         plot_width=plot_width)
        reg_plot.title.text = title
        reg_plot.xaxis.axis_label = 'time (days)'
        reg_plot.yaxis.axis_label = 'population'

        for index, column in enumerate(columns):
            reg_plot.line(dataframe.index, dataframe[column],
                          line_width=line_width,
                          color=colors[index],
                          legend=column)

        reg_plot.legend.location = "top_right"

        reg_plot.legend.label_text_font_size = legend_font_size

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

    def plot_seasonal(self, dataframes: hint.dataframes,
                            columns:    list,
                            title:      str) -> dict:
        """
        Create all of the plots for a seasonal decomposition
        Args:
            dataframes: dataframes of the decomposition
            columns:    columns to plot
            title:      base title

        Returns:
            dictionary of plots
        """

        decomp = {}
        for decomp_title, dataframe in dataframes.items():
            plot_title = '{} {}'.format(title, decomp_title)
            decomp[decomp_title] = self._plot_seasonal(dataframe,
                                                       columns,
                                                       plot_title)

        return decomp

    def plot_seasonals(self, dataframes: dict,
                             columns:    list,
                             title:      str) -> dict:
        """
        Create all of the decomposition plots for all of the life stages

        Args:
            dataframes: dataframes of the decomposition
            columns:    columns to plot
            title:      base title

        Returns:
            dictionary of plots
        """

        decomp = {}
        for table_name, data in dataframes.items():
            name = table_name.split('_')[1]
            plot_title = '{} {}'.format(title, name)
            decomp[table_name] = self.plot_seasonal(data,
                                                    columns,
                                                    plot_title)

        return decomp

    def plot(self, columns: list) -> dict:
        """
        Plot all the seasonal decompositions

        Args:
            columns: columns to plot

        Returns:
            dictionary of plots
        """

        decomp = {}
        for title, dataframes in self.seasonal.items():
            decomp[title] = self.plot_seasonals(dataframes,
                                                columns,
                                                title)

        return decomp

    @classmethod
    def create(cls, base_name: str,
                    frequency: int,
                    columns:   list) -> dict:
        """
        Create all of the seasonal plots

        Args:
            base_name: name of the simulation
            frequency: decomposition frequency
            columns:   list of columns to use

        Returns:
            all of the plots
        """

        dataframes = Seasonal.create(base_name, frequency)
        plot       = cls(dataframes)

        return plot.plot(columns)


@dclass.dataclass
class PlotLowHighData(object):
    """
    Class to plot seasonal decompositions
    """

    seasonal_low: dict
    seasonal_high: dict

    @staticmethod
    def _plot_seasonal(dataframe_low:  hint.dataframe,
                       dataframe_high: hint.dataframe,
                       columns:        list,
                       title:          str):
        """
        Plot a seasonal dataframe

        Args:
            dataframe_low:  dataframe to plot low
            dataframe_high: dataframe to plot high
            columns:        list of columns to plot
            title:          title of plot

        Returns:
            a plot
        """

        reg_plot            = plt.figure(plot_height=plot_height,
                                         plot_width=plot_width)
        reg_plot.title.text = title
        reg_plot.xaxis.axis_label = 'time (days)'
        reg_plot.yaxis.axis_label = 'population'

        for index, column in enumerate(columns):
            reg_plot.line(dataframe_low.index, dataframe_low[column],
                          line_width=line_width,
                          color=colors[index],
                          legend='Low {}'.format(column))
            reg_plot.line(dataframe_high.index, dataframe_high[column],
                          line_width=line_width,
                          color=colors[index],
                          line_dash='dashed',
                          legend='High {}'.format(column))

        reg_plot.legend.location = "top_right"

        reg_plot.legend.label_text_font_size = legend_font_size

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

    def plot_seasonal(self, dataframes_low:  hint.dataframes,
                            dataframes_high: hint.dataframes,
                            columns:         list,
                            title:           str) -> dict:
        """
        Create all of the plots for a seasonal decomposition
        Args:
            dataframes_low:  dataframes of the decomposition low
            dataframes_high: dataframes of the decomposition high
            columns:         columns to plot
            title:           base title

        Returns:
            dictionary of plots
        """

        decomp = {}
        for decomp_title, dataframe_low in dataframes_low.items():
            dataframe_high = dataframes_high[decomp_title]
            plot_title = '{} {}'.format(title, decomp_title)
            decomp[decomp_title] = self._plot_seasonal(dataframe_low,
                                                       dataframe_high,
                                                       columns,
                                                       plot_title)

        return decomp

    def plot_seasonals(self, dataframes_low:  dict,
                             dataframes_high: dict,
                             columns:         list,
                             title:           str) -> dict:
        """
        Create all of the decomposition plots for all of the life stages

        Args:
            dataframes_low:  dataframes of the decomposition low
            dataframes_high: dataframes of the decomposition high
            columns:         columns to plot
            title:           base title

        Returns:
            dictionary of plots
        """

        decomp = {}
        for table_name, data_low in dataframes_low.items():
            data_high = dataframes_high[table_name]
            name = table_name.split('_')[1]
            plot_title = '{} {}'.format(title, name)
            decomp[table_name] = self.plot_seasonal(data_low,
                                                    data_high,
                                                    columns,
                                                    plot_title)

        return decomp

    def plot(self, columns: list) -> dict:
        """
        Plot all the seasonal decompositions

        Args:
            columns: columns to plot

        Returns:
            dictionary of plots
        """

        decomp = {}
        for title, dataframes_low in self.seasonal_low.items():
            dataframes_high = self.seasonal_high[title]
            decomp[title] = self.plot_seasonals(dataframes_low,
                                                dataframes_high,
                                                columns,
                                                title)

        return decomp

    @classmethod
    def create(cls, base_name_low:  str,
                    base_name_high: str,
                    frequency:      int,
                    columns:        list) -> dict:
        """
        Create all of the seasonal plots

        Args:
            base_name_low:  name of the simulation low
            base_name_high: name of the simulation low
            frequency:      decomposition frequency
            columns:        list of columns to use

        Returns:
            all of the plots
        """

        dataframes_low  = Seasonal.create(base_name_low, frequency)
        dataframes_high = Seasonal.create(base_name_high, frequency)
        plot       = cls(dataframes_low, dataframes_high)

        return plot.plot(columns)
