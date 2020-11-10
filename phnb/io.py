import phnb.config as config
from phnb.parsing import convert_tree_to_xml

from xml.dom import minidom
from xml.etree import ElementTree as ET
from pprint import pprint
import datetime

def get_tree_xml_from_disk():
    return ET.parse(config.tree_file, parser=ET.XMLParser(encoding='iso-8859-1')).getroot()

def save_tree_to_disk(root_node):
    xmltree = convert_tree_to_xml(root_node)
    # Use xml.dom.minidom to write out with spaces representing nest depth
    xmltree = ET.ElementTree(ET.fromstring(minidom.parseString(ET.tostring(xmltree.getroot())).toprettyxml(indent="    ")))
    xmltree.write(config.tree_file)

def phnblog(*messages):
    output = (datetime.datetime.now().isoformat(), ) + messages
    with open(config.log_file, "a") as outfile:
        outfile.write("\n" + " ".join(str(message) for message in output))
 
