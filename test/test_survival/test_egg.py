import unittest      as ut
import unittest.mock as mk

import dataclasses as dclass

import source.keyword as keyword

import source.agents.egg as agent_egg

import source.survival.egg as survival


class EggTest(agent_egg.Egg):
    """Class to add dynamic values for tests"""

    mass     = mk.MagicMock(spec=float)
    genotype = mk.MagicMock(spec=str)


class TestEgg(ut.TestCase):
    """test the Egg survival class"""

    def setUp(self):
        """Setup the tests"""

        self.survival = mk.MagicMock(spec=callable)

        self.Egg = survival.Egg(self.survival)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Egg, survival.Egg)

        self.assertEqual(self.Egg.survival, self.survival)

        self.assertTrue(dclass.is_dataclass(self.Egg))

    def test__use_survival(self):
        """test if we use the survival system"""

        self.assertTrue(self.Egg._use_survival)

        self.Egg.survival = None
        self.assertFalse(self.Egg._use_survival)

    def test__survive(self):
        """test determine if egg survives"""

        egg = mk.create_autospec(EggTest, spec_set=True)

        with mk.patch.object(survival.Egg, '_use_survival',
                             autospec=True) as mkUse:
            mkUse.__get__ = mk.MagicMock(side_effect=[False, True])

            # Test when we don't have a model
            self.assertTrue(self.Egg._survive(egg))
            self.assertEqual(self.survival.call_args_list, [])

            # Test when have a model
            self.assertEqual(self.Egg._survive(egg),
                             self.survival.return_value)
            self.assertEqual(self.survival.call_args_list,
                             [mk.call(egg.mass, egg.genotype, egg.bt)])

    def test_survive(self):
        """test run the behavior"""

        egg = mk.create_autospec(EggTest, spec_set=True)

        with mk.patch.object(survival.Egg, '_survive',
                             autospec=True) as mkSurvive:
            mkSurvive.side_effect = [True, False]

            # Test if survives
            self.Egg.survive(egg)
            self.assertEqual(egg.die.call_args_list, [])
            self.assertEqual(mkSurvive.call_args_list,
                             [mk.call(self.Egg, egg)])

            mkSurvive.reset_mock()
            # Test if not survives
            self.Egg.survive(egg)
            self.assertEqual(egg.die.call_args_list,
                             [mk.call(keyword.survival)])
            self.assertEqual(mkSurvive.call_args_list,
                             [mk.call(self.Egg, egg)])

    def test_setup(self):
        """test setup the class"""

        # Test if have the model
        kwargs = {keyword.egg_survival: self.survival}
        self.Egg = survival.Egg.setup(**kwargs)
        self.assertIsInstance(self.Egg, survival.Egg)
        self.assertEqual(self.Egg.survival, self.survival)

        # Test if have the model
        kwargs = {}
        self.Egg = survival.Egg.setup(**kwargs)
        self.assertIsInstance(self.Egg, survival.Egg)
        self.assertEqual(self.Egg.survival, None)
