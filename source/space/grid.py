import datetime
import dataclasses as dclass

import source.hint as hint

import source.space.graph as graph


@dclass.dataclass
class Grid(graph.Graph):
    """
    Base class for grid graphs

    Constructor:
        grid: create the grid graph
    """

    @staticmethod
    def _boundary(n: int,
                  m: int) -> hint.boundary:
        """
        Get vertices on grid boundary

        Args:
            n:
            m:

        Returns:
            (bottom vertices,
             top    vertices,
             left   vertices,
             right  vertices)
            on grid boundary
        """

        vertices = list(range(n*m))

        bottom = vertices[:n]
        top    = vertices[-n:]

        left  = []
        right = []
        for vertex in vertices:
            if 0 == (vertex % n):
                left.append(vertex)

            if (n - 1) == (vertex % n):
                right.append(vertex)

        return bottom, top, left, right

    def _upper_indicator(self, i: int,
                               j: int,
                               n: int,
                               m: int) -> bool:
        """
        Determine if there will be a 1 or 0 in the jth position of the
            ith column of the adjacency matrix

        Args:
            i: column
            j: row
            n: number of rows    in grid
            m: number of columns in grid

        Returns:
            0 or 1
        """

        pass

    def _upper_generator(self, n: int,
                               m: int) -> hint.upper_grid:
        """
        Generate the upper triangle of the adjacency matrix

        Args:
            n: number of rows    in grid
            m: number of columns in grid

        Returns:
            upper triangular matrix
        """

        num = n*m

        column = []
        for i in range(num):
            row = []
            for j in range(num):
                if self._upper_indicator(i, j, n, m):
                    row.append(1)
                else:
                    row.append(0)
            column.append(row)

        return column

    def _upper_torus(self, upper: hint.upper_grid,
                           n:     int,
                           m:     int) -> None:
        """
        Adjust grid adjacency matrix to be for a torus

        Args:
            upper: the upper adjacency matrix
            n:     number of rows    in grid
            m:     number of columns in grid

        Effects:
            modify the upper adjacency matrix to be for a torus grid
        """

        pass

    @staticmethod
    def _full(upper: hint.upper_grid) -> hint.graph_adjacency:
        """
        Generate a full adjacency matrix from an upper grid

        Args:
            upper: the upper adjacency matrix

        Returns:
            a full adjacency matrix
        """

        upper_matrix = graph.Adjacency(upper)
        lower_matrix = upper_matrix.transpose()

        return upper_matrix + lower_matrix

    def _generator(self, n:     int,
                         m:     int,
                         torus: bool) -> hint.graph_adjacency:
        """
        Generate an adjacency matrix for grid

        Args:
            n:     number of rows    in grid
            m:     number of columns in grid
            torus: if the grid is a torus

        Returns:
            An adjacency matrix
        """

        upper = self._upper_generator(n, m)
        if torus:
            self._upper_torus(upper, n, m)

        return self._full(upper)

    @classmethod
    def grid(cls, n:        int,
                  m:        int,
                  torus:    bool,
                  parallel: bool = False) -> 'Grid':
        """
        Create a grid graph

        Args:
            n:     number of rows    in grid
            m:     number of columns in grid
            torus: if the grid is a torus
            parallel: determine if this is a parallel compute

        Returns:
            a setup class
        """

        grid = cls.empty()

        if parallel:
            print('Creating Adjacency {}'.format(datetime.datetime.now()))
        adjacency    = grid._generator(n, m, torus)
        if parallel:
            print('Creating Distance {}'.format(datetime.datetime.now()))
        distance     = adjacency.dijkstra(parallel)
        if parallel:
            print('Creating Neighborhood {}'.format(datetime.datetime.now()))
        neighborhood = distance.convert()

        return cls(neighborhood, distance, adjacency)


@dclass.dataclass
class Hexagon(Grid):
    """
    Class for hexagon tile grid graphs
    """

    def _upper_indicator(self, i: int,
                               j: int,
                               n: int,
                               m: int) -> bool:
        """
        Determine if there will be a 1 or 0 in the jth position of the
            ith column of the adjacency matrix

        Args:
            i: column
            j: row
            n: number of rows    in grid
            m: number of columns in grid

        Returns:
            0 or 1
        """

        # Above
        if j == (i + n):
            return True

        # To the right
        if ((n - 1) != (i % n)) and (j == (i + 1)):
            return True

        # Diagonal
        if (0 != (i % n)) and (j == (i + n - 1)):
            return True

        return False

    def _upper_torus(self, upper: hint.upper_grid,
                           n:     int,
                           m:     int) -> None:
        """
        Adjust grid adjacency matrix to be for a torus

        Args:
            upper: the upper adjacency matrix
            n:     number of rows    in grid
            m:     number of columns in grid

        Effects:
            modify the upper adjacency matrix to be for a torus grid
        """

        bottom, top, left, right = self._boundary(n, m)

        # Top-Bottom
        for index in range(n):
            # Vertical edges
            upper[bottom[index]][top[index]] = 1

            # Diagonals
            if index < (n - 1):
                upper[bottom[index]][top[index + 1]] = 1

        upper[bottom[n - 1]][top[0]] = 1

        # Left-Right
        for index in range(m):
            # Horizontal edges
            upper[left[index]][right[index]] = 1

            # Diagonals
            if index < (m - 1):
                upper[left[index]][right[index + 1]] = 1


