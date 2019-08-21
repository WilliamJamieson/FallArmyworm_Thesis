import unittest      as ut
import unittest.mock as mk

import collections as collect

import source.space.location as location


class TestLocation(ut.TestCase):
    """test the Location class"""

    def setUp(self):
        """Setup the tests"""

        self.locs = [mk.MagicMock(spec=int) for _ in range(3)]

        self.Location = location.Location(self.locs)

    def test___init__(self):
        """test __init__ for class"""

        self.assertIsInstance(self.Location, collect.UserList)
        self.assertIsInstance(self.Location, location.Location)

        self.assertEqual(self.Location,      self.locs)
        self.assertEqual(self.Location.data, self.locs)
        
    def test_location_key(self):
        """test create a location key"""

        self.assertEqual(self.Location.location_key, tuple(self.locs))

    def test_depth(self):
        """test get the depth of the location"""

        with mk.patch.object(location, 'len') as mkLen:
            self.assertEqual(self.Location.depth,
                             mkLen.return_value)
            self.assertEqual(mkLen.call_args_list,
                             [mk.call(self.locs)])

        self.assertEqual(self.Location.depth, 3)

    def test_level(self):
        """test get operation level of location"""

        with mk.patch.object(location, 'len') as mkLen:
            self.assertEqual(self.Location.level,
                             mkLen.return_value.__sub__.return_value)
            self.assertEqual(mkLen.return_value.__sub__.call_args_list,
                             [mk.call(1)])
            self.assertEqual(mkLen.call_args_list,
                             [mk.call(self.locs)])

        self.assertEqual(self.Location.level, 2)
