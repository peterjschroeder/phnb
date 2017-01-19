from .node import Node
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

def convert_tree_to_xml(root_node):
  def create_xml(node):
    xml_node = ET.Element('node')

    if node.done != None:
      xml_node.set('type', 'todo') 
      donestate = node.done and 'yes' or 'no'
      xml_node.set('done', donestate)

    data = ET.Element('data')
    data.text = node.contents
    xml_node.append(data)

    if node.has_children:
        xml_children = (create_xml(child) for child in node.children)
        for child in xml_children:
            xml_node.append(child)

    return xml_node

  root_xml_node = ET.Element('tree')
  if root_node.has_children:
      base_child_nodes = (create_xml(node) for node in root_node.children)

      for base_child_node in base_child_nodes:
        root_xml_node.append(base_child_node)

  tree = ET.ElementTree(root_xml_node)
  return tree

def pnblog(*messages):
  output = (datetime.datetime.now().isoformat(), ) + messages
  
  with open("/tmp/outfile.out", "a") as outfile:
    outfile.write("\n" + " ".join(str(message) for message in output))
