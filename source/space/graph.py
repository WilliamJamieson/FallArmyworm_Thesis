import collections as collect
import dataclasses as dclass
import numpy       as np
import pickle      as pickle

import joblib          as para
import multiprocessing as multi

import source.hint    as hint
import source.keyword as keyword


class VertexNeighborhood(collect.UserDict):
    """
    Class to find vertices a given distance from a vertex in a graph

    Variables:
        dictionary:
            key   -> distance
            value -> set of vertices at distance
        _vertex: vertex measuring from

    Properties:
        minimum: minimum distance from vertex
        maximum: maximum distance from vertex

    Methods:
        add:          vertex at distance
        neighborhood: get vertices in a distance range

    Constructors:
        empty: setup empty class
    """

    def __init__(self, vertex:       int,
                       neighborhood: hint.neighborhood_dict):
        super().__init__(neighborhood)

        self.vertex = vertex

    @property
    def minimum(self) -> float:
        """Get minimum distance from vertex"""

        return min(self.keys())

    @property
    def maximum(self) -> float:
        """Get maximum distance from vertex"""

        return max(self.keys())

    def add(self, distance: float,
                  vertex:   int) -> None:
        """
        Add a vertex at distance

        Args:
            distance: distance for vertex
            vertex:   vertex to add

        Effects:
            adds vertex at distance
        """

        if distance in self:
            self[distance].add(vertex)
        else:
            self[distance] = {vertex}

    def _convert(self, distance: float) -> float:
        """
        Convert a given distance to the closest value in dictionary

        Args:
            distance: distance to convert

        Returns:
            a distance within dictionary
        """

        return min(self.keys(), key=lambda x: abs(x - distance))

    def _upper_lower(self, **kwargs) -> hint.upper_lower:
        """
        Get the upper and lower bounds on distance

        Args:
            **kwargs: pass in of upper and lower bounds

        Returns:
            the upper and lower bounds on the distance
        """

        if keyword.upper in kwargs:
            distance: float = kwargs[keyword.upper]
            upper = self._convert(distance)
        else:
            upper = np.inf

        if keyword.lower in kwargs:
            distance: float = kwargs[keyword.lower]
            lower = self._convert(distance)
        else:
            lower = 0

        return upper, lower

    @staticmethod
    def _append_distance(distance: float,
                         upper:    float,
                         lower:    float,
                         union:    hint.vertices,
                         vertices: hint.vertices) -> hint.vertices:
        """
        Union to vertices if distance is okay

        Args:
            distance: distance in question
            upper:    upper bound on distance
            lower:    lower bound on distance
            union:    vertices which may be used
            vertices: vertices to union to

        Effects:
            union to vertices if correct
        """
        if lower <= distance <= upper:
            return vertices.union(union)
        else:
            return vertices

    def neighborhood(self, **kwargs) -> hint.vertices:
        """
        Get the vertices in distance range given

        Args:
            **kwargs: pass in of upper and lower bounds

        Returns:
            vertices in distance range
        """

        upper, lower = self._upper_lower(**kwargs)

        vertices = set()
        for distance, union in self.items():
            vertices = self._append_distance(distance, upper, lower,
                                             union, vertices)

        return vertices

    @classmethod
    def empty(cls, vertex: int) -> 'VertexNeighborhood':
        """
        Setup an empty vertex neighborhood

        Args:
            vertex: the origin vertex

        Returns:
            setup class
        """

        return cls(vertex, {})


