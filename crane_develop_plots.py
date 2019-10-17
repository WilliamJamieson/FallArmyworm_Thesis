import sys

import plots.development as dev


if __name__ == '__main__':
    if len(sys.argv) > 1:
        save_name = sys.argv[1]
    else:
        save_name = None

    dev.create_plots(save_name)
