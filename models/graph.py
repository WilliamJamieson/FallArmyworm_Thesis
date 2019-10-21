import pickle   as pickle

import source.hint as hint


# MUST be Adjusted for corrected paths
hex_1x1   = '/home/william/Dropbox/Research/Parallel_FallArmyworm/models/hex_1x1.graph'
hex_2x2   = '/home/william/Dropbox/Research/Parallel_FallArmyworm/models/hex_2x2.graph'
hex_4x4   = '/home/william/Dropbox/Research/Parallel_FallArmyworm/models/hex_4x4.graph'
hex_8x8   = '/home/william/Dropbox/Research/Parallel_FallArmyworm/models/hex_8x8.graph'
hex_10x10 = '/home/william/Dropbox/Research/Parallel_FallArmyworm/models/hex_10x10.graph'
hex_25x25 = '/home/william/Dropbox/Research/Parallel_FallArmyworm/models/hex_25x25.graph'
hex_50x50 = '/home/william/Dropbox/Research/Parallel_FallArmyworm/models/hex_50x50.graph'


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
