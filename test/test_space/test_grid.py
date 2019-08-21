import unittest      as ut
import unittest.mock as mk

import dataclasses   as dclass
import numpy         as np
import numpy.testing as utnp

import source.space.graph as graph
import source.space.grid  as grid


class TestGrid(ut.TestCase):
    """test the base Grid graph"""

    def setUp(self):
        """Setup the tests"""

        self.neighborhood = mk.create_autospec(graph.GraphNeighborhood,
                                               spec_set=True)
        self.distance     = mk.create_autospec(graph.GraphDistance,
                                               spec_set=True)
        self.adjacency    = mk.create_autospec(graph.Adjacency,
                                               spec_set=True)

        self.Grid = grid.Grid(self.neighborhood,
                              self.distance,
                              self.adjacency)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Grid, graph.Graph)
        self.assertIsInstance(self.Grid, grid.Grid)

        self.assertEqual(self.Grid.neighborhood, self.neighborhood)
        self.assertEqual(self.Grid.distance,     self.distance)
        self.assertEqual(self.Grid.adjacency,    self.adjacency)

        self.assertTrue(dclass.is_dataclass(self.Grid))

    def test__boundary(self):
        """test get the boundary vertices"""

        bottom, top, left, right = self.Grid._boundary(4, 4)
        self.assertEqual(bottom, [0,   1,  2,  3])
        self.assertEqual(top,    [12, 13, 14, 15])
        self.assertEqual(left,   [0,   4,  8, 12])
        self.assertEqual(right,  [3,   7, 11, 15])

        bottom, top, left, right = self.Grid._boundary(4, 6)
        self.assertEqual(bottom, [0,   1,  2,  3])
        self.assertEqual(top,    [20, 21, 22, 23])
        self.assertEqual(left,   [0,   4,  8, 12, 16, 20])
        self.assertEqual(right,  [3,   7, 11, 15, 19, 23])

        bottom, top, left, right = self.Grid._boundary(6, 4)
        self.assertEqual(bottom, [0,   1,  2,  3,  4,  5])
        self.assertEqual(top,    [18, 19, 20, 21, 22, 23])
        self.assertEqual(left,   [0,   6, 12, 18])
        self.assertEqual(right,  [5,  11, 17, 23])

    def test__upper_indicator(self):
        """test the upper matrix 1 indicator"""

        i = mk.MagicMock(spec=int)
        j = mk.MagicMock(spec=int)
        n = mk.MagicMock(spec=int)
        m = mk.MagicMock(spec=int)

        self.assertIsNone(self.Grid._upper_indicator(i, j, n, m))

    def test__upper_generator(self):
        """test the upper matrix generator"""

        n = mk.MagicMock(spec=int)
        m = mk.MagicMock(spec=int)

        n.__mul__.return_value = 2

        indicator = [True, False, False, True]
        with mk.patch.object(grid.Grid, '_upper_indicator',
                             autospec=True) as mkUpper:
            mkUpper.side_effect = indicator

            self.assertEqual(self.Grid._upper_generator(n, m),
                             [[1, 0],
                              [0, 1]])
            self.assertEqual(mkUpper.call_args_list,
                             [mk.call(self.Grid, 0, 0, n, m),
                              mk.call(self.Grid, 0, 1, n, m),
                              mk.call(self.Grid, 1, 0, n, m),
                              mk.call(self.Grid, 1, 1, n, m)])
            self.assertEqual(n.__mul__.call_args_list,
                             [mk.call(m)])

    def test__upper_torus(self):
        """test adjust upper matrix to be a torus"""

        upper = mk.MagicMock(spec=list)
        n     = mk.MagicMock(spec=int)
        m     = mk.MagicMock(spec=int)

        self.assertIsNone(self.Grid._upper_torus(upper, n, m))

    def test__full(self):
        """test turn upper matrix into full adjacency matrix"""

        upper = mk.MagicMock(spec=list)

        upper_matrix = mk.create_autospec(graph.Adjacency,
                                          spec_set=True)

        with mk.patch.object(graph, 'Adjacency') as mkAdjacency:
            mkAdjacency.return_value = upper_matrix

            self.assertEqual(self.Grid._full(upper),
                             upper_matrix.__add__.return_value)
            self.assertEqual(upper_matrix.__add__.call_args_list,
                             [mk.call(upper_matrix.transpose.return_value)])
            self.assertEqual(mkAdjacency.call_args_list,
                             [mk.call(upper)])
            self.assertEqual(upper_matrix.transpose.call_args_list,
                             [mk.call()])

        # Practical test
        upper = [[0, 1, 0, 1],
                 [0, 0, 1, 0],
                 [0, 0, 0, 1],
                 [0, 0, 0, 0]]
        true_full = [[0, 1, 0, 1],
                     [1, 0, 1, 0],
                     [0, 1, 0, 1],
                     [1, 0, 1, 0]]
        full = self.Grid._full(upper)
        self.assertIsInstance(full, graph.Adjacency)
        utnp.assert_array_equal(full, true_full)

    def test__generator(self):
        """test the grid generator"""

        n = mk.MagicMock(spec=int)
        m = mk.MagicMock(spec=int)

        # test method calls
        with mk.patch.object(grid.Grid, '_upper_generator',
                             autospec=True) as mkUpper:
            with mk.patch.object(grid.Grid, '_upper_torus',
                                 autospec=True) as mkTorus:
                with mk.patch.object(grid.Grid, '_full') as mkFull:
                    # Torus is False
                    self.assertEqual(self.Grid._generator(n, m, False),
                                     mkFull.return_value)
                    self.assertEqual(mkFull.call_args_list,
                                     [mk.call(mkUpper.return_value)])
                    self.assertEqual(mkUpper.call_args_list,
                                     [mk.call(self.Grid, n, m)])
                    self.assertEqual(mkTorus.call_args_list, [])

                    mkUpper.reset_mock()
                    mkFull.reset_mock()
                    # Torus is True
                    self.assertEqual(self.Grid._generator(n, m, True),
                                     mkFull.return_value)
                    self.assertEqual(mkFull.call_args_list,
                                     [mk.call(mkUpper.return_value)])
                    self.assertEqual(mkUpper.call_args_list,
                                     [mk.call(self.Grid, n, m)])
                    self.assertEqual(mkTorus.call_args_list,
                                     [mk.call(self.Grid,
                                              mkUpper.return_value, n, m)])

        # test method call order
        with mk.patch.object(grid.Grid, '_upper_generator') as mkUpper:
            with mk.patch.object(grid.Grid, '_upper_torus') as mkTorus:
                with mk.patch.object(grid.Grid, '_full') as mkFull:
                    master = mk.MagicMock()
                    master.attach_mock(mkUpper, 'upper')
                    master.attach_mock(mkTorus, 'torus')
                    master.attach_mock(mkFull,  'full')

                    # Torus is False
                    adjacency = self.Grid._generator(n, m, False)
                    self.assertEqual(master.mock_calls,
                                     [mk.call.upper(n, m),
                                      mk.call.full(mkUpper.return_value)])
                    self.assertEqual(adjacency, mkFull.return_value)

                    master.reset_mock()
                    # Torus is True
                    adjacency = self.Grid._generator(n, m, True)
                    self.assertEqual(master.mock_calls,
                                     [mk.call.upper(n, m),
                                      mk.call.torus(mkUpper.return_value, n, m),
                                      mk.call.full(mkUpper.return_value)])
                    self.assertEqual(adjacency, mkFull.return_value)

        # test practical
        indicator = [False, True, False, False]
        with mk.patch.object(grid.Grid, '_upper_indicator',
                             autospec=True) as mkUpper:
            mkUpper.side_effect = indicator

            adjacency = self.Grid._generator(2, 1, False)
            self.assertIsInstance(adjacency, graph.Adjacency)
            utnp.assert_array_equal(adjacency, [[0, 1],
                                                [1, 0]])

    def test_grid(self):
        """test generate a grid graph"""

        n     = mk.MagicMock(spec=int)
        m     = mk.MagicMock(spec=int)
        torus = mk.MagicMock(spec=int)

        self.adjacency.dijkstra.return_value = self.distance
        self.distance. convert. return_value = self.neighborhood

        with mk.patch.object(grid.Grid, '_generator') as mkGenerator:
            mkGenerator.return_value = self.adjacency

            self.Grid = grid.Grid.grid(n, m, torus)
            self.assertIsInstance(self.Grid, grid.Grid)
            self.assertEqual(self.Grid.neighborhood, self.neighborhood)
            self.assertEqual(self.Grid.distance,     self.distance)
            self.assertEqual(self.Grid.adjacency,    self.adjacency)

            self.assertEqual(mkGenerator.call_args_list,
                             [mk.call(n, m, torus)])
            self.assertEqual(self.adjacency.dijkstra.call_args_list,
                             [mk.call(False)])
            self.assertEqual(self.distance.convert.call_args_list,
                             [mk.call()])

        # test practical
        indicator = [False, True, False, False]
        with mk.patch.object(grid.Grid, '_upper_indicator',
                             autospec=True) as mkUpper:
            mkUpper.side_effect = indicator

            self.Grid = grid.Grid.grid(2, 1, False)
            self.assertIsInstance(self.Grid, grid.Grid)
            self.assertIsInstance(self.Grid.neighborhood,
                                  graph.GraphNeighborhood)
            self.assertEqual(self.Grid.neighborhood,
                             {0: {0: {0},
                                  1: {1}},
                              1: {0: {1},
                                  1: {0}}})
            self.assertIsInstance(self.Grid.distance, graph.GraphDistance)
            self.assertEqual(self.Grid.distance,
                             {0: {0: 0,
                                  1: 1},
                              1: {0: 1,
                                  1: 0}})
            self.assertIsInstance(self.Grid.adjacency, graph.Adjacency)
            utnp.assert_array_equal(self.Grid.adjacency,
                                    [[0, 1],
                                     [1, 0]])


