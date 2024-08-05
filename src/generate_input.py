""" Easily generate trees with HybridSim from a combination of parameters
"""
from pathlib import Path
import subprocess
import ete3
import re
import os
import tempfile
import shutil
from contextlib import contextmanager
from itertools import product

coal_pattern = re.compile(r'\[Randomly selected coalescent trees \(with generating lineage trees as comments\)\](.*?)END;', re.DOTALL)
tree_pattern = re.compile(r'=(.*?)\n')

default_params = """
#NEXUS
begin hybridsim ;
    epochs = (1);
    speciation rate = (3 ,0.5);
    hybridization rate = (0 ,2);
    introgression rate = 0;
    hybridization distribution = (0.1 ,1 ,0.25 ,1 ,0.5 ,2);
    reticulation threshold = 1;
    reticulation function = linear;
    minimum reticulations = 2;
    reduce reticulations to = 2;
    coalesce = true;
    coalescence rate = {};
    halt time = 20;
    halt taxa = {};
    halt reticulations = 30;
    dollo sites per tree = 0;
    filo sites per tree = 0;
    number random trees = {};
end;
"""


@contextmanager
def temp_dir():
    temp_dir = tempfile.mkdtemp()
    try:
        yield os.path.abspath(temp_dir)
    finally:
        shutil.rmtree(temp_dir)


def generate_FACT(trees: list[str]) -> str:
    """ Generate the content for FACT package input nexus file 
    """
    content = "BEGIN TREES;\ntranslate\n"
    taxa = list(ete3.Tree(trees[0]).get_leaf_names())
    taxa_formated = []
    trees_formated = trees.copy()

    for i, tax in enumerate(taxa, start=1):
        taxa_formated.append(f"{i} random_taxa_{i}")
        for j, t in enumerate(trees_formated):
            trees_formated[j] = t.replace(tax + ":", str(i) + ":")
    content += ",\n".join(taxa_formated) + ";\n"

    for i, t in enumerate(trees_formated, start=1):
        content += f"tree {i} = {t}\n"
    content += "END;\n"

    return content

def generate_hs(hs: str, k: int, n: int, c: float, n_batch: int) -> list[list[str]]:
    """ Generate a list of phylogenetic trees with HybridSim
    """
    assert k > 0 and n > 0 and c > 0 and n_batch > 0, "Simulations parameters should be strictly positives"

    with temp_dir() as nexus_dir:
        # Write the params in the input file
        params = default_params.format(c, n, k*n_batch)
        file_in = f"{nexus_dir}/{k}x{n}x{c}_in.nexus"
        file_out = f"{nexus_dir}/{k}x{n}x{c}_out.nexus"
        with open(file_in, 'w') as f:
            f.write(params)

        # Run the simulation
        java_cmd = [shutil.which("java"), "-jar", hs, "-i", file_in, "-o", file_out]
        try:
            subprocess.run(java_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            print(f"An error occurred: {e}")

        # Read the output file and parse regex
        with open(file_out, 'r') as f:
            content = f.read()

        match = coal_pattern.search(content)
        if not match:
            raise ValueError(f"error in the {block} regex pattern on file {file_out}")
        tree_block = match.group(1)
        trees = tree_pattern.findall(tree_block)

    return [trees[i*k:(i+1)*k] for i in range(n_batch)]


K = [90, 70, 50, 30, 10] # values for number of trees
N = [50, 40, 30, 20, 10] # values for number of leaves
C = [10, 7.5, 5, 2.5, 1] # valurs for coalescence rate
NB_BATCH = 5 # number of batch per combination of parameters

DIR_NWK = Path("datasets/eval/HS") # directory to store input files
DIR_FACT = Path("datasets/eval/FACT") # directory to store nexus files for FACT package
HS_PATH = "/home/maggie/Dev/HybridSim/hybridsim319.jar" # path to the hybridsim java program

for k, n, c in product(K, N, C):
    batches = generate_hs(HS_PATH, k, n, c, NB_BATCH)
    for i, b in enumerate(batches):
        path_nwk = DIR_NWK / (f"k{k}_n{n}_c{c}_b{i}.txt")
        path_nexus = DIR_FACT / (f"k{k}_n{n}_c{c}_b{i}.nexus")
        with open(path_nwk, 'w') as f:
            f.write("\n".join(b))
        with open(path_nexus, 'w') as f:
            f.write(generate_FACT(b))
