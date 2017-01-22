import pnb.config as config
from pnb.parsing import convert_tree_to_xml

from xml.etree import ElementTree as ET
from pprint import pprint
import datetime

def get_tree_xml_from_disk():
  return ET.parse(config.tree_file).getroot()

def save_tree_to_disk(root_node):
  xmltree = convert_tree_to_xml(root_node)
  xmltree.write(config.tree_file)

def pnblog(*messages):
  output = (datetime.datetime.now().isoformat(), ) + messages
  with open(config.log_file, "a") as outfile:
    outfile.write("\n" + " ".join(str(message) for message in output))
