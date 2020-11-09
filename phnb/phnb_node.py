from typing import TypeVar,Generic,List
from phnb.node import Node
from phnb.io import phnblog

# weh
class TODONode:
  @property
  def done(self):
    return self._done

  @done.setter
  def done(self, done):
    self._done = done
    self.reset_percent()

  @property
  def percent(self):
    if self._percent == None:
        self._percent = self.get_percent()
    return self._percent

  @percent.setter
  def percent(self, percent):
    self._percent = percent

  def reset_percent(self):
    self.percent = None
    for n in self.all_parents:
      if n.percent == None:
        break
      n.percent = None
    if self._widget != None:
      self.refresh_percent_display()

  def get_percent(self):
    if self.done == None:
      return None
    elif self.done == True:
      return 1
    elif self.done != False:
      raise ValueError('Non-bool value for done!')

    if not self.has_children:
      return 0
      
    percent = 0
    todonodes = 0
    for node in self.children:
      if node.percent != None:
        todonodes += 1
        percent += node.percent

    if todonodes > 0:
      return (percent / todonodes)
    else:
      return 0

class PHNBNode(Node, TODONode):
  def __init__(self, 
    root: 'Node',
    contents: str = "",
    parent: 'Node' = None, 
    children: List['Node'] = None,
    expanded: bool = False,
    sticky_expanded: bool = False,
    done: bool = None,
    is_temp: bool = False,
  ) -> None:

    if not children:
      children = []

    self._widget = None
    self._percent = None
    self._done = done

    # the only node which shouldn't have root passed in is the root node.
    if root is None:
        self._root = self
    else:
        self._root = root

    self.parent = parent
    self.children = children
    self.contents = contents
    self.expanded = expanded
    self.sticky_expanded = sticky_expanded
    self.is_temp = is_temp

  @property
  def root(self):
    return self._root
  
  @root.setter
  def root(self, root):
    self._root = root

  @property
  def is_root(self):
    return self.root == self

  def __str__(self):
    return str(self.contents)

  @property
  def contents(self) -> str:
    return self._contents

  @contents.setter
  def contents(self, contents: str):
    self._contents = contents

  @property
  def expanded(self):
    # there may be a more elegant way to do this
    return self._expanded or self._sticky_expanded

  @expanded.setter
  def expanded(self, expanded):
    self._expanded = expanded 

  @property
  def sticky_expanded(self):
    return self._sticky_expanded

  @sticky_expanded.setter
  def sticky_expanded(self, sticky_expanded):
    self._sticky_expanded = sticky_expanded 

  @property
  def prefix(self):
    prefix = "   "
    percent = self.percent
    done = self.done
    if percent != None:
      if done == True:
          prefix = '[X]'
      elif percent == 0:
        prefix = '[ ]'
      elif percent == 1:
        prefix = '100'
      else:
        prefix = '%2d%%' % (self.percent * 100)
    else:
      if self.children:
        if self.sticky_expanded:
          prefix = " - "
        else:
          prefix = " + "
    return prefix

  @property
  def output_str(self):
      ''' Return an appropriately nested text representation of the node,
          prefixed with spaces to display as <code> in markup. '''
      return "    " * self.depth + self.prefix + " " + str(self)
  
  def find_child_by_prefix(self, prefix):
    ''' `prefix` here means prefix search, not UI prefix as above '''
    for child in self.children:
        if child.contents[:len(prefix)] == prefix:
            if not child.is_temp:
                return child
    return None
 
# vim: ts=2 et sw=2 sts=2