class VertexDistance(collect.UserDict):
    """
    Class to measure between vertex distances:

    Variables:
        dictionary:
            key   -> vertex measuring to
            value -> distance between
        vertex: vertex measuring from

    Properties:
        minimum: get the vertex of minimum distance
        radius:  get the minimum distance

    Methods:
        add:       vertex at distance
        convert:   convert class to neighborhood
        distances: find subset of class

    Constructors:
        empty: create an empty class (all distances are inf)
    """

    def __init__(self, vertex:    int,
                       distances: hint.distance_dict):
        super().__init__(distances)

        self.vertex = vertex

    @property
    def minimum(self) -> int:
        """Get the vertex of minimum distance"""

        return min(self, key=self.get)

    @property
    def radius(self) -> float:
        """Get the minimum distance"""

        return min(self.values())

    def add(self, vertex:   int,
                  distance: float) -> None:
        """
        Set the distance between vertices if distance is less than old distance

        Args:
            vertex:   vertex measuring to
            distance: distance to vertex

        Effects:
            if distance is less than current distance set distance
            else leave alone
        """

        if vertex not in self:
            self[vertex] = np.inf

        if distance < self[vertex]:
            self[vertex] = distance

    def convert(self) -> hint.vertex_neighborhood:
        """
        Convert class to a vertex neighborhood

        Returns:
            a vertex neighborhood representation of class
        """

        neighborhood = VertexNeighborhood.empty(self.vertex)
        for vertex, distance in self.items():
            neighborhood.add(distance, vertex)

        return neighborhood

    def distances(self, vertices: hint.vertices) -> 'VertexDistance':
        """
        Return the subset of distances for class

        Args:
            vertices: the subset of vertices measuring to

        Returns:
            a subset of the distances
        """

        distances = {}
        for vertex in vertices:
            distances[vertex] = self[vertex]

        return VertexDistance(self.vertex, distances)

    @classmethod
    def empty(cls, vertex: int,
                   vertices: hint.vertices) -> 'VertexDistance':
        """
        Setup an empty vertex distance class

        Args:
            vertex:   vertex measuring from
            vertices: vertices measuring to

        Returns:
            no distance set class
        """

        new = cls(vertex, {})
        for this in vertices:
            new.add(this, np.inf)

        return new


class GraphNeighborhood(collect.UserDict):
    """
    Class to contain all neighborhoods in graph

    Variables:
        dictionary:
            key   -> vertex
            value -> neighborhood

    Properties:
        minimum: minimum distance in graph
        maximum: maximum distance in graph

    Methods:
        add:          vertex at distance
        neighborhood: get neighborhood of a vertex
    """

    def __init__(self, neighborhoods: hint.neighborhoods):
        super().__init__(neighborhoods)

    @property
    def minimum(self) -> float:
        """Get the minimum distance in graph"""

        return min([neighborhood.minimum for neighborhood in self.values()])

    @property
    def maximum(self) -> float:
        """Get the maximum distance in graph"""

        return max([neighborhood.maximum for neighborhood in self.values()])

    def add(self, vertex: int,
                  pair:   hint.distance_pair) -> None:
        """
        Add a vertex at distance from another vertex

        Args:
            vertex: start vertex
            pair:   a distance pair (end vertex, distance from start)

        Effects:
            adds vertex at distance
        """

        end, distance = pair

        if vertex not in self:
            self[vertex] = VertexNeighborhood.empty(vertex)

        self[vertex].add(distance, end)

    def neighborhood(self, vertex: int, **kwargs) -> hint.vertices:
        """
        Get the neighborhood defined by the bounds for the vertex

        Args:
            vertex:   start vertex
            **kwargs: pass in of upper and lower bounds

        Returns:
            neighborhood of the vertex
        """

        return self[vertex].neighborhood(**kwargs)


class GraphDistance(collect.UserDict):
    """
    Class to measure between vertex distances:

    Variables:
        dictionary:
            key   -> vertex measuring to
            value -> distance between

    Methods:
        add:     add vertex at distance
        convert: convert class to neighborhood

    Constructors:
        empty: create an empty class (all distances are inf)
    """

    def __init__(self, distances: hint.distances):
        super().__init__(distances)

    def add(self, vertex: int,
                  pair:   hint.distance_pair) -> None:
        """
        Add a distance between vertices

        Args:
            vertex: start vertex
            pair:   a distance pair (end vertex, distance from start)

        Effects:
            updates distance between vertices
        """

        end, distance = pair

        if vertex not in self:
            self[vertex] = VertexDistance.empty(vertex, set())

        self[vertex].add(end, distance)

    def convert(self) -> hint.graph_neighborhood:
        """
        Convert class to a graph neighborhood

        Returns:
            a converted class
        """

        neighborhoods = {}
        for vertex, distances in self.items():
            neighborhoods[vertex] = distances.convert()

        return GraphNeighborhood(neighborhoods)

    @classmethod
    def empty(cls, vertices: hint.vertices) -> 'GraphDistance':
        """
        Initialize a graph distance class

        Args:
            vertices: set of vertices for class

        Returns:
            an initialized graph distance class
        """

        distances = {}
        for vertex in vertices:
            distances[vertex] = VertexDistance.empty(vertex, vertices)

        return cls(distances)


