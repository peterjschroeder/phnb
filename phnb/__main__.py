#!/usr/bin/env python3

import phnb.config as config
from phnb.io import get_tree_xml_from_disk
from phnb.parsing import parse_xml_into_nodes
from phnb.phnb_tree_browser import PHNBTreeBrowser
from phnb.phnb_urwid_node import PHNBUrwidNode

import os
import urwid
import subprocess

def main():
  # Disable flow control (ctrl s / ctrl q)
  subprocess.Popen(['/bin/stty','-ixon'])

  tree = get_tree_xml_from_disk()
  root, base_xml_nodes = parse_xml_into_nodes(tree, PHNBUrwidNode)
  phnbtb = PHNBTreeBrowser(root)
  main_loop = urwid.MainLoop(phnbtb.view, phnbtb.palette)
  main_loop.run()

main()
 
# vim: ts=2 et sw=2 sts=2
