import os

import bokeh.plotting     as plt
import bokeh.layouts      as lay
import bokeh.models       as mdl
import bokeh.palettes     as palettes
# import bokeh.models.tools as tools

import dataclasses   as dclass
import pandas        as pd
import sqlalchemy    as sql

import source.hint as hint


start_point = 200

plot_width  = 1500
plot_height = 400

colors = palettes.Set1[3]



save_file = 'parallel_timeseries_decomp.html'
# source_name = 'long_sim_25_gen_no_im_bt_10_no_hetero.sqlite'
source_name = 'parallel_sim_25_gen_no_bt_only_sus'
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

    def process_dataframes(self, start: int) -> dict:
        """
        Process all of the dataframes together

        Args:
            start: the correct starting point

        Returns:
            all the data frames cut down
        """

        data = self.cut_run_dataframes(start)

        data['mean']    = self.mean_dataframe(data)
        data['median']  = self.median_dataframe(data)
        data['std']     = self.std_dataframe(data)
        data['q_lower'] = self.q_lower_dataframe(data)
        # data['q_upper'] = self.q_upper_dataframe(data)
        data['min']     = self.min_dataframe(data)
        data['max']     = self.max_dataframe(data)

        return data


reader   = ReadData(source_name, source_path, tables)
run_data = reader.process_dataframes(start_point)

mean    = run_data['mean']
median  = run_data['median']
std     = run_data['std']
q_lower = run_data['q_lower']
min_val = run_data['min']
max_val = run_data['max']

egg_mean    = mean[tables[0]]
larva_mean  = mean[tables[1]]
pupa_mean   = mean[tables[2]]
female_mean = mean[tables[3]]

egg_median    = median[tables[0]]
larva_median  = median[tables[1]]
pupa_median   = median[tables[2]]
female_median = median[tables[3]]

egg_mean_source    = mdl.ColumnDataSource(egg_mean)
larva_mean_source  = mdl.ColumnDataSource(larva_mean)
pupa_mean_source   = mdl.ColumnDataSource(pupa_mean)
female_mean_source = mdl.ColumnDataSource(female_mean)

egg_median_source    = mdl.ColumnDataSource(egg_median)
larva_median_source  = mdl.ColumnDataSource(larva_median)
pupa_median_source   = mdl.ColumnDataSource(pupa_median)
female_median_source = mdl.ColumnDataSource(female_median)

egg_mean_plot = plt.figure(plot_width=plot_width, plot_height=plot_height)
egg_mean_plot.title.text = 'Egg Mean Timeseries Data'
egg_mean_plot.yaxis.axis_label = 'Mean Population'
egg_mean_plot.xaxis.axis_label = 'time (days)'
egg_mean_plot.line(x='index', y='genotype_resistant',
                   source=egg_mean_source,
                   color=colors[0], legend='Resistant')
egg_mean_plot.line(x='index', y='genotype_heterozygous',
                   source=egg_mean_source,
                   color=colors[1], legend='Heterozygous')
egg_mean_plot.line(x='index', y='genotype_susceptible',
                   source=egg_mean_source,
                   color=colors[0], legend='Susceptible')

larva_mean_plot = plt.figure(plot_width=plot_width, plot_height=plot_height,
                             x_range=egg_mean_plot.x_range)
larva_mean_plot.title.text = 'Larva Mean Timeseries Data'
larva_mean_plot.yaxis.axis_label = 'Mean Population'
larva_mean_plot.xaxis.axis_label = 'time (days)'
larva_mean_plot.line(x='index', y='genotype_resistant',
                     source=larva_mean_source,
                     color=colors[0], legend='Resistant')
larva_mean_plot.line(x='index', y='genotype_heterozygous',
                     source=larva_mean_source,
                     color=colors[1], legend='Heterozygous')
larva_mean_plot.line(x='index', y='genotype_susceptible',
                     source=larva_mean_source,
                     color=colors[0], legend='Susceptible')

pupa_mean_plot = plt.figure(plot_width=plot_width, plot_height=plot_height,
                            x_range=egg_mean_plot.x_range)
pupa_mean_plot.title.text = 'Pupa Mean Timeseries Data'
pupa_mean_plot.yaxis.axis_label = 'Mean Population'
pupa_mean_plot.xaxis.axis_label = 'time (days)'
pupa_mean_plot.line(x='index', y='genotype_resistant',
                    source=pupa_mean_source,
                    color=colors[0], legend='Resistant')
pupa_mean_plot.line(x='index', y='genotype_heterozygous',
                    source=pupa_mean_source,
                    color=colors[1], legend='Heterozygous')
pupa_mean_plot.line(x='index', y='genotype_susceptible',
                    source=pupa_mean_source,
                    color=colors[0], legend='Susceptible')

female_mean_plot = plt.figure(plot_width=plot_width, plot_height=plot_height,
                              x_range=egg_mean_plot.x_range)
female_mean_plot.title.text = 'Female Mean Timeseries Data'
female_mean_plot.yaxis.axis_label = 'Mean Population'
female_mean_plot.xaxis.axis_label = 'time (days)'
female_mean_plot.line(x='index', y='genotype_resistant',
                      source=female_mean_source,
                      color=colors[0], legend='Resistant')
female_mean_plot.line(x='index', y='genotype_heterozygous',
                      source=female_mean_source,
                      color=colors[1], legend='Heterozygous')
female_mean_plot.line(x='index', y='genotype_susceptible',
                      source=female_mean_source,
                      color=colors[0], legend='Susceptible')

egg_median_plot = plt.figure(plot_width=plot_width, plot_height=plot_height,
                             x_range=egg_mean_plot.x_range)
egg_median_plot.title.text = 'Egg Median Timeseries Data'
egg_median_plot.yaxis.axis_label = 'Median Population'
egg_median_plot.xaxis.axis_label = 'time (days)'
egg_median_plot.line(x='index', y='genotype_resistant',
                     source=egg_median_source,
                     color=colors[0], legend='Resistant')
egg_median_plot.line(x='index', y='genotype_heterozygous',
                     source=egg_median_source,
                     color=colors[1], legend='Heterozygous')
egg_median_plot.line(x='index', y='genotype_susceptible',
                     source=egg_median_source,
                     color=colors[0], legend='Susceptible')

larva_median_plot = plt.figure(plot_width=plot_width, plot_height=plot_height,
                               x_range=egg_mean_plot.x_range)
larva_median_plot.title.text = 'Larva Median Timeseries Data'
larva_median_plot.yaxis.axis_label = 'Median Population'
larva_median_plot.xaxis.axis_label = 'time (days)'
larva_median_plot.line(x='index', y='genotype_resistant',
                       source=larva_median_source,
                       color=colors[0], legend='Resistant')
larva_median_plot.line(x='index', y='genotype_heterozygous',
                       source=larva_median_source,
                       color=colors[1], legend='Heterozygous')
larva_median_plot.line(x='index', y='genotype_susceptible',
                       source=larva_median_source,
                       color=colors[0], legend='Susceptible')

pupa_median_plot = plt.figure(plot_width=plot_width, plot_height=plot_height,
                              x_range=egg_mean_plot.x_range)
pupa_median_plot.title.text = 'Pupa Median Timeseries Data'
pupa_median_plot.yaxis.axis_label = 'Median Population'
pupa_median_plot.xaxis.axis_label = 'time (days)'
pupa_median_plot.line(x='index', y='genotype_resistant',
                      source=pupa_median_source,
                      color=colors[0], legend='Resistant')
pupa_median_plot.line(x='index', y='genotype_heterozygous',
                      source=pupa_median_source,
                      color=colors[1], legend='Heterozygous')
pupa_median_plot.line(x='index', y='genotype_susceptible',
                      source=pupa_median_source,
                      color=colors[0], legend='Susceptible')

female_median_plot = plt.figure(plot_width=plot_width, plot_height=plot_height,
                                x_range=egg_mean_plot.x_range)
female_median_plot.title.text = 'Female Median Timeseries Data'
female_median_plot.yaxis.axis_label = 'Median Population'
female_median_plot.xaxis.axis_label = 'time (days)'
female_median_plot.line(x='index', y='genotype_resistant',
                        source=female_median_source,
                        color=colors[0], legend='Resistant')
female_median_plot.line(x='index', y='genotype_heterozygous',
                        source=female_median_source,
                        color=colors[1], legend='Heterozygous')
female_median_plot.line(x='index', y='genotype_susceptible',
                        source=female_median_source,
                        color=colors[0], legend='Susceptible')

series_data_title = mdl.Div(text='<h1>48 Run Timeseries Data</h1>')
series_data_plot = lay.gridplot([[egg_mean_plot,    egg_median_plot],
                                 [larva_mean_plot,  larva_median_plot],
                                 [pupa_mean_plot,   pupa_median_plot],
                                 [female_mean_plot, female_median_plot]])
plt.show(lay.column(series_data_title,
                    series_data_plot))