class Adjacency(np.ndarray):
    """
    Class to contain an adjacency matrix

    Variables:
        array -> square matrix array

    Properties:
        num:      number of vertices
        vertices: the vertex set

    Methods:
        dijkstra: generate a distance table
    """

    def __new__(cls, array):
        obj = np.asarray(array).view(cls)

        return obj

    @property
    def num(self) -> int:
        """Number of vertices"""

        return self.shape[0]

    @property
    def vertices(self) -> hint.vertices:
        """Get the set of all vertices"""

        return set(range(self.num))

    def _start_search(self, distance: hint.vertex_distance) -> hint.vertices:
        """
        Setup to start the search

        Args:
            distance: the distance class for a single root vertex

        Returns:
            the unvisited set of vertices
            and the current search neighborhood
        """

        vertex = distance.vertex
        distance.add(vertex, 0)

        return self.vertices

    @staticmethod
    def _minimum(unvisited: hint.vertices,
                 distance:  hint.vertex_distance) -> float:
        """
        Find the minimum distance within the unvisited vertices

        Args:
            unvisited: list of unvisited vertices
            distance:  the distance class for a single root vertex

        Returns:
            a minimum within the unvisited
        """

        distances = distance.distances(unvisited)

        return distances.radius

    def _terminate(self, unvisited: hint.vertices,
                         distance:  hint.vertex_distance) -> bool:
        """
        Determine if search is finished

        Args:
            unvisited: list of unvisited vertices
            distance:  the distance class for a single root vertex

        Returns:
            True if no more unvisited
            True if the radius of the unvisited vertices is inf
            False otherwise
        """

        if not unvisited:
            return True

        if self._minimum(unvisited, distance) == np.inf:
            return True

        return False

    @staticmethod
    def _current(unvisited: hint.vertices,
                 distance:  hint.vertex_distance) -> int:
        """
        Get the current target of a dijkstra search

        Args:
            unvisited: list of unvisited vertices
            distance:  the distance class for a single root vertex

        Returns:
            a search target
        """

        distances = distance.distances(unvisited)

        return distances.minimum

    def _adjacent(self, vertex: int) -> hint.vertices:
        """
        Get the vertices adjacent to the vertex

        Args:
            vertex: the vertex to search from

        Returns:
            set of vertices adjacent to vertex
        """

        return set(self[vertex].nonzero()[0])

    def _visit(self, current:   int,
                     unvisited: hint.vertices) -> hint.vertices:
        """
        Get the vertices to visit from current vertex

        Args:
            current:   the current vertex we are searching from
            unvisited: the unvisited vertices

        Returns:
            a set of vertices to visit
        """

        adjacent = self._adjacent(current)

        return unvisited.intersection(adjacent)

    def _distance(self, current:  int,
                        vertex:   int,
                        distance: hint.vertex_distance) -> float:
        """
        Get the distance via current to vertex

        Args:
            current:  the current vertex we are searching from
            vertex:   the vertex we are going to
            distance: the distance class for a single root vertex

        Returns:
            the distance via the current vertex from the root vertex
        """

        length = distance[current]
        extra  = self[current][vertex]

        return length + extra

    def _update(self, current: int,
                      visit:   hint.vertices,
                      distance: hint.vertex_distance) -> None:
        """
        Update the distances in distance based on visit and current

        Args:
            current:  the current vertex we are searching from
            visit:    the vertices to visit
            distance: the distance class for a single root vertex

        Effects:
            updates the distances in the distance class
        """

        for vertex in visit:
            new = self._distance(current, vertex, distance)
            distance.add(vertex, new)

    def _search(self, unvisited: hint.vertices,
                      distance:  hint.vertex_distance) -> None:
        """
        Run a search on the current distances for next step
        Args:
            unvisited: the set of unvisited vertices
            distance:  the distance class for a single root vertex

        Effects:
            Runs a single search level on the distance
        """

        current = self._current(unvisited, distance)
        visit   = self._visit(current, unvisited)

        self._update(current, visit, distance)
        unvisited.remove(current)

    def _dijkstra(self, distance: hint.vertex_distance) -> None:
        """
        Run Dijkstra's to find min distance starting at root vertex

        Args:
            distance: the distance class for a single root vertex

        Effects:
            Fill in distances in distance
        """

        unvisited = self._start_search(distance)

        for _ in range(self.num + 1):
            if self._terminate(unvisited, distance):
                break
            else:
                self._search(unvisited, distance)
        else:
            raise RuntimeError('Search of vertex {} has failed'.
                               format(distance.vertex))

    def _para_dijkstra(self, vertex: int) -> hint.vertex_distance:
        """
        Run Dijkstra's to find min distance starting at root vertex using
            parallel library

        Args:
            vertex:   the vertex

        Returns:
            vertex distance system for vertex
        """

        print('Dijkstra for vertex: {}'.format(vertex))

        distance = VertexDistance.empty(vertex, self.vertices)
        self._dijkstra(distance)

        return distance

    def dijkstra(self, parallel: bool = False) -> hint.graph_distance:
        """
        Run Dijkstra's Algorithm to find a graph distance object

        Returns:
            a graph distance object
        """

        if parallel:
            inputs = range(self.num)
            num    = multi.cpu_count()
            print('Num Cores: {}'.format(num))

            values = para.Parallel(n_jobs=num)(para.delayed(self._para_dijkstra)(values)
                                               for values in inputs)
            dist_dict = {}
            for index, value in enumerate(values):
                dist_dict[index] = value

            distances = GraphDistance(dist_dict)
        else:
            distances = GraphDistance.empty(self.vertices)
            for distance in distances.values():
                self._dijkstra(distance)

        return distances


