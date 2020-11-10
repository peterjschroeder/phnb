from phnb.phnb_edit import PHNBEdit
import phnb.config as config

import urwid
from urwid.wimp import SelectableIcon

class PHNBTreeWidget(urwid.WidgetWrap):
    def __init__(self, node):
        self._node = node
        self.listbox = node.root.listbox
        self._expanded = False
        self._sticky_expanded = False
        self._selectable = True
        self._contentswidget = None
        self._editingwidget = None
        self._prefixwidget = None
        self._old_w = None
        self.sticky_expanded = False
        widget = self.indented_widget
        self.__super.__init__(widget)

    @property
    def is_leaf(self):
        return self.node.children == []

    @property
    def is_root(self):
        return self.node.is_root

    @property
    def expanded(self):
        return self._expanded

    @expanded.setter
    def expanded(self, expanded):
        self._expanded = expanded
        self.node.expanded = expanded
        self.refresh_prefix()

    @property
    def sticky_expanded(self):
        return self._sticky_expanded

    @sticky_expanded.setter
    def sticky_expanded(self, sticky_expanded):
        self._sticky_expanded = sticky_expanded
        self.node.sticky_expanded = sticky_expanded

    @property
    def contents(self):
        # could grab node.contents as well. they should always be the same.
        return self.contents_widget.base_widget.get_text()[0]

    def selectable(self):
        return self._selectable

    @property
    def indented_widget(self):
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
        return urwid.Padding(widget,
            width=('relative', 100), left=self.indent_cols)

    @property
    def indent_cols(self):
        depth = self.node.depth
            
        # correct for root
        if depth > 0:
            depth = depth - 1

        #TODO: get this value from config
        indent_cols_mult = 3

        return indent_cols_mult * depth

    def update_contents(self):
        self.contents_widget.base_widget.set_text(self.node.contents)

    def get_editing_widget(self):
        return urwid.Padding(urwid.AttrMap(
            PHNBEdit(
            caption='',
            edit_text=self.contents
        ), 'edit',
        ), width=('relative', 100), left=self.indent_cols + config.prefix_width,
        )

    def start_editing(self):
        if self._editingwidget is None:
            self.listbox.mode = 'edit'

            self._editingwidget = self.get_editing_widget()
            self._editingwidget.base_widget.tree_widget = self
            
            # TODO: understand keypress behavior and widget display, so you can just do an overlay
            # back up the live widget, then replace it with the editing widget
            self._old_w = self._w
            self._w = self._editingwidget

    def stop_editing(self):
        edit_text = self._editingwidget.base_widget.get_edit_text()
        self.node.contents = edit_text
        self.update_contents()
        self._w = self._old_w
        self.listbox.mode = 'main'
        self._editingwidget = None

    def add_text(self, text):
        self.node.contents += text
        self.update_contents()

    # unused
    def set_text(self, text):
        self.node.contents = text
        self.update_contents()
    
    @property
    def palette(self):
        return self.is_leaf and 'body' or 'parent'

    @property
    def contents_widget(self):
        if self._contentswidget is None:
            self._contentswidget = urwid.AttrMap(
                urwid.Text(self.node.contents), 
                self.palette, 
                # TODO: make this focus mapping work
                #'focus'
            )
        return self._contentswidget

    @contents_widget.setter
    def contents_widget(self, contents_widget):
        self._contentswidget = contents_widget
        self._w.base_widget.widget_list[1] = contents_widget

    def refresh_contents_widget(self):
        self.contents_widget = self.contents_widget

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
        # TODO: lowpri: cache/memoize the icons
        # TODO: lowpri: have edit mode show a prefix
        return urwid.AttrMap(SelectableIcon(self.node.prefix, 1), self.palette)

    def refresh(self):
        self.refresh_prefix()
        self.refresh_cols()

    def refresh_cols(self):
        self._w.left = self.indent_cols

    def refresh_prefix(self):
        if not self.is_root:
            self.prefix_widget = self.gen_prefix()

    def refresh_parent_prefixes(self):
        for node in self.node.all_parents:
            if not node.is_root:
                node.widget.refresh_prefix()

    @property
    def prefix_text(self):
        #edit_padding = ' ' * self.indent_cols
        #edit_prefix = self.prefix_widget.base_widget.get_text()[0]
        #return edit_padding + edit_prefix + ' '
        return self.prefix_widget.base_widget.get_text()[0] + " "

    @property
    def node(self):
        return self._node

    @node.setter
    def node(self, node):
        self._node = node

    def next_inorder(self):
        '''Return the next PHNBTreeWidget depth first from this one.'''
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
        '''Return the previous PHNBTreeWidget depth first from this one.'''
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
        if self._w.selectable():
            key = self.__super.keypress(size, key)
            return key
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
            if self.node.has_children:
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
            if self.node.has_children:
                last_child = self.node.last_child.widget
            else:
                return None
            # recursively search down for the last descendant
            last_descendant = last_child.last_child
            if last_descendant is None:
                return last_child
            else:
                return last_descendant
 
