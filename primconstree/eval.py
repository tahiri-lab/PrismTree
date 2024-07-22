""" Run several instance of primconstree and extended majority rule 
    on different datasets, compute metrics, and save results in a file.
"""
from pathlib import Path
import os
import logging
import timeit
import json
from Bio.Phylo.Consensus import majority_consensus
from Bio.Phylo import parse
from misc import read_trees, phylo_to_ete3
from primconstree import primconstree
from distances import average_rf

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

INPUT_DIR = "datasets/eval/vary_k"
OUTPUT_FILE = "outputs/eval/vary_k.json"
NWCK_FORMAT = 5
NB_BATCH = 10
BENCHMARK = 10


def run_primconstree(input_trees, k, benchmark):
    instance = {"batches": [], "durations": [], "rf": []}
    for i in range(0, len(input_trees), k):
        batch_input = input_trees[i:i+k]
        batch = {
            "input": batch_input,
            "cons": primconstree(batch_input, None, 0, True, False, False)
        }
        instance["batches"].append(batch)
        instance["rf"].append(average_rf(batch["input"], batch["cons"]))
        if benchmark > 0:
            tm = timeit.Timer(lambda: primconstree(batch_input, None, 0, True, False, False))
            batch["duration"] = tm.timeit(benchmark)
            instance["durations"].append(batch["duration"])
    return instance


def run_majority(input_trees, k, benchmark):
    instance = {"batches": [], "durations": [], "rf": []}
    for i in range(0, len(input_trees), k):
        batch_input = input_trees[i:i+k]
        batch = {
            "input": [phylo_to_ete3(t) for t in batch_input],
            "cons": phylo_to_ete3(majority_consensus(batch_input, 0)),
            "duration": None
        }
        instance["batches"].append(batch)
        instance["rf"].append(average_rf(batch["input"], batch["cons"]))
        if benchmark > 0:
            tm = timeit.Timer(lambda: majority_consensus(batch_input, 0))
            batch["duration"] = tm.timeit(benchmark)
            instance["durations"].append(batch["duration"])
    return instance


def run_eval(input_dir, n_batch, benchmark):
    files = [file.name for file in Path(input_dir).iterdir() if file.is_file()]
    eval_data = []
    for filename in files:
        path = input_dir + "/" + filename
        input_ete3 = read_trees(path, NWCK_FORMAT)
        input_bio = list(parse(path, "newick"))

        if len(input_ete3) % n_batch != 0:
            raise ValueError(f"Number of trees in file {path} = {len(input_ete3)}"
                             f"is not compatible with number of batchs {n_batch}")

        k = int(len(input_ete3)/n_batch)
        n = int(len(input_ete3[0].get_leaves()))

        logging.info("Processing file %s: nb batch = %i, k = %i, n = %i", filename, n_batch, k, n)
        if benchmark > 0:
            logging.info("Benchmarking with %i iterations", benchmark)

        eval_data.append({
            "file": path,
            "nb_batch": n_batch,
            "k": k,
            "n": n,
            "prim": run_primconstree(input_ete3, k, benchmark),
            "maj": run_majority(input_bio, k, benchmark)
        })

    return eval_data

logging.info("Running evaluation")
data = run_eval(INPUT_DIR, NB_BATCH, BENCHMARK)

logging.info("Saving results to %s", OUTPUT_FILE)
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    save = data.copy()
    for d in save:
        del d["prim"]["batches"]
        del d["maj"]["batches"]
    json.dump(data, f, indent=4)

logging.info("Process finished")
