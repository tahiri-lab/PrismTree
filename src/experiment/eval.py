""" Run several instance of primconstree and extended majority rule
    on different datasets, compute metrics, and save results in a file.
"""
import os
import json
import logging
import timeit
from io import StringIO
from itertools import product
from Bio.Phylo.Consensus import majority_consensus
from Bio import Phylo
import ete3
from ..primconstree.misc import phylo_to_ete3
from ..primconstree.algorithm import primconstree
from .distances import average_rf, average_bsd
from .tree_gen import generate_trees


def consensus(input_trees: list, alg: list) -> tuple[list[ete3.Tree], ete3.Tree, timeit.Timer]:
    """ Compute the consensus tree from a list of input trees using the specified algorithm

    Args:
        input_trees (list): list of input trees (ete3 for pct, Bio.Phylo for maj)
        alg (str): algorithm to use (pct, old_pct, maj)

    Returns:
        tuple: input trees, consensus, timit timer for benchmark
    """
    if alg == "pct":
        cons = primconstree(input_trees, None, 0, False, False, False)
        tm = timeit.Timer(lambda: primconstree(input_trees, None, 0, False, False, False))
        return input_trees, cons, tm
    if alg == "old_pct":
        cons = primconstree(input_trees, None, 0, True, False, False)
        tm = timeit.Timer(lambda: primconstree(input_trees, None, 0, True, False, False))
        return input_trees, cons, tm
    if alg == "maj":
        cons = phylo_to_ete3(majority_consensus(input_trees, 0))
        tm = timeit.Timer(lambda: majority_consensus(input_trees, 0))
        input_ete3 = [phylo_to_ete3(t) for t in input_trees]
        return input_ete3, cons, tm
    raise ValueError(f"Unknown algorithm {alg}")


def run_consensus_batch(alg: str, input_trees: list, k: int,
                        benchmark: int, nwk_format: int = 5) -> dict:
    """ Compute consensus trees and metrics for several batches of input trees

    Args:
        alg (str): algorithm to use (pct, old_pct, maj)
        input_trees (list): list of input trees (ete3 for pct, Bio.Phylo for maj)
        k (int): number of trees per batch
        benchmark (int): number of iterations for benchmark (0 for no benchmark)
        nwk_format (int, optional): newick format to write trees. Defaults to 5.

    Returns:
        dict: input and consensus as newick strings, metrics
    """
    logging.info("Processing batches with algorithm %s", alg)
    instance = {"batches": [], "durations": [], "rf": [], "bsd": []}
    for i in range(0, len(input_trees), k):
        batch_input, batch_cons, tm = consensus(input_trees[i:i+k], alg)
        batch = {
            "input": [t.write(format=nwk_format) for t in batch_input],
            "cons": batch_cons.write(format=nwk_format)
        }
        instance["batches"].append(batch)
        instance["rf"].append(average_rf(batch_input, batch_cons))
        instance["bsd"].append(average_bsd(batch_input, batch_cons, True))
        if benchmark > 0:
            batch["duration"] = tm.timeit(benchmark)
            instance["durations"].append(batch["duration"])
    return instance


def run_combination(input_dir: str, k: int, n: int, c:int, nb_batch: int,
                    benchmark: int) -> dict:
    """ Run consensus algorithms and collect metrics on a combination of parameters k and n.
        Algorithms used are PrimConsTree (pct), old version of PrimConsTree (old_pct)
        and Extended majority rule (maj).

    Args:
        input_dir (str): directory containing input trees file, must contain a file named kxn.txt
        k (int): number of trees per batch
        n (int): number of leaves per tree
        c (int): coalescence rate
        nb_batch (int): number of batches to process, input file must contain at least k*nb_batch trees
        benchmark (int): number of iterations for benchmark (0 for no benchmark)

    Returns:
        dict: parameters and results for each algorithm
    """
    filename = f"{input_dir}/{k}x{n}.txt"
    nwks = generate_trees("src/experiment/data/hs/nexus_in", "src/experiment/data/hs/nexus_out", k*nb_batch, n, c, "coal")
    input_ete3 = [ete3.Tree(nwk) for nwk in nwks]
    input_bio = [Phylo.read(StringIO(nwk), "newick") for nwk in nwks]
    if len(input_ete3) != k * nb_batch:
        raise ValueError(f"Input sizes of {filename} ({len(input_ete3)}) does not match the number of k x batches : {k} x {nb_batch}")

    prim = run_consensus_batch("pct", input_ete3, k, benchmark)
    old_prim = run_consensus_batch("old_pct", input_ete3, k, benchmark)
    maj = run_consensus_batch("maj", input_bio, k, benchmark)
    comb = {
        "file": filename,
        "nb_batch": nb_batch,
        "benchmark": benchmark,
        "k": k,
        "n": n,
        "c": c,
        "pct": prim,
        "old_pct": old_prim,
        "maj": maj
    }
    return comb


def run_all_combinations(input_dir: str, k_values: list, n_values: list, c_values: list,
                         nb_batch: int, benchmark: int) -> dict:
    """ Run all combinations of parameters k and n on a directory of input files

    Args:
        input_dir (str): directory containing input trees files
        k_values (list): list of k values (number of trees per batch)
        n_values (list): list of n values (number of leaves per tree)
        c_values (list): list of c values (coalescence rate)
        nb_batch (int): number of batches per input file
        benchmark (int): number of iterations for benchmark (0 for no benchmark)

    Returns:
        dict: results for each combination
    """
    combs = {}
    for k, n, c in product(k_values, n_values, c_values):
        logging.info("Processing combination k=%i n=%i c=%i with %i batches, and %i benchmark iterations",
                    k, n, c, nb_batch, benchmark)
        combs[f"{k}x{n}x{c}"] = run_combination(input_dir, k, n, c, nb_batch, benchmark)
    return combs


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

INPUT_DIR = "src/experiment/data/hybrid_sim/coal"
OUTPUT_FILE = "src/experiment/results/hs-coal2.json"
N = [10, 20  ] #, 30, 40, 50]
K = [10, 30  ] #, 50, 70, 90]
C = [10, 7.5 ] #, 5, 2.5, 1]
NWCK_FORMAT = 5
BATCH_PER_COMB = 3
BENCHMARK = 10

combinations = run_all_combinations(INPUT_DIR, K, N, C, BATCH_PER_COMB, BENCHMARK)

os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
with open(OUTPUT_FILE, "w") as f:
    json.dump(combinations, f, indent=4)