class TestHexagon(ut.TestCase):
    """test the Hexagon tile grid"""

    def setUp(self):
        """Setup the tests"""

        self.neighborhood = mk.create_autospec(graph.GraphNeighborhood,
                                               spec_set=True)
        self.distance     = mk.create_autospec(graph.GraphDistance,
                                               spec_set=True)
        self.adjacency    = mk.create_autospec(graph.Adjacency,
                                               spec_set=True)

        self.Grid = grid.Hexagon(self.neighborhood,
                                 self.distance,
                                 self.adjacency)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Grid, grid.Grid)
        self.assertIsInstance(self.Grid, grid.Hexagon)

        self.assertEqual(self.Grid.neighborhood, self.neighborhood)
        self.assertEqual(self.Grid.distance,     self.distance)
        self.assertEqual(self.Grid.adjacency,    self.adjacency)

        self.assertTrue(dclass.is_dataclass(self.Grid))

    def test__upper_indicator(self):
        """test the upper matrix 1 indicator"""

        self.assertFalse(self.Grid._upper_indicator(0, 0, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(0, 1, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(0, 2, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(0, 3, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(0, 4, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(0, 5, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(0, 6, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(0, 7, 4, 4))

        self.assertFalse(self.Grid._upper_indicator(1, 0, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(1, 1, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(1, 2, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(1, 3, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(1, 4, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(1, 5, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(1, 6, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(1, 7, 4, 4))

        self.assertFalse(self.Grid._upper_indicator(2, 0, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(2, 1, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(2, 2, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(2, 3, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(2, 4, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(2, 5, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(2, 6, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(2, 7, 4, 4))

        self.assertFalse(self.Grid._upper_indicator(3, 0, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(3, 1, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(3, 2, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(3, 3, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(3, 4, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(3, 5, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(3, 6, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(3, 7, 4, 4))

        self.assertFalse(self.Grid._upper_indicator(4, 0, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(4, 1, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(4, 2, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(4, 3, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(4, 4, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(4, 5, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(4, 6, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(4, 7, 4, 4))

        self.assertFalse(self.Grid._upper_indicator(5, 0, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(5, 1, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(5, 2, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(5, 3, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(5, 4, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(5, 5, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(5, 6, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(5, 7, 4, 4))

        self.assertFalse(self.Grid._upper_indicator(6, 0, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(6, 1, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(6, 2, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(6, 3, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(6, 4, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(6, 5, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(6, 6, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(6, 7, 4, 4))

        self.assertFalse(self.Grid._upper_indicator(7, 0, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(7, 1, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(7, 2, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(7, 3, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(7, 4, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(7, 5, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(7, 6, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(7, 7, 4, 4))

    def test__upper_generator(self):
        """test the upper matrix generator as a practical test"""

        matrix = self.Grid._upper_generator(4, 4)
        correct = [[0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
        self.assertEqual(matrix, correct)

        matrix = self.Grid._upper_generator(4, 2)
        correct = [[0, 1, 0, 0, 1, 0, 0, 0],
                   [0, 0, 1, 0, 1, 1, 0, 0],
                   [0, 0, 0, 1, 0, 1, 1, 0],
                   [0, 0, 0, 0, 0, 0, 1, 1],
                   [0, 0, 0, 0, 0, 1, 0, 0],
                   [0, 0, 0, 0, 0, 0, 1, 0],
                   [0, 0, 0, 0, 0, 0, 0, 1],
                   [0, 0, 0, 0, 0, 0, 0, 0]]
        self.assertEqual(matrix, correct)

        matrix = self.Grid._upper_generator(2, 4)
        correct = [[0, 1, 1, 0, 0, 0, 0, 0],
                   [0, 0, 1, 1, 0, 0, 0, 0],
                   [0, 0, 0, 1, 1, 0, 0, 0],
                   [0, 0, 0, 0, 1, 1, 0, 0],
                   [0, 0, 0, 0, 0, 1, 1, 0],
                   [0, 0, 0, 0, 0, 0, 1, 1],
                   [0, 0, 0, 0, 0, 0, 0, 1],
                   [0, 0, 0, 0, 0, 0, 0, 0]]
        self.assertEqual(matrix, correct)

        matrix = self.Grid._upper_generator(3, 4)
        correct = [[0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
        self.assertEqual(matrix, correct)

    def test__upper_torus(self):
        """test adjust upper matrix to be a torus"""

        zeros = np.zeros((16, 16), dtype=np.int64)
        upper = list(zeros.tolist())
        self.Grid._upper_torus(upper, 4, 4)
        # top-bottom verticals
        self.assertEqual(upper[0][12], 1)
        self.assertEqual(upper[1][13], 1)
        self.assertEqual(upper[2][14], 1)
        self.assertEqual(upper[3][15], 1)
        # left-right horizontals
        self.assertEqual(upper[ 0][ 3], 1)
        self.assertEqual(upper[ 4][ 7], 1)
        self.assertEqual(upper[ 8][11], 1)
        self.assertEqual(upper[12][15], 1)
        # top-bottom angles
        self.assertEqual(upper[0][13], 1)
        self.assertEqual(upper[1][14], 1)
        self.assertEqual(upper[2][15], 1)
        self.assertEqual(upper[3][12], 1)
        # left-right angles
        self.assertEqual(upper[0][7],  1)
        self.assertEqual(upper[4][11], 1)
        self.assertEqual(upper[8][15], 1)
        upper = np.array(upper)
        self.assertEqual(len(upper.nonzero()[0]), 15)
        self.assertEqual(len(upper.nonzero()[1]), 15)

        zeros = np.zeros((12, 12), dtype=np.int64)
        upper = list(zeros.tolist())
        self.Grid._upper_torus(upper, 3, 4)
        # top-bottom verticals
        self.assertEqual(upper[0][ 9], 1)
        self.assertEqual(upper[1][10], 1)
        self.assertEqual(upper[2][11], 1)
        # top-bottom angles
        self.assertEqual(upper[0][10], 1)
        self.assertEqual(upper[1][11], 1)
        self.assertEqual(upper[2][ 9], 1)
        # left-right horizontals
        self.assertEqual(upper[0][ 2], 1)
        self.assertEqual(upper[3][ 5], 1)
        self.assertEqual(upper[6][ 8], 1)
        self.assertEqual(upper[9][11], 1)
        # left-right angles
        self.assertEqual(upper[0][ 5], 1)
        self.assertEqual(upper[3][ 8], 1)
        self.assertEqual(upper[6][11], 1)
        upper = np.array(upper)
        self.assertEqual(len(upper.nonzero()[0]), 13)
        self.assertEqual(len(upper.nonzero()[1]), 13)

        zeros = np.zeros((12, 12), dtype=np.int64)
        upper = list(zeros.tolist())
        self.Grid._upper_torus(upper, 4, 3)
        # top-bottom verticals
        self.assertEqual(upper[0][ 8], 1)
        self.assertEqual(upper[1][ 9], 1)
        self.assertEqual(upper[2][10], 1)
        self.assertEqual(upper[3][11], 1)
        # top-bottom angles
        self.assertEqual(upper[0][ 9], 1)
        self.assertEqual(upper[1][10], 1)
        self.assertEqual(upper[2][11], 1)
        self.assertEqual(upper[3][ 8], 1)
        # left-right horizontals
        self.assertEqual(upper[0][ 3], 1)
        self.assertEqual(upper[4][ 7], 1)
        self.assertEqual(upper[8][11], 1)
        # left-right angles
        self.assertEqual(upper[0][ 7], 1)
        self.assertEqual(upper[4][11], 1)
        upper = np.array(upper)
        self.assertEqual(len(upper.nonzero()[0]), 13)
        self.assertEqual(len(upper.nonzero()[1]), 13)

    def test__generator(self):
        """test the grid generator as a practical test"""

        matrix = self.Grid._generator(4, 4, False)
        correct = np.array([[0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])
        correct += correct.transpose()
        utnp.assert_array_equal(matrix, correct)

        matrix = self.Grid._generator(4, 4, True)
        correct = np.array([[0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0],
                            [0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
                            [0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1],
                            [0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 1],
                            [0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])
        correct += correct.transpose()
        utnp.assert_array_equal(matrix, correct)

        matrix = self.Grid._generator(4, 2, False)
        correct = np.array([[0, 1, 0, 0, 1, 0, 0, 0],
                            [0, 0, 1, 0, 1, 1, 0, 0],
                            [0, 0, 0, 1, 0, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 1, 1],
                            [0, 0, 0, 0, 0, 1, 0, 0],
                            [0, 0, 0, 0, 0, 0, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 1],
                            [0, 0, 0, 0, 0, 0, 0, 0]])
        correct += correct.transpose()
        utnp.assert_array_equal(matrix, correct)

        matrix = self.Grid._generator(4, 2, True)
        correct = np.array([[0, 1, 0, 1, 1, 1, 0, 1],
                            [0, 0, 1, 0, 1, 1, 1, 0],
                            [0, 0, 0, 1, 0, 1, 1, 1],
                            [0, 0, 0, 0, 1, 0, 1, 1],
                            [0, 0, 0, 0, 0, 1, 0, 1],
                            [0, 0, 0, 0, 0, 0, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 1],
                            [0, 0, 0, 0, 0, 0, 0, 0]])
        correct += correct.transpose()
        utnp.assert_array_equal(matrix, correct)

        matrix = self.Grid._generator(2, 4, False)
        correct = np.array([[0, 1, 1, 0, 0, 0, 0, 0],
                            [0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 1, 1, 0, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0],
                            [0, 0, 0, 0, 0, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 1, 1],
                            [0, 0, 0, 0, 0, 0, 0, 1],
                            [0, 0, 0, 0, 0, 0, 0, 0]])
        correct += correct.transpose()
        utnp.assert_array_equal(matrix, correct)

        matrix = self.Grid._generator(2, 4, True)
        correct = np.array([[0, 1, 1, 1, 0, 0, 1, 1],
                            [0, 0, 1, 1, 0, 0, 1, 1],
                            [0, 0, 0, 1, 1, 1, 0, 0],
                            [0, 0, 0, 0, 1, 1, 0, 0],
                            [0, 0, 0, 0, 0, 1, 1, 1],
                            [0, 0, 0, 0, 0, 0, 1, 1],
                            [0, 0, 0, 0, 0, 0, 0, 1],
                            [0, 0, 0, 0, 0, 0, 0, 0]])
        correct += correct.transpose()
        utnp.assert_array_equal(matrix, correct)


class TestSquare(ut.TestCase):
    """test the Square tile grid"""

    def setUp(self):
        """Setup the tests"""

        self.neighborhood = mk.create_autospec(graph.GraphNeighborhood,
                                               spec_set=True)
        self.distance     = mk.create_autospec(graph.GraphDistance,
                                               spec_set=True)
        self.adjacency    = mk.create_autospec(graph.Adjacency,
                                               spec_set=True)

        self.Grid = grid.Square(self.neighborhood,
                                self.distance,
                                self.adjacency)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Grid, grid.Grid)
        self.assertIsInstance(self.Grid, grid.Square)

        self.assertEqual(self.Grid.neighborhood, self.neighborhood)
        self.assertEqual(self.Grid.distance,     self.distance)
        self.assertEqual(self.Grid.adjacency,    self.adjacency)

        self.assertTrue(dclass.is_dataclass(self.Grid))

    def test__upper_indicator(self):
        """test the upper matrix 1 indicator"""

        self.assertFalse(self.Grid._upper_indicator(0, 0, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(0, 1, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(0, 2, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(0, 3, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(0, 4, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(0, 5, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(0, 6, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(0, 7, 4, 4))

        self.assertFalse(self.Grid._upper_indicator(1, 0, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(1, 1, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(1, 2, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(1, 3, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(1, 4, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(1, 5, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(1, 6, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(1, 7, 4, 4))

        self.assertFalse(self.Grid._upper_indicator(2, 0, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(2, 1, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(2, 2, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(2, 3, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(2, 4, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(2, 5, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(2, 6, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(2, 7, 4, 4))

        self.assertFalse(self.Grid._upper_indicator(3, 0, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(3, 1, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(3, 2, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(3, 3, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(3, 4, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(3, 5, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(3, 6, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(3, 7, 4, 4))

    def test__upper_torus(self):
        """test adjust upper matrix to be a torus"""

        zeros = np.zeros((16, 16), dtype=np.int64)
        upper = list(zeros.tolist())
        self.Grid._upper_torus(upper, 4, 4)
        self.assertEqual(upper[ 0][12], 1)
        self.assertEqual(upper[ 1][13], 1)
        self.assertEqual(upper[ 2][14], 1)
        self.assertEqual(upper[ 3][15], 1)
        self.assertEqual(upper[ 0][ 3], 1)
        self.assertEqual(upper[ 4][ 7], 1)
        self.assertEqual(upper[ 8][11], 1)
        self.assertEqual(upper[12][15], 1)
        upper = np.array(upper)
        self.assertEqual(len(upper.nonzero()[0]), 8)
        self.assertEqual(len(upper.nonzero()[1]), 8)

        zeros = np.zeros((12, 12), dtype=np.int64)
        upper = list(zeros.tolist())
        self.Grid._upper_torus(upper, 3, 4)
        self.assertEqual(upper[ 0][ 9], 1)
        self.assertEqual(upper[ 1][10], 1)
        self.assertEqual(upper[ 2][11], 1)
        self.assertEqual(upper[ 0][ 2], 1)
        self.assertEqual(upper[ 3][ 5], 1)
        self.assertEqual(upper[ 6][ 8], 1)
        self.assertEqual(upper[ 9][11], 1)
        upper = np.array(upper)
        self.assertEqual(len(upper.nonzero()[0]), 7)
        self.assertEqual(len(upper.nonzero()[1]), 7)

        zeros = np.zeros((12, 12), dtype=np.int64)
        upper = list(zeros.tolist())
        self.Grid._upper_torus(upper, 4, 3)
        self.assertEqual(upper[ 0][ 8], 1)
        self.assertEqual(upper[ 1][ 9], 1)
        self.assertEqual(upper[ 2][10], 1)
        self.assertEqual(upper[ 3][11], 1)
        self.assertEqual(upper[ 0][ 3], 1)
        self.assertEqual(upper[ 4][ 7], 1)
        self.assertEqual(upper[ 8][11], 1)
        upper = np.array(upper)
        self.assertEqual(len(upper.nonzero()[0]), 7)
        self.assertEqual(len(upper.nonzero()[1]), 7)

    def test__generator(self):
        """test the grid generator as a practical test"""

        matrix = self.Grid._generator(4, 4, False)
        correct = np.array([[0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])
        correct += correct.transpose()
        utnp.assert_array_equal(matrix, correct)

        matrix = self.Grid._generator(4, 4, True)
        correct = np.array([[0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                            [0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
                            [0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
                            [0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])
        correct += correct.transpose()
        utnp.assert_array_equal(matrix, correct)


class TestMoore(ut.TestCase):
    """test the Moore tile grid"""

    def setUp(self):
        """Setup the tests"""

        self.neighborhood = mk.create_autospec(graph.GraphNeighborhood,
                                               spec_set=True)
        self.distance     = mk.create_autospec(graph.GraphDistance,
                                               spec_set=True)
        self.adjacency    = mk.create_autospec(graph.Adjacency,
                                               spec_set=True)

        self.Grid = grid.Moore(self.neighborhood,
                               self.distance,
                               self.adjacency)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Grid, grid.Grid)
        self.assertIsInstance(self.Grid, grid.Moore)

        self.assertEqual(self.Grid.neighborhood, self.neighborhood)
        self.assertEqual(self.Grid.distance,     self.distance)
        self.assertEqual(self.Grid.adjacency,    self.adjacency)

        self.assertTrue(dclass.is_dataclass(self.Grid))

    def test__upper_indicator(self):
        """test the upper matrix 1 indicator"""

        self.assertFalse(self.Grid._upper_indicator(0, 0, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(0, 1, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(0, 2, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(0, 3, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(0, 4, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(0, 5, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(0, 6, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(0, 7, 4, 4))

        self.assertFalse(self.Grid._upper_indicator(1, 0, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(1, 1, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(1, 2, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(1, 3, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(1, 4, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(1, 5, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(1, 6, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(1, 7, 4, 4))

        self.assertFalse(self.Grid._upper_indicator(2, 0, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(2, 1, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(2, 2, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(2, 3, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(2, 4, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(2, 5, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(2, 6, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(2, 7, 4, 4))

        self.assertFalse(self.Grid._upper_indicator(3, 0, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(3, 1, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(3, 2, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(3, 3, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(3, 4, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(3, 5, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(3, 6, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(3, 7, 4, 4))

    def test__upper_torus(self):
        """test adjust upper matrix to be a torus"""

        zeros = np.zeros((16, 16), dtype=np.int64)
        upper = list(zeros.tolist())
        self.Grid._upper_torus(upper, 4, 4)
        # Vertical
        self.assertEqual(upper[ 0][12], 1)
        self.assertEqual(upper[ 1][13], 1)
        self.assertEqual(upper[ 2][14], 1)
        self.assertEqual(upper[ 3][15], 1)
        # Vertical left
        self.assertEqual(upper[ 0][13], 1)
        self.assertEqual(upper[ 1][14], 1)
        self.assertEqual(upper[ 2][15], 1)
        self.assertEqual(upper[ 3][12], 1)
        # Vertical right
        self.assertEqual(upper[ 0][15], 1)
        self.assertEqual(upper[ 1][12], 1)
        self.assertEqual(upper[ 2][13], 1)
        self.assertEqual(upper[ 3][14], 1)
        # Horizontal
        self.assertEqual(upper[ 0][ 3], 1)
        self.assertEqual(upper[ 4][ 7], 1)
        self.assertEqual(upper[ 8][11], 1)
        self.assertEqual(upper[12][15], 1)
        # Horizontal left
        self.assertEqual(upper[ 0][ 7], 1)
        self.assertEqual(upper[ 4][11], 1)
        self.assertEqual(upper[ 8][15], 1)
        # Horizontal left
        self.assertEqual(upper[ 0][ 3], 1)
        self.assertEqual(upper[ 4][ 7], 1)
        self.assertEqual(upper[ 8][11], 1)
        upper = np.array(upper)
        self.assertEqual(len(upper.nonzero()[0]), 22)
        self.assertEqual(len(upper.nonzero()[1]), 22)

        zeros = np.zeros((12, 12), dtype=np.int64)
        upper = list(zeros.tolist())
        self.Grid._upper_torus(upper, 3, 4)
        # Vertical
        self.assertEqual(upper[ 0][ 9], 1)
        self.assertEqual(upper[ 1][10], 1)
        self.assertEqual(upper[ 2][11], 1)
        # Vertical left
        self.assertEqual(upper[ 0][10], 1)
        self.assertEqual(upper[ 1][11], 1)
        self.assertEqual(upper[ 2][ 9], 1)
        # Vertical right
        self.assertEqual(upper[ 0][11], 1)
        self.assertEqual(upper[ 1][ 9], 1)
        self.assertEqual(upper[ 2][10], 1)
        # Horizontal
        self.assertEqual(upper[ 0][ 2], 1)
        self.assertEqual(upper[ 3][ 5], 1)
        self.assertEqual(upper[ 6][ 8], 1)
        self.assertEqual(upper[ 9][11], 1)
        # Horizontal left
        self.assertEqual(upper[ 0][ 5], 1)
        self.assertEqual(upper[ 3][ 8], 1)
        self.assertEqual(upper[ 6][11], 1)
        # Horizontal right
        self.assertEqual(upper[ 0][11], 1)
        self.assertEqual(upper[ 3][ 2], 1)
        self.assertEqual(upper[ 6][ 8], 1)
        upper = np.array(upper)
        self.assertEqual(len(upper.nonzero()[0]), 19)
        self.assertEqual(len(upper.nonzero()[1]), 19)

        zeros = np.zeros((12, 12), dtype=np.int64)
        upper = list(zeros.tolist())
        self.Grid._upper_torus(upper, 4, 3)
        # Vertical
        self.assertEqual(upper[ 0][ 8], 1)
        self.assertEqual(upper[ 1][ 9], 1)
        self.assertEqual(upper[ 2][10], 1)
        self.assertEqual(upper[ 3][11], 1)
        # Vertical left
        self.assertEqual(upper[ 0][ 9], 1)
        self.assertEqual(upper[ 1][10], 1)
        self.assertEqual(upper[ 2][11], 1)
        self.assertEqual(upper[ 3][ 8], 1)
        # Vertical right
        self.assertEqual(upper[ 0][11], 1)
        self.assertEqual(upper[ 1][ 8], 1)
        self.assertEqual(upper[ 2][ 9], 1)
        self.assertEqual(upper[ 3][10], 1)
        # Horizontal
        self.assertEqual(upper[ 0][ 3], 1)
        self.assertEqual(upper[ 4][ 7], 1)
        self.assertEqual(upper[ 8][11], 1)
        # Horizontal left
        self.assertEqual(upper[ 0][ 7], 1)
        self.assertEqual(upper[ 4][11], 1)
        # Horizontal right
        self.assertEqual(upper[ 0][11], 1)
        self.assertEqual(upper[ 4][ 7], 1)
        upper = np.array(upper)
        self.assertEqual(len(upper.nonzero()[0]), 19)
        self.assertEqual(len(upper.nonzero()[1]), 19)

    def test__generator(self):
        """test the grid generator as a practical test"""

        matrix = self.Grid._generator(4, 4, False)
        correct = np.array([[0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])
        correct += correct.transpose()
        utnp.assert_array_equal(matrix, correct)

        matrix = self.Grid._generator(4, 4, True)
        correct = np.array([[0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1],
                            [0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0],
                            [0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1],
                            [0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 1, 1],
                            [0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])
        correct += correct.transpose()
        utnp.assert_array_equal(matrix, correct)


class TestTriangle(ut.TestCase):
    """test the Triangle tile grid"""

    def setUp(self):
        """Setup the tests"""

        self.neighborhood = mk.create_autospec(graph.GraphNeighborhood,
                                               spec_set=True)
        self.distance     = mk.create_autospec(graph.GraphDistance,
                                               spec_set=True)
        self.adjacency    = mk.create_autospec(graph.Adjacency,
                                               spec_set=True)

        self.Grid = grid.Triangle(self.neighborhood,
                                  self.distance,
                                  self.adjacency)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Grid, grid.Grid)
        self.assertIsInstance(self.Grid, grid.Triangle)

        self.assertEqual(self.Grid.neighborhood, self.neighborhood)
        self.assertEqual(self.Grid.distance,     self.distance)
        self.assertEqual(self.Grid.adjacency,    self.adjacency)

        self.assertTrue(dclass.is_dataclass(self.Grid))

    def test__upper_indicator(self):
        """test the upper matrix 1 indicator"""

        self.assertFalse(self.Grid._upper_indicator(0, 0, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(0, 1, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(0, 2, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(0, 3, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(0, 4, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(0, 5, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(0, 6, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(0, 7, 4, 4))

        self.assertFalse(self.Grid._upper_indicator(1, 0, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(1, 1, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(1, 2, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(1, 3, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(1, 4, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(1, 5, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(1, 6, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(1, 7, 4, 4))

        self.assertFalse(self.Grid._upper_indicator(2, 0, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(2, 1, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(2, 2, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(2, 3, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(2, 4, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(2, 5, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(2, 6, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(2, 7, 4, 4))

        self.assertFalse(self.Grid._upper_indicator(3, 0, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(3, 1, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(3, 2, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(3, 3, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(3, 4, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(3, 5, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(3, 6, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(3, 7, 4, 4))

        self.assertFalse(self.Grid._upper_indicator(4,  0, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(4,  1, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(4,  2, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(4,  3, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(4,  4, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(4,  5, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(4,  6, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(4,  7, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(4,  8, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(4,  9, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(4, 10, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(4, 11, 4, 4))

        self.assertFalse(self.Grid._upper_indicator(5,  0, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(5,  1, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(5,  2, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(5,  3, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(5,  4, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(5,  5, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(5,  6, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(5,  7, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(5,  8, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(5,  9, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(5, 10, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(5, 11, 4, 4))

        self.assertFalse(self.Grid._upper_indicator(6,  0, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(6,  1, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(6,  2, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(6,  3, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(6,  4, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(6,  5, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(6,  6, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(6,  7, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(6,  8, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(6,  9, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(6, 10, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(6, 11, 4, 4))

        self.assertFalse(self.Grid._upper_indicator(7,  0, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(7,  1, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(7,  2, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(7,  3, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(7,  4, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(7,  5, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(7,  6, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(7,  7, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(7,  8, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(7,  9, 4, 4))
        self.assertFalse(self.Grid._upper_indicator(7, 10, 4, 4))
        self.assertTrue( self.Grid._upper_indicator(7, 11, 4, 4))

    def test__upper_torus(self):
        """test adjust upper matrix to be a torus"""

        zeros = np.zeros((16, 16), dtype=np.int64)
        upper = list(zeros.tolist())
        self.Grid._upper_torus(upper, 4, 4)
        # Vertical
        self.assertEqual(upper[ 1][13], 1)
        self.assertEqual(upper[ 3][15], 1)
        # Horizontal
        self.assertEqual(upper[ 0][ 3], 1)
        self.assertEqual(upper[ 4][ 7], 1)
        self.assertEqual(upper[ 8][11], 1)
        self.assertEqual(upper[12][15], 1)
        upper = np.array(upper)
        self.assertEqual(len(upper.nonzero()[0]), 6)
        self.assertEqual(len(upper.nonzero()[1]), 6)

        zeros = np.zeros((12, 12), dtype=np.int64)
        upper = list(zeros.tolist())
        with self.assertRaisesRegex(ValueError, 'n must be even'):
            self.Grid._upper_torus(upper, 3, 4)

        zeros = np.zeros((12, 12), dtype=np.int64)
        upper = list(zeros.tolist())
        self.Grid._upper_torus(upper, 4, 3)
        # Vertical
        self.assertEqual(upper[ 0][ 8], 1)
        self.assertEqual(upper[ 2][10], 1)
        # Horizontal
        self.assertEqual(upper[ 0][ 3], 1)
        self.assertEqual(upper[ 4][ 7], 1)
        self.assertEqual(upper[ 8][11], 1)
        upper = np.array(upper)
        self.assertEqual(len(upper.nonzero()[0]), 5)
        self.assertEqual(len(upper.nonzero()[1]), 5)

    def test__generator(self):
        """test the grid generator as a practical test"""

        matrix = self.Grid._generator(4, 4, False)
        correct = np.array([[0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])
        correct += correct.transpose()
        utnp.assert_array_equal(matrix, correct)

        matrix = self.Grid._generator(4, 4, True)
        correct = np.array([[0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
                            [0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                            [0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])
        correct += correct.transpose()
        utnp.assert_array_equal(matrix, correct)

        matrix = self.Grid._generator(4, 3, False)
        correct = np.array([[0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])
        correct += correct.transpose()
        utnp.assert_array_equal(matrix, correct)

        matrix = self.Grid._generator(4, 3, True)
        correct = np.array([[0, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0],
                            [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])
        correct += correct.transpose()
        utnp.assert_array_equal(matrix, correct)
