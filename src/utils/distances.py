""" Implementation of metrics to compare trees
"""
from math import sqrt
from itertools import combinations
import ete3
from Bio.Phylo import read
from io import StringIO
import subprocess


def average_rf(input_trees: list[ete3.Tree], consensus: ete3.Tree) -> float:
    """ Compute the average normalized Robinson and Foulds distance between the input trees and the consensus

    Args:
        input_trees (list[ete3.Tree]): the list of input trees
        consensus (ete3.Tree): the consensus computed with any algorithm

    Return:
        float: the average normalized rf distance
    """
    rf_sum = 0
    for tree in input_trees:
        rf, max_rf = tree.robinson_foulds(consensus, unrooted_trees=True)[:2]
        rf_sum += rf / max_rf
    return rf_sum / len(input_trees)


def average_tqd(input_trees: list[ete3.Tree], consensus: ete3.Tree, exec: str) -> float:
    """ Compute the average triplet/quartet distance between the input trees and the consensus

    Args:
        input_trees (list[ete3.Tree]): the list of input trees
        consensus (ete3.Tree): the consensus computed with any algorithm
        exec (str): quartet_dist | triplet_dist

    Return:
        float: the average triplet distance
    """
    dist = 0
    minus = 0
    for tree in input_trees:
        cmd = ["./src/utils/tqdist.sh", exec, tree.write(format=9), consensus.write(format=9)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        try:
            dist += float(result.stdout)
        except Exception:
            print(f"WARNING error computing the {exec} distance metric !!!!\n executable stdrr: '{result.stderr}'")
            print(consensus.write())
            print(tree.write())
            print()
            minus += 1
    return dist/(len(tree) - minus)


def bsd(t1: ete3.Tree, t2: ete3.Tree, normalize: bool = True) -> float:
    """ Compute the Branch Score Distance between two trees with branch length
    
    Args:
        t1 (ete3.Tree): tree to compare
        t2 (ete3.Tree): tree to compare
        normalize (bool): if True, the distance between each bipartition is normalized with respect to the lenght of its tree
    
    Return:
        float: the bsd between t1 and t2
    """
    # Get distance of each bipartition in each tree
    dist_t1 = {}
    for node in t1.traverse():
        if node.up:
            clade = frozenset(node.get_leaf_names())
            dist_t1[clade] = node.dist
    size_t1 = sum(dist_t1.values()) if normalize else 1

    dist_t2 = {}
    for node in t2.traverse():
        if node.up:
            clade = frozenset(node.get_leaf_names())
            dist_t2[clade] = node.dist
    size_t2 = sum(dist_t2.values()) if normalize else 1

    # Fill the bipartition missing in one tree with 0
    for n in dist_t1:
        if n not in dist_t2:
            dist_t2[n] = 0
    for n in dist_t2:
        if n not in dist_t1:
            dist_t1[n] = 0

    # Compute the distance
    diffs = [((dist_t1[n] / size_t1) - (dist_t2[n] / size_t2))**2 for n in dist_t1]
    return sqrt(sum(diffs))


def average_bsd(input_trees: list[ete3.Tree], consensus: ete3.Tree, normalize: bool = True) -> float:
    """ Compute the average Branch Score Distance between the input trees and the consensus

    Args:
        input_trees (list[ete3.Tree]): the list of input trees
        consensus (ete3.Tree): the consensus computed with any algorithm
        normalize (bool): if True, distance between 2 trees is normalized with respect to the total length of each tree

    Return:
        float: the average normalized bsd distance
    """
    total = 0
    for tree in input_trees:
        total += bsd(tree, consensus, normalize)
    return total / len(input_trees)
