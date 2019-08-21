import unittest      as ut
import unittest.mock as mk

import collections   as collect
import dataclasses   as dclass
import numpy         as np
import numpy.testing as utnp
import pickle        as pickle

import source.keyword as keyword

import source.space.graph as graph


class TestVertexNeighborhood(ut.TestCase):
    """test the VertexNeighborhood class"""

    def setUp(self):
        """Setup the tests"""

        self.vertex = mk.MagicMock(spec=int)

        self.neighborhood = {}
        for index in range(3):
            neighborhood = set()
            for _ in range(3):
                neighborhood.add(mk.MagicMock(spec=int))
            self.neighborhood[index] = neighborhood

        self.Neighborhood = graph.VertexNeighborhood(self.vertex,
                                                     self.neighborhood)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Neighborhood, collect.UserDict)
        self.assertIsInstance(self.Neighborhood, graph.VertexNeighborhood)

        self.assertEqual(self.Neighborhood.vertex, self.vertex)

        for vertex, neighborhood in self.neighborhood.items():
            self.assertIn(vertex, self.Neighborhood)
            self.assertEqual(self.Neighborhood[vertex], neighborhood)
        for vertex, neighborhood in self.Neighborhood.items():
            self.assertIn(vertex, self.neighborhood)
            self.assertEqual(self.neighborhood[vertex], neighborhood)
        self.assertEqual(self.neighborhood, self.Neighborhood)

    def test_minimum(self):
        """test get minimum vertex distance"""

        # Call tests
        with mk.patch.object(graph.VertexNeighborhood, 'keys',
                             autospec=True) as mkKeys:
            with mk.patch('builtins.min') as mkMax:
                self.assertEqual(self.Neighborhood.minimum,
                                 mkMax.return_value)
                self.assertEqual(mkMax.call_args_list,
                                 [mk.call(mkKeys.return_value)])
                self.assertEqual(mkKeys.call_args_list,
                                 [mk.call(self.neighborhood)])

        # Practical test
        self.assertEqual(self.Neighborhood.minimum, 0)

    def test_maximum(self):
        """test get maximum vertex distance"""

        # Call tests
        with mk.patch.object(graph.VertexNeighborhood, 'keys',
                             autospec=True) as mkKeys:
            with mk.patch('builtins.max') as mkMax:
                self.assertEqual(self.Neighborhood.maximum,
                                 mkMax.return_value)
                self.assertEqual(mkMax.call_args_list,
                                 [mk.call(mkKeys.return_value)])
                self.assertEqual(mkKeys.call_args_list,
                                 [mk.call(self.neighborhood)])

        # Practical test
        self.assertEqual(self.Neighborhood.maximum, 2)

    def test_add(self):
        """test set an vertex at a distance"""

        # Existing distance set
        vertices = {}
        for distance in self.neighborhood:
            vertices[distance] = mk.MagicMock(spec=int)

        for distance, vertex in vertices.items():
            self.assertNotIn(vertex, self.Neighborhood[distance])
            self.Neighborhood.add(distance, vertex)
            self.assertIn(vertex, self.Neighborhood[distance])
        for distance, neighborhood in self.Neighborhood.items():
            self.assertIn(vertices[distance], neighborhood)
            self.assertEqual(len(neighborhood), 4)
        self.assertEqual(len(self.Neighborhood), 3)

        # New distance set
        vertices = {}
        for _ in range(3):
            vertices[mk.MagicMock(spec=float)] = mk.MagicMock(spec=int)

        for distance, vertex in vertices.items():
            self.assertNotIn(distance, self.Neighborhood)
            self.Neighborhood.add(distance, vertex)
            self.assertIn(distance, self.Neighborhood)
            self.assertEqual(self.Neighborhood[distance], {vertex})
            self.assertEqual(len(self.Neighborhood[distance]), 1)
        self.assertEqual(len(self.Neighborhood), 6)

    def test__convert(self):
        """test convert a distance to those within the system"""

        for dist in self.Neighborhood:
            # Test distances above and below the distances in the class
            self.assertEqual(dist, self.Neighborhood._convert(dist))
            self.assertEqual(dist, self.Neighborhood._convert(dist + 0.1))
            self.assertEqual(dist, self.Neighborhood._convert(dist + 0.2))
            self.assertEqual(dist, self.Neighborhood._convert(dist + 0.3))
            self.assertEqual(dist, self.Neighborhood._convert(dist + 0.4))
            self.assertEqual(dist, self.Neighborhood._convert(dist + 0.5))
            self.assertEqual(dist, self.Neighborhood._convert(dist - 0.1))
            self.assertEqual(dist, self.Neighborhood._convert(dist - 0.2))
            self.assertEqual(dist, self.Neighborhood._convert(dist - 0.3))

            # Test going above the distances in the class
            self.assertEqual(self.Neighborhood.maximum, self.Neighborhood.
                             _convert(dist + self.Neighborhood.maximum))

            # Test going below the distances in the class
            self.assertEqual(self.Neighborhood.minimum, self.Neighborhood.
                             _convert(dist - self.Neighborhood.maximum))

    def test__upper_lower(self):
        """test get the upper and lower bounds for neighborhood"""

        upper = mk.MagicMock(spec=float)
        lower = mk.MagicMock(spec=float)

        with mk.patch.object(graph.VertexNeighborhood, '_convert',
                             autospec=True) as mkConvert:
            # Pass in both
            kwargs = {keyword.upper: upper,
                      keyword.lower: lower}
            convert = [mk.MagicMock(spec=float), mk.MagicMock(spec=float)]
            mkConvert.side_effect = convert
            self.assertEqual(self.Neighborhood._upper_lower(**kwargs),
                             (convert[0], convert[1]))
            self.assertEqual(mkConvert.call_args_list,
                             [mk.call(self.Neighborhood, upper),
                              mk.call(self.Neighborhood, lower)])

            mkConvert.reset_mock()
            # Pass in only upper
            kwargs = {keyword.upper: upper}
            convert = [mk.MagicMock(spec=float)]
            mkConvert.side_effect = convert
            self.assertEqual(self.Neighborhood._upper_lower(**kwargs),
                             (convert[0], 0))
            self.assertEqual(mkConvert.call_args_list,
                             [mk.call(self.Neighborhood, upper)])

            mkConvert.reset_mock()
            # Pass in only lower
            kwargs = {keyword.lower: lower}
            convert = [mk.MagicMock(spec=float)]
            mkConvert.side_effect = convert
            self.assertEqual(self.Neighborhood._upper_lower(**kwargs),
                             (np.inf, convert[0]))
            self.assertEqual(mkConvert.call_args_list,
                             [mk.call(self.Neighborhood, lower)])

            mkConvert.reset_mock()
            # Pass in nothing
            self.assertEqual(self.Neighborhood._upper_lower(),
                             (np.inf, 0))
            self.assertEqual(mkConvert.call_args_list, [])

    def test__append_distance(self):
        """test append correct distances"""

        distance = mk.MagicMock(spec=float)
        upper    = mk.MagicMock(spec=float)
        lower    = mk.MagicMock(spec=float)
        union    = mk.MagicMock(spec=set)
        vertices = mk.MagicMock(spec=set)

        lower_test = [False, True,  True, True]
        upper_test = [       False, True, True]

        lower.   __le__.side_effect = lower_test
        distance.__le__.side_effect = upper_test

        # Less than lower
        self.assertEqual(self.Neighborhood.
                         _append_distance(distance, upper, lower,
                                          union, vertices),
                         vertices)
        self.assertEqual(vertices.union.call_args_list, [])
        self.assertEqual(lower.   __le__.call_args_list, [mk.call(distance)])
        self.assertEqual(distance.__le__.call_args_list, [])

        lower.__le__.reset_mock()
        # Greater than upper
        self.assertEqual(self.Neighborhood.
                         _append_distance(distance, upper, lower,
                                          union, vertices),
                         vertices)
        self.assertEqual(vertices.union.call_args_list, [])
        self.assertEqual(lower.   __le__.call_args_list, [mk.call(distance)])
        self.assertEqual(distance.__le__.call_args_list, [mk.call(upper)])

        lower.   __le__.reset_mock()
        distance.__le__.reset_mock()
        # Correct bounds
        self.assertEqual(self.Neighborhood.
                         _append_distance(distance, upper, lower,
                                          union, vertices),
                         vertices.union.return_value)
        self.assertEqual(vertices.union.call_args_list,
                         [mk.call(union)])
        self.assertEqual(lower.   __le__.call_args_list, [mk.call(distance)])
        self.assertEqual(distance.__le__.call_args_list, [mk.call(upper)])

        lower.   __le__.reset_mock()
        distance.__le__.reset_mock()
        vertices = {mk.MagicMock(), mk.MagicMock()}
        union    = {mk.MagicMock(), mk.MagicMock()}
        # Test union
        result = self.Neighborhood._append_distance(distance, upper, lower,
                                                    union, vertices)
        self.assertNotEqual(result, vertices)
        self.assertNotEqual(result, union)
        self.assertEqual(len(result), 4)
        for vertex in vertices:
            self.assertIn(vertex, result)
        for vertex in union:
            self.assertIn(vertex, result)
        for vertex in vertices:
            self.assertTrue((vertex in vertices) or (vertex in union))

    def test_neighborhood(self):
        """test get the neighborhood"""

        kwargs = {'test': mk.MagicMock()}

        upper = mk.MagicMock(spec=float)
        lower = mk.MagicMock(spec=float)
        upper_lower = (upper, lower)

        vertices = []
        for _ in self.Neighborhood:
            vertices.append(mk.MagicMock(spec=set))
        self.assertEqual(len(vertices), 3)

        with mk.patch.object(graph.VertexNeighborhood, '_upper_lower',
                             autospec=True) as mkGet:
            with mk.patch.object(graph.VertexNeighborhood,
                                 '_append_distance') as mkAppend:
                mkGet.return_value   = upper_lower
                mkAppend.side_effect = vertices

                self.assertEqual(self.Neighborhood.neighborhood(**kwargs),
                                 vertices[-1])
                self.assertEqual(mkGet.call_args_list,
                                 [mk.call(self.Neighborhood, **kwargs)])

                keys   = list(self.Neighborhood.keys())
                values = list(self.Neighborhood.values())
                tmp = [set()]
                tmp.extend(vertices)
                vertices = tmp
                for index, call in enumerate(mkAppend.call_args_list):
                    self.assertEqual(call, mk.call(keys[index],
                                                   upper,
                                                   lower,
                                                   values[index],
                                                   vertices[index]))
                self.assertEqual(len(mkAppend.call_args_list), 3)

    def test_empty(self):
        """test generate empty Vertex neighborhood"""

        self.Neighborhood = graph.VertexNeighborhood.empty(self.vertex)
        self.assertIsInstance(self.Neighborhood, graph.VertexNeighborhood)
        self.assertEqual(self.Neighborhood.vertex, self.vertex)
        self.assertEqual(self.Neighborhood, {})


