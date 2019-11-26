import datetime
import pickle

import bokeh.plotting     as plt
import bokeh.models       as mdl
import bokeh.palettes     as palettes
import bokeh.models.tools as tools

import dataclasses   as dclass
import pandas        as pd

import numpy        as np
import scipy.signal as signal

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
class Periodogram(object):
    """
    Class to read data
    """
    base_name:  str
    dataframes: dict = dclass.field(default=dict)

    def __post_init__(self):
        """read the data frames"""

        data_file = '{}_summary.data'.format(self.base_name)

        with open(data_file, 'rb') as read_file:
            self.dataframes = pickle.load(read_file)

    @staticmethod
    def _make_periodogram(dataframe: hint.dataframe,
                          column:    str,
                          label:     str) -> hint.dataframe:
        """
        Create a periodogram from a data table
        Args:
            dataframe: the data source
            column:    column of the source
            label:     type of data

        Returns:
            dictionary of periodogram data
        """

        freq, power = signal.periodogram(dataframe[column])

        period = (1 / freq[1:]).tolist()
        period.insert(0, np.inf)

        primary_index = np.argmax(power)
        primary       = period[primary_index]

        data = {
            runs.freq:   freq,
            runs.power:  power,
            runs.period: period,
        }

        if runs.genotype in column:
            genotype = column.split('_')[1]
        else:
            genotype = 'R allele'

        periodogram = pd.DataFrame.from_dict(data)
        periodogram[runs.primary]  = primary
        periodogram[runs.genotype] = genotype
        periodogram[runs.comb]     = label

        return periodogram

    def _make_periodograms(self, dataframe: hint.dataframe,
                                 label:     str) -> hint.dataframes:
        """
        Create all of the periodograms

        Args:
            dataframe: the dataframe to decompose
            label:     the type of data

        Returns:
            dictionary of all the periodograms by column
        """

        data = {}
        for column in runs.columns:
            print('           {} Creating column {} periodograms'.
                  format(datetime.datetime.now(), column))
            data[column] = self._make_periodogram(dataframe, column, label)

        return data

    def make_periodograms(self, label: str) -> dict:
        """
        Create all of the periodograms for the data type

        Args:
            label:  the data type

        Returns:
            dictionary of all the periodograms
        """

        dataframes: hint.dataframes = self.dataframes[label]

        data = {}
        for table_name, dataframe in dataframes.items():
            print('       {} Creating table {} periodograms'.
                  format(datetime.datetime.now(), table_name))
            data[table_name] = self._make_periodograms(dataframe, label)

        return data

    def periodograms(self) -> dict:
        """
        Create all of the periodograms

        Returns:
            all of the periodograms
        """

        data = {}
        for label in runs.summaries:
            print('    {} Creating {} periodograms'.
                  format(datetime.datetime.now(), label))
            data[label] = self.make_periodograms(label)

        return data

    @classmethod
    def create(cls, base_name: str) -> dict:
        """
        create all of the periodogram data

        Args:
            base_name: name of the simulation

        Returns:
            dictionary of periodogram data
        """

        periodograms = cls(base_name)

        return periodograms.periodograms()


