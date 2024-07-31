""" Easily generate trees with HybridSim from a combination of parameters
"""
from pathlib import Path
import subprocess
import re
import os

PATH_TO_HS = "/home/maggie/Dev/HybridSim/hybridsim319.jar"

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
    coalescence rate = {};
    halt time = 20;
    halt taxa = {};
    halt reticulations = 30;
    dollo sites per tree = 0;
    filo sites per tree = 0;
    number random trees = {};
end;
"""


def generate_trees(nexus_in, nexus_out, k, n, c=1, block="coal"):
    os.makedirs(nexus_in, exist_ok=True)
    os.makedirs(nexus_out, exist_ok=True)

    # Write the params in the input file
    params = default_params.format(c, n, k)
    filename = f"/{k}x{n}x{c}.nexus"
    with open(nexus_in + filename, 'w') as f:
        f.write(params)

    # Run the simulation
    absolute_path_in = Path(nexus_in + filename).resolve()
    absolute_path_out = Path(nexus_out + filename).resolve()
    java_cmd = ["java", "-jar", PATH_TO_HS, "-i", absolute_path_in, "-o", absolute_path_out]
    try:
        subprocess.run(java_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

    # Read the output file and parse regex
    with open(absolute_path_out, 'r') as f:
        content = f.read()

    if block == "rnd":
        pattern = rnd_pattern
    else:
        pattern = coal_pattern

    match = pattern.search(content)
    if not match:
        raise ValueError(f"error in the {block} regex pattern on file {filename}")
    tree_block = match.group(1)
    trees = tree_pattern.findall(tree_block)

    return trees
