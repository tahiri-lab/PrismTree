from pathlib import Path
import logging
from misc import read_trees, phylo_to_ete3
from primconstree import primconstree
from Bio.Phylo.Consensus import majority_consensus
from Bio.Phylo import parse
import timeit
import json

INPUT_DIR = "datasets/eval/vary_k"
NWCK_FORMAT = 5
BENCHMARK = False
NUM_IT = 100

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

folder = Path(INPUT_DIR)
files = [file.name for file in folder.iterdir() if file.is_file()]
prim_data = []
maj_data = []

# Parsing all inputs, building primconstree and extended majority rule
logging.info("Reading trees from input directory %s", INPUT_DIR)
for file in files:
    prim = {}
    maj = {}
    try:
        file_path = INPUT_DIR + "/" + file
        prim["input"] = read_trees(file_path, NWCK_FORMAT)
        maj["input"] = list(parse(file_path, "newick"))
        logging.info("Generate Primconstree")
        prim["cons"] = primconstree(prim["input"], 0, None, True, False, False)
        logging.info("Generate Majority rule")
        maj["cons"] = majority_consensus(maj["input"], 0)
        if BENCHMARK:
            logging.info("Benchmark Primconstree")
            t_p = timeit.Timer(lambda: primconstree(prim["input"], 0, None, True, False, False))
            prim["dur"] = t_p.timeit(NUM_IT)
            logging.info("Benchmark Majority rule")
            t_m = timeit.Timer(lambda: majority_consensus(maj["input"], 0))
            maj["dur"] = t_m.timeit(NUM_IT)
        else:
            prim["dur"], maj["dur"] = None, None
    except Exception as e:
        logging.error("Could not read file %s : %s", file, str(e))
        continue
    prim["k"], maj["k"] = len(prim["input"]), len(maj["input"])
    prim["n"], maj["n"] = len(prim["input"][0].get_leaf_names()), len(maj["input"][0].get_terminals())
    maj["input"] = [phylo_to_ete3(t) for t in maj["input"]]
    maj["cons"] = phylo_to_ete3(maj["cons"])
    prim_data.append(prim)
    maj_data.append(maj)
    logging.info("Read %i trees, with %i leaves from %s", prim["k"], prim["n"], file)
logging.info("All input parsed and consensus done")


# Computing the distances between primconstree consensus and input trees
for i, p in enumerate(prim_data):
    cons = p["cons"]
    total_dist = 0
    for t in p["input"]:
        rf, max_rf, _, _, _, _, _ = t.robinson_foulds(cons, unrooted_trees=True)
        normalized_rf = rf / max_rf
        total_dist += normalized_rf
    p["rf"] = total_dist

# Computing the distances between primconstree consensus and input trees
for i, m in enumerate(maj_data):
    cons = m["cons"]
    total_dist = 0
    for t in m["input"]:
        rf, max_rf, _, _, _, _, _ = t.robinson_foulds(cons, unrooted_trees=True)
        normalized_rf = rf / max_rf
        total_dist += normalized_rf
    m["rf"] = total_dist


with open("outputs/test.json", "w") as f:
    save = []
    for p, m in zip(prim_data, maj_data):
        save.append({"primconstree": {"k": p["k"], "n": p["n"], "rf": p["rf"], "duration": p["dur"]}, "majority": {"k": m["k"], "n": m["n"], "rf": m["rf"], "duration": m["dur"]}})
    json.dump(save, f, indent=4)