@dclass.dataclass
class Square(Grid):
    """
    Class for square tile grid graphs
    """

    def _upper_indicator(self, i: int,
                               j: int,
                               n: int,
                               m: int) -> bool:
        """
        Determine if there will be a 1 or 0 in the jth position of the
            ith column of the adjacency matrix

        Args:
            i: column
            j: row
            n: number of rows    in grid
            m: number of columns in grid

        Returns:
            0 or 1
        """

        # Above
        if j == (i + n):
            return True

        # To the right
        if ((n - 1) != (i % n)) and (j == (i + 1)):
            return True

        return False

    def _upper_torus(self, upper: hint.upper_grid,
                           n:     int,
                           m:     int) -> None:
        """
        Adjust grid adjacency matrix to be for a torus

        Args:
            upper: the upper adjacency matrix
            n:     number of rows    in grid
            m:     number of columns in grid

        Effects:
            modify the upper adjacency matrix to be for a torus grid
        """

        bottom, top, left, right = self._boundary(n, m)

        # Top-Bottom
        for index in range(n):
            # Vertical edges
            upper[bottom[index]][top[index]] = 1

        # Left-Right
        for index in range(m):
            # Horizontal edges
            upper[left[index]][right[index]] = 1


@dclass.dataclass
class Moore(Grid):
    """
    Class for Moore tile grid graphs
        -square tiles that allow movements to the diagonals
    """

    def _upper_indicator(self, i: int,
                               j: int,
                               n: int,
                               m: int) -> bool:
        """
        Determine if there will be a 1 or 0 in the jth position of the
            ith column of the adjacency matrix

        Args:
            i: column
            j: row
            n: number of rows    in grid
            m: number of columns in grid

        Returns:
            0 or 1
        """

        # Above
        if j == (i + n):
            return True

        # To the right
        if ((n - 1) != (i % n)) and (j == (i + 1)):
            return True

        # Diagonal left
        if (0 != (i % n)) and (j == (i + n - 1)):
            return True

        # Diagonal right
        if ((n - 1) != (i % n)) and (j == i + n + 1):
            return True

        return False

    def _upper_torus(self, upper: hint.upper_grid,
                           n:     int,
                           m:     int) -> None:
        """
        Adjust grid adjacency matrix to be for a torus

        Args:
            upper: the upper adjacency matrix
            n:     number of rows    in grid
            m:     number of columns in grid

        Effects:
            modify the upper adjacency matrix to be for a torus grid
        """

        bottom, top, left, right = self._boundary(n, m)

        # Top-Bottom
        for index in range(n):
            # Vertical edges
            upper[bottom[index]][top[index]] = 1

            # Diagonals left
            if index < (n - 1):
                upper[bottom[index]][top[index + 1]] = 1

            # Diagonals right
            if index > 0:
                upper[bottom[index]][top[index - 1]] = 1

        upper[bottom[n - 1]][top[0]] = 1
        upper[bottom[0]][top[n - 1]] = 1

        # Left-Right
        for index in range(m):
            # Horizontal edges
            upper[left[index]][right[index]] = 1

            # Diagonals left
            if index < (m - 1):
                upper[left[index]][right[index + 1]] = 1

            # Diagonals right
            if index > 0:
                upper[left[index]][right[index - 1]] = 1


@dclass.dataclass
class Triangle(Grid):
    """
    Class for triangle tile grid graphs
    """

    def _upper_indicator(self, i: int,
                               j: int,
                               n: int,
                               m: int) -> bool:
        """
        Determine if there will be a 1 or 0 in the jth position of the
            ith column of the adjacency matrix

        Args:
            i: column
            j: row
            n: number of rows    in grid
            m: number of columns in grid

        Returns:
            0 or 1
        """

        # To the right
        if ((n - 1) != (i % n)) and (j == (i + 1)):
            return True

        # Above on even rows
        if (0 == ((i // n) % 2)) and (0 == (i % 2)) and (j == (i + n)):
            return True

        # Above on odd rows
        if (1 == ((i // n) % 2)) and (1 == (i % 2)) and (j == (i + n)):
            return True

        return False

    def _upper_torus(self, upper: hint.upper_grid,
                           n:     int,
                           m:     int) -> None:
        """
        Adjust grid adjacency matrix to be for a torus

        Args:
            upper: the upper adjacency matrix
            n:     number of rows    in grid
            m:     number of columns in grid

        Effects:
            modify the upper adjacency matrix to be for a torus grid
        """

        bottom, top, left, right = self._boundary(n, m)

        if 1 == (n % 2):
            raise ValueError('n must be even')

        # Top-Bottom
        for index in range(n):
            if (0 == (m % 2)) and (1 == (index % 2)):
                upper[bottom[index]][top[index]] = 1
            elif (1 == (m % 2)) and (0 == (index % 2)):
                upper[bottom[index]][top[index]] = 1

        # Left-Right
        for index in range(m):
            upper[left[index]][right[index]] = 1
