from xml.etree import ElementTree as ET

def parse_xml_into_nodes(tree, node_class):
  ''' 
  Parse an old-style hnb xml structure into pnb's internal representation.
  
  Starting with the 'tree' element of the config file (the root of the structure),
  iterate through and create appropriate node objects for each one. 
  '''

  root_node = node_class(contents='I AM ROOT', root=None)

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
      child_node = node_class(contents=data.text, done=done, root=root_node)
      parent_node.append_child(child_node)

    # Iterate through the children of this node
    xml_kids = xml_node.findall('node')
    for xml_kid in xml_kids:
      parse_xml(xml_kid, child_node)

  base_xml_nodes = [n for n in tree.getchildren()]
  for base_xml_node in base_xml_nodes:
    parse_xml(base_xml_node, root_node)
  return root_node, base_xml_nodes

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
