import urwid
import os
from phnb.phnb_tree_walker import PHNBTreeWalker
from phnb.phnb_tree_listbox import PHNBTreeListBox

class PHNBTreeBrowser:
  palette = [
    ('body', 'dark gray', 'black'),
    ('parent', 'light gray', 'black'),
    ('edit', 'light red', 'white', 'standout'),
    ('focus', 'white', 'black','underline'),
    ('head', 'light blue', 'black', 'standout'),
    ('foot', 'dark green', 'black'),

    ('key', 'light cyan', 'black','underline'),
    ('title', 'white', 'black', 'bold'),
    ('flag', 'dark gray', 'light gray'),
    ('error', 'dark red', 'light gray'),
    ]

  footer_text = [
    ('title', "Example Data Browser"), "  ",
    ('key', "UP"), ",", ('key', "DOWN"), ",",
    ('key', "PAGE UP"), ",", ('key', "PAGE DOWN"),
    "  ",
    ('key', "+"), ",",
    ('key', "-"), "  ",
    ('key', "LEFT"), "  ",
    ('key', "HOME"), "  ",
    ('key', "END"), "  ",
    ('key', "Q"),
    ]

  def __init__(self, root):
    self.topnode = root.first_child
    self.header = urwid.Text("Welcome to PHNB!")
    self.footer = urwid.Text(self.footer_text, align='left')
    self.listbox = PHNBTreeListBox(walker=PHNBTreeWalker(self.topnode), browser=self)

    # ??
    self.listbox.offset_rows = 10

    # make the listbox easily visible from nodes
    root.listbox = self.listbox

    self.view = urwid.Frame(
      urwid.AttrMap(self.listbox, 'body'),
      header=urwid.AttrMap(self.header, 'head'),
      footer=urwid.AttrMap(self.footer, 'foot'))

 
# vim: ts=2 et sw=2 sts=2
