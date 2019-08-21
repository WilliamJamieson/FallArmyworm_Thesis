import unittest      as ut
import unittest.mock as mk

import collections as collect

import source.keyword as keyword

import source.simulation.models as models


class TestModels(ut.TestCase):
    """test the input Models handling system"""

    def setUp(self):
        """Setup the tests"""

        self.models = {}
        for input_key in keyword.required_inputs:
            self.models[input_key] = mk.MagicMock()
        for _ in range(3):
            self.models[mk.MagicMock(spec=str)] = mk.MagicMock()

        self.Models = models.Models(self.models)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Models, collect.UserDict)
        self.assertIsInstance(self.Models, models.Models)

        self.assertEqual(self.Models,      self.models)
        self.assertEqual(self.Models.data, self.Models)

    def test_add_model(self):
        """test add a model"""

        model = mk.MagicMock()

        # Test add new
        self.assertNotIn(model.model_key, self.Models)
        self.Models.add_model(model)
        self.assertIn(model.model_key, self.Models)
        self.assertEqual(self.Models[model.model_key], model)
        self.assertNotEqual(self.Models, self.models)

        # Test try overwrite
        with self.assertRaisesRegex(TypeError,
                                    'Input data clash: {}'.
                                            format(model.model_key)):
            self.Models.add_model(model)

    def test_add_variable(self):
        """test add a variable to the class"""

        variable_key = mk.MagicMock(spec=str)
        variable     = mk.MagicMock()

        # Test add new
        self.assertNotIn(variable_key, self.Models)
        self.Models.add_variable(variable_key, variable)
        self.assertIn(variable_key, self.Models)
        self.assertEqual(self.Models[variable_key], variable)
        self.assertNotEqual(self.Models, self.models)

        # Test try overwrite
        with self.assertRaisesRegex(TypeError,
                                    'Input data clash: {}'.
                                            format(variable_key)):
            self.Models.add_variable(variable_key, variable)

    def test_check_inputs(self):
        """test check the inputs"""

        self.Models.check_inputs()
        for input_key in keyword.required_inputs:
            del self.Models[input_key]
            with self.assertRaisesRegex(TypeError,
                                        'Required input, {}, not given'.
                                                format(input_key)):
                self.Models.check_inputs()
            self.Models[input_key] = mk.MagicMock()
            self.Models.check_inputs()

    def test_setup(self):
        """test setup the model inputs"""

        args   = (mk.MagicMock() for _ in range(3))
        kwargs = {'test{}'.format(index): mk.MagicMock() for index in range(3)}

        with mk.patch.object(models.Models, 'check_inputs',
                             autospec=True) as mkCheck:
            self.Models = models.Models.setup(*args, **kwargs)
            self.assertEqual(len(self.Models), 6)
            for arg in args:
                self.assertIn(arg.model_key, self.Models)
                self.assertEqual(self.Models[arg.model_key], arg)
            for variable_key, variable in kwargs.items():
                self.assertIn(variable_key, self.Models)
                self.assertEqual(self.Models[variable_key], variable)

            self.assertEqual(mkCheck.call_args_list,
                             [mk.call(self.Models)])