@dclass.dataclass
class PlotData(object):
    """
    Class to plot periodograms
    """

    periodograms: dict

    @staticmethod
    def _plot_periodogram(dataframe: hint.dataframe,
                          title:     str) -> dict:
        """
        Create a Bokeh plot of the periodogram dataframe
        Args:
            dataframe: the dataframe to use
            title:     the title for the plot

        Returns:
            a dictionary of Bokeh plots
        """

        source = mdl.ColumnDataSource(dataframe)

        base_title = 'for {}, main period: {}'.\
            format(dataframe[runs.genotype].iloc[0],
                   np.round(dataframe[runs.primary].iloc[0], 3))

        reg_plot            = plt.figure(plot_height=plot_height,
                                         plot_width=plot_width)
        reg_plot.title.text = '{} {}'.\
            format(title, base_title)
        reg_plot.xaxis.axis_label = 'Frequency'
        reg_plot.yaxis.axis_label = 'Power Spectral Density'

        reg_plot.line(x=runs.freq, y=runs.power, source=source,
                      line_width=line_width,
                      color=colors[0])

        reg_hover = tools.HoverTool()
        reg_hover.tooltips = [
            ('Frequency', '@freq'),
            ('Period', '@period'),
            ('Spectral Density', '@power'),
            ('Genotype', '@genotype'),
            ('Source', '@comb')
        ]
        reg_plot.add_tools(reg_hover)

        reg_plot.title.text_font_size = title_font_size
        reg_plot.yaxis.axis_line_width = axis_line_width
        reg_plot.xaxis.axis_line_width = axis_line_width
        reg_plot.yaxis.axis_label_text_font_size = axis_font_size
        reg_plot.xaxis.axis_label_text_font_size = axis_font_size
        reg_plot.yaxis.major_label_text_font_size = axis_tick_font_size
        reg_plot.xaxis.major_label_text_font_size = axis_tick_font_size
        reg_plot.ygrid.grid_line_width = grid_line_width
        reg_plot.xgrid.grid_line_width = grid_line_width

        log_plot = plt.figure(plot_height=plot_height,
                              plot_width=plot_width,
                              y_axis_type='log')
        log_plot.title.text = '{} log-scale {}'.\
            format(title, base_title)
        log_plot.xaxis.axis_label = 'Frequency'
        log_plot.yaxis.axis_label = 'log(Power Spectral Density)'

        log_plot.line(x=runs.freq, y=runs.power, source=source,
                      line_width=line_width,
                      color=colors[0])

        log_hover = tools.HoverTool()
        log_hover.tooltips = [
            ('Frequency', '@freq'),
            ('Period', '@period'),
            ('Spectral Density', '@power'),
            ('Genotype', '@genotype'),
            ('Source', '@comb')
        ]
        log_plot.add_tools(log_hover)

        log_plot.title.text_font_size = title_font_size
        log_plot.yaxis.axis_line_width = axis_line_width
        log_plot.xaxis.axis_line_width = axis_line_width
        log_plot.yaxis.axis_label_text_font_size = axis_font_size
        log_plot.xaxis.axis_label_text_font_size = axis_font_size
        log_plot.yaxis.major_label_text_font_size = axis_tick_font_size
        log_plot.xaxis.major_label_text_font_size = axis_tick_font_size
        log_plot.ygrid.grid_line_width = grid_line_width
        log_plot.xgrid.grid_line_width = grid_line_width

        return {
            runs.reg: reg_plot,
            runs.log: log_plot
        }

    def _plot_periodograms(self, dataframes: hint.dataframes,
                                 title:      str) -> dict:
        """
        Plot all of the periodograms for the data

        Args:
            dataframes: the periodogram data for a given title
            title:      the main title

        Returns:
            plots of all data from a given type
        """

        periodograms = {}
        for column_name, dataframe in dataframes.items():
            print('               {} Creating plot for {}'.
                  format(datetime.datetime.now(), column_name))
            periodograms[column_name] = self._plot_periodogram(dataframe,
                                                               title)

        return periodograms

    def plot_periodograms(self, periodograms: dict,
                                title:        str) -> dict:
        """
        Plot all the periodograms for a type of data

        Args:
            periodograms: dict of data by table
            title:        the base type of data tile

        Returns:
            dictionary of plots
        """

        plots = {}
        for table_name,  dataframes in periodograms.items():
            print('           {} Creating plot for {}'.
                  format(datetime.datetime.now(), table_name))
            name = table_name.split('_')[1]
            plot_title = '{} {}'.format(title, name)
            plots[table_name] = self._plot_periodograms(dataframes, plot_title)

        return plots

    def plot(self) -> dict:
        """
        Plot all of the periodograms

        Returns:
            all of the plots
        """

        plots = {}
        for title, periodograms in self.periodograms.items():
            print('        {} Creating plot for {}'.
                  format(datetime.datetime.now(), title))
            plots[title] = self.plot_periodograms(periodograms, title)

        return plots

    @classmethod
    def create(cls, base_name: str) -> dict:
        """
        Plot all of the periodograms
        Args:
            base_name: name of the simulation

        Returns:
            all of the bokeh plots
        """

        periodograms = Periodogram.create(base_name)
        plot         = cls(periodograms)
        print('    {} Creating plots'.
              format(datetime.datetime.now()))

        return plot.plot()


