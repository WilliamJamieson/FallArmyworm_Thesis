import sys
import datetime

import source.space.grid as grid


# print('Creating 10x10 at: {}'.format(datetime.datetime.now()))
# graph = grid.Hexagon.grid(10, 10, True, True)
# print('Size of graph: {}'.format(sys.getsizeof(graph)))
# print('Saving 10x10 at: {}'.format(datetime.datetime.now()))
# graph.save('hex_10x10.graph')
#
# print('Creating 25x25 at: {}'.format(datetime.datetime.now()))
# graph = grid.Hexagon.grid(25, 25, True, True)
# print('Size of graph: {}'.format(sys.getsizeof(graph)))
# print('Saving 25x25 at: {}'.format(datetime.datetime.now()))
# graph.save('hex_25x25.graph')

print('Creating 50x50 at: {}'.format(datetime.datetime.now()))
graph = grid.Hexagon.grid(50, 50, True, True)
print('Size of graph: {}'.format(sys.getsizeof(graph)))
print('Saving 50x50 at: {}'.format(datetime.datetime.now()))
graph.save('hex_50x50.graph')

# print('Creating 100x100 at: {}'.format(datetime.datetime.now()))
# graph = space_grid.Hexagon.grid(100, 100, True, True)
# print('Size of graph: {}'.format(sys.getsizeof(graph)))
# print('Saving 100x100 at: {}'.format(datetime.datetime.now()))
# graph.save('hex_100x100.graph')
# print('End of graph save: {}'.format(datetime.datetime.now()))
