from utils.trees import read_trees
from primconstree import algorithm
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str, help='input file path')
    parser.add_argument('version', type=int, help='Primconstree version for the MST criteria (0): last version, (1): previous version', nargs="?", default=0)
    parser.add_argument('avg_on_merge', type=int, help='if (0): sum branch lenght on merging two branches, if (1): average them', nargs="?", default=0)
    parser.add_argument('debug', type=int, help='if (0): return the consensus immediatly, if (1): print informations on several steps and draw graphs', nargs="?", default=0)

    args = parser.parse_args()
    filename = args.file
    old_pct = bool(args.version)
    avg_on_merge = bool(args.avg_on_merge)
    debug = bool(args.debug)

    input_trees = read_trees(filename)
    consensus = algorithm.primconstree(input_trees, old_pct, avg_on_merge, debug)
    print(consensus.write())

if __name__ == '__main__':
    main()