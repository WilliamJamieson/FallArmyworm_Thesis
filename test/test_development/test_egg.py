import unittest      as ut
import unittest.mock as mk

import dataclasses as dclass

import source.keyword as keyword

import source.agents.egg   as agent_egg
import source.agents.larva as agent_larva

import source.development.egg as development


class EggTest(agent_egg.Egg):
    """Class to add dynamic values for tests"""

    mass     = mk.MagicMock(spec=float)
    genotype = mk.MagicMock(spec=str)
    age      = mk.MagicMock(spec=int)


class TestEgg(ut.TestCase):
    """test the Egg development class"""

    def setUp(self):
        """Setup the tests"""

        self.development = mk.MagicMock(spec=callable)

        self.Egg = development.Egg(self.development)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Egg, development.Egg)

        self.assertEqual(self.Egg.development, self.development)

        self.assertTrue(dclass.is_dataclass(self.Egg))

    def test__use_development(self):
        """test if we use the development system"""

        self.assertTrue(self.Egg._use_development)

        self.Egg.development = None
        self.assertFalse(self.Egg._use_development)

    def test__develop(self):
        """test determine if egg develops"""

        egg = mk.create_autospec(EggTest, spec_set=True)

        with mk.patch.object(development.Egg, '_use_development',
                             autospec=True) as mkUse:
            mkUse.__get__ = mk.MagicMock(side_effect=[False, True])

            # Test when we don't have a model
            self.assertFalse(self.Egg._develop(egg))
            self.assertEqual(self.development.call_args_list, [])

            # Test when have a model
            self.assertEqual(self.Egg._develop(egg),
                             self.development.return_value)
            self.assertEqual(self.development.call_args_list,
                             [mk.call(egg.mass, egg.age, egg.genotype)])

    def test__make_larva(self):
        """test make a larva"""

        egg   = mk.create_autospec(EggTest, spec_set=True)
        larva = mk.create_autospec(agent_larva.Larva, spec_set=True)

        with mk.patch.object(agent_larva.Larva, 'advance',
                             autospec=True) as mkAdvance:
            mkAdvance.return_value = larva

            self.Egg._make_larva(egg)
            self.assertEqual(larva.activate.call_args_list,
                             [mk.call()])
            self.assertEqual(mkAdvance.call_args_list,
                             [mk.call(egg)])

    def test_develop(self):
        """test run development system"""

        egg = mk.create_autospec(EggTest, spec_set=True)

        with mk.patch.object(development.Egg, '_develop',
                             autospec=True) as mkDevelop:
            with mk.patch.object(development.Egg, '_make_larva',
                                 autospec=True) as mkMake:
                mkDevelop.side_effect = [False, True]
                master = mk.MagicMock()
                master.attach_mock(egg,    'egg')
                master.attach_mock(mkMake, 'make')

                # Does not develop
                self.Egg.develop(egg)
                self.assertEqual(mkDevelop.call_args_list,
                                 [mk.call(self.Egg, egg)])
                self.assertEqual(master.mock_calls, [])

                mkDevelop.reset_mock()
                # Does develop
                self.Egg.develop(egg)
                self.assertEqual(mkDevelop.call_args_list,
                                 [mk.call(self.Egg, egg)])
                self.assertEqual(master.mock_calls,
                                 [mk.call.egg.deactivate(),
                                  mk.call.make(egg)])

    def test_setup(self):
        """test setup the class"""

        # Test if have the model
        kwargs = {keyword.egg_development: self.development}
        self.Egg = development.Egg.setup(**kwargs)
        self.assertIsInstance(self.Egg, development.Egg)
        self.assertEqual(self.Egg.development, self.development)

        # Test if have the model
        kwargs = {}
        self.Egg = development.Egg.setup(**kwargs)
        self.assertIsInstance(self.Egg, development.Egg)
        self.assertEqual(self.Egg.development, None)