class TestVertexDistance(ut.TestCase):
    """test the VertexDistance class"""

    def setUp(self):
        """Setup the tests"""

        self.vertex = mk.MagicMock(spec=int)

        self.distances = {}
        for index in range(3):
            self.distances[index] = mk.MagicMock(spec=float)

        self.Distance = graph.VertexDistance(self.vertex, self.distances)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Distance, collect.UserDict)
        self.assertIsInstance(self.Distance, graph.VertexDistance)

        self.assertEqual(self.Distance.vertex, self.vertex)

        for vertex, distance in self.distances.items():
            self.assertIn(vertex, self.Distance)
            self.assertEqual(self.Distance[vertex], distance)
        for vertex, distance in self.Distance.items():
            self.assertIn(vertex, self.distances)
            self.assertEqual(self.distances[vertex], distance)
        self.assertEqual(self.Distance, self.distances)

    def test_minimum(self):
        """test get the vertex with minimum distance"""

        distances = {1: 9, 2: 1, 3: 7, 6: 4, 8: 2}
        self.Distance = graph.VertexDistance(self.vertex, distances)
        self.assertEqual(self.Distance.minimum, 2)

        distances = {1: 9, 2: 4, 3: 7, 6: 4, 8: 2}
        self.Distance = graph.VertexDistance(self.vertex, distances)
        self.assertEqual(self.Distance.minimum, 8)

        distances = {1: 9, 2: 4, 3: 7, 6: 4, 8: 12}
        self.Distance = graph.VertexDistance(self.vertex, distances)
        self.assertEqual(self.Distance.minimum, 2)

    def test_radius(self):
        """test get the minimum distance"""

        with mk.patch('builtins.min') as mkMin:
            with mk.patch.object(graph.VertexDistance, 'values',
                                 autospec=True) as mkValues:
                self.assertEqual(self.Distance.radius,
                                 mkMin.return_value)
                self.assertEqual(mkMin.call_args_list,
                                 [mk.call(mkValues.return_value)])
                self.assertEqual(mkValues.call_args_list,
                                 [mk.call(self.distances)])

    def test_add(self):
        """test set the distance"""

        # Does not exist
        vertex   = mk.MagicMock(spec=int)
        distance = mk.MagicMock(spec=float)
        distance.__lt__.return_value = True
        self.assertNotIn(vertex, self.Distance)
        self.Distance.add(vertex, distance)
        self.assertIn(vertex, self.Distance)
        self.assertEqual(self.Distance[vertex], distance)
        self.assertEqual(len(self.Distance), 4)

        # Change inf distance
        vertex   = mk.MagicMock(spec=int)
        distance = mk.MagicMock(spec=float)
        distance.__lt__.return_value = True
        self.assertNotIn(vertex, self.Distance)
        self.Distance[vertex] = np.inf
        self.assertIn(vertex, self.Distance)
        self.assertEqual(self.Distance[vertex], np.inf)
        self.Distance.add(vertex, distance)
        self.assertEqual(self.Distance[vertex], distance)
        self.assertEqual(len(self.Distance), 5)

        # Exists but is not smaller
        for vertex in self.Distance:
            distance = mk.MagicMock(spec=float)
            distance.__lt__.return_value = False
            self.assertIn(vertex, self.Distance)
            self.Distance.add(vertex, distance)
            self.assertIn(vertex, self.Distance)
            self.assertNotEqual(self.Distance[vertex], distance)
        self.assertEqual(len(self.Distance), 5)

    def test_convert(self):
        """test convert to neighborhood"""

        neighborhood = self.Distance.convert()
        self.assertIsInstance(neighborhood, graph.VertexNeighborhood)
        self.assertEqual(neighborhood.vertex, self.vertex)
        for distance, hood in neighborhood.items():
            self.assertIsInstance(hood, set)
            for vertex in hood:
                self.assertEqual(self.Distance[vertex], distance)
        for vertex, distance in self.Distance.items():
            self.assertIn(distance, neighborhood)
            self.assertEqual(neighborhood[distance], {vertex})
        self.assertEqual(len(neighborhood), len(self.Distance))
            
    def test_distances(self):
        """test get a subset of the distances"""

        all_vertices = list(self.Distance.keys())
        for index in range(3):
            vertices = set(all_vertices[:index + 1])
            distances = self.Distance.distances(vertices)
            self.assertIsInstance(distances, graph.VertexDistance)
            self.assertEqual(distances.vertex, self.vertex)
            for vertex, distance in distances.items():
                self.assertIn(vertex, self.Distance)
                self.assertEqual(self.Distance[vertex], distance)
            self.assertEqual(len(distances), index + 1)

    def test_empty(self):
        """test generate an empty class"""

        vertices = set()
        for _ in range(3):
            vertices.add(mk.MagicMock(spec=int))

        self.Distance = graph.VertexDistance.empty(self.vertex, vertices)
        self.assertIsInstance(self.Distance, graph.VertexDistance)
        self.assertEqual(self.Distance.vertex, self.vertex)
        for vertex in vertices:
            self.assertIn(vertex, self.Distance)
            self.assertEqual(self.Distance[vertex], np.inf)
        for vertex, distance in self.Distance.items():
            self.assertIn(vertex, vertices)
            self.assertEqual(distance, np.inf)
        self.assertEqual(len(self.Distance), len(vertices))
        
        # Test practical convert
        neighborhood = self.Distance.convert()
        self.assertIsInstance(neighborhood, graph.VertexNeighborhood)
        self.assertEqual(neighborhood.vertex, self.vertex)
        for distance, hood in neighborhood.items():
            self.assertEqual(distance, np.inf)
            self.assertEqual(hood, vertices)
        self.assertEqual(len(neighborhood), 1)


