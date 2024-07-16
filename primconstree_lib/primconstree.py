import logging
import networkx as nx
import ete3
from super_graph import SuperGraph
from mst_to_consensus import remove_unecessary_nodes
from misc import read_trees, create_unique_file


def primconstree(inputfile: str, format: int = 0, outputfile: str = None, modified_prim: bool = True, 
                avg_on_merge: bool = False, debug: bool = False) -> ete3.Tree:
    """ Generate the primconstree tree
        arguments:
            - inputfile (str): file to get the input trees from
            - format (int): the newick format (from ete3)
            - outputfile (str): the outputfile to write in newick (same format as input) (if None doesn't write)
            - modified_prim (boolean): if True use the last criterion (degree of included vertex)
            - avg_on_merge (boolean): if True average the edges length when deleting redundant internal node, else sum
            - debug (boolean): if True, draw the super graph the MST with unnecessary nodes and the consensus tree
        returns:
            - (ete3.Tree): The consensus tree as a Tree object
    """
    logging.info("Generating PrimConsTree from input file %s", inputfile)

    inputs = read_trees(inputfile, 0)
    super_graph = SuperGraph(inputs)
    logging.debug("Super-Graph Generated")
    if debug:
        super_graph.display_info(False)
        super_graph.draw_graph("frequency", False, False)

    super_graph.modified_prim(super_graph.root, modified_prim)
    logging.debug("MST found with modified prim (modified_prim = %s)", str(modified_prim))
    if debug:
        super_graph.draw_graph("avglen", False, True)

    tree = super_graph.to_tree(super_graph.root)
    if debug:
        print("\nConsensus tree with unecessary nodes\n")
        print(tree)

    remove_unecessary_nodes(tree, list(super_graph.leaves.values()), avg_on_merge)
    tree = super_graph.replace_leaves_names(tree)
    logging.debug("Proper consensus tree generated from MST (avg_on_merge = %s)", str(avg_on_merge))
    if debug:
        print("\nFinal consensus tree\n")
        print(tree)

    if debug:
        print("\nNodes distances to parent:")
        for n in tree.traverse():
            print("\t", n.name, "=>", n.dist)

    if outputfile:
        logging.info("Saving consensus tree to output file : %s", outputfile)
        filename_unique = create_unique_file(outputfile)
        if filename_unique != outputfile:
            logging.warning("File %s already exists, writing to : %s", outputfile, filename_unique)
        tree.write(outfile=filename_unique, format=0)
        logging.info("Saved consensus tree to output file : %s", filename_unique)

    return Tree
    