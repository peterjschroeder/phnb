#!/usr/bin/env python3

from pnb.parsing import parse_xml_into_nodes
from pnb.pnbtreebrowser import PNBTreeBrowser
from pnb.urwid_pnb_tree import PNBUrwidNode
from pnb.io import get_tree_xml_from_disk
import pnb.config as config

import os
import urwid

def main():
    tree = get_tree_xml_from_disk()
    root, base_xml_nodes = parse_xml_into_nodes(tree, PNBUrwidNode)
    pnbtb = PNBTreeBrowser(root)
    main_loop = urwid.MainLoop(pnbtb.view, pnbtb.palette)
    main_loop.run()

main()