class TestGraphNeighborhood(ut.TestCase):
    """test the GraphNeighborhood class"""

    def setUp(self):
        """Setup the tests"""

        self.neighborhoods = {}
        for index in range(3):
            self.neighborhoods[index] = \
                mk.create_autospec(graph.VertexNeighborhood,
                                   spec_set=True)

        self.Neighborhood = graph.GraphNeighborhood(self.neighborhoods)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Neighborhood, collect.UserDict)
        self.assertIsInstance(self.Neighborhood, graph.GraphNeighborhood)

        for vertex, neighborhood in self.neighborhoods.items():
            self.assertIn(vertex, self.Neighborhood)
            self.assertEqual(self.Neighborhood[vertex], neighborhood)
        for vertex, neighborhood in self.Neighborhood.items():
            self.assertIn(vertex, self.neighborhoods)
            self.assertEqual(self.neighborhoods[vertex], neighborhood)
        self.assertEqual(self.Neighborhood, self.neighborhoods)
        
    def test_minimum(self):
        """test get the minimum distance in the graph"""

        minimum = []
        for neighborhood in self.neighborhoods.values():
            this = mk.MagicMock(spec=float)
            neighborhood.minimum = this
            minimum.append(this)

        with mk.patch('builtins.min') as mkMin:
            self.assertEqual(self.Neighborhood.minimum,
                             mkMin.return_value)
            self.assertEqual(mkMin.call_args_list,
                             [mk.call(minimum)])

    def test_maximum(self):
        """test get the maximum distance in the graph"""

        maximum = []
        for neighborhood in self.neighborhoods.values():
            this = mk.MagicMock(spec=float)
            neighborhood.maximum = this
            maximum.append(this)

        with mk.patch('builtins.max') as mkMax:
            self.assertEqual(self.Neighborhood.maximum,
                             mkMax.return_value)
            self.assertEqual(mkMax.call_args_list,
                             [mk.call(maximum)])

    def test_add(self):
        """test add a distance between vertices"""

        # Existing distance set
        pairs = {}
        for vertex in self.neighborhoods:
            pairs[vertex] = (mk.MagicMock(spec=int), mk.MagicMock(spec=float))

        for vertex, pair in pairs.items():
            self.Neighborhood.add(vertex, pair)
            self.assertEqual(self.Neighborhood[vertex].
                             add.call_args_list,
                             [mk.call(pair[1], pair[0])])
        for vertex, neighborhood in self.Neighborhood.items():
            self.assertEqual(neighborhood.add.call_args_list,
                             [mk.call(pairs[vertex][1], pairs[vertex][0])])
            neighborhood.reset_mock()

        # New distance set
        with mk.patch.object(graph.VertexNeighborhood, 'empty') as mkEmpty:
            mkEmpty.return_value = mk.create_autospec(graph.GraphNeighborhood,
                                                      spec_set=True)
            vertex = mk.MagicMock(spec=int)
            pair = (mk.MagicMock(spec=int), mk.MagicMock(spec=float))

            self.assertNotIn(vertex, self.Neighborhood)
            self.Neighborhood.add(vertex, pair)
            self.assertIn(vertex, self.Neighborhood)
            self.assertEqual(self.Neighborhood[vertex],
                             mkEmpty.return_value)
            self.assertEqual(mkEmpty.call_args_list,
                             [mk.call(vertex)])
            self.assertEqual(mkEmpty.return_value.add.call_args_list,
                             [mk.call(pair[1], pair[0])])

    def test_neighborhood(self):
        """test get the neighborhood defined by the vertex and distances"""

        kwargs = {'test': mk.MagicMock()}

        for vertex in self.Neighborhood:
            self.assertEqual(self.Neighborhood.neighborhood(vertex, **kwargs),
                             self.neighborhoods[vertex].
                                  neighborhood.return_value)
            self.assertEqual(self.neighborhoods[vertex].
                                  neighborhood.call_args_list,
                             [mk.call(**kwargs)])


