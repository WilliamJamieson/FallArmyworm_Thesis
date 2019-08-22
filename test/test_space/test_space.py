import unittest      as ut
import unittest.mock as mk

import collections  as collect
import numpy.random as rnd


import source.keyword as keyword

import source.space.graph    as main_graph
import source.space.grid     as grid
import source.space.location as agent_location
import source.space.space    as space


class GraphTest(main_graph.Graph):
    """Class to add dynamic values for tests"""

    neighborhood = mk.create_autospec(main_graph.GraphNeighborhood,
                                      spec_set=True)
    adjacency    = mk.create_autospec(main_graph.Adjacency,
                                      spec_set=True)


class TestSpace(ut.TestCase):
    """test Space class"""

    def setUp(self):
        """Setup the tests"""

        self.graphs    = [mk.create_autospec(GraphTest, spec_set=True)
                          for _ in range(3)]
        self.locations = [mk.create_autospec(agent_location, spec_set=True)
                          for _ in range(3)]

        self.location_keys = {mk.MagicMock(spec=int):
                                  [mk.MagicMock(spec=tuple) for _ in range(3)]
                              for _ in range(3)}

        self.Space = space.Space(self.graphs,
                                 self.locations,
                                 self.location_keys)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Space, collect.UserList)
        self.assertIsInstance(self.Space, space.Space)

        self.assertEqual(self.Space.locations,     self.locations)
        self.assertEqual(self.Space.location_keys, self.location_keys)

        self.assertEqual(self.Space,      self.graphs)
        self.assertEqual(self.Space.data, self.graphs)

    def test_depth(self):
        """test get the depth of locations"""

        with mk.patch.object(space, 'len') as mkLen:
            self.assertEqual(self.Space.depth,
                             mkLen.return_value)
            self.assertEqual(mkLen.call_args_list,
                             [mk.call(self.Space)])

        self.assertEqual(self.Space.depth, 3)

    def test_neighborhood(self):
        """test get the neighborhood of a location"""

        for graph in self.graphs:
            graph.neighborhood = mk.create_autospec(main_graph.
                                                        GraphNeighborhood,
                                                    spec_set=True)

        location = mk.create_autospec(agent_location.Location, spec_set=True)
        kwargs   = {'test': mk.MagicMock()}

        for level in range(len(self.graphs)):
            location.level = level
            self.assertEqual(self.Space.neighborhood(location, **kwargs),
                             self.graphs[level].neighborhood.
                                neighborhood.return_value)
            self.assertEqual(self.graphs[level].neighborhood.
                                neighborhood.call_args_list,
                             [mk.call(location.__getitem__.return_value,
                                      **kwargs)])
            self.assertEqual(location.__getitem__.call_args_list,
                             [mk.call(level)])
            location.reset_mock()

            self.graphs[level].reset_mock()
            for graph in self.graphs:
                self.assertEqual(graph.neighborhood.neighborhood.call_args_list,
                                 [])

        self.assertEqual(len(self.graphs), 3)

    def test_extend_location(self):
        """test extend a location"""

        for graph in self.graphs:
            graph.adjacency = mk.create_autospec(main_graph.Adjacency,
                                                 spec_set=True)

        location = mk.create_autospec(agent_location.Location, spec_set=True)
        location.copy.return_value = \
            mk.create_autospec(agent_location.Location, spec_set=True)

        with mk.patch.object(rnd, 'choice') as mkRND:
            with mk.patch.object(space, 'list') as mkList:
                for depth in range(len(self.graphs)):
                    location.depth = depth
                    self.assertEqual(self.Space.extend_location(location),
                                     location.copy.return_value)
                    self.assertEqual(location.copy.call_args_list,
                                     [mk.call()])
                    self.assertEqual(location.copy.return_value.append.
                                        call_args_list,
                                     [mk.call(mkRND.return_value)])
                    location.reset_mock()
                    self.assertEqual(mkRND.call_args_list,
                                     [mk.call(mkList.return_value)])
                    mkRND.reset_mock()
                    self.assertEqual(mkList.call_args_list,
                                     [mk.call(self.graphs[depth].
                                                adjacency.vertices)])
                    mkList.reset_mock()

                self.assertEqual(len(self.graphs), 3)

    def test_new_location(self):
        """test generate a new location"""

        for graph in self.graphs:
            graph.adjacency = mk.create_autospec(main_graph.Adjacency,
                                                 spec_set=True)

        with mk.patch.object(rnd, 'choice') as mkRND:
            with mk.patch.object(space, 'list') as mkList:
                for depth in range(1, len(self.graphs) + 1):
                    locs     = [mk.MagicMock(spec=int) for _ in range(depth)]
                    vertices = [mk.MagicMock(spec=list) for _ in range(depth)]
                    mkRND. side_effect = locs
                    mkList.side_effect = vertices

                    location = self.Space.new_location(depth)
                    self.assertIsInstance(location, agent_location.Location)
                    self.assertEqual(len(location), depth)
                    for level in range(depth):
                        self.assertEqual(location[level],
                                         locs[level])
                        self.assertEqual(mkRND.call_args_list[level],
                                         mk.call(vertices[level]))
                        self.assertEqual(mkList.call_args_list[level],
                                         mk.call(self.graphs[level].
                                                    adjacency.vertices))
                    self.assertEqual(len(mkList.call_args_list), depth)
                    self.assertEqual(len(mkRND.call_args_list),  depth)
                    self.assertEqual(len(location),              depth)
                    mkList.reset_mock()
                    mkRND.reset_mock()

                self.assertEqual(len(self.graphs), 3)

    def test__make_locations(self):
        """test generate location data for a specific level"""

        vertices = []
        for graph in self.graphs:
            vertex          = {mk.MagicMock(spec=int) for _ in range(3)}
            graph.adjacency = mk.create_autospec(main_graph.Adjacency,
                                                 spec_set=True)
            graph.adjacency.vertices = vertex
            vertices.append(vertex)

        for level in range(len(self.graphs)):
            vertex = vertices[level]
            locations = []
            new       = []
            keys      = []
            locs      = []
            for _ in range(3):
                location = mk.create_autospec(agent_location.Location,
                                              spec_set=True)
                copies = []
                for _ in vertex:
                    copy = mk.create_autospec(agent_location.Location,
                                                     spec_set=True)
                    copies.append(copy)
                    new.append(copy)
                    keys.append(copy.location_key)
                location.copy.side_effect = copies
                locations.append(location)
                locs.append(copies)

            self.assertEqual(self.Space._make_locations(locations, level),
                             (new, keys))
            for index_i, location in enumerate(locations):
                for index_j, vert in enumerate(vertex):
                    self.assertEqual(location.copy.call_args_list[index_j],
                                     mk.call())
                    self.assertEqual(locs[index_i][index_j].
                                        append.call_args_list,
                                     [mk.call(vert)])
                self.assertEqual(len(location.copy.call_args_list),
                                 len(vertex))
                self.assertEqual(len(vertex), 3)

        self.assertEqual(len(self.graphs), 3)
        
    def test_get_locations(self):
        """test get the locations from graphs"""

        make               = []
        true_locations     = []
        true_location_keys = {}
        for index in range(3):
            locs = [mk.create_autospec(agent_location.Location,
                                            spec_set=True)
                         for _ in range(3)]
            keys = [mk.MagicMock(spec=tuple) for _ in range(3)]
            make.append((locs, keys))
            true_locations.extend(locs)
            true_location_keys[index + 1] = keys

        with mk.patch.object(space.Space, 'depth', autospec=True) as mkDepth:
            with mk.patch.object(space.Space, '_make_locations',
                                 autospec=True) as mkMake:
                mkDepth.__get__ = mk.MagicMock(return_value=4)
                mkMake.side_effect = make

                locations, location_keys = self.Space.get_locations()

                self.assertIsInstance(locations, list)
                self.assertEqual(len(locations), 10)
                first = locations.pop(0)
                self.assertIsInstance(first, agent_location.Location)
                self.assertEqual(first, [0])
                self.assertEqual(locations, true_locations)

                self.assertIsInstance(location_keys, dict)
                self.assertEqual(len(location_keys), 4)
                self.assertIn(0, location_keys)
                self.assertIsInstance(location_keys[0], list)
                self.assertEqual(location_keys[0][0], (0,))
                self.assertEqual(len(location_keys[0]), 1)
                del location_keys[0]
                self.assertEqual(location_keys, true_location_keys)

                self.assertEqual(len(mkMake.call_args_list), 3)
                call = mkMake.call_args_list.pop(0)
                self.assertEqual(call,
                                 mk.call(self.Space, [first], 1))
                for index, call in enumerate(mkMake.call_args_list):
                    self.assertEqual(call,
                                     mk.call(self.Space,
                                             make[index][0], index + 2))
                self.assertEqual(len(mkMake.call_args_list), 2)

    # noinspection PyTypeChecker
    def test_create_grid(self):
        """test create a grid graph"""

        grid_args = (mk.MagicMock(), mk.MagicMock())

        with mk.patch.object(grid.Hexagon, 'grid') as mkHexagon:
            with mk.patch.object(grid.Square, 'grid') as mkSquare:
                with mk.patch.object(grid.Moore, 'grid') as mkMoore:
                    with mk.patch.object(grid.Triangle, 'grid') as mkTriangle:
                        # hexagon
                        grid_generator = (keyword.hexagon, *grid_args)
                        self.assertEqual(self.Space.create_grid(grid_generator),
                                         mkHexagon.return_value)
                        self.assertEqual(mkHexagon.call_args_list,
                                         [mk.call(*grid_args)])
                        # square
                        grid_generator = (keyword.square, *grid_args)
                        self.assertEqual(self.Space.create_grid(grid_generator),
                                         mkSquare.return_value)
                        self.assertEqual(mkSquare.call_args_list,
                                         [mk.call(*grid_args)])
                        # moore
                        grid_generator = (keyword.moore, *grid_args)
                        self.assertEqual(self.Space.create_grid(grid_generator),
                                         mkMoore.return_value)
                        self.assertEqual(mkMoore.call_args_list,
                                         [mk.call(*grid_args)])
                        # triangle
                        grid_generator = (keyword.triangle, *grid_args)
                        self.assertEqual(self.Space.create_grid(grid_generator),
                                         mkTriangle.return_value)
                        self.assertEqual(mkTriangle.call_args_list,
                                         [mk.call(*grid_args)])

    def test_setup(self):
        """test setup space"""

        # test calls
        with mk.patch.object(space.Space, 'get_locations',
                             autospec=True) as mkGet:
            with mk.patch.object(space.Space, 'create_grid') as mkGrid:
                # test use generators
                grid_generators = [mk.MagicMock(spec=tuple) for _ in range(3)]
                graphs = [mk.create_autospec(GraphTest, spec_set=True)
                          for _ in range(3)]

                mkGet.return_value = (self.locations, self.location_keys)
                mkGrid.side_effect = graphs

                self.Space = space.Space.setup(grid_generators)
                self.assertIsInstance(self.Space, space.Space)

                self.assertEqual(self.Space.locations,     self.locations)
                self.assertEqual(self.Space.location_keys, self.location_keys)
                self.assertEqual(mkGet.call_args_list,
                                 [mk.call(self.Space)])

                self.assertEqual(len(self.Space), 4)
                graph = self.Space.pop(0)
                self.assertIsInstance(graph, main_graph.Graph)
                self.assertIsInstance(graph.neighborhood,
                                      main_graph.GraphNeighborhood)
                self.assertEqual(len(graph.neighborhood), 1)
                self.assertIn(0, graph.neighborhood)
                self.assertIsInstance(graph.neighborhood[0],
                                      main_graph.VertexNeighborhood)
                self.assertEqual(graph.neighborhood[0].vertex, 0)
                self.assertEqual(len(graph.neighborhood[0]), 1)
                self.assertIn(0, graph.neighborhood[0])
                self.assertEqual(graph.neighborhood[0][0], {0})
                self.assertEqual(graph.neighborhood, {0: {0: {0}}})
                self.assertIsInstance(graph.distance,
                                      main_graph.GraphDistance)
                self.assertEqual(len(graph.distance), 1)
                self.assertIn(0, graph.distance)
                self.assertIsInstance(graph.distance[0],
                                      main_graph.VertexDistance)
                self.assertEqual(graph.distance[0].vertex, 0)
                self.assertEqual(len(graph.distance[0]), 1)
                self.assertIn(0, graph.distance[0])
                self.assertEqual(graph.distance[0][0], 0)
                self.assertEqual(graph.distance, {0: {0: 0}})
                self.assertIsInstance(graph.adjacency,
                                      main_graph.Adjacency)
                self.assertEqual(graph.adjacency.tolist(), [[0]])

                self.assertEqual(len(self.Space), 3)
                self.assertEqual(self.Space, graphs)
                for index, call in enumerate(mkGrid.call_args_list):
                    self.assertEqual(call,
                                     mk.call(grid_generators[index]))
                for index, grid_generator in enumerate(grid_generators):
                    self.assertEqual(mkGrid.call_args_list[index],
                                     mk.call(grid_generator))
                self.assertEqual(len(mkGrid.call_args_list),
                                 len(grid_generators))

                mkGrid.reset_mock()
                mkGet.reset_mock()
                # Pass in graphs
                self.Space = space.Space.setup(graphs)
                self.assertIsInstance(self.Space, space.Space)

                self.assertEqual(self.Space.locations,     self.locations)
                self.assertEqual(self.Space.location_keys, self.location_keys)
                self.assertEqual(mkGet.call_args_list,
                                 [mk.call(self.Space)])

                self.assertEqual(len(self.Space), 4)
                graph = self.Space.pop(0)
                self.assertIsInstance(graph, main_graph.Graph)
                self.assertIsInstance(graph.neighborhood,
                                      main_graph.GraphNeighborhood)
                self.assertEqual(len(graph.neighborhood), 1)
                self.assertIn(0, graph.neighborhood)
                self.assertIsInstance(graph.neighborhood[0],
                                      main_graph.VertexNeighborhood)
                self.assertEqual(graph.neighborhood[0].vertex, 0)
                self.assertEqual(len(graph.neighborhood[0]), 1)
                self.assertIn(0, graph.neighborhood[0])
                self.assertEqual(graph.neighborhood[0][0], {0})
                self.assertEqual(graph.neighborhood, {0: {0: {0}}})
                self.assertIsInstance(graph.distance,
                                      main_graph.GraphDistance)
                self.assertEqual(len(graph.distance), 1)
                self.assertIn(0, graph.distance)
                self.assertIsInstance(graph.distance[0],
                                      main_graph.VertexDistance)
                self.assertEqual(graph.distance[0].vertex, 0)
                self.assertEqual(len(graph.distance[0]), 1)
                self.assertIn(0, graph.distance[0])
                self.assertEqual(graph.distance[0][0], 0)
                self.assertEqual(graph.distance, {0: {0: 0}})
                self.assertIsInstance(graph.adjacency,
                                      main_graph.Adjacency)
                self.assertEqual(graph.adjacency.tolist(), [[0]])

                self.assertEqual(len(self.Space), 3)
                self.assertEqual(self.Space, graphs)

                self.assertEqual(mkGrid.call_args_list, [])

        # Test practical
        grid_generators = [(keyword.square, 3, 3, False),
                           (keyword.square, 2, 2, False)]
        self.Space = space.Space.setup(grid_generators)
        self.assertIsInstance(self.Space, space.Space)

        self.assertIsInstance(self.Space.locations, list)
        self.assertEqual(len(self.Space.locations), 46)

        location = self.Space.locations[0]
        self.assertIsInstance(location, agent_location.Location)
        self.assertEqual(location, [0])

        locations_1 = self.Space.locations[1:10]
        self.assertEqual(len(locations_1), 9)
        locations_2 = self.Space.locations[10:]
        self.assertEqual(len(locations_2), 36)

        counter = 0
        for vertex_1 in range(9):
            self.assertIsInstance(locations_1[vertex_1],
                                  agent_location.Location)
            self.assertEqual(locations_1[vertex_1], [0, vertex_1])
            for vertex_2 in range(4):
                self.assertIsInstance(locations_2[counter],
                                      agent_location.Location)
                self.assertEqual(locations_2[counter], [0, vertex_1, vertex_2])
                counter += 1
        self.assertEqual(counter, 36)

        self.assertEqual(len(self.Space), 3)
        graph = self.Space.pop(0)
        self.assertIsInstance(graph, main_graph.Graph)
        self.assertIsInstance(graph.neighborhood,
                              main_graph.GraphNeighborhood)
        self.assertEqual(len(graph.neighborhood), 1)
        self.assertIn(0, graph.neighborhood)
        self.assertIsInstance(graph.neighborhood[0],
                              main_graph.VertexNeighborhood)
        self.assertEqual(graph.neighborhood[0].vertex, 0)
        self.assertEqual(len(graph.neighborhood[0]), 1)
        self.assertIn(0, graph.neighborhood[0])
        self.assertEqual(graph.neighborhood[0][0], {0})
        self.assertEqual(graph.neighborhood, {0: {0: {0}}})
        self.assertIsInstance(graph.distance,
                              main_graph.GraphDistance)
        self.assertEqual(len(graph.distance), 1)
        self.assertIn(0, graph.distance)
        self.assertIsInstance(graph.distance[0],
                              main_graph.VertexDistance)
        self.assertEqual(graph.distance[0].vertex, 0)
        self.assertEqual(len(graph.distance[0]), 1)
        self.assertIn(0, graph.distance[0])
        self.assertEqual(graph.distance[0][0], 0)
        self.assertEqual(graph.distance, {0: {0: 0}})
        self.assertIsInstance(graph.adjacency,
                              main_graph.Adjacency)
        self.assertEqual(graph.adjacency.tolist(), [[0]])

        space_1_neighborhood = {0: {0: {0},
                                    1: {1, 3},
                                    2: {2, 4, 6},
                                    3: {5, 7},
                                    4: {8}},
                                1: {0: {1},
                                    1: {0, 2, 4},
                                    2: {3, 5, 7},
                                    3: {6, 8}},
                                2: {0: {2},
                                    1: {1, 5},
                                    2: {0, 4, 8},
                                    3: {3, 7},
                                    4: {6}},
                                3: {0: {3},
                                    1: {0, 4, 6},
                                    2: {1, 5, 7},
                                    3: {2, 8}},
                                4: {0: {4},
                                    1: {1, 3, 5, 7},
                                    2: {0, 2, 6, 8}},
                                5: {0: {5},
                                    1: {2, 4, 8},
                                    2: {1, 3, 7},
                                    3: {0, 6}},
                                6: {0: {6},
                                    1: {3, 7},
                                    2: {0, 4, 8},
                                    3: {1, 5},
                                    4: {2}},
                                7: {0: {7},
                                    1: {4, 6, 8},
                                    2: {1, 3, 5},
                                    3: {0, 2}},
                                8: {0: {8},
                                    1: {5, 7},
                                    2: {2, 4, 6},
                                    3: {1, 3},
                                    4: {0}}}
        space_2_neighborhood = {0: {0: {0},
                                    1: {1, 2},
                                    2: {3}},
                                1: {0: {1},
                                    1: {0, 3},
                                    2: {2}},
                                2: {0: {2},
                                    1: {0, 3},
                                    2: {1}},
                                3: {0: {3},
                                    1: {1, 2},
                                    2: {0}}}
        space_1_distance = {0: {0: 0,
                                1: 1,
                                2: 2,
                                3: 1,
                                4: 2,
                                5: 3,
                                6: 2,
                                7: 3,
                                8: 4},
                            1: {0: 1,
                                1: 0,
                                2: 1,
                                3: 2,
                                4: 1,
                                5: 2,
                                6: 3,
                                7: 2,
                                8: 3},
                            2: {0: 2,
                                1: 1,
                                2: 0,
                                3: 3,
                                4: 2,
                                5: 1,
                                6: 4,
                                7: 3,
                                8: 2},
                            3: {0: 1,
                                1: 2,
                                2: 3,
                                3: 0,
                                4: 1,
                                5: 2,
                                6: 1,
                                7: 2,
                                8: 3},
                            4: {0: 2,
                                1: 1,
                                2: 2,
                                3: 1,
                                4: 0,
                                5: 1,
                                6: 2,
                                7: 1,
                                8: 2},
                            5: {0: 3,
                                1: 2,
                                2: 1,
                                3: 2,
                                4: 1,
                                5: 0,
                                6: 3,
                                7: 2,
                                8: 1},
                            6: {0: 2,
                                1: 3,
                                2: 4,
                                3: 1,
                                4: 2,
                                5: 3,
                                6: 0,
                                7: 1,
                                8: 2},
                            7: {0: 3,
                                1: 2,
                                2: 3,
                                3: 2,
                                4: 1,
                                5: 2,
                                6: 1,
                                7: 0,
                                8: 1},
                            8: {0: 4,
                                1: 3,
                                2: 2,
                                3: 3,
                                4: 2,
                                5: 1,
                                6: 2,
                                7: 1,
                                8: 0}}
        space_2_distance = {0: {0: 0,
                                1: 1,
                                2: 1,
                                3: 2},
                            1: {0: 1,
                                1: 0,
                                2: 2,
                                3: 1},
                            2: {0: 1,
                                1: 2,
                                2: 0,
                                3: 1},
                            3: {0: 2,
                                1: 1,
                                2: 1,
                                3: 0}}
        space_1_adj = [[0, 1, 0, 1, 0, 0, 0, 0, 0],
                       [1, 0, 1, 0, 1, 0, 0, 0, 0],
                       [0, 1, 0, 0, 0, 1, 0, 0, 0],
                       [1, 0, 0, 0, 1, 0, 1, 0, 0],
                       [0, 1, 0, 1, 0, 1, 0, 1, 0],
                       [0, 0, 1, 0, 1, 0, 0, 0, 1],
                       [0, 0, 0, 1, 0, 0, 0, 1, 0],
                       [0, 0, 0, 0, 1, 0, 1, 0, 1],
                       [0, 0, 0, 0, 0, 1, 0, 1, 0]]
        space_2_adj = [[0, 1, 1, 0],
                       [1, 0, 0, 1],
                       [1, 0, 0, 1],
                       [0, 1, 1, 0]]

        self.assertEqual(len(self.Space), 2)
        graph = self.Space.pop(0)
        self.assertIsInstance(graph, main_graph.Graph)
        self.assertIsInstance(graph.neighborhood,
                              main_graph.GraphNeighborhood)
        self.assertEqual(graph.neighborhood, space_1_neighborhood)
        self.assertIsInstance(graph.distance,
                              main_graph.GraphDistance)
        self.assertEqual(graph.distance, space_1_distance)
        self.assertIsInstance(graph.adjacency,
                              main_graph.Adjacency)
        self.assertEqual(graph.adjacency.tolist(), space_1_adj)

        self.assertEqual(len(self.Space), 1)
        graph = self.Space.pop(0)
        self.assertIsInstance(graph, main_graph.Graph)
        self.assertIsInstance(graph.neighborhood,
                              main_graph.GraphNeighborhood)
        self.assertEqual(graph.neighborhood, space_2_neighborhood)
        self.assertIsInstance(graph.distance,
                              main_graph.GraphDistance)
        self.assertEqual(graph.distance, space_2_distance)
        self.assertIsInstance(graph.adjacency,
                              main_graph.Adjacency)
        self.assertEqual(graph.adjacency.tolist(), space_2_adj)
