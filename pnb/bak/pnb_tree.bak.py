#!/usr/bin/python3

import urwid
from urwid.wimp import SelectableIcon
from .pnbnode import PNBNode
from .util import pnblog

class PNBEdit(urwid.Edit):
    def keypress(self, size, key):
        if key == 'up':
            key = 'home'
        elif key == 'down':
            key = 'end'

        if key == 'enter':
            # this, uh, seems ugly
            edit_text = self.get_edit_text()
            self.tree_widget.node.contents = edit_text
            self.tree_widget._w = self.old_w
            self.tree_widget.contents_widget.original_widget.set_text(self.tree_widget.node.contents)
            self.tree_widget.editing = False
            return None

        key = self.__super.keypress(size, key)
        if key is not None:
            pnblog(key)
            raise ValueError("LDFJS")

class PNBTreeWidget(urwid.WidgetWrap):
    '''A widget representing something in a nested tree display.'''
    # TODO: revamp these settings, include done percentage
    # TODO: include urwid.CheckBox as an option for icon
    unexpanded_icon = SelectableIcon('  +', 2)
    expanded_icon = SelectableIcon('  -', 2)
    not_done_icon = SelectableIcon('[ ]', 2)
    done_icon = SelectableIcon('[X]', 2)

    def __init__(self, node):
        self._node = node
        self.is_leaf = node.children == []
        self.is_root = node.is_root
        self._expanded = False
        self._selectable = True
        self._contentswidget = None
        self._prefixwidget = None
        self.editing = False
        self.sticky_expanded = False
        widget = self.indented_widget
        self.__super.__init__(widget)

    @property
    def expanded(self):
        return self._expanded

    @expanded.setter
    def expanded(self, expanded):
        self._expanded = expanded
        self.update_prefix()

    @property
    def contents(self):
        return self.contents_widget.original_widget.get_text()[0]

    def selectable(self):
        return self._selectable

    @property
    def indented_widget(self):
        # TODO: fix the display of leaf vs. non-leaf widgets by having the expanded/not/etc icons reflect the actual state of the node
        if self.is_root:
            # Don't display the root node, but still set it up with the same fields as others
            widget = urwid.Columns(
                [('fixed', 4, urwid.Text('')),
                 urwid.Text('')], 
                dividechars=0)
        else:
            widget = urwid.Columns(
                [('fixed', 4, self.prefix_widget),
                 self.contents_widget], 
                dividechars=0)
        indent_cols = self.indent_cols
        return urwid.Padding(widget,
            width=('relative', 100), left=indent_cols)

    @property
    def indent_cols(self):
        depth = self.node.depth
            
        # correct for root
        if depth > 0:
            depth = depth - 1

        #TODO: get this value from config
        indent_cols_mult = 3

        return indent_cols_mult * depth

    @property
    def contents_widget(self):
        if self._contentswidget is None:
            self._contentswidget = urwid.AttrMap(urwid.Text(self.node.contents), 'body', 'focus')
        return self._contentswidget

    @contents_widget.setter
    def contents_widget(self, contents_widget):
        self._contentswidget = contents_widget
        self._w.base_widget.widget_list[1] = contents_widget

    @property
    def prefix_widget(self):
        if self._prefixwidget is None:
            self._prefixwidget = self.gen_prefix()
        return self._prefixwidget

    @prefix_widget.setter
    def prefix_widget(self, prefix_widget):
        self._prefixwidget = prefix_widget
        self._w.base_widget.widget_list[0] = prefix_widget

    def gen_prefix(self):
        # TODO: fix editing behavior
        # TODO: cache/memoize these
        return SelectableIcon(self.node.prefix, 1)

    def update_prefix(self):
        # TODO: check for percent, if there, display
        # TODO: if leaf node, display blank text widget or such
        if not self.is_root:
            self.prefix_widget = self.gen_prefix()

    def update_parent_prefixes(self):
        for node in self.node.all_parents:
            if not node.is_root:
                node.widget.update_prefix()

    @property
    def full_prefix_text(self):
        #TODO: use urwid.Padding instead
        edit_padding = ' ' * self.indent_cols
        edit_prefix = self.prefix_widget.get_text()[0]
        return edit_padding + edit_prefix + ' '


    @property
    def node(self):
        return self._node

    def next_inorder(self):
        '''Return the next PNBTreeWidget depth first from this one.'''
        # first check if there's a child widget
        firstchild = self.first_child()
        if firstchild is not None:
            return firstchild

        # now we need to hunt for the next sibling
        thisnode = self.node
        nextnode = thisnode.next_sib
        depth = thisnode.depth
        while nextnode is None and depth > 0:
            # keep going up the tree until we find an ancestor next sibling
            thisnode = thisnode.parent
            nextnode = thisnode.next_sib
            depth -= 1
            assert depth == thisnode.depth
        if nextnode is None:
            # we're at the end of the tree
            return None
        else:
            return nextnode.widget

    def prev_inorder(self):
        '''Return the previous PNBTreeWidget depth first from this one.'''
        thisnode = self.node
        prevnode = thisnode.prev_sib
        if prevnode is not None:
            # we need to find the last child of the previous widget if its
            # expanded
            prevwidget = prevnode.widget
            last_child = prevwidget.last_child
            if last_child is None:
                return prevwidget
            else:
                return last_child
        else:
            # need to hunt for the parent
            depth = thisnode.depth
            if prevnode is None and depth == 0:
                return None
            elif prevnode is None:
                prevnode = thisnode.parent
            return prevnode.widget

    def keypress(self, size, key):
        # TODO: creation of new nodes on the fly
        # TODO: act differently based on modes - ctrl-t shouldn't crash during edit
        # TODO: config file format for key/action mappings
        # TODO: figure out why this function is run twice?
        if key == 'right':
            self.expanded = True
            # TODO: create a child node and associated widget
        elif key == 'left':
            # TODO: surely there's a better place to do this
            # first check here isn't strictly 
            if not self.node.parent.is_root:
                parwidget = self.node.parent._widget
                if not parwidget.node.sticky_expanded:
                    parwidget.expanded = False
                if not self.node.sticky_expanded:
                    self.expanded = False
        elif key == '+':
            self.node.sticky_expanded = True
            self.expanded = True
        elif key == '-':
            self.node.sticky_expanded = False
            self.expanded = False

        # todo functionality
        elif key == 'ctrl t':
            done = self.node.done

            # 'None' for done means it is not a todo node
            if done == None:
                self.node.done = False
            elif done != None:
                self.node.done = None

            self.update_prefix()
            self.update_parent_prefixes()
            return None

        elif key == 'ctrl d':
            done = self.node.done
            if done != None:
                self.node.done = not done
                self.update_prefix()
                self.update_parent_prefixes()
                return None

        elif key == 'ctrl e':
            pnblog(dir(self.contents_widget))
        
        # editing nodes
        elif key == 'enter':
            if self.editing == False:
                # TODO: clean all of this up
                self.editing = True
                old_w = self._w
                edit_widget = PNBEdit(
                    caption=self.full_prefix_text, 
                    edit_text=self.contents
                )
                edit_widget.old_w = old_w
                edit_widget.tree_widget = self
                self._w = edit_widget
                return None

        if self._w.selectable():
            return self.__super.keypress(size, key)
        else:
            return key

    def mouse_event(self, size, event, button, col, row, focus):
        if self.is_leaf or event != 'mouse press' or button!=1:
            return False

        if row == 0 and col == self.indent_cols:
            self.expanded = not self.expanded
            return True

        return False

    def first_child(self):
        '''Return first child if expanded.'''
        if self.is_leaf or not self.expanded:
            return None
        else:
            if len(self.node.children) > 0:
                first_node = self.node.first_child
                return first_node.widget
            else:
                return None

    @property
    def last_child(self):
        '''Return last child if expanded.'''
        if self.is_leaf or not self.expanded:
            return None
        else:
            if len(self.node.children) > 0:
                last_child = self.node.last_child.widget
            else:
                return None
            # recursively search down for the last descendant
            last_descendant = last_child.last_child
            if last_descendant is None:
                return last_child
            else:
                return last_descendant