class TestGraphDistance(ut.TestCase):
    """test the GraphDistance class"""

    def setUp(self):
        """Setup the tests"""

        self.distances = {}
        for index in range(3):
            self.distances[index] = mk.create_autospec(graph.VertexDistance,
                                                       spec_set=True)

        self.Distance = graph.GraphDistance(self.distances)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Distance, collect.UserDict)
        self.assertIsInstance(self.Distance, graph.GraphDistance)

        for vertex, distances in self.distances.items():
            self.assertIn(vertex, self.Distance)
            self.assertEqual(self.Distance[vertex], distances)
        for vertex, distances in self.Distance.items():
            self.assertIn(vertex, self.distances)
            self.assertEqual(self.distances[vertex], distances)
        self.assertEqual(self.Distance, self.distances)

    def test_add(self):
        """test add an item in class"""

        # Existing distance set
        pairs = {}
        for vertex in self.distances:
            pairs[vertex] = (mk.MagicMock(spec=int), mk.MagicMock(spec=float))

        for vertex, pair in pairs.items():
            self.Distance.add(vertex, pair)
            self.assertEqual(self.Distance[vertex].add.call_args_list,
                             [mk.call(pair[0], pair[1])])
        for vertex, distances in self.Distance.items():
            self.assertEqual(distances.add.call_args_list,
                             [mk.call(pairs[vertex][0], pairs[vertex][1])])
            distances.reset_mock()

        # New distance set
        with mk.patch.object(graph.VertexDistance, 'empty') as mkEmpty:
            mkEmpty.return_value = mk.create_autospec(graph.VertexDistance,
                                                      spec_set=True)
            vertex = mk.MagicMock(spec=int)
            pair   = (mk.MagicMock(spec=int), mk.MagicMock(spec=float))

            self.assertNotIn(vertex, self.Distance)
            self.Distance.add(vertex, pair)
            self.assertIn(vertex, self.Distance)
            self.assertEqual(self.Distance[vertex],
                             mkEmpty.return_value)
            self.assertEqual(mkEmpty.call_args_list,
                             [mk.call(vertex, set())])
            self.assertEqual(mkEmpty.return_value.add.call_args_list,
                             [mk.call(pair[0], pair[1])])

    def test_convert(self):
        """test convert to a graph neighborhood"""

        neighborhoods = self.Distance.convert()
        self.assertIsInstance(neighborhoods, graph.GraphNeighborhood)
        for vertex, neighborhood in neighborhoods.items():
            self.assertIn(vertex, self.Distance)
            self.assertEqual(neighborhood,
                             self.Distance[vertex].convert.return_value)
            self.assertEqual(self.Distance[vertex].convert.call_args_list,
                             [mk.call()])
        for vertex, distance in self.Distance.items():
            self.assertIn(vertex, neighborhoods)
            self.assertEqual(neighborhoods[vertex],
                             distance.convert.return_value)
            self.assertEqual(distance.convert.call_args_list,
                             [mk.call()])
        self.assertEqual(len(neighborhoods), len(self.Distance))

    def test_empty(self):
        """test create an empty class"""

        vertices = set()
        for _ in range(3):
            vertices.add(mk.MagicMock(spec=int))

        self.Distance = graph.GraphDistance.empty(vertices)
        self.assertIsInstance(self.Distance, graph.GraphDistance)
        for vertex in vertices:
            self.assertIn(vertex, self.Distance)
            self.assertIsInstance(self.Distance[vertex], graph.VertexDistance)
            self.assertEqual(self.Distance[vertex].vertex, vertex)
            for this, dist in self.Distance[vertex].items():
                self.assertIn(this, vertices)
                self.assertEqual(dist, np.inf)
            self.assertEqual(len(self.Distance[vertex]), len(vertices))
        self.assertEqual(len(vertices), 3)
        for vertex, distance in self.Distance.items():
            self.assertIn(vertex, vertices)
            self.assertIsInstance(distance, graph.VertexDistance)
            self.assertEqual(distance.vertex, vertex)
            for this, dist in distance.items():
                self.assertIn(this, vertices)
                self.assertEqual(dist, np.inf)
            self.assertEqual(len(distance), len(vertices))
        self.assertEqual(len(self.Distance), len(vertices))

        # Test practical convert
        neighborhoods = self.Distance.convert()
        self.assertIsInstance(neighborhoods, graph.GraphNeighborhood)
        for vertex, neighborhood in neighborhoods.items():
            self.assertIn(vertex, self.Distance)
            self.assertIsInstance(neighborhood, graph.VertexNeighborhood)
            self.assertEqual(neighborhood.vertex, vertex)
            for distance, hood in neighborhood.items():
                self.assertEqual(distance, np.inf)
                self.assertEqual(hood, vertices)
            self.assertEqual(len(neighborhood), 1)
        self.assertEqual(len(neighborhoods), len(vertices))


