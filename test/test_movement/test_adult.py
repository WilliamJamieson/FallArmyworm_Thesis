import unittest      as ut
import unittest.mock as mk

import dataclasses  as dclass
import numpy.random as rnd

import source.keyword as keyword

import source.agents.adult as agent_adult

import source.movement.adult as movement


class AdultTest(agent_adult.Adult):
    """Class to add dynamic values for tests"""

    mass     = mk.MagicMock(spec=float)
    genotype = mk.MagicMock(spec=str)


class TestAdult(ut.TestCase):
    """test the Adult movement class"""

    def setUp(self):
        """Setup the tests"""

        self.movement = mk.MagicMock(spec=callable)

        self.Adult = movement.Adult(self.movement)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Adult, movement.Adult)

        self.assertEqual(self.Adult.movement, self.movement)

        self.assertTrue(dclass.is_dataclass(self.Adult))

    def test__use_movement(self):
        """test if we use the movement system"""

        self.assertTrue(self.Adult._use_movement)

        self.Adult.movement = None
        self.assertFalse(self.Adult._use_movement)

    def test__distance(self):
        """test determine if adult distances"""

        adult = mk.create_autospec(AdultTest, spec_set=True)

        self.assertEqual(self.Adult._distance(adult),
                         self.movement.return_value)
        self.assertEqual(self.movement.call_args_list,
                         [mk.call(adult.mass, adult.genotype)])

    def test__vertex(self):
        """test get the vertex to move to"""

        adult = mk.create_autospec(AdultTest, spec_set=True)

        with mk.patch.object(movement.Adult, '_distance',
                             autospec=True) as mkDistance:
            with mk.patch.object(movement, 'list') as mkList:
                with mk.patch.object(rnd, 'choice') as mkRND:
                    kwargs = {keyword.upper: mkDistance.return_value,
                              keyword.lower: mkDistance.return_value}

                    self.assertEqual(self.Adult._vertex(adult),
                                     mkRND.return_value)
                    self.assertEqual(mkRND.call_args_list,
                                     [mk.call(mkList.return_value)])
                    self.assertEqual(mkList.call_args_list,
                                     [mk.call(adult.vertices.return_value)])
                    self.assertEqual(adult.vertices.call_args_list,
                                     [mk.call(**kwargs)])
                    self.assertEqual(mkDistance.call_args_list,
                                     [mk.call(self.Adult, adult)])

    def test_move(self):
        """test move the adult"""

        adult = mk.create_autospec(AdultTest, spec_set=True)

        with mk.patch.object(movement.Adult, '_use_movement',
                             autospec=True) as mkUse:
            with mk.patch.object(movement.Adult, '_vertex',
                                 autospec=True) as mkVertex:
                mkUse.__get__ = mk.MagicMock(side_effect=[False, True])

                # Test if no movement
                self.Adult.move(adult)
                self.assertEqual(adult.transfer.call_args_list, [])
                self.assertEqual(mkVertex.call_args_list, [])

                # Test if movement
                self.Adult.move(adult)
                self.assertEqual(adult.transfer.call_args_list,
                                 [mk.call(mkVertex.return_value,
                                          keyword.adult_level)])
                self.assertEqual(mkVertex.call_args_list,
                                 [mk.call(self.Adult, adult)])

    def test_setup(self):
        """test setup the class"""

        # Test if have the model
        kwargs = {keyword.adult_movement: self.movement}
        self.Adult = movement.Adult.setup(**kwargs)
        self.assertIsInstance(self.Adult, movement.Adult)
        self.assertEqual(self.Adult.movement, self.movement)

        # Test if have the model
        kwargs = {}
        self.Adult = movement.Adult.setup(**kwargs)
        self.assertIsInstance(self.Adult, movement.Adult)
        self.assertEqual(self.Adult.movement, None)
