import unittest      as ut
import unittest.mock as mk

import dataclasses  as dclass
import numpy.random as rnd

import source.keyword as keyword

import source.agents.larva as agent_larva

import source.movement.larva as movement


class LarvaTest(agent_larva.Larva):
    """Class to add dynamic values for tests"""

    mass     = mk.MagicMock(spec=float)
    genotype = mk.MagicMock(spec=str)


class TestLarva(ut.TestCase):
    """test the Larva movement class"""

    def setUp(self):
        """Setup the tests"""

        self.movement = mk.MagicMock(spec=callable)

        self.Larva = movement.Larva(self.movement)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Larva, movement.Larva)

        self.assertEqual(self.Larva.movement, self.movement)

        self.assertEqual(self.Larva.behavior, keyword.movement_larva)

        self.assertTrue(dclass.is_dataclass(self.Larva))

    def test__use_movement(self):
        """test if we use the movement system"""

        self.assertTrue(self.Larva._use_movement)

        self.Larva.movement = None
        self.assertFalse(self.Larva._use_movement)

    def test__distance(self):
        """test determine if larva distances"""

        larva = mk.create_autospec(LarvaTest, spec_set=True)

        self.assertEqual(self.Larva._distance(larva),
                         self.movement.return_value)
        self.assertEqual(self.movement.call_args_list,
                         [mk.call(larva.mass, larva.genotype)])

    def test__vertex(self):
        """test get the vertex to move to"""

        larva = mk.create_autospec(LarvaTest, spec_set=True)

        with mk.patch.object(movement.Larva, '_distance',
                             autospec=True) as mkDistance:
            with mk.patch.object(movement, 'list') as mkList:
                with mk.patch.object(rnd, 'choice') as mkRND:
                    kwargs = {keyword.upper: mkDistance.return_value,
                              keyword.lower: mkDistance.return_value}

                    self.assertEqual(self.Larva._vertex(larva),
                                     mkRND.return_value)
                    self.assertEqual(mkRND.call_args_list,
                                     [mk.call(mkList.return_value)])
                    self.assertEqual(mkList.call_args_list,
                                     [mk.call(larva.vertices.return_value)])
                    self.assertEqual(larva.vertices.call_args_list,
                                     [mk.call(**kwargs)])
                    self.assertEqual(mkDistance.call_args_list,
                                     [mk.call(self.Larva, larva)])

    def test_move(self):
        """test move the larva"""

        larva = mk.create_autospec(LarvaTest, spec_set=True)

        with mk.patch.object(movement.Larva, '_use_movement',
                             autospec=True) as mkUse:
            with mk.patch.object(movement.Larva, '_vertex',
                                 autospec=True) as mkVertex:
                mkUse.__get__ = mk.MagicMock(side_effect=[False, True])

                # Test if no movement
                self.Larva.move(larva)
                self.assertEqual(larva.transfer.call_args_list, [])
                self.assertEqual(mkVertex.call_args_list, [])

                # Test if movement
                self.Larva.move(larva)
                self.assertEqual(larva.transfer.call_args_list,
                                 [mk.call(mkVertex.return_value,
                                          keyword.larva_level)])
                self.assertEqual(mkVertex.call_args_list,
                                 [mk.call(self.Larva, larva)])

    def test_setup(self):
        """test setup the class"""

        # Test if have the model
        kwargs = {keyword.larva_movement: self.movement}
        self.Larva = movement.Larva.setup(**kwargs)
        self.assertIsInstance(self.Larva, movement.Larva)
        self.assertEqual(self.Larva.movement, self.movement)
        self.assertEqual(self.Larva.behavior, keyword.movement_larva)

        # Test if have the model
        kwargs = {}
        self.Larva = movement.Larva.setup(**kwargs)
        self.assertIsInstance(self.Larva, movement.Larva)
        self.assertEqual(self.Larva.movement, None)
        self.assertEqual(self.Larva.behavior, keyword.movement_larva)