class VertexDistanceTest(graph.VertexDistance):
    """Class to add dynamic values for tests"""

    vertex = mk.MagicMock(spec=int)


class TestAdjacency(ut.TestCase):
    """test the Adjacency class"""

    def setUp(self):
        """Setup the tests"""

        self.matrix = []
        for _ in range(3):
            row = []
            for _ in range(3):
                row.append(mk.MagicMock(spec=float))
            self.matrix.append(row)

        self.Adjacency = graph.Adjacency(self.matrix)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Adjacency, np.ndarray)
        self.assertIsInstance(self.Adjacency, graph.Adjacency)

        utnp.assert_array_equal(self.Adjacency, self.matrix)

    def test_num(self):
        """test get the number of vertices"""

        with mk.patch.object(graph.Adjacency, 'shape',
                             autospec=True) as mkShape:
            self.assertEqual(self.Adjacency.num,
                             mkShape.__getitem__.return_value)
            self.assertEqual(mkShape.__getitem__.call_args_list,
                             [mk.call(0)])

        # Practical
        self.assertEqual(self.Adjacency.num, 3)

    def test_vertices(self):
        """test the vertex set"""

        with mk.patch.object(graph.Adjacency, 'num', autospec=True) as mkNum:
            with mk.patch.object(graph, 'set') as mkSet:
                with mk.patch.object(graph, 'range') as mkRange:
                    self.assertEqual(self.Adjacency.vertices,
                                     mkSet.return_value)
                    self.assertEqual(mkSet.call_args_list,
                                     [mk.call(mkRange.return_value)])
                    self.assertEqual(mkRange.call_args_list,
                                     [mk.call(mkNum)])

        # Practical
        self.assertEqual(self.Adjacency.vertices, {0, 1, 2})

    def test__start_search(self):
        """test start a search"""

        distance = mk.create_autospec(VertexDistanceTest, spec_set=True)

        with mk.patch.object(graph.Adjacency, 'vertices',
                             autospec=True) as mkVertices:
            self.assertEqual(self.Adjacency._start_search(distance),
                             mkVertices)
            self.assertEqual(distance.add.call_args_list,
                             [mk.call(distance.vertex, 0)])
            
    def test__minimum(self):
        """test get the minimum distance within an unvisited set"""

        unvisited = mk.MagicMock(spec=set)
        distance  = mk.create_autospec(VertexDistanceTest, spec_set=True)
        distance.distances.return_value = \
            mk.create_autospec(VertexDistanceTest, spec_set=True)

        self.assertEqual(self.Adjacency._minimum(unvisited, distance),
                         distance.distances.return_value.radius)
        self.assertEqual(distance.distances.call_args_list,
                         [mk.call(unvisited)])

    def test__terminate(self):
        """test the terminate conditions check"""

        unvisited = {mk.MagicMock(spec=int)}
        distance  = mk.create_autospec(VertexDistanceTest, spec_set=True)

        with mk.patch.object(graph.Adjacency, '_minimum') as mkMinimum:
            mkMinimum.side_effect = [0, np.inf]

            # No termination
            self.assertFalse(self.Adjacency._terminate(unvisited, distance))
            self.assertEqual(mkMinimum.call_args_list,
                             [mk.call(unvisited, distance)])

            mkMinimum.reset_mock()
            # Minimum termination
            self.assertTrue(self.Adjacency._terminate(unvisited, distance))
            self.assertEqual(mkMinimum.call_args_list,
                             [mk.call(unvisited, distance)])

            mkMinimum.reset_mock()
            # Empty unvisited termination
            self.assertTrue(self.Adjacency._terminate(set(), distance))
            self.assertEqual(mkMinimum.call_args_list, [])

    def test__current(self):
        """test choose the next vertex to search"""

        unvisited = mk.MagicMock(spec=set)
        distance  = mk.create_autospec(VertexDistanceTest, spec_set=True)
        distance.distances.return_value = \
            mk.create_autospec(VertexDistanceTest, spec_set=True)

        self.assertEqual(self.Adjacency._current(unvisited, distance),
                         distance.distances.return_value.minimum)
        self.assertEqual(distance.distances.call_args_list,
                         [mk.call(unvisited)])

    def test__adjacent(self):
        """test get the adjacent vertices"""

        matrix = [[0, 1, 1, 1],
                  [0, 0, 1, 1],
                  [0, 0, 0, 1],
                  [0, 0, 0, 0]]
        self.Adjacency = graph.Adjacency(matrix)

        for vertex in self.Adjacency.vertices:
            self.assertEqual(self.Adjacency._adjacent(vertex),
                             set(range(vertex + 1, 4)))

    def test__visit(self):
        """test get the vertices to visit"""

        current   = mk.MagicMock(spec=int)
        unvisited = mk.MagicMock(spec=set)

        with mk.patch.object(graph.Adjacency, '_adjacent',
                             autospec=True) as mkAdjacent:
            self.assertEqual(self.Adjacency._visit(current, unvisited),
                             unvisited.intersection.return_value)
            self.assertEqual(unvisited.intersection.call_args_list,
                             [mk.call(mkAdjacent.return_value)])
            self.assertEqual(mkAdjacent.call_args_list,
                             [mk.call(self.Adjacency, current)])

            mkAdjacent.return_value = {1, 2, 4}
            unvisited               = {0, 1, 2, 3}
            self.assertEqual(self.Adjacency._visit(current, unvisited),
                             {1, 2})

    def test__distance(self):
        """test get the distance"""

        current  = mk.MagicMock(spec=int)
        vertex   = mk.MagicMock(spec=int)
        distance = mk.create_autospec(VertexDistanceTest, spec_set=True)

        with mk.patch.object(graph.Adjacency, '__getitem__',
                             autospec=True) as mkGet:
            mkGet.return_value = mk.MagicMock(spec=np.ndarray)
            self.assertEqual(self.Adjacency._distance(current, vertex,
                                                      distance),
                             distance.__getitem__.return_value.
                                      __add__.return_value)
            self.assertEqual(distance.__getitem__.return_value.
                                      __add__.call_args_list,
                             [mk.call(mkGet.return_value.
                                            __getitem__.return_value)])
            self.assertEqual(distance.__getitem__.call_args_list,
                             [mk.call(current)])
            self.assertEqual(mkGet.return_value.__getitem__.call_args_list,
                             [mk.call(vertex)])
            self.assertEqual(mkGet.call_args_list,
                             [mk.call(current)])
            distance.reset_mock()

        # Practical
        for current in range(3):
            for vertex in range(3):
                self.assertEqual(self.Adjacency._distance(current, vertex,
                                                          distance),
                                 distance.__getitem__.return_value.
                                          __add__.return_value)
                self.assertEqual(distance.__getitem__.return_value.
                                          __add__.call_args_list,
                                 [mk.call(self.matrix[current][vertex])])
                self.assertEqual(distance.__getitem__.call_args_list,
                                 [mk.call(current)])
                distance.reset_mock()

    def test__update(self):
        """test update the distances"""

        current  = mk.MagicMock(spec=int)
        distance = mk.create_autospec(VertexDistanceTest, spec_set=True)
        visit    = set()
        new      = []
        for _ in range(3):
            visit.add(mk.MagicMock(spec=int))
            new.append(mk.MagicMock(spec=float))

        with mk.patch.object(graph.Adjacency, '_distance',
                             autospec=True) as mkDistance:
            mkDistance.side_effect = new

            self.Adjacency._update(current, visit, distance)
            for index, vertex in enumerate(visit):
                self.assertEqual(distance.add.call_args_list[index],
                                 mk.call(vertex, new[index]))
                self.assertEqual(mkDistance.call_args_list[index],
                                 mk.call(self.Adjacency, current, vertex,
                                         distance))
            self.assertEqual(len(distance.add.call_args_list), 3)
            self.assertEqual(len(mkDistance.call_args_list), 3)

    def test__search(self):
        """test perform one search step"""

        unvisited = mk.MagicMock(spec=set)
        distance  = mk.create_autospec(VertexDistanceTest, spec_set=True)

        with mk.patch.object(graph.Adjacency, '_current') as mkCurrent:
            with mk.patch.object(graph.Adjacency, '_visit',
                                 autospec=True) as mkVisit:
                with mk.patch.object(graph.Adjacency, '_update',
                                     autospec=True) as mkUpdate:
                    self.Adjacency._search(unvisited, distance)
                    self.assertEqual(unvisited.remove.call_args_list,
                                     [mk.call(mkCurrent.return_value)])
                    self.assertEqual(mkUpdate.call_args_list,
                                     [mk.call(self.Adjacency,
                                              mkCurrent.return_value,
                                              mkVisit.return_value,
                                              distance)])
                    self.assertEqual(mkVisit.call_args_list,
                                     [mk.call(self.Adjacency,
                                              mkCurrent.return_value,
                                              unvisited)])
                    self.assertEqual(mkCurrent.call_args_list,
                                     [mk.call(unvisited, distance)])
                    
    def test__dijkstra(self):
        """test run dijkstra on single vertex"""

        distance = mk.create_autospec(VertexDistanceTest, spec_set=True)

        with mk.patch.object(graph.Adjacency, '_start_search',
                             autospec=True) as mkStart:
            with mk.patch.object(graph.Adjacency, 'num',
                                 autospec=True) as mkNum:
                with mk.patch.object(graph.Adjacency, '_terminate',
                                     autospec=True) as mkTerminate:
                    with mk.patch.object(graph.Adjacency, '_search',
                                         autospec=True) as mkSearch:
                        mkNum.__get__ = mk.MagicMock(return_value=3)

                        # Error (too many searches)
                        mkTerminate.side_effect = [False, False, False, False]
                        with self.assertRaisesRegex(RuntimeError,
                                                    'Search of vertex {} has '
                                                    'failed'.
                                                     format(distance.vertex)):
                            self.Adjacency._dijkstra(distance)
                        for call in mkTerminate.call_args_list:
                            self.assertEqual(call, mk.call(self.Adjacency,
                                                           mkStart.return_value,
                                                           distance))
                        for call in mkSearch.call_args_list:
                            self.assertEqual(call, mk.call(self.Adjacency,
                                                           mkStart.return_value,
                                                           distance))
                        self.assertEqual(len(mkTerminate.call_args_list), 4)
                        self.assertEqual(len(mkSearch.call_args_list),    4)
                        self.assertEqual(mkStart.call_args_list,
                                         [mk.call(self.Adjacency, distance)])

                        mkStart.reset_mock()
                        mkTerminate.reset_mock()
                        mkSearch.reset_mock()
                        # Maximum amount (3) of searches
                        mkTerminate.side_effect = [False, False, False, True]
                        self.Adjacency._dijkstra(distance)
                        for call in mkTerminate.call_args_list:
                            self.assertEqual(call, mk.call(self.Adjacency,
                                                           mkStart.return_value,
                                                           distance))
                        for call in mkSearch.call_args_list:
                            self.assertEqual(call, mk.call(self.Adjacency,
                                                           mkStart.return_value,
                                                           distance))
                        self.assertEqual(len(mkTerminate.call_args_list), 4)
                        self.assertEqual(len(mkSearch.call_args_list),    3)
                        self.assertEqual(mkStart.call_args_list,
                                         [mk.call(self.Adjacency, distance)])

                        mkStart.reset_mock()
                        mkTerminate.reset_mock()
                        mkSearch.reset_mock()
                        # Amount (2) searches
                        mkTerminate.side_effect = [False, False, True]
                        self.Adjacency._dijkstra(distance)
                        for call in mkTerminate.call_args_list:
                            self.assertEqual(call, mk.call(self.Adjacency,
                                                           mkStart.return_value,
                                                           distance))
                        for call in mkSearch.call_args_list:
                            self.assertEqual(call, mk.call(self.Adjacency,
                                                           mkStart.return_value,
                                                           distance))
                        self.assertEqual(len(mkTerminate.call_args_list), 3)
                        self.assertEqual(len(mkSearch.call_args_list),    2)
                        self.assertEqual(mkStart.call_args_list,
                                         [mk.call(self.Adjacency, distance)])

                        mkStart.reset_mock()
                        mkTerminate.reset_mock()
                        mkSearch.reset_mock()
                        # Amount (1) searches
                        mkTerminate.side_effect = [False, True]
                        self.Adjacency._dijkstra(distance)
                        for call in mkTerminate.call_args_list:
                            self.assertEqual(call, mk.call(self.Adjacency,
                                                           mkStart.return_value,
                                                           distance))
                        for call in mkSearch.call_args_list:
                            self.assertEqual(call, mk.call(self.Adjacency,
                                                           mkStart.return_value,
                                                           distance))
                        self.assertEqual(len(mkTerminate.call_args_list), 2)
                        self.assertEqual(len(mkSearch.call_args_list),    1)
                        self.assertEqual(mkStart.call_args_list,
                                         [mk.call(self.Adjacency, distance)])

                        mkStart.reset_mock()
                        mkTerminate.reset_mock()
                        mkSearch.reset_mock()
                        # Amount (1) searches
                        mkTerminate.side_effect = [True]
                        self.Adjacency._dijkstra(distance)
                        for call in mkTerminate.call_args_list:
                            self.assertEqual(call, mk.call(self.Adjacency,
                                                           mkStart.return_value,
                                                           distance))
                        for call in mkSearch.call_args_list:
                            self.assertEqual(call, mk.call(self.Adjacency,
                                                           mkStart.return_value,
                                                           distance))
                        self.assertEqual(len(mkTerminate.call_args_list), 1)
                        self.assertEqual(len(mkSearch.call_args_list),    0)
                        self.assertEqual(mkStart.call_args_list,
                                         [mk.call(self.Adjacency, distance)])

    def test_dijkstra(self):
        """test run Dijkstra's for whole graph"""

        distance = {}
        for _ in range(3):
            distance[mk.MagicMock()] = mk.create_autospec(VertexDistanceTest,
                                                          spec_set=True)

        with mk.patch.object(graph.Adjacency, '_dijkstra',
                             autospec=True) as mkDijkstra:
            with mk.patch.object(graph.Adjacency, 'vertices',
                                 autospec=True) as mkVertices:
                with mk.patch.object(graph.GraphDistance, 'empty') as mkEmpty:
                    mkEmpty.return_value = mk.create_autospec(graph.
                                                              GraphDistance,
                                                              spec_set=True)
                    mkEmpty.return_value.values.return_value = distance.values()

                    self.assertEqual(self.Adjacency.dijkstra(),
                                     mkEmpty.return_value)
                    self.assertEqual(mkEmpty.call_args_list,
                                     [mk.call(mkVertices)])
                    distances = list(distance.values())
                    for index, call in enumerate(mkDijkstra.call_args_list):
                        self.assertEqual(call,
                                         mk.call(self.Adjacency,
                                                 distances[index]))
                    self.assertEqual(len(mkDijkstra.call_args_list), 3)

        # Practical construction test

        # GRAPH
        # 0   1
        #     |
        #   .-2-.
        #   |   |
        #   3---4
        #   |   |
        #   5---6

        matrix = [[0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 1, 0, 0, 0, 0],
                  [0, 1, 0, 1, 1, 0, 0],
                  [0, 0, 1, 0, 1, 1, 0],
                  [0, 0, 1, 1, 0, 0, 1],
                  [0, 0, 0, 1, 0, 0, 1],
                  [0, 0, 0, 0, 1, 1, 0]]
        self.Adjacency = graph.Adjacency(matrix)
        distances = self.Adjacency.dijkstra()

        distance_0 = {0: 0,
                      1: np.inf,
                      2: np.inf,
                      3: np.inf,
                      4: np.inf,
                      5: np.inf,
                      6: np.inf}
        self.assertEqual(distances[0], distance_0)
        distance_1 = {0: np.inf,
                      1: 0,
                      2: 1,
                      3: 2,
                      4: 2,
                      5: 3,
                      6: 3}
        self.assertEqual(distances[1], distance_1)
        distance_2 = {0: np.inf,
                      1: 1,
                      2: 0,
                      3: 1,
                      4: 1,
                      5: 2,
                      6: 2}
        self.assertEqual(distances[2], distance_2)
        distance_3 = {0: np.inf,
                      1: 2,
                      2: 1,
                      3: 0,
                      4: 1,
                      5: 1,
                      6: 2}
        self.assertEqual(distances[3], distance_3)
        distance_4 = {0: np.inf,
                      1: 2,
                      2: 1,
                      3: 1,
                      4: 0,
                      5: 2,
                      6: 1}
        self.assertEqual(distances[4], distance_4)
        distance_5 = {0: np.inf,
                      1: 3,
                      2: 2,
                      3: 1,
                      4: 2,
                      5: 0,
                      6: 1}
        self.assertEqual(distances[5], distance_5)
        distance_6 = {0: np.inf,
                      1: 3,
                      2: 2,
                      3: 2,
                      4: 1,
                      5: 1,
                      6: 0}
        self.assertEqual(distances[6], distance_6)

        true_distance = {0: distance_0,
                         1: distance_1,
                         2: distance_2,
                         3: distance_3,
                         4: distance_4,
                         5: distance_5,
                         6: distance_6}
        self.assertEqual(distances, true_distance)

        # Test convert practical
        neighborhood = distances.convert()
        
        neighborhood_0 = {np.inf: {1, 2, 3, 4, 5, 6},
                          0:      {0}}
        self.assertEqual(neighborhood[0], neighborhood_0)
        neighborhood_1 = {np.inf: {0},
                          0:      {1},
                          1:      {2},
                          2:      {3, 4},
                          3:      {5, 6}}
        self.assertEqual(neighborhood[1], neighborhood_1)
        neighborhood_2 = {np.inf: {0},
                          0:      {2},
                          1:      {1, 3, 4},
                          2:      {5, 6}}
        self.assertEqual(neighborhood[2], neighborhood_2)
        neighborhood_3 = {np.inf: {0},
                          0:      {3},
                          1:      {2, 4, 5},
                          2:      {1, 6}}
        self.assertEqual(neighborhood[3], neighborhood_3)
        neighborhood_4 = {np.inf: {0},
                          0:      {4},
                          1:      {2, 3, 6},
                          2:      {1, 5}}
        self.assertEqual(neighborhood[4], neighborhood_4)
        neighborhood_5 = {np.inf: {0},
                          0:      {5},
                          1:      {3, 6},
                          2:      {2, 4},
                          3:      {1}}
        self.assertEqual(neighborhood[5], neighborhood_5)
        neighborhood_6 = {np.inf: {0},
                          0:      {6},
                          1:      {4, 5},
                          2:      {2, 3},
                          3:      {1}}
        self.assertEqual(neighborhood[6], neighborhood_6)

        true_neighborhood = {0: neighborhood_0,
                             1: neighborhood_1,
                             2: neighborhood_2,
                             3: neighborhood_3,
                             4: neighborhood_4,
                             5: neighborhood_5,
                             6: neighborhood_6}
        self.assertEqual(neighborhood, true_neighborhood)


