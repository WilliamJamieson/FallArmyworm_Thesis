import collections  as collect
import numpy.random as rnd

import source.hint    as hint
import source.keyword as keyword

import source.space.graph    as main_graph
import source.space.grid     as grid
import source.space.location as agent_location


class Space(collect.UserList):
    """
    Class to contain space references for class

    Variables:
        - list:
            index: level of graph
            value: graph at level

        locations:     list of all possible locations
        location_keys: dict
            key:   level of interest
            value: list of location keys at that level
    """

    def __init__(self, graphs:        hint.graphs,
                       locations:     hint.locations,
                       location_keys: hint.locations_key):
        super().__init__(graphs)

        self.locations     = locations
        self.location_keys = location_keys

    @property
    def depth(self) -> int:
        """Get the depth of this location"""

        return len(self)

    def neighborhood(self, location: hint.location, **kwargs) -> hint.vertices:
        """
        Get the vertices in distance range of location

        Args:
            location: location to search from
            **kwargs: upper/lower bounds of search

        Returns:
            vertices in range of location
        """

        level             = location.level
        graph: hint.graph = self[level]
        vertex            = location[level]

        return graph.neighborhood.neighborhood(vertex, **kwargs)

    def extend_location(self, location: hint.location) -> hint.location:
        """
        Extend a location by one level to new depth

        Args:
            location: location to extend

        Returns:
            a location randomly extend by 1 level
        """

        graph: hint.graph = self[location.depth]
        vertices          = list(graph.adjacency.vertices)
        vertex            = rnd.choice(vertices)

        new = location.copy()
        new.append(vertex)

        return new

    def new_location(self, depth: int) -> hint.location:
        """
        Create a new location at random

        Args:
            depth: depth of location desired

        Returns:
            a random location of the correct depth
        """

        locs = []
        for level in range(depth):
            graph: hint.graph = self[level]
            vertices          = list(graph.adjacency.vertices)
            locs.append(rnd.choice(vertices))

        return agent_location.Location(locs)

    def _make_attrs(self, attrs: hint.attrs_dict,
                          depth: int) -> hint.attrs_loc:
        """
        Create an attrs tracking dictionary for locations at depth

        Args:
            attrs: the attrs dict for each agent
            depth: depth of the locations

        Returns:
            a it extended to locations with correct depth
        """

        location_keys = self.location_keys[depth]

        attrs_loc = {}
        for location_key in location_keys:
            attrs_loc[location_key] = attrs

        return attrs_loc

    def make_attrs(self, attrs: hint.attrs_depth) -> hint.attrs_loc:
        """
        Create a complete attrs initializer for the agents storage

        Args:
            attrs: dict
                key:  depth
                value: attrs dict for each agent

        Returns:
            attrs initializer
        """

        attrs_loc = {}
        for depth, attrs_dict in attrs.items():
            attrs_loc.update(self._make_attrs(attrs_dict, depth))

        return attrs_loc

    def _make_locations(self, locations: hint.locations,
                         level:     int) -> hint.location_pairs:
        """
        Extend the location keys out to level

        Args:
            locations: current list of location keys
            level:     new level

        Returns:
            all of the new locations
        """

        graph: hint.graph = self[level]
        vertices          = graph.adjacency.vertices

        new  = []
        keys = []
        for location in locations:
            for vertex in vertices:
                new_location = location.copy()
                new_location.append(vertex)
                new. append(new_location)
                keys.append(new_location.location_key)

        return new, keys

    def get_locations(self) -> hint.location_data:
        """
        Generate all of the locations possible

        Returns:
            list of all locations
        """

        locations     = [agent_location.Location([0])]
        location_keys = {0: [locations[0].location_key]}

        locs = locations.copy()
        for level in range(1, self.depth):
            locs, keys = self._make_locations(locs, level)
            locations += locs
            location_keys[level] = keys

        return locations, location_keys

    @staticmethod
    def create_grid(grid_generator: hint.grid_generator) -> hint.graph:
        """
        Create a grid for the space

        Args:
            grid_generator: generation arguments

        Returns:
            A setup grid
        """

        grid_key  = grid_generator[0]
        grid_args = grid_generator[1:]

        if grid_key == keyword.hexagon:
            return grid.Hexagon.grid(*grid_args)
        elif grid_key == keyword.square:
            return grid.Square.grid(*grid_args)
        elif grid_key == keyword.moore:
            return grid.Moore.grid(*grid_args)
        elif grid_key == keyword.triangle:
            return grid.Triangle.grid(*grid_args)
        else:
            raise TypeError('Invalid type of grid')

    @classmethod
    def setup(cls, grid_generators: hint.grid_generators) -> 'Space':
        """
        Setup space properly

        Args:
            grid_generators: the grid generators for the class
                (note master is not needed)

        Returns:
            fully setup class
        """

        graphs = [main_graph.Graph.setup([[0]])]

        for grid_generator in grid_generators:
            if isinstance(grid_generator, main_graph.Graph):
                graphs.append(grid_generator)
            else:
                graphs.append(cls.create_grid(grid_generator))

        new           = cls(graphs, [], {})
        new.locations, new.location_keys = new.get_locations()

        return new
