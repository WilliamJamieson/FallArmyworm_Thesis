import collections as collect

import source.keyword as keyword


class Models(collect.UserDict):
    """
    Class to handle the input mathematical models

    Variables:
        - dict:
            key: model_key
            value: mathematical model

    Methods:
        add_model:    add model
        add_variable: add a variable
        check_inputs: check that all the requirements are in place

    Constructors:
        setup: setup the model from data
    """

    def add_model(self, model) -> None:
        """
        Add the model to the system

        Args:
            model: the mathematical model

        Effects:
            Add model to system
        """

        if model.model_key not in self:
            self[model.model_key] = model
        else:
            raise TypeError('Input data clash: {}'.format(model.model_key))

    def add_variable(self, variable_key: str,
                           variable) -> None:
        """
        Add the fixed variable under the keyword
        Args:
            variable_key: keyword for variable
            variable:     variable value

        Effects:
            Add variable to system
        """

        if variable_key not in self:
            self[variable_key] = variable
        else:
            raise TypeError('Input data clash: {}'.format(variable_key))

    def check_inputs(self) -> None:
        """
        Run check on the inputs

        Raises:
            TypeError for any input not in system
        """

        for input_key in keyword.required_inputs:
            if input_key not in self:
                raise TypeError('Required input, {}, not given'.
                                format(input_key))

    @classmethod
    def setup(cls, *args, **kwargs) -> 'Models':
        """
        Add all the input data to the system

        Args:
            *args:    the input mathematical models
            **kwargs: the input variables

        Returns:
            setup class
        """

        new = cls()
        for model in args:
            new.add_model(model)

        for variable_key, variable in kwargs.items():
            new.add_variable(variable_key, variable)

        new.check_inputs()

        return new
