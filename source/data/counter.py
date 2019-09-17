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
        record:   record the value
        refresh:  reset the columns
        columns:  create a dict
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

    def refresh(self) -> None:
        """
        Reset all the data in columns to zero
            - part of a data refresh system

        Effects:
            clear all the data to empty
        """

        for column in self.values():
            column.clear()

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


class BaseCount(collect.UserDict):
    """
    Base class for attribute counting

    Variables:
        dict:
            key:   attribute value
            value: count tracker

        attr: attribute we are counting

    Methods:
        add:     add agent to count
        sub:     subtract agent from count
        record:  record the count in the data columns
        refresh: refresh the stored values in data columns

        get_data_columns: get the data columns to output
    """

    def __init__(self, counts: hint.counts_dict,
                       attr:   str):
        super().__init__(counts)

        self.attr = attr

    def add(self, agent: hint.agent) -> None:
        """
        Adds agent to counter

        Args:
            agent: agent to count

        Effects:
            add count of attribute
        """

        pass

    def sub(self, agent: hint.agent) -> None:
        """
        Subtracts agent from counter

        Args:
            agent: agent to count

        Effects:
            remove count of attribute
        """

        pass

    def record(self) -> None:
        """
        Record the current count

        Effect:
            Records all of the data
        """

        pass

    def refresh(self) -> None:
        """
        Refresh the data in the columns

        Effects:
            clears the columns
            adds current count
        """

        pass

    def get_data_columns(self) -> hint.data_column_dict:
        """
        Get the data_columns for class

        Returns:
            the data columns
        """

        pass


class Count(BaseCount):
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
        add:     add agent to count
        sub:     subtract agent from count
        record:  record the count in the data columns
        refresh: refresh the stored values in data columns

    Constructors:
        setup: create a counter
    """

    def __init__(self, counts:       hint.count_dict,
                       attr:         str,
                       removal:      bool,
                       data_columns: hint.data_columns):
        super().__init__(counts, attr)

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

    def _reset(self) -> None:
        """
        Reset the counts of the system

        Effects:
            set counts to zero
        """

        for key in self:
            self[key] = 0

    def record(self) -> None:
        """
        Record the current count

        Effect:
            Records all of the data
        """

        self.data_columns.record(self)

        if self.removal:
            self._reset()

    def refresh(self) -> None:
        """
        Refresh the data in the columns

        Effects:
            clears the columns
            adds current count
        """

        self.data_columns.refresh()
        self.data_columns.record(self)

    def get_data_columns(self) -> hint.data_column_dict:
        """
        Get the data_columns for class

        Returns:
            the data columns
        """

        return self.data_columns.columns()

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


class CountFilter(BaseCount):
    """
    Class to allow for filtering of counts

    Variables:
        dict:
            key:   attribute value
            value: count system

        attr: attribute we are counting

    Methods:
        add:     add agent to count
        sub:     subtract agent from count
        record:  record the count in the data columns
        refresh: refresh the stored values in data columns

        get_data_columns: get the data columns to output
    """

    def add(self, agent: hint.agent) -> None:
        """
        Adds agent to counter

        Args:
            agent: agent to count

        Effects:
            add count of attribute
        """

        value = getattr(agent, self.attr)
        self[value].add(agent)

    def sub(self, agent: hint.agent) -> None:
        """
        Subtracts agent from counter

        Args:
            agent: agent to count

        Effects:
            remove count of attribute
        """

        value = getattr(agent, self.attr)
        self[value].sub(agent)

    def record(self) -> None:
        """
        Record the current count

        Effect:
            Records all of the data
        """

        for count in self.values():
            count.record()

    def refresh(self) -> None:
        """
        Refresh the data in the columns

        Effects:
            clears the columns
            adds current count
        """

        for count in self.values():
            count.refresh()

    def get_data_columns(self) -> hint.data_column_dict:
        """
        Get the data_columns for class

        Returns:
            the data columns
        """

        data = {}

        for attr_value, count in self.items():
            key_prefix   = '{}_{}'.format(self.attr, attr_value)
            data_columns = count.get_data_columns()

            for key_suffix, column in data_columns.items():
                key = '{}_{}'.format(key_prefix, key_suffix)
                data[key] = column

        return data

    @classmethod
    def empty(cls, attr:    str,
                   values:  hint.attr_values,
                   attrs:   hint.attrs) -> 'CountFilter':
        """
        Setup an empty counter

        Args:
            attr:    attribute to count
            values:  values for attribute
            attrs:   dictionary of the sub filters

        Returns:
            a setup class
        """


        attr_list = list(attrs.keys())
        if len(attr_list) == 1:
            attr_value = attr_list.pop(0)
            counts = {value: Count.empty(attr_value,
                                         *attrs[attr_value])
                      for value in values}

        elif len(attr_list) > 1:
            attr_value  = attr_list.pop(0)
            attr_values = attrs[attr_value]
            new_attrs = {attr_key: attrs[attr_key]
                         for attr_key in attr_list}

            counts = {value: cls.empty(attr_value, attr_values[0], new_attrs)
                      for value in values}

        else:
            raise TypeError('Needs data for sub filter')

        return cls(counts, attr)


class Counts(collect.UserDict):
    """
    Class to contain all attribute counts

    Variables:
        - dict:
            key:   attribute
            value: attribute counter

    Methods:
        add:     add agent to count
        sub:     subtract agent from count
        record:  record the count in the data columns
        refresh: refresh the stored values in data columns
        columns: create the data columns for this set of counts

        dataframe: create a dataframe for storage

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

    def refresh(self) -> None:
        """
        Refresh all the stored counts

        Effects:
            starts the stored data over
        """

        for counter in self.values():
            counter.refresh()

    def columns(self) -> hint.data_column_dict:
        """
        Create a dictionary of all data_columns

        Returns:
            dictionary of data columns
        """

        columns = {}
        for count in self.values():
            columns.update(count.get_data_columns())

        return columns

    def dataframe(self) -> hint.dataframe:
        """
        Create a dataframe of the recorded data

        Returns:
            A dataframe of the data
        """

        return pd.DataFrame.from_dict(self.columns())

    def count(self, attr_key: str,
                    attr:     str,
                    values:   hint.attr_values,
                    other:    hint.attr_other) -> None:
        """
        Add count to system

        Args:
            attr_key: key for the storage
            attr:     attribute to count
            values:   values for attribute
            other:    pass in last bit of information

        Effects:
            Adds count to system
        """

        if isinstance(other, bool):
            self[attr_key] = Count.empty(attr, values, other)
        else:
            if len(other) > 0:
                self[attr_key] = CountFilter.empty(attr, values, other)
            else:
                self[attr_key] = Count.empty(attr, values, False)

    @classmethod
    def empty(cls, attrs: hint.attrs_dict) -> 'Counts':
        """
        Setup an empty counter

        Args:
            attrs: attributes to count

        Returns:
            a setup class
        """

        new = cls({})
        for attr_key, attr_filter in attrs.items():
            new.count(attr_key, *attr_filter)

        return new
