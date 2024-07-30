""" Given a list of K and a list of N, generate trees with hybridsim for each combination of size
"""
from genericpath import exists
from itertools import product
from pathlib import Path
import subprocess
import re
import os

N = [10, 20, 30, 40, 50] # Max 50
K = [10, 30, 50, 70, 90]

PATH_TO_HS = "/home/maggie/Dev/HybridSim/hybridsim319.jar"
DIR_HS = "src/experiment/data/hybrid_sim"
DIR_NEXUS_IN = DIR_HS + "/nexus_in"
DIR_NEXUS_OUT = DIR_HS + "/nexus_out"
DIR_COAL = DIR_HS + "/coal"
DIR_RND = DIR_HS + "/rnd"

rnd_pattern = re.compile(r'\[Randomly selected lineage \(i.e. no coalescent\) trees\](.*?)END;', re.DOTALL)
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
    coalescence rate = 6;
    halt time = 20;
    halt taxa = {};
    halt reticulations = 30;
    dollo sites per tree = 0;
    filo sites per tree = 0;
    number random trees = {};
end;
"""

os.makedirs(DIR_NEXUS_IN, exist_ok=True)
os.makedirs(DIR_NEXUS_OUT, exist_ok=True)
os.makedirs(DIR_COAL, exist_ok=True)
os.makedirs(DIR_RND, exist_ok=True)

for k, n in product(K, N):
    params = default_params.format(n, k)
    filename = f"/{k}x{n}.nexus"
    with open(DIR_NEXUS_IN + filename, 'w') as f:
        f.write(params)

    absolute_path_in = Path(DIR_NEXUS_IN + filename).resolve()
    absolute_path_out = Path(DIR_NEXUS_OUT + filename).resolve()
    java_cmd = ["java", "-jar", PATH_TO_HS, "-i", absolute_path_in, "-o", absolute_path_out]
    try:
        result = subprocess.run(java_cmd)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

    with open(absolute_path_out, 'r') as f:
        content = f.read()

    rnd_match = rnd_pattern.search(content)
    coal_match = coal_pattern.search(content)

    if rnd_match:
        rnd_tree_block = rnd_match.group(1)
    else:
        raise ValueError("error in the regex pattern on file " + filename)
    if coal_match:
        coal_tree_block = coal_match.group(1)
    else:
        raise ValueError("error in the regex pattern coal on file " + filename)

    rnd_trees = tree_pattern.findall(rnd_tree_block)
    coal_trees = tree_pattern.findall(coal_tree_block)

    filename2 = f"/{k}x{n}.txt"
    with open(DIR_RND + filename2, 'w') as f:
        f.write('\n'.join(rnd_trees))
    with open(DIR_COAL + filename2, 'w') as f:
        f.write('\n'.join(coal_trees))
