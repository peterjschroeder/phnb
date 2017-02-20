#!/usr/bin/env python3

import pnb.config as config
from pnb.io import get_tree_xml_from_disk
from pnb.parsing import parse_xml_into_nodes
from pnb.pnb_tree_browser import PNBTreeBrowser
from pnb.pnb_urwid_node import PNBUrwidNode

import os
import urwid
import subprocess

def main():
  # Disable flow control (ctrl s / ctrl q)
  subprocess.Popen(['/usr/bin/stty','-ixon'])

  tree = get_tree_xml_from_disk()
  root, base_xml_nodes = parse_xml_into_nodes(tree, PNBUrwidNode)
  pnbtb = PNBTreeBrowser(root)
  main_loop = urwid.MainLoop(pnbtb.view, pnbtb.palette)
  main_loop.run()

main()
 
# vim: ts=2 et sw=2 sts=2
