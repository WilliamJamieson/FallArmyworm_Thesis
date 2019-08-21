import unittest      as ut
import unittest.mock as mk

import dataclasses as dclass

import source.keyword as keyword

import source.agents.adult as agent_adult

import source.survival.adult as survival


class AdultTest(agent_adult.Adult):
    """Class to add dynamic values for tests"""

    mass     = mk.MagicMock(spec=float)
    genotype = mk.MagicMock(spec=str)


class TestAdult(ut.TestCase):
    """test the Adult survival class"""

    def setUp(self):
        """Setup the tests"""

        self.survival = mk.MagicMock(spec=callable)

        self.Adult = survival.Adult(self.survival)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Adult, survival.Adult)

        self.assertEqual(self.Adult.survival, self.survival)

        self.assertTrue(dclass.is_dataclass(self.Adult))

    def test__use_survival(self):
        """test if we use the survival system"""

        self.assertTrue(self.Adult._use_survival)

        self.Adult.survival = None
        self.assertFalse(self.Adult._use_survival)

    def test__survive(self):
        """test determine if adult survives"""

        adult = mk.create_autospec(AdultTest, spec_set=True)

        with mk.patch.object(survival.Adult, '_use_survival',
                             autospec=True) as mkUse:
            mkUse.__get__ = mk.MagicMock(side_effect=[False, True])

            # Test when we don't have a model
            self.assertTrue(self.Adult._survive(adult))
            self.assertEqual(self.survival.call_args_list, [])

            # Test when have a model
            self.assertEqual(self.Adult._survive(adult),
                             self.survival.return_value)
            self.assertEqual(self.survival.call_args_list,
                             [mk.call(adult.mass, adult.genotype)])

    def test_survive(self):
        """test run the behavior"""

        adult = mk.create_autospec(AdultTest, spec_set=True)

        with mk.patch.object(survival.Adult, '_survive',
                             autospec=True) as mkSurvive:
            mkSurvive.side_effect = [True, False]

            # Test if survives
            self.Adult.survive(adult)
            self.assertEqual(adult.die.call_args_list, [])
            self.assertEqual(mkSurvive.call_args_list,
                             [mk.call(self.Adult, adult)])

            mkSurvive.reset_mock()
            # Test if not survives
            self.Adult.survive(adult)
            self.assertEqual(adult.die.call_args_list,
                             [mk.call(keyword.survival)])
            self.assertEqual(mkSurvive.call_args_list,
                             [mk.call(self.Adult, adult)])

    def test_setup(self):
        """test setup the class"""

        # Test if have the model
        kwargs = {keyword.adult_survival: self.survival}
        self.Adult = survival.Adult.setup(**kwargs)
        self.assertIsInstance(self.Adult, survival.Adult)
        self.assertEqual(self.Adult.survival, self.survival)

        # Test if have the model
        kwargs = {}
        self.Adult = survival.Adult.setup(**kwargs)
        self.assertIsInstance(self.Adult, survival.Adult)
        self.assertEqual(self.Adult.survival, None)