@dclass.dataclass
class PlotLowHighData(object):
    """
    Class to plot periodograms
    """

    periodograms_low: dict
    periodograms_high: dict

    @staticmethod
    def _plot_periodogram(dataframe_low:  hint.dataframe,
                          dataframe_high: hint.dataframe,
                          title:          str) -> dict:
        """
        Create a Bokeh plot of the periodogram dataframe
        Args:
            dataframe_low:  the dataframe low  survival
            dataframe_high: the dataframe high survival
            title:          the title for the plot

        Returns:
            a dictionary of Bokeh plots
        """

        source_low  = mdl.ColumnDataSource(dataframe_low)
        source_high = mdl.ColumnDataSource(dataframe_high)

        base_title = 'for {}, main period: {} or {}'. \
            format(dataframe_low[runs.genotype].iloc[0],
                   np.round(dataframe_low[runs.primary].iloc[0], 3),
                   np.round(dataframe_high[runs.primary].iloc[0], 3))

        reg_plot            = plt.figure(plot_height=plot_height,
                                         plot_width=plot_width)
        reg_plot.title.text = '{} {}'. \
            format(title, base_title)
        reg_plot.xaxis.axis_label = 'Frequency'
        reg_plot.yaxis.axis_label = 'Power Spectral Density'

        reg_plot.line(x=runs.freq, y=runs.power, source=source_low,
                      line_width=line_width,
                      color=colors[0],
                      legend='Low Survival')
        reg_plot.line(x=runs.freq, y=runs.power, source=source_high,
                      line_width=line_width,
                      color=colors[1],
                      legend='High Survival')

        reg_hover = tools.HoverTool()
        reg_hover.tooltips = [
            ('Frequency', '@freq'),
            ('Period', '@period'),
            ('Spectral Density', '@power'),
            ('Genotype', '@genotype'),
            ('Source', '@comb')
        ]
        reg_plot.add_tools(reg_hover)

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

        log_plot = plt.figure(plot_height=plot_height,
                              plot_width=plot_width,
                              y_axis_type='log')
        log_plot.title.text = '{} log-scale {}'. \
            format(title, base_title)
        log_plot.xaxis.axis_label = 'Frequency'
        log_plot.yaxis.axis_label = 'log(Power Spectral Density)'

        log_plot.line(x=runs.freq, y=runs.power, source=source_low,
                      line_width=line_width,
                      color=colors[0],
                      legend='Low Survival')
        log_plot.line(x=runs.freq, y=runs.power, source=source_high,
                      line_width=line_width,
                      color=colors[1],
                      legend='High Survival')

        log_hover = tools.HoverTool()
        log_hover.tooltips = [
            ('Frequency', '@freq'),
            ('Period', '@period'),
            ('Spectral Density', '@power'),
            ('Genotype', '@genotype'),
            ('Source', '@comb')
        ]
        log_plot.add_tools(log_hover)

        log_plot.legend.location = "top_right"

        log_plot.legend.label_text_font_size = legend_font_size
        log_plot.title.text_font_size = title_font_size
        log_plot.yaxis.axis_line_width = axis_line_width
        log_plot.xaxis.axis_line_width = axis_line_width
        log_plot.yaxis.axis_label_text_font_size = axis_font_size
        log_plot.xaxis.axis_label_text_font_size = axis_font_size
        log_plot.yaxis.major_label_text_font_size = axis_tick_font_size
        log_plot.xaxis.major_label_text_font_size = axis_tick_font_size
        log_plot.ygrid.grid_line_width = grid_line_width
        log_plot.xgrid.grid_line_width = grid_line_width

        return {
            runs.reg: reg_plot,
            runs.log: log_plot
        }

    def _plot_periodograms(self, dataframes_low:  hint.dataframes,
                                 dataframes_high: hint.dataframes,
                                 title:           str) -> dict:
        """
        Plot all of the periodograms for the data

        Args:
            dataframes_low:  the periodogram data for a given title low  data
            dataframes_high: the periodogram data for a given title high data
            title:      the main title

        Returns:
            plots of all data from a given type
        """

        periodograms = {}
        for column_name, dataframe_low in dataframes_low.items():
            print('               {} Creating plot for {}'.
                  format(datetime.datetime.now(), column_name))
            dataframe_high = dataframes_high[column_name]
            periodograms[column_name] = self._plot_periodogram(dataframe_low,
                                                               dataframe_high,
                                                               title)

        return periodograms

    def plot_periodograms(self, periodograms_low:  dict,
                                periodograms_high: dict,
                                title:             str) -> dict:
        """
        Plot all the periodograms for a type of data

        Args:
            periodograms_low:  dict of data by table for low
            periodograms_high: dict of data by table for high
            title:            the base type of data tile

        Returns:
            dictionary of plots
        """

        plots = {}
        for table_name,  dataframes_low in periodograms_low.items():
            print('           {} Creating plot for {}'.
                  format(datetime.datetime.now(), table_name))
            dataframes_high = periodograms_high[table_name]
            name = table_name.split('_')[1]
            plot_title = '{} {}'.format(title, name)
            plots[table_name] = self._plot_periodograms(dataframes_low,
                                                        dataframes_high,
                                                        plot_title)

        return plots

    def plot(self) -> dict:
        """
        Plot all of the periodograms

        Returns:
            all of the plots
        """

        plots = {}
        for title, periodograms_low in self.periodograms_low.items():
            print('        {} Creating plot for {}'.
                  format(datetime.datetime.now(), title))
            periodograms_high = self.periodograms_high[title]
            plots[title] = self.plot_periodograms(periodograms_low,
                                                  periodograms_high,
                                                  title)

        return plots

    @classmethod
    def create(cls, base_name_low:  str,
                    base_name_high: str) -> dict:
        """
        Plot all of the periodograms
        Args:
            base_name_low:  name of the simulation low
            base_name_high: name of the simulation high

        Returns:
            all of the bokeh plots
        """

        periodograms_low  = Periodogram.create(base_name_low)
        periodograms_high = Periodogram.create(base_name_high)
        plot              = cls(periodograms_low, periodograms_high)
        print('    {} Creating plots'.
              format(datetime.datetime.now()))

        return plot.plot()
