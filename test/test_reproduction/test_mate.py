import unittest      as ut
import unittest.mock as mk

import dataclasses  as dclass
import numpy.random as rnd

import source.keyword as keyword

import source.agents.adult as agent_adult

import source.reproduction.mate as mating


class AdultTest(agent_adult.Adult):
    """Class to add dynamic values for tests"""

    mass     = mk.MagicMock(spec=float)
    age      = mk.MagicMock(spec=int)
    genotype = mk.MagicMock(spec=str)
    num_eggs = mk.MagicMock(spec=int)


class TestMate(ut.TestCase):
    """test Mate behavior class"""

    def setUp(self):
        """Setup the tests"""

        self.mating = mk.MagicMock(spec=callable)
        self.radius = mk.MagicMock(spec=callable)

        self.Mate = mating.Mate(self.mating,
                                self.radius)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Mate, mating.Mate)

        self.assertEqual(self.Mate.mating, self.mating)
        self.assertEqual(self.Mate.radius, self.radius)

        self.assertEqual(self.Mate.behavior, keyword.mate)

        self.assertTrue(dclass.is_dataclass(self.Mate))

    def test__use_mating(self):
        """test if we use the mating system"""

        self.assertTrue(self.Mate._use_mating)

        self.Mate.mating = None
        self.assertFalse(self.Mate._use_mating)

    def test__use_radius(self):
        """test if we use the radius system"""

        self.assertTrue(self.Mate._use_radius)

        self.Mate.radius = None
        self.assertFalse(self.Mate._use_radius)
        
    def test__mate_with(self):
        """test mate with the other adult"""

        adult = mk.create_autospec(AdultTest, spec_set=True)
        mate  = mk.create_autospec(AdultTest, spec_set=True)

        self.Mate._mate_with(adult, mate)
        self.assertEqual(adult.set_mate.call_args_list,
                         [mk.call(mate)])
        self.assertEqual(mate.set_mate.call_args_list,
                         [mk.call(adult)])

    def test__bounds(self):
        """test get the bounds on the radius"""

        adult = mk.create_autospec(AdultTest, spec_set=True)

        with mk.patch.object(mating.Mate, '_use_radius',
                             autospec=True) as mkUse:
            mkUse.__get__ = mk.MagicMock(side_effect=[False, True])

            # Test if no radius model
            self.assertEqual(self.Mate._bounds(adult),
                             {keyword.upper: 0,
                              keyword.lower: 0})
            self.assertEqual(self.radius.call_args_list, [])

            # Test if radius model
            self.assertEqual(self.Mate._bounds(adult),
                             {keyword.upper: self.radius.return_value,
                              keyword.lower: 0})
            self.assertEqual(self.radius.call_args_list,
                             [mk.call(adult.mass, adult.genotype)])

    def test__mates(self):
        """test get the adults to mate"""

        adult = mk.create_autospec(AdultTest, spec_set=True)

        bounds = {'test': mk.MagicMock()}

        with mk.patch.object(mating.Mate, '_bounds',
                             autospec=True) as mkBounds:
            mkBounds.return_value = bounds

            self.assertEqual(self.Mate._mates(adult),
                             adult.mates.return_value)
            self.assertEqual(adult.mates.call_args_list,
                             [mk.call(**bounds)])
            self.assertEqual(mkBounds.call_args_list,
                             [mk.call(self.Mate, adult)])

    def test__encounter(self):
        """test determine if we encounter a mate"""

        adult = mk.create_autospec(AdultTest, spec_set=True)
        mates = mk.MagicMock(spec=list)

        with mk.patch.object(mating, 'len') as mkLen:
            self.assertEqual(self.Mate._encounter(adult, mates),
                             self.mating.return_value)
            self.assertEqual(self.mating.call_args_list,
                             [mk.call(mkLen.return_value,
                                      adult.mass, adult.genotype)])
            self.assertEqual(mkLen.call_args_list,
                             [mk.call(mates)])

    def test__perform(self):
        """test perform a mating ritual"""

        adult = mk.create_autospec(AdultTest, spec_set=True)

        with mk.patch.object(mating.Mate, '_mates', autospec=True) as mkMates:
            with mk.patch.object(mating.Mate, '_encounter',
                                 autospec=True) as mkEncounter:
                with mk.patch.object(mating.Mate, '_mate_with',
                                     autospec=True) as mkMate:
                    with mk.patch.object(rnd, 'choice') as mkRND:
                        mkEncounter.side_effect = [False, True]

                        # No encounter
                        self.Mate._perform(adult)
                        self.assertEqual(mkMate.call_args_list, [])
                        self.assertEqual(mkRND.call_args_list, [])
                        self.assertEqual(mkEncounter.call_args_list,
                                         [mk.call(self.Mate,
                                                  adult, mkMates.return_value)])
                        self.assertEqual(mkMates.call_args_list,
                                         [mk.call(self.Mate, adult)])

                        mkEncounter.reset_mock()
                        mkMates.reset_mock()
                        # Has encounter
                        self.Mate._perform(adult)
                        self.assertEqual(mkMate.call_args_list,
                                         [mk.call(adult, mkRND.return_value)])
                        self.assertEqual(mkRND.call_args_list,
                                         [mk.call(mkMates.return_value)])
                        self.assertEqual(mkEncounter.call_args_list,
                                         [mk.call(self.Mate,
                                                  adult, mkMates.return_value)])
                        self.assertEqual(mkMates.call_args_list,
                                         [mk.call(self.Mate, adult)])

    def test_mate(self):
        """test run mate behavior"""

        adult = mk.create_autospec(AdultTest, spec_set=True)

        with mk.patch.object(mating.Mate, '_use_mating',
                             autospec=True) as mkUse:
            with mk.patch.object(mating.Mate, '_perform',
                                 autospec=True) as mkPerform:
                mkUse.__get__ = mk.MagicMock(side_effect=[False, True])

                # Test use is False
                self.Mate.mate(adult)
                self.assertEqual(mkPerform.call_args_list, [])

                # Test use is True
                self.Mate.mate(adult)
                self.assertEqual(mkPerform.call_args_list,
                                 [mk.call(self.Mate, adult)])

    def test_setup(self):
        """test setup the class"""

        # Test if have the models
        kwargs = {keyword.mating:      self.mating,
                  keyword.mate_radius: self.radius}
        self.Mate = mating.Mate.setup(**kwargs)
        self.assertIsInstance(self.Mate, mating.Mate)
        self.assertEqual(self.Mate.mating, self.mating)
        self.assertEqual(self.Mate.radius, self.radius)
        self.assertEqual(self.Mate.behavior, keyword.mate)

        # Test if have no models
        kwargs = {}
        self.Mate = mating.Mate.setup(**kwargs)
        self.assertIsInstance(self.Mate, mating.Mate)
        self.assertEqual(self.Mate.mating, None)
        self.assertEqual(self.Mate.radius, None)
        self.assertEqual(self.Mate.behavior, keyword.mate)
