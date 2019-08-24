import pickle   as pickle

import source.hint as hint


# MUST be Adjusted for corrected paths
hex_10x10 = '/home/william/Dropbox/Research/Parallel_FallArmyworm/data/hex_10x10.graph'
hex_25x25 = '/home/william/Dropbox/Research/Parallel_FallArmyworm/data/hex_25x25.graph'
hex_50x50 = '/home/william/Dropbox/Research/Parallel_FallArmyworm/data/hex_50x50.graph'


def graph(side: int) -> hint.graph:
    """
    Read a graph from data

    Args:
        side: the side count

    Returns:
        a prebuilt graph read from a file
    """

    if side == 10:
        file_name = hex_10x10
    elif side == 25:
        file_name = hex_25x25
    elif side == 50:
        file_name = hex_50x50
    else:
        raise FileExistsError('No file for graph of that side')

    with open(file_name, 'rb') as graph_file:
        return pickle.load(graph_file)
