from pnb.node import Node
import pnb.config as config

from xml.etree import ElementTree as ET
import json
import datetime

def print_r(
  node: Node, 
  level: int = 0,
  ) -> None:
  print(" " * level, node, sep="")
  kids = node.children
  if kids:
    for kid in kids:
      print_r(kid, level+1)

def str_tree(
    node: Node, 
  ) -> list:
  ''' Returns a list of strings, one for each node in the tree. '''

  def str_tree_helper(
      node: Node, 
      level: int = 0,
      output_list: list = None,
    ) -> list:
    if output_list == None:
      output_list = []
    output_list.append("  " * level + str(node))
    kids = node.children
    if kids:
      for kid in kids:
        str_tree_helper(kid, level+1, output_list)
    if level == 0:
      return output_list
    
  # TODO: Assuming root node for now
  output = []
  for node in node.children:
    output.extend(str_tree_helper(node))
  return output

def node_to_dict(node):
  dick = {}
  dick['done'] = node.done
  dick['contents'] = node.contents
  dick['children'] = [node_to_dict(n) for n in node.children]
  return dick

def node_to_json(node):
  return json.dumps(node_to_dict(node))

def print_recur_from_xml(root, it=0):
  ''' Utility function for debugging XML parsing issues. '''
  datalist = root.findall('data')
  if datalist:
    data = datalist[0]
    print(" "*it, data.text)

  kids = root.findall('node')

  it += 2
  for kid in kids:
    printRecur(kid, it)
 
# vim: set ts=2 et sw=2 sts=2