class PNBUrwidNode(PNBNode):
    @property
    def widget(self):
        if self._widget is None:
            self._widget = PNBTreeWidget(self)
        return self._widget

    @property
    def fresh_widget(self):
        self._widget = None
        return self.widget

    def get_value(self):
        return self.contents

    @property
    def is_root(self):
        # TODO: fix the way this is calculated such that root sees self.root
        #return self.root == self
        return self.parent == None

class PNBTreeWalker(urwid.ListWalker):
    '''ListWalker-compatible class for displaying TreeWidgets

    positions are TreeNodes.'''

    def __init__(self, start_from):
        '''start_from: PNBUrwidNode with the initial focus.'''
        self.focus = start_from

    def get_focus(self):
        widget = self.focus.widget
        return widget, self.focus

    def set_focus(self, focus):
        # TODO: here or somewhere, have focus add/remove the attrwrap for focus
        self.focus = focus
        self._modified()

    def get_next(self, start_from):
        widget = start_from.widget
        target = widget.next_inorder()
        if target is None:
            return None, None
        else:
            return target, target.node

    def get_prev(self, start_from):
        widget = start_from.widget
        target = widget.prev_inorder()
        if target is None:
            return None, None
        else:
            return target, target.node


class PNBTreeListBox(urwid.ListBox):
    def keypress(self, size, key):
        pnblog(self.__hash__)
        if self.set_focus_pending or self.set_focus_valign_pending:
            # why doesn't this trigger the focus map stuff?
            self._set_focus_complete(size, focus=True)

        focus_widget, pos = self.body.get_focus()
        if focus_widget is None: # empty listbox, can't do anything
            return key
        
        if focus_widget.selectable():
            (maxcol, maxrow) = size
            key = focus_widget.keypress((maxcol,),key)

        # If we want to override the behavior of listbox
        if key == 'up':
            self.move_focus_to_prev_sib(size)
        elif key == 'down':
            self.move_focus_to_next_sib(size)
        elif key == 'left':
            self.move_focus_to_parent(size)
        elif key == 'right':
            self.move_focus_to_first_child(size)
        elif key == 'home':
            self.move_focus_to_first_sib(size)
        elif key == 'end':
            self.move_focus_to_last_sib(size)
        else:
            # TODO: track down remaining keypress events
            return key

    def change_focus(self, size, focus):
        widget, pos = self.body.get_focus()
        #TODO: get the focus map stuff working
        pos.widget.contents_widget.set_attr_map({None: 'body'})
        focus.widget.contents_widget.set_attr_map({None: 'focus'})
        self.__super.change_focus(size, focus)

    def move_focus_to_parent(self, size):
        widget, pos = self.body.get_focus()
        parent = pos.parent
        if parent and not (parent == pos.root):
            self.change_focus(size, parent)

    def move_focus_to_prev_sib(self, size):
        widget, pos = self.body.get_focus()
        prev_sib = pos.prev_sib
        if prev_sib:
            self.change_focus(size, prev_sib)

    def move_focus_to_next_sib(self, size):
        widget, pos = self.body.get_focus()
        next_sib = pos.next_sib
        if next_sib:
            self.change_focus(size, next_sib)

    def move_focus_to_first_child(self, size):
        widget, pos = self.body.get_focus()
        first_child = pos.first_child
        if first_child:
            self.change_focus(size, first_child)

    def move_focus_to_first_sib(self, size):
        widget, pos = self.body.get_focus()
        parent = pos.parent
        if parent:
            self.change_focus(size, parent.first_child)

    def move_focus_to_last_sib(self, size):
        widget, pos = self.body.get_focus()
        parent = pos.parent
        if parent:
            self.change_focus(size, parent.last_child)
