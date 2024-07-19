from pathlib import Path
import logging
import timeit
import json
from misc import read_trees, phylo_to_ete3
from primconstree import primconstree
from Bio.Phylo.Consensus import majority_consensus
from Bio.Phylo import parse


INPUT_DIR = "datasets/eval/vary_n"
OUTPUT_FILE = "outputs/vary_n.json"
NWCK_FORMAT = 5
NB_BATCH = 10
BENCHMARK = False
NUM_IT = 100

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Parsing all inputs, building primconstree and extended majority rule
logging.info("Reading trees from input directory %s", INPUT_DIR)
folder = Path(INPUT_DIR)
files = [file.name for file in folder.iterdir() if file.is_file()]

data = []
for file in files:
    file_path = INPUT_DIR + "/" + file
    input_ete3 = read_trees(file_path, NWCK_FORMAT)
    input_bio = list(parse(file_path, "newick"))

    instance = {"prim": {"batchs": []}, "maj": {"batchs": []}}
    instance["file"] = file_path
    instance["nb_batch"] = NB_BATCH
    instance["k"] = int(len(input_ete3)/NB_BATCH)
    instance["n"] = int(len(input_ete3[0].get_leaves()))

    logging.info("Processing file %s: nb batch = %i, k = %i, n = %i",
                 file, NB_BATCH, instance["k"], instance["n"])
    if BENCHMARK:
        logging.info("Benchmarking with %i iterations", NUM_IT)

    for i in range(0, len(input_ete3), instance["k"]):
        p_batch = {}
        m_batch = {}
        p_batch["input"] = input_ete3[i:i+instance["k"]]
        m_batch["input"] = input_bio[i:i+instance["k"]]
        p_batch["cons"] = primconstree(
            p_batch["input"], 0, None, True, False, False)
        m_batch["cons"] = majority_consensus(m_batch["input"], 0)
        if BENCHMARK:
            t_p = timeit.Timer(lambda: primconstree(
                p_batch["input"], 0, None, True, False, False))
            p_batch["dur"] = t_p.timeit(NUM_IT)
            t_m = timeit.Timer(lambda: majority_consensus(m_batch["input"], 0))
            m_batch["dur"] = t_m.timeit(NUM_IT)
        else:
            p_batch["dur"], m_batch["dur"] = None, None

        # Converting biopython tree to ete3 tree to facilitate comparison
        m_batch["input"] = [phylo_to_ete3(t) for t in m_batch["input"]]
        m_batch["cons"] = phylo_to_ete3(m_batch["cons"])
        instance["prim"]["batchs"].append(p_batch)
        instance["maj"]["batchs"].append(m_batch)

    data.append(instance)

for i, d in enumerate(data):
    k = d["k"]
    for p_batch, m_batch in zip(d["prim"]["batchs"], d["maj"]["batchs"]):
        p_cons = p_batch["cons"]
        m_cons = m_batch["cons"]
        p_batch["rf_sum"] = 0
        m_batch["rf_sum"] = 0
        for p_tree, m_tree in zip(p_batch["input"], m_batch["input"]):
            p_rf, p_max_rf = p_tree.robinson_foulds(
                p_cons, unrooted_trees=True)[:2]
            m_rf, m_max_rf = m_tree.robinson_foulds(
                m_cons, unrooted_trees=True)[:2]
            p_batch["rf_sum"] += p_rf / p_max_rf
            m_batch["rf_sum"] += m_rf / m_max_rf
        p_batch["rf_avg"] = p_batch["rf_sum"] / k
        m_batch["rf_avg"] = m_batch["rf_sum"] / k
    d["prim"]["rf_avg_values"] = [b["rf_avg"] for b in d["prim"]["batchs"]]
    d["maj"]["rf_avg_values"] = [b["rf_avg"] for b in d["maj"]["batchs"]]
    d["prim"]["rf_avg"] = sum(d["prim"]["rf_avg_values"]) / NB_BATCH
    d["maj"]["rf_avg"] = sum(d["maj"]["rf_avg_values"]) / NB_BATCH


with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    logging.info("Writing results to %s", OUTPUT_FILE)
    save = data.copy()
    for d in save:
        del d["prim"]["batchs"]
        del d["maj"]["batchs"]
    json.dump(data, f, indent=4)

logging.info("Process finished")
