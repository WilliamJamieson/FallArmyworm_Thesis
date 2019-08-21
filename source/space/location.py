import collections as collect

import source.hint as hint


class Location(collect.UserList):
    """
    Class to contain a location

    Variables:
        - list:
            index: level of location
            value: location vertex

    Properties:
        location_key: a tuple form of location
        depth:        length of location
    """

    def __init__(self, locs: hint.locs):
        super().__init__(locs)

    @property
    def location_key(self) -> hint.location_key:
        """Get the location key for the location"""

        return tuple(self)

    @property
    def depth(self) -> int:
        """Get the depth of this location"""

        return len(self)

    @property
    def level(self) -> int:
        """Get level this location operates at"""

        return len(self) - 1
