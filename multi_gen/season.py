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

plot_width  = 800
plot_height = 500

colors    = palettes.Colorblind[8]
save_file = 'periodogram_plots.html'

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
            dataframe:
            columns:
            title:

        Returns:

        """


resistant_sim = Seasonal(simulation_runs[0], 82).seasonal()
