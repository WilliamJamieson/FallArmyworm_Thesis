import os

import pickle   as pickle

import source.hint as hint

graph_path = os.path.dirname(os.path.abspath(__file__))
print('Graph path is: {}'.format(graph_path))


# MUST be Adjusted for corrected paths
hex_1x1   = '{}/hex_1x1.graph'.format(graph_path)
hex_2x2   = '{}/hex_2x2.graph'.format(graph_path)
hex_4x4   = '{}/hex_4x4.graph'.format(graph_path)
hex_8x8   = '{}/hex_8x8.graph'.format(graph_path)
hex_10x10 = '{}/hex_10x10.graph'.format(graph_path)
hex_25x25 = '{}/hex_25x25.graph'.format(graph_path)
hex_50x50 = '{}/hex_50x50.graph'.format(graph_path)


def graph(side: int) -> hint.graph:
    """
    Read a graph from data

    Args:
        side: the side count

    Returns:
        a prebuilt graph read from a file
    """

    if side == 1:
        file_name = hex_1x1
    elif side == 2:
        file_name = hex_2x2
    elif side == 4:
        file_name = hex_4x4
    elif side == 8:
        file_name = hex_8x8
    elif side == 10:
        file_name = hex_10x10
    elif side == 25:
        file_name = hex_25x25
    elif side == 50:
        file_name = hex_50x50
    else:
        raise FileExistsError('No file for graph of that side')

    with open(file_name, 'rb') as graph_file:
        return pickle.load(graph_file)