@dclass.dataclass
class Graph(object):
    """
    Class to handle a graph

    Variables:
        _neighborhood: neighborhood table
        _distance:     distance table
        _adjacency:    adjacency matrix

    Properties:
        minimum: minimum distance in graph
        maximum: maximum distance in graph

        distance: distance table (pass through)

        num:      number of vertices
        vertices: the vertex set

    Methods:
        neighborhood: neighborhood finding

    Constructors:
        setup: setup the class from a matrix
        empty: create a single vertex graph
    """

    neighborhood: hint.graph_neighborhood
    distance:     hint.graph_distance
    adjacency:    hint.graph_adjacency

    def save(self, file_name: str) -> None:
        """
        Save graph to file_name for reuse

        Args:
            file_name: name of file to pickle to

        Effects:
            writes data to file
        """

        with open(file_name, 'wb') as graph_dump:
            pickle.dump(self, graph_dump, protocol=pickle.HIGHEST_PROTOCOL)

    @classmethod
    def setup(cls, matrix,
                   parallel: bool = False) -> 'Graph':
        """
        Setup a graph from a matrix

        Args:
            matrix: the matrix
            parallel: determine if this is a parallel compute

        Returns:
            Fully setup class
        """

        adjacency    = Adjacency(matrix)
        distance     = adjacency.dijkstra(parallel)
        neighborhood = distance.convert()

        return cls(neighborhood, distance, adjacency)

    @classmethod
    def empty(cls) -> 'Graph':
        """
        Generate an empty class

        Returns:
            a single vertex graph
        """

        return cls.setup([[0]])
