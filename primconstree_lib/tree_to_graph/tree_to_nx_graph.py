import os
import sys


# Get the current directory of the script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Add the parent directory to the system path
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from tree.rename_set_of_trees_avg_branch_lengths import (
    rename_set_of_trees_compute_avg_branch_length,
)
