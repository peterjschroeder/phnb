import phnb.config as config
from phnb.parsing import convert_tree_to_xml

from xml.etree import ElementTree as ET
from pprint import pprint
import datetime

def get_tree_xml_from_disk():
  return ET.parse(config.tree_file, parser=ET.XMLParser(encoding='iso-8859-1')).getroot()

def save_tree_to_disk(root_node):
  xmltree = convert_tree_to_xml(root_node)
  # TODO: use xml.dom.minidom or such to write out with spaces representing nest depth
  xmltree.write(config.tree_file)

def phnblog(*messages):
  output = (datetime.datetime.now().isoformat(), ) + messages
  with open(config.log_file, "a") as outfile:
    outfile.write("\n" + " ".join(str(message) for message in output))
 
# vim: ts=2 et sw=2 sts=2
