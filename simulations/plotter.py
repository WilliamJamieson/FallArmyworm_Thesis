import dataclasses       as dclass
import matplotlib.pyplot as plt
import pandas            as pd
import sqlalchemy        as sql

import source.hint as hint


save_fig   = True
save_title = 'gen_25_plot_no_im.png'
logy       = False


@dclass.dataclass
class ReadData(object):
    """
    Class to read data
    """

    file_names:  list
    table_names: list

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


name0  = '0_to_50_long_sim_3_gen_no_im.sqlite'
name1  = '50_to_100_long_sim_3_gen_no_im.sqlite'
name2  = '100_to_150_long_sim_3_gen_no_im.sqlite'
name3  = '150_to_179_long_sim_3_gen_no_im.sqlite'
names  = [name0, name1, name2, name3]
table0 = '(0,)_egg'
table1 = '(0,)_larva'
table2 = '(0,)_pupa'
table3 = '(0,)_female'
tables = [table0, table1, table2, table3]
reader = ReadData(names, tables)

data = reader.dataframes()

plt.figure(figsize=[10, 10])
plt.suptitle('Three Generations')

# plot Eggs
plt.subplot(4, 1, 1)
data[table0]['genotype_resistant'].   plot(color='b', label='Resistant',
                                           logy=logy)
data[table0]['genotype_heterozygous'].plot(color='r', label='Heterozygous',
                                           logy=logy)
data[table0]['genotype_susceptible']. plot(color='k', label='Susceptible',
                                           logy=logy)

plt.legend()
plt.ylabel('egg population')

# plot Larva
plt.subplot(4, 1, 2)
data[table1]['genotype_resistant'].   plot(color='b', label='Resistant',
                                           logy=logy)
data[table1]['genotype_heterozygous'].plot(color='r', label='Heterozygous',
                                           logy=logy)
data[table1]['genotype_susceptible']. plot(color='k', label='Susceptible',
                                           logy=logy)

plt.legend()
plt.ylabel('larva population')

# plot Pupa
plt.subplot(4, 1, 3)
data[table2]['genotype_resistant'].   plot(color='b', label='Resistant',
                                           logy=logy)
data[table2]['genotype_heterozygous'].plot(color='r', label='Heterozygous',
                                           logy=logy)
data[table2]['genotype_susceptible']. plot(color='k', label='Susceptible',
                                           logy=logy)

plt.legend()
plt.ylabel('pupa population')

# plot Female
plt.subplot(4, 1, 4)
data[table3]['genotype_resistant'].   plot(color='b', label='Resistant',
                                           logy=logy)
data[table3]['genotype_heterozygous'].plot(color='r', label='Heterozygous',
                                           logy=logy)
data[table3]['genotype_susceptible']. plot(color='k', label='Susceptible',
                                           logy=logy)

plt.legend()
plt.ylabel('female population')
plt.xlabel('time (days)')

if save_fig:
    plt.savefig(save_title)
plt.show()
