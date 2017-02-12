from typing import TypeVar,Generic,List

class Node(object):
  def __str__(self) -> str:
    raise NotImplementedError

  @property
  def parent(self) -> 'Node':
    return self._parent

  @parent.setter
  def parent(self, parent: 'Node'):
    self._parent = parent

  @property
  def depth(self) -> int:
    if self.parent == None:
      return 0
    return self.parent.depth + 1
  
  @property
  def children(self) -> List['Node']:
    return self._children

  @children.setter
  def children(self, children: List['Node']):
    self._children = children

  @property
  def has_children(self):
    return len(self.children) > 0

  @property
  def first_child(self) -> 'Node':
    try: return self.children[0]
    except IndexError:
      return None

  @property
  def last_child(self) -> 'Node':
    try: return self.children[-1]
    except IndexError:
      return None

  def append_child(self, child: 'Node'):
    ''' Add a new child node. '''
    child.parent = self
    self.children.append(child)
    self.reset_percent()
  
  def insert_child(self, index: int, child: 'Node'):
    child.parent = self
    self.children.insert(index, child)
    self.reset_percent()

  @property
  def next_sib(self):
    if len(self.sibs) > 1:
      if self.sibindex < len(self.sibs) - 1:
        return self.sibs[self.sibindex + 1]
    return None

  @property
  def prev_sib(self):
    if len(self.sibs) > 1:
      if self.sibindex > 0:
        return self.sibs[self.sibindex - 1]
    return None

  @property
  def sibs(self):
    if self.parent == None:
      # TODO: learn how to do real exceptions boi
      # TODO: do this for anything which accesses parent.blah
      return [self]

    return self.parent.children

  @property
  def sibindex(self):
    return self.sibs.index(self)

  @property
  def all_descendents(self):
    ''' Recursively yield all child nodes under this one, including itself. '''
    yield self
    for child in self.children:
      yield from child.all_descendents

  @property
  def all_parents(self):
    ''' Recursively yield all of this node's parents, including root. '''
    parent = self.parent
    if parent != None:
      yield self.parent
      yield from parent.all_parents
    
  @property
  def empty_only_orphan(self):
    return self.contents == "" and len(self.sibs) == 1 and len(self.children) == 0