class TestGraph(ut.TestCase):
    """test the Graph class"""

    def setUp(self):
        """Setup the tests"""

        self.neighborhood = mk.create_autospec(graph.GraphNeighborhood,
                                               spec_set=True)
        self.distance     = mk.create_autospec(graph.GraphDistance,
                                               spec_set=True)
        self.adjacency    = mk.create_autospec(graph.Adjacency,
                                               spec_set=True)

        self.Graph = graph.Graph(self.neighborhood,
                                 self.distance,
                                 self.adjacency)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Graph, graph.Graph)

        self.assertEqual(self.Graph.neighborhood, self.neighborhood)
        self.assertEqual(self.Graph.distance,     self.distance)
        self.assertEqual(self.Graph.adjacency,    self.adjacency)

        self.assertTrue(dclass.is_dataclass(self.Graph))

    def test_setup(self):
        """test setup the class"""

        matrix = mk.MagicMock(spec=list)

        self.adjacency.dijkstra.return_value = self.distance
        self.distance. convert. return_value = self.neighborhood

        with mk.patch.object(graph, 'Adjacency') as mkAdjacency:
            mkAdjacency.return_value = self.adjacency

            self.Graph = graph.Graph.setup(matrix)
            self.assertIsInstance(self.Graph, graph.Graph)
            self.assertEqual(self.Graph.neighborhood, self.neighborhood)
            self.assertEqual(self.Graph.distance,     self.distance)
            self.assertEqual(self.Graph.adjacency,    self.adjacency)

            self.assertEqual(mkAdjacency.call_args_list,
                             [mk.call(matrix)])
            self.assertEqual(self.adjacency.dijkstra.call_args_list,
                             [mk.call(False)])
            self.assertEqual(self.distance.convert.call_args_list,
                             [mk.call()])

    def test_save(self):
        """test save to a file"""

        file_name = mk.MagicMock(spec=str)

        with mk.patch('builtins.open', mk.mock_open()) as mkOpen:
            with mk.patch.object(pickle, 'dump') as mkDump:
                self.Graph.save(file_name)
                self.assertEqual(mkDump.call_args_list,
                                 [mk.call(self.Graph, mkOpen.return_value,
                                          protocol=pickle.HIGHEST_PROTOCOL)])
                self.assertEqual(mkOpen.call_args_list,
                                 [mk.call(file_name, 'wb')])

    def test_empty(self):
        """test create a single vertex graph"""

        self.Graph = graph.Graph.empty()

        self.assertIsInstance(self.Graph, graph.Graph)

        self.assertIsInstance(self.Graph.neighborhood, graph.GraphNeighborhood)
        self.assertEqual(self.Graph.neighborhood, {0: {0: {0}}})

        self.assertIsInstance(self.Graph.distance,     graph.GraphDistance)
        self.assertEqual(self.Graph.distance, {0: {0: 0}})
        self.assertIsInstance(self.Graph.adjacency,    graph.Adjacency)
        utnp.assert_array_equal(self.Graph.adjacency, [[0]])
