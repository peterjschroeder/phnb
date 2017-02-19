#!/usr/bin/python3

# TODO: set up python folding on lappy
# TODO: make scrolling show few line buffer

import os
import urwid
from urwid.util import move_prev_char, move_next_char
from pnb.pnb_tree_widget import PNBTreeWidget
from pnb.pnb_tree_walker import PNBTreeWalker
from pnb.pnb_urwid_node import PNBUrwidNode
from pnb.io import pnblog, save_tree_to_disk
import pnb.config as config

# there should be a cleaner way to access the Edit functions.
fucker = urwid.Edit()

# XXX in use temporarily for checking/incrementing/decrementing reference counts
class Lawl:
  pass
lawl = Lawl()
lawl.marked_node = None


class PNBTreeListBox(urwid.ListBox):
  def __init__(self, walker, browser):
    self.browser = browser
    self.mode = 'main'
    self.text_buffer = ''
    self.temp_node = None
    self.pressed_key = None
    self.__super.__init__(walker)

    # TODO: have these associated with the class itself, not each object
    #     (or even better, read them from a config file)
    self.mode_mapping = {
      'main': self.mode_main_keypress,
      'main-select': self.mode_main_select_keypress,
      'main-newnode': self.mode_main_newnode_keypress,
      'main-subnode': self.mode_main_subnode_keypress,
      'edit': self.mode_edit_keypress,
      'confirm-delete': self.mode_confirm_delete_keypress,
      'vim-cmd': self.mode_vim_cmd_keypress,
    }

  @property
  def mode(self):
    return self._mode

  @mode.setter
  def mode(self, mode):
    self._mode = mode
    self.add_footer_text(mode)

  def keypress(self, size, key):
    self.size = size
    self.pressed_key = key
    pnblog(self.pressed_key)

    w, node = self.body.get_focus()

    # TODO: have this done by focus status
    node.widget.contents_widget.set_attr_map({None: node.widget.palette})
    node.widget.prefix_widget.set_attr_map({None: node.widget.palette})

    if self.mode in self.mode_mapping:
      keypress_func = self.mode_mapping[self.mode]
      keypress_func()

    # TODO: make this clean up the prefix too (general display cleanup function?)
    # get the (possibly) new widget/node and perform any necessary actions on them
    focus_widget, node = self.body.get_focus()
    focus_widget.contents_widget.set_attr_map({None: 'focus'})
    focus_widget.prefix_widget.set_attr_map({None: 'focus'})

    return self.pressed_key


  def mode_main_keypress(self):
    w, node = self.body.get_focus()
    key = self.pressed_key
    # TODO: intercept ctrl c
    # TODO: ctrl c / ctrl v copy and paste

    keymap = config.per_mode_mappings['main']
    if key in keymap:
      commands = keymap[key]
      for command in commands:
        func = getattr(self, command)
        func()

    elif (key != None and fucker.valid_char(key)):
      self.main_mode_input_char()
    
  def mode_main_select_keypress(self):
    w, node = self.body.get_focus()
    key = self.pressed_key
    if key == 'backspace':
      self.backspace()
    else:
      self.mode_main_keypress()

  def mode_main_newnode_keypress(self):
    w, node = self.body.get_focus()
    key = self.pressed_key
    if key == 'backspace':
      self.backspace()
    elif key == 'right':
      self.mode_main_keypress()
    elif key == 'enter':
      #TODO: function
      self.commit_newnode()
    elif (key != None and fucker.valid_char(key)):
      #TODO: consolidate this and others into single keypress func
      self.main_mode_input_char()
      node.widget.add_text(key)
    else:
      self.mode_main_keypress()
      self._del_node(node)
      self.mode = 'main'

  def mode_main_subnode_keypress(self):
    w, node = self.body.get_focus()
    key = self.pressed_key

    if key == 'enter':
      self.mode = 'main'
      node.widget.update_contents()
    elif key == 'backspace':
      node.contents = node.contents[:-1]
      node.widget.update_contents()
    elif (key != None and fucker.valid_char(key)):
      node.widget.add_text(key)
      return None
    elif key == 'left':
      #TODO: figure out more general way to clean up subnode
      self._del_node(node)
      self.mode = 'main'
      return None
    else:
      self.mode_main_keypress()

  def mode_confirm_delete_keypress(self):
    w, node = self.body.get_focus()
    key = self.pressed_key

    if key in ('y', 'Y', 'delete'):
      self._del_node(node)
      self.mode = 'main'
    elif key in ('n', 'N', 'enter'):
      self.mode = 'main'

    return None

  def mode_edit_keypress(self):
    w, node = self.body.get_focus()
    key = self.pressed_key

    # pass through keypresses to the editing widget
    if w.selectable():
      key = w.keypress(self.size, key)
    
    return key


  def mode_vim_cmd_keypress(self):
    w, node = self.body.get_focus()
    key = self.pressed_key

    # TODO: make these make the newly created node appear in the 
    #     correct place relative to the selected node?
    if key in ('i', 'a', 'I', 'A'):
      self.mode = 'main'

    vim_mode_cmd_mapping = {
      'j': self.move_focus_to_next_sib,
      }
      
    return None

  def create_temp_node(self, parent_node):
    done = (parent_node.done == None) and None
    temp_node = PNBUrwidNode(contents=self.text_buffer,
                   root=parent_node.root,
                   done=done,
                   is_temp=True)

    self.temp_node = temp_node
    parent_node.append_child(temp_node)
    lawl.marked_node = self.temp_node

  def commit_newnode(self):
    self.temp_node.is_temp = False
    self.temp_node = None
    self.text_buffer = ''
    self.mode = 'main'

  def delete_node(self):
    widget, node = self.body.get_focus()

    sibs = node.parent.children
    index = sibs.index(node)
    
    # TODO: add a deletion dialog
    if node.has_children:
      #self.add_footer_text('Node has children! Confirm deletion? [Y/n]')
      self.mode = 'confirm-delete'
      return None

    self._del_node(node)

  def _del_node(self, node):
    # TODO: this leaks memory. why?
    par = node.parent
    sibs = par.children
    index = sibs.index(node)
    if len(sibs) == 1:
      if par.is_root:
        self.add_footer_text("can't delete last node!")
        return 
      else:
        del sibs[0]
        self.change_focus(par)
        par.widget.refresh_prefix()
        node.destruct()

    elif len(sibs) > 1:
      del sibs[index]
      if index >= len(sibs):
        delindex = -1
      else:
        delindex = index
      self.change_focus(sibs[delindex])

      node.destruct()

  def get_temp_node_index(self, parent_node):
    index = parent_node.children.index(self.temp_node)
    return index

  def del_temp_node(self, parent_node):
    ''' Deletes the temporary node attached to a particular parent node. 
      Returns a safe index on which to focus. '''
    # TODO: check for memory leaks // other references to this node?
    index = self.get_temp_node_index(parent_node)
    self.temp_node.destruct()
    self.temp_node = None
    del parent_node.children[index]

    if index >= 1:
      delindex = index - 1
    else:
      delindex = 0

    return delindex

  def mark_node(self):
    widget, node = self.body.get_focus()
    lawl.marked_node = node

  def debug_marked_node(self):
    import gc
    referrers = gc.get_referrers(lawl.marked_node)
    pnblog("NUM REFS:", len(referrers))
    for i in referrers:
      pnblog(i)

  def email_subtree(self):
    # TODO: thread
    # TODO: use subprocess or such, send errors to pnblog
    from email.mime.text import MIMEText
    widget, node = self.body.get_focus()
    #output = '\nGenerated from PNB: \n'
    for n in node.all_descendents:
      output += "  " + n.output_str + '\n'
    msg = MIMEText(output, 'plain')
    msg['To'] = config.email_addr
    msg['Subject'] = str(node)
    pnblog(msg.as_string())
    p = os.popen(config.email_cmd,'w')
    p.write(msg.as_string())
    p.close()

  def debug_node(self):
    widget, node = self.body.get_focus()
    pnblog(node.__dict__)
    pnblog(node.widget.__dict__)

  def try_to_delete_node(self):
    lol_node = lawl.marked_node
    lol_node._widget._node = None
    lol_node._widget = None

  def change_focus(self, target, *args):
    self.text_buffer = ''
    self.temp_node = None
    if self.mode == 'main-subnode':
      self.mode = 'main'
    self.__super.change_focus(self.size, target)

  def mouse_event(self, size, event, button, col, row, focus):
    # TODO: make this select // expand // drag nodes
    #pnblog(self.body.get_focus())
    #pnblog(size, event, button, col, row, focus)
    #pnblog(self.body.get_focus())
    #if self.is_leaf or event != 'mouse press' or button!=1:
      #return False

    #if row == 0 and col == self.indent_cols:
      #self.expanded = not self.expanded
      #return True

    return False

  def add_header_text(self, text):
    # more 'set header text' for now
    # TODO: make the header a queue or overlay or whatever
    self.browser.header.set_text(" " + text)

  def add_footer_text(self, text):
    # more 'set mode text' for now
    self.browser.footer.base_widget.set_text(text)

  def buffer_change_focus(self, target):
    self.__super.change_focus(self.size, target)

  def move_focus_to_parent(self):
    widget, node = self.body.get_focus()
    parent = node.parent
    if not parent.is_root:

      # special case the deletion of an empty node if it's the only child
      # TODO: this doesn't seem to get called?
      if node.empty_only_orphan:
        node.destruct()
        del parent.children[0]

      parwidget = parent._widget
      if not parwidget.node.sticky_expanded:
        parwidget.expanded = False
      if not node.sticky_expanded:
        node.expanded = False

      self.change_focus(parent)

  def move_focus_to_prev_sib(self):
    widget, node = self.body.get_focus()
    prev_sib = node.prev_sib
    if prev_sib:
      self.change_focus(prev_sib)

  def move_focus_to_next_sib(self):
    # TODO: make sure scrolling behavior leaves some context at top
    widget, node = self.body.get_focus()
    next_sib = node.next_sib
    if next_sib:
      self.change_focus(next_sib)

  def move_focus_to_first_child(self):
    widget, node = self.body.get_focus()
    if not node.empty_only_orphan:
      if not node.first_child:
        # children of todo nodes are instantiated as uncompleted todo nodes
        done = (node.done == None) and None
        node.append_child(PNBUrwidNode(contents="",
                        root=node.root,
                        done=done)
                      )
        created_node = True
      else:
        created_node = False

      node.expanded = True
      self.change_focus(node.first_child)
      if created_node:
        self.mode = 'main-subnode'
      widget.refresh_contents_widget()
      widget.refresh_prefix()

  def move_focus_to_first_sib(self):
    widget, node = self.body.get_focus()
    parent = node.parent
    if parent:
      self.change_focus(parent.first_child)

  def move_focus_to_last_sib(self):
    widget, node = self.body.get_focus()
    parent = node.parent
    if parent:
      self.change_focus(parent.last_child)

  def backspace(self):
    widget, node = self.body.get_focus()
    if len(self.text_buffer) > 0:
      self.text_buffer = self.text_buffer[:-1]

      # if there's still text in the buffer after backspacing
      if len(self.text_buffer) > 0:
        # check if we match with an existing node
        pnblog('buffer', self.text_buffer)
        target_node = node.parent.find_child_by_prefix(self.text_buffer)

        if target_node != None:
          # we were in a state where there was no match and we'd created a new node
          # delete it it and return to select mode
          if self.mode == 'main-newnode':
            self.del_temp_node(node.parent)
            self.mode = 'main-select'
            self.buffer_change_focus(target_node)
          # we were already in select mode, select the appropriate node
          elif self.mode == 'main-select':
            if target_node != node:
              self.buffer_change_focus(target_node)

        # we didn't match, modify the temporary node
        else:
          self.temp_node.widget.set_text(self.text_buffer)

      # if we've backspaced back to nothing
      else:
        if self.mode == 'main-newnode':
          delindex = self.del_temp_node(node.parent)
          self.mode = 'main'
          self.change_focus(node.parent.children[delindex])
        elif self.mode == 'main-select':
          self.mode = 'main'
  
  def set_sticky_expand(self):
    widget, node = self.body.get_focus()
    widget.sticky_expanded = True
    widget.expanded = True

  def unset_sticky_expand(self):
    widget, node = self.body.get_focus()
    widget.sticky_expanded = False
    widget.expanded = False

  def toggle_todo(self):
    widget, node = self.body.get_focus()

    done = node.done

    # 'None' for done means it is not a todo node
    if done == None:
      node.done = False
    elif done != None:
      node.done = None

    widget.refresh_prefix()
    widget.refresh_parent_prefixes()

  def toggle_done(self):
    widget, node = self.body.get_focus()

    done = node.done
    if done != None:
      node.done = not done

      widget.refresh_prefix()
      widget.refresh_parent_prefixes()

  def save_tree(self):
    widget, node = self.body.get_focus()
    save_tree_to_disk(node.root)
    self.add_footer_text('Saved!')

  def start_editing(self):
    widget, node = self.body.get_focus()
    widget.start_editing()

  def main_mode_input_char(self):
    widget, node = self.body.get_focus()
    key = self.pressed_key

    self.text_buffer += key
    target_node = node.parent.find_child_by_prefix(self.text_buffer)

    # a match was found, change to it
    if target_node != None:
      self.mode = 'main-select'
      self.buffer_change_focus(target_node)
    # no match was found, and there's no temp node to append the character to
    else:
      # no node, but we have typed a character which creates unique node text
      if self.temp_node == None:
        # so create that node, and switch focus to it
        self.create_temp_node(node.parent)
        self.mode = 'main-newnode'
        self.buffer_change_focus(self.temp_node)

  def enter_vim_mode(self):
    self.mode = 'vim-cmd'

  def move_node_to_prev_sib(self):
    ''' Swap the node with its predecessor, if it exists. '''
    widget, node = self.body.get_focus()
    prev_sib = node.prev_sib
    if prev_sib and prev_sib != node:
      p = node.parent.children
      a = prev_sib.sibindex
      b = node.sibindex
      p[b], p[a] = p[a], p[b]

  def move_node_to_next_sib(self):
    ''' Swap the node with its successor, if it exists. '''
    widget, node = self.body.get_focus()
    next_sib = node.next_sib
    if next_sib and next_sib != node:
      p = node.parent.children
      a = next_sib.sibindex
      b = node.sibindex
      p[b], p[a] = p[a], p[b]

  def move_node_under_prev_sib(self):
    ''' Move the node under its predecessor, if it exists. '''
    widget, node = self.body.get_focus()
    prev_sib = node.prev_sib
    if prev_sib:
      del node.parent.children[node.sibindex]
      prev_sib.append_child(node)

      for n in prev_sib.all_descendents:
        n.widget.refresh()

  def move_node_under_grandparent(self):
    ''' Move the node under its parent's parent, if possible. '''
    widget, node = self.body.get_focus()
    par = node.parent
    if not par.is_root:
      del par.children[node.sibindex]

      par.parent.insert_child(par.sibindex + 1, node)

      par.widget.refresh()
      node.widget.refresh()
      for n in node.all_parents:
        n.widget.refresh()
  
  def move_node_and_below_under_prev_sib(self):
    # TODO: fix for "all nodes" case
    widget, node = self.body.get_focus()
    nodelist = node.parent.children[node.sibindex:]
    prev_sib = node.prev_sib

    if prev_sib:
      for node in nodelist:
        del node.parent.children[node.sibindex]
        prev_sib.append_child(node)

    prev_sib.widget.refresh()
    for node in nodelist:
      node.widget.refresh()
      for n in node.all_descendents:
        n.widget.refresh_cols()

  def move_node_and_below_under_grandparent(self):
    widget, node = self.body.get_focus()
    nodelist = node.parent.children[node.sibindex:]
    par = node.parent

    if not par.is_root:
      gpar = par.parent
      for node in reversed(nodelist):
        del par.children[node.sibindex]

        gpar.insert_child(par.sibindex + 1, node)
      
      par.widget.refresh()
      for n in nodelist:
        n.widget.refresh()
        for sn in n.all_descendents:
          sn.widget.refresh_cols()
 
# vim: set ts=2 et sw=2 sts=2
