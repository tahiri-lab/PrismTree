""" Run several instance of primconstree and extended majority rule
    on different datasets, compute metrics, and save results in a file.
"""
import logging
import json
import os
import subprocess
from itertools import product
import timeit
from Bio.Phylo.Consensus import majority_consensus
from Bio import Phylo
import ete3
from utils.trees import phylo_to_ete3, read_trees, map_from_fact, set_cst_length    
from primconstree.algorithm import primconstree
from utils.distances import average_rf, average_bsd, average_tqd
from utils.misc import create_unique_file


PATH_TO_FACT1 = "/PATH/TO/fact" #FACT compiled binary
PATH_TO_FACT2 = "/PATH/TO/fact2" #FACT2 compiled binary


def consensus(filename: str, alg: list) -> tuple[ete3.Tree, timeit.Timer]:
    """ Compute the consensus tree from a list of input trees using the specified algorithm

    Args:
        filename (str): appropriate input file for the consensus method
        alg (str): algorithm to use (pct, old_pct, maj)

    Returns:
        tuple: consensus, timit timer for benchmark
    """
    def fcdt(input_file):
        cmd = [PATH_TO_FACT2, "freq", input_file]
        result = subprocess.run(cmd, capture_output=True, text=True)
        cons = ete3.Tree(map_from_fact(result.stdout.replace('\n', ';')))
        return set_cst_length(cons, 1)

    if alg == "pct":
        input_trees = read_trees(filename)
        cons = primconstree(input_trees, False, False, False)
        tm = timeit.Timer(lambda: primconstree(input_trees, False, False, False))
        return cons, tm
    if alg == "old_pct":
        input_trees = read_trees(filename)
        cons = primconstree(input_trees, True, False, False)
        tm = timeit.Timer(lambda: primconstree(input_trees, True, False, False))
        return cons, tm
    if alg == "maj":
        input_trees = list(Phylo.parse(filename, "newick")) 
        bio_cons = majority_consensus(input_trees, 0)
        cons = phylo_to_ete3(bio_cons)
        tm = timeit.Timer(lambda: majority_consensus(input_trees, 0))
        return cons, tm
    if alg == "freq":
        cons = fcdt(filename)
        tm = timeit.Timer(lambda: fcdt(filename))
        return cons, tm
    if alg == "maj_plus":
        cmd = ["./src/utils/fact1.sh", PATH_TO_FACT1, filename, "100000000"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        cons = ete3.Tree(map_from_fact(result.stdout.replace('\n', ';')))
        cons = set_cst_length(cons, 1)
        return cons, None
    
    raise ValueError(f"Unknown algorithm {alg}")


def eval_consensus(alg: str, filename: str, input_trees: list[ete3.Tree], benchmark: int) -> dict:
    """ Compute consensus trees and metrics for several batches of input trees

    Args:
        alg (str): algorithm to use (pct, old_pct, maj)
        filename (str): input file for the consensus
        input_trees (list): list of input trees as ete3 objects
        benchmark (int): number of iterations for benchmark (0 for no benchmark)

    Returns:
        dict: input and consensus as newick strings, metrics
    """
    logging.info("Processing algorithm %s", alg)

    cons, tm = consensus(filename, alg)
    if benchmark > 0 and tm is not None:
        duration = tm.timeit(benchmark)
    else:
        duration = 0

    return {
        "cons": cons.write(),
        "rf": average_rf(input_trees, cons),
        "bsd": average_bsd(input_trees, cons, True),
        "tdist": average_tqd(input_trees, cons, "triplet_dist"),
        "qdist": average_tqd(input_trees, cons, "quartet_dist"),
        "duration": duration
    }


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

INPUT_TXT = "datasets/eval/HS" # directory to take the inputs from
INPUT_NEX = "datasets/eval/FACT" # directory to take the inputs for FACT2 algorithms
RESULTS_FILE = "outputs/eval/HS-FINAL.json" # file to output the results
K = [10, 30, 50, 70, 90] # values for number of trees
N = [10, 20, 30, 40, 50] # values for number of leaves
C = [10, 7.5, 5, 2.5, 1] # values for coalescence rate
ALGS = ["pct", "freq", "maj", "old_pct"] # algorithms to perfoem (maj, pct, old_pct, freq)
NB_BATCH = 5 # number of batch per combination of parameters
BENCHMARK = 3 # number of iteration on benchmark execution time (0 for no benchmark)


# Execute evaluation on each parameters combinations
combinations = []
for k, n, c, b in product(K, N, C, range(NB_BATCH)):
    logging.info("Processing combination k=%i n=%i c=%i b=%i batches, with %i benchmark iterations",
                k, n, c, b, BENCHMARK)

    file_txt = f"{INPUT_TXT}/k{k}_n{n}_c{c}_b{b}.txt"
    file_nex = f"{INPUT_NEX}/k{k}_n{n}_c{c}_b{b}.nexus"
    input_trees = read_trees(file_txt)

    # Save parameters
    comb = {
        "file": file_txt,
        "k": k,
        "n": n,
        "c": c,
        "batch": b,
        "benchmark": BENCHMARK,
        "inputs": [t.write() for t in input_trees]
    }
    
    # Evaluate consensus trees
    for a in ALGS:
        input_file = file_nex if a in ["freq", "maj_plus"] else file_txt
        comb[a] = eval_consensus(a, input_file, input_trees, BENCHMARK)

    combinations.append(comb)


# Save results
result_file = create_unique_file(RESULTS_FILE)
with open(result_file, "w") as f:
    json.dump(combinations, f, indent=4)

logging.info("Saved results to %s", result_file)
