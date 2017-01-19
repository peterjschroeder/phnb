# -*- coding: UTF-8 -*-
# TODO: clean up hierarchy
#from .pnbnode import PNBNode
from .urwid_pnb_tree import PNBUrwidNode

from xml.etree import ElementTree as ET
from pprint import pprint

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

def parse_xml_into_nodes(xmlfile):
  ''' 
  Parse an old-style hnb xml structure into pnb's internal representation.
  
  Starting with the 'tree' element of the config file (the root of the structure),
  iterate through and create appropriate node objects for each one. 
  '''

  root_node = PNBUrwidNode(contents='I AM ROOT', root=None)

  def parse_xml(xml_node, parent_node):
    datalist = xml_node.findall('data')

    if datalist:
      data = datalist[0]

      # If the node has the 'todo' tag, set its done state based on the 'done' tag
      node_type = xml_node.get('type') 
      done = None
      if node_type == 'todo':
        # 'yes' for 'todo' => True, anything else (usually 'no') => False
        done = xml_node.get('done') == 'yes' or False

      # Create the new node object and add it to the list of its parent's children
      child_node = PNBUrwidNode(contents=data.text, done=done, root=root_node)
      parent_node.append_child(child_node)

    # Iterate through the children of this node
    xml_kids = xml_node.findall('node')
    for xml_kid in xml_kids:
      parse_xml(xml_kid, child_node)

  tree = ET.parse(xmlfile).getroot()
  base_xml_nodes = [n for n in tree.getchildren()]
  for base_xml_node in base_xml_nodes:
    parse_xml(base_xml_node, root_node)
  return root_node, base_xml_nodes

