""" Run several instance of primconstree and extended majority rule
    on different datasets, compute metrics, and save results in a file.
"""
import logging
import json
import os
from itertools import product
import timeit
from Bio.Phylo.Consensus import majority_consensus
from Bio import Phylo
import ete3
from utils.trees import phylo_to_ete3, read_trees
from primconstree.algorithm import primconstree
from utils.distances import average_rf, average_bsd
from utils.misc import create_unique_file


def consensus(input_trees: list, alg: list) -> tuple[list[ete3.Tree], ete3.Tree, timeit.Timer]:
    """ Compute the consensus tree from a list of input trees using the specified algorithm

    Args:
        input_trees (list): list of input trees (ete3 for pct, Bio.Phylo for maj)
        alg (str): algorithm to use (pct, old_pct, maj)

    Returns:
        tuple: input trees, consensus, timit timer for benchmark
    """
    if alg == "pct":
        cons = primconstree(input_trees, False, False, False)
        tm = timeit.Timer(lambda: primconstree(input_trees, False, False, False))
        return input_trees, cons, tm
    if alg == "old_pct":
        cons = primconstree(input_trees, True, False, False)
        tm = timeit.Timer(lambda: primconstree(input_trees, True, False, False))
        return input_trees, cons, tm
    if alg == "maj":
        cons = phylo_to_ete3(majority_consensus(input_trees, 0))
        tm = timeit.Timer(lambda: majority_consensus(input_trees, 0))
        input_ete3 = [phylo_to_ete3(t) for t in input_trees]
        return input_ete3, cons, tm
    raise ValueError(f"Unknown algorithm {alg}")


def eval_consensus(alg: str, input_trees: list, benchmark: int) -> dict:
    """ Compute consensus trees and metrics for several batches of input trees

    Args:
        alg (str): algorithm to use (pct, old_pct, maj)
        input_trees (list): list of input trees (ete3 for pct, Bio.Phylo for maj)
        benchmark (int): number of iterations for benchmark (0 for no benchmark)

    Returns:
        dict: input and consensus as newick strings, metrics
    """
    logging.info("Processing algorithm %s", alg)

    batch_input, batch_cons, tm = consensus(input_trees, alg)
    if benchmark > 0:
        duration = tm.timeit(benchmark)
    else:
        duration = 0

    return {
        "cons": batch_cons.write(),
        "rf": average_rf(batch_input, batch_cons),
        "bsd": average_bsd(batch_input, batch_cons, True),
        "duration": duration
    }


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

INPUT_DIR = "datasets/eval/HS" # directory to take the inputs from
RESULTS_FILE = "outputs/eval/HS.json" # file to output the results
K = [90, 70, 50, 30, 10] # values for number of trees
N = [50, 40, 30, 20, 10] # values for number of leaves
C = [10, 7.5, 5, 2.5, 1] # valurs for coalescence rate
NB_BATCH = 5 # number of batch per combination of parameters
BENCHMARK = 2 # number of iteration on benchmark execution time (0 for no benchmark)


# Execute evaluation on parameters combinations
combinations = []
for k, n, c, b in product(K, N, C, range(NB_BATCH)):
    logging.info("Processing combination k=%i n=%i c=%i b=%i batches, with %i benchmark iterations",
                k, n, c, b, BENCHMARK)

    filename = f"{INPUT_DIR}/k{k}_n{n}_c{c}_b{b}.txt"
    input_ete3 = read_trees(filename)
    input_bio = list(Phylo.parse(filename, "newick"))

    comb = {
        "file": filename,
        "k": k,
        "n": n,
        "c": c,
        "batch": b,
        "benchmark": BENCHMARK,
        "inputs": [t.write() for t in input_ete3],
        "pct": eval_consensus("pct", input_ete3, BENCHMARK),
        "old_pct": eval_consensus("old_pct", input_ete3, BENCHMARK),
        "maj": eval_consensus("maj", input_bio, BENCHMARK)
    }
    combinations.append(comb)


# Save results
result_file = create_unique_file(RESULTS_FILE)
with open(result_file, "w") as f:
    json.dump(combinations, f, indent=4)

logging.info("Saved results to %s", result_file)
