#!/usr/bin/env python3

from .node import Node
from .util import str_tree, node_to_dict, node_to_json, pnblog
from .io import parse_xml_into_nodes
from .pnbtreebrowser import PNBTreeBrowser

import os
import urwid

# TODO: get homedir
tree_file = '/home/glenn/.pnb'

def main():
    root, base_xml_nodes = parse_xml_into_nodes(tree_file)
    pnbtb = PNBTreeBrowser(root)
    main_loop = urwid.MainLoop(pnbtb.view, pnbtb.palette)
    main_loop.run()

main()
