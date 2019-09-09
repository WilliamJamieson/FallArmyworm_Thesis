import os

import dataclasses       as dclass
import matplotlib.pyplot as plt
import numpy             as np
import pandas            as pd
import sqlalchemy        as sql

import source.hint as hint


save_fig   = True
save_name  = 'long_sim_25_gen_no_im_bt_10_no_hetero.sqlite'
save_title = 'gen_25_plot_no_im_no_bt_10_hetero.png'
fig_title  = 'Many Generations on 10/90 Bt Field'
logy       = False

resistant    = 'genotype_resistant'
heterozygous = 'genotype_heterozygous'
susceptible  = 'genotype_susceptible'
proportion   = 'proportion'


@dclass.dataclass
class ReadData(object):
    """
    Class to read data
    """

    base_name:   str
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

        files = [f for f in os.listdir(os.curdir) if os.path.isfile(f)]
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

    @staticmethod
    def resistant_prop(row: pd.Series) -> float:
        """
        Function to compute the resistant allele proportion for a given step

        Args:
            row: row of the series

        Returns:
            resistant allele proportion
        """

        total  = 2 * (row[resistant] + row[heterozygous] + row[susceptible])
        allele = 2 * row[resistant] + row[heterozygous]

        if total == 0:
            return np.nan
        else:
            return allele / total

    def add_resistant_prop(self, dataframe: hint.dataframe) -> None:
        """
        Add the resistant prop row to the dataframe

        Args:
            dataframe: the dataframe to add to

        Returns:
            a dataframe with the a new column
        """

        dataframe[proportion] = dataframe.\
            apply(lambda row: self.resistant_prop(row), axis=1)

    def create_prop(self, dataframes: hint.dataframes) -> None:
        """
        Add the resistant prop to all the dataframes

        Args:
            dataframes: the dataframes to use

        Effects:
            adds proportion columns
        """

        for dataframe in dataframes.values():
            self.add_resistant_prop(dataframe)


table0 = '(0,)_egg'
table1 = '(0,)_larva'
table2 = '(0,)_pupa'
table3 = '(0,)_female'
tables = [table0, table1, table2, table3]
reader = ReadData(save_name, tables)

data = reader.cut_dataframes(200)
reader.create_prop(data)

plt.figure(figsize=[30, 15])
plt.suptitle(fig_title)

# plot Eggs
plt.subplot(4, 1, 1)
data[table0][resistant].   plot(color='b', label='Resistant',
                                           logy=logy)
data[table0][heterozygous].plot(color='r', label='Heterozygous',
                                           logy=logy)
data[table0][susceptible]. plot(color='k', label='Susceptible',
                                           logy=logy)

plt.legend()
plt.ylabel('egg population')

# plot Larva
plt.subplot(4, 1, 2)
data[table1][resistant].   plot(color='b', label='Resistant',
                                           logy=logy)
data[table1][heterozygous].plot(color='r', label='Heterozygous',
                                           logy=logy)
data[table1][susceptible]. plot(color='k', label='Susceptible',
                                           logy=logy)

plt.legend()
plt.ylabel('larva population')

# plot Pupa
plt.subplot(4, 1, 3)
data[table2][resistant].   plot(color='b', label='Resistant',
                                           logy=logy)
data[table2][heterozygous].plot(color='r', label='Heterozygous',
                                           logy=logy)
data[table2][susceptible]. plot(color='k', label='Susceptible',
                                           logy=logy)

plt.legend()
plt.ylabel('pupa population')

# plot Female
plt.subplot(4, 1, 4)
data[table3][resistant].   plot(color='b', label='Resistant',
                                           logy=logy)
data[table3][heterozygous].plot(color='r', label='Heterozygous',
                                           logy=logy)
data[table3][susceptible]. plot(color='k', label='Susceptible',
                                           logy=logy)

plt.legend()
plt.ylabel('female population')
plt.xlabel('time (days)')

if save_fig:
    plt.savefig(save_title)
plt.show()

plt.figure(figsize=[50, 10])
data[table0][proportion].plot(color='b', label='Egg', logy=logy)
data[table1][proportion].plot(color='r', label='Larva', logy=logy)
data[table2][proportion].plot(color='k', label='Pupa', logy=logy)
data[table3][proportion].plot(color='g', label='Female', logy=logy)

plt.legend()
plt.ylabel('population')
plt.xlabel('time (days)')
plt.title('{} {}'.format(fig_title, 'Resistant Proportion'))

if save_fig:
    plt.savefig('{}_{}'.format('proportion', save_title))
plt.show()
