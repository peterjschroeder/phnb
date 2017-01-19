from .util import str_tree, pnblog
from .ui_movement import UIMovement
from .ui_editing import UINodeEditor

import curses

class UI(UIMovement, UINodeEditor):
  def __init__(self, scr, root) -> None:
    curses.use_default_colors()
    for i in range(0, curses.COLORS):
      curses.init_pair(i, i, -1)
    self.scr = scr
    self.root = root
    self.root.ui = self

    #TODO: ensure root has children
    self.selected = self.root.first_child

    # Make the cursor very visible
    curses.curs_set(2)

    h, w = scr.getmaxyx()
    # with 1-char border
    #win_tree = (h - 2, w - 4, 1, 2)
    win_tree = (h-1, w, 0, 0)
    self.win_tree = scr.derwin(*win_tree)

    win_info = (1, w, h-1, 0)
    self.win_info = scr.derwin(*win_info)
    self.win_info.bkgd('$')

    # If you want to debug window position
    #self.win_tree.bkgd('@')

    self.redraw_ui()

  def redraw_ui(self):
    (h, w) = self.scr.getmaxyx()
    self.scr.clear()
    # global ui elements can go here
    self.scr.refresh()

    self.redraw_tree()

  def redraw_tree(self):
    self.win_tree.clear()
    h, w = self.win_tree.getmaxyx()
    

    y = 0
    for node in self.root.visible_descendents:
      #make pad?
      self.win_tree.addstr(y, 0, str(node))
      y += node.height
    # XXX
    #y = 0
    #for node in self.root.visible_descendents:
      #y += self.display_node(node, y)
    
    #for i, out in enumerate(str_tree(self.root)):
      #if i >= h:
        #break
      #self.win_tree.addstr(i, 0, out)

    # TODO: move cursor to position of selected node
    # TODO: helper functions for movement through tree
    # TODO LATER: proper scrolling
    # TODO: break before bottom of screen, scrolling, etc

    self.win_tree.refresh()

  def redraw_info(self):
    self.win_info.clear()
    #h, w = self.win_info.getmaxyx()
    # TODO: populate

    self.win_info.refresh()

  def wait_input(self):
    self.win_tree.refresh()
    self.win_info.refresh()
    key = self.scr.getch()
    if key == curses.KEY_RIGHT:
      (y, x) = self.win_tree.getyx()
      self.win_tree.move(y, x + 1)
    elif key == curses.KEY_LEFT:
      self.win_tree.move(0,0)
    elif key == ord('i'):
      self.win_tree.insch("X")
    elif key == ord('c'):
      self.win_tree.clear()
    elif key == ord('r'):
      self.win_tree.refresh()
    elif key == ord('t'):
      self.redraw_tree()
    elif key == ord('R'):
      self.redraw_ui()
    elif key == ord('\n'):
      self.redraw_ui()
