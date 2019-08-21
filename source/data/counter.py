import collections as collect

import pandas as pd

import source.hint as hint


class DataColumn(collect.UserList):
    """
    Class to keep up with data counts over time:

    Variables:
        list:
            index: time-step
            value: count at end of time-step

        attr_value: value of attribute to count

    Methods:
        record: record the value

    Constructors:
        empty: setup the list
    """

    def __init__(self, data: hint.data_list,
                       attr_value: str):
        super().__init__(data)

        self.attr_value = attr_value

    def record(self, count: hint.counter) -> None:
        """
        Record the attribute from count

        Args:
            count: count system

        Effects:
            records the current count
        """

        self.append(count[self.attr_value])

    @classmethod
    def empty(cls, attr_value: str) -> 'DataColumn':
        """
        Create an empty data column

        Args:
            attr_value: attribute to record

        Returns:
            an empty data column
        """

        return cls([], attr_value)


class DataColumns(collect.UserDict):
    """
    Class to keep track of all the attribute values overtime for a single count:

    Variables:
        dict:
            key:   attr_value
            value: a data column

        attr: the attribute to be tracked

    Methods:
        record:  record the value
        columns: create a dict
            key:   attr_attr_value
            value: DataColumn

    Constructors:
        empty: setup the list
    """

    def __init__(self, data: hint.data_column_dict,
                       attr: str):
        super().__init__(data)

        self.attr = attr

    def record(self, count: hint.counter) -> None:
        """
        Record the attribute from count

        Args:
            count: count system

        Effects:
            records the current count
        """

        for column in self.values():
            column.record(count)

    def columns(self) -> hint.data_column_dict:
        """
        Create a dictionary of data_columns

        Returns:
            dictionary of data columns
        """

        data = {}

        for attr_value, data_column in self.items():
            key = '{}_{}'.format(self.attr, attr_value)
            data[key] = data_column

        return data

    @classmethod
    def empty(cls, attr:       str,
                   attr_values: hint.attr_values) -> 'DataColumns':
        """
        Create an empty data column

        Args:
            attr:        attribute
            attr_values: attribute values

        Returns:
            an empty set of data columns
        """

        data = {}
        for attr_value in attr_values:
            data[attr_value] = DataColumn.empty(attr_value)

        return cls(data, attr)


class Count(collect.UserDict):
    """
    Class to keep track of attribute counts

    Variables:
        dict:
            key:   attribute value
            value: count

        attr:    attribute to keep track of
        removal: boolean to keep count of removal only

        data_columns: data columns for system

    Methods:
        add:    add agent to count
        sub:    subtract agent from count
        record: record the count in the data columns

    Constructors:
        setup: create a counter
    """

    def __init__(self, counts:       hint.count_dict,
                       attr:         str,
                       removal:      bool,
                       data_columns: hint.data_columns):
        super().__init__(counts)

        self.attr    = attr
        self.removal = removal

        self.data_columns = data_columns

    def add(self, agent: hint.agent) -> None:
        """
        Adds agent to counter

        Args:
            agent: agent to count

        Effects:
            add count of attribute
        """

        if not self.removal:
            value = getattr(agent, self.attr)
            self[value] += 1

    def sub(self, agent: hint.agent) -> None:
        """
        Subtracts agent from counter

        Args:
            agent: agent to count

        Effects:
            remove count of attribute
        """

        value = getattr(agent, self.attr)

        if self.removal:
            if value in self:
                self[value] += 1
        else:
            self[value] -= 1

    def record(self) -> None:
        """
        Record the current count

        Effect:
            Records all of the data
        """

        self.data_columns.record(self)

    @classmethod
    def empty(cls, attr:    str,
                   values:  hint.attr_values,
                   removal: bool) -> 'Count':
        """
        Setup an empty counter

        Args:
            attr:    attribute to count
            values:  values for attribute
            removal: determine if we only count removals

        Returns:
            a setup class
        """

        counts       = {value: 0 for value in values}
        data_columns = DataColumns.empty(attr, values)

        return cls(counts, attr, removal, data_columns)


class Counts(collect.UserDict):
    """
    Class to contain all attribute counts

    Variables:
        - dict:
            key:   attribute
            value: attribute counter

    Methods:
        add:    add agent to count
        sub:    subtract agent from count
        record: record the count in the data columns

    Constructors:
        setup: create a counter
    """

    def __init__(self, counts: hint.counter_dict):
        super().__init__(counts)

    def add(self, agent: hint.agent) -> None:
        """
        Adds agent to counter

        Args:
            agent: agent to count

        Effects:
            add count of attribute
        """

        for counter in self.values():
            counter.add(agent)

    def sub(self, agent: hint.agent) -> None:
        """
        Subtracts agent from counter

        Args:
            agent: agent to count

        Effects:
            remove count of attribute
        """

        for counter in self.values():
            counter.sub(agent)

    def record(self) -> None:
        """
        Record the current counts

        Effect:
            Records all of the data
        """

        for counter in self.values():
            counter.record()

    def columns(self) -> hint.data_column_dict:
        """
        Create a dictionary of all data_columns

        Returns:
            dictionary of data columns
        """

        columns = {}
        for count in self.values():
            columns.update(count.data_columns.columns())

        return columns

    def dataframe(self) -> hint.dataframe:
        """
        Create a dataframe of the recorded data

        Returns:
            A dataframe of the data
        """

        return pd.DataFrame.from_dict(self.columns())

    def count(self, attr:    str,
                    values:  hint.attr_values,
                    removal: bool) -> None:
        """
        Add count to system


        Args:
            attr:    attribute to count
            values:  values for attribute
            removal: determine if we only count removals

        Effects:
            Adds count to system
        """

        self[attr] = Count.empty(attr, values, removal)

    @classmethod
    def empty(cls, attrs: hint.attrs) -> 'Counts':
        """
        Setup an empty counter

        Args:
            attrs: attributes to count

        Returns:
            a setup class
        """

        new = cls({})
        for attr, values in attrs.items():
            new[attr] = Count.empty(attr, *values)

        return new
