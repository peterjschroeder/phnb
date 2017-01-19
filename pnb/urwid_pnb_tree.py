#!/usr/bin/python3

# TODO: set up python folding on lappy
# TODO: make scrolling show few line buffer

import urwid
from urwid.util import move_prev_char, move_next_char
from urwid.wimp import SelectableIcon
from .pnbnode import PNBNode
from .util import pnblog, convert_tree_to_xml
#from .config import mode_mappings

# there should be a cleaner way to access the Edit functions.
fucker = urwid.Edit()

class Lawl:
    pass

lawl = Lawl()
lawl.marked_node = None

class PNBEdit(urwid.Edit):
    # TODO: figure out how to make text indent correctly during editing of long nodes
    # TODO: make newlines lead to new nodes during edit (or not, not crucial)
    edit_node_key_remappings = {
        'up': 'home',
        'down': 'end',
        'ctrl a': 'home',
        'ctrl e': 'end',
    }
    def keypress(self, size, key):
        if key in self.edit_node_key_remappings:
            key = self.edit_node_key_remappings[key]

        p = self.edit_pos
        if key == 'enter':
            self.tree_widget.stop_editing()
            return None

        # TODO: ctrl u clears line

        # TODO: make a yank buffer
        elif key=="ctrl w":
            #self.pref_col_maxcol = None, None
            if not self._delete_highlighted():
                if p == 0:
                    return key
                # TODO: make this work in a function
                # first delete all whitespace
                while (p != 0) and (self.edit_text[p-1] == ' '):
                    p = move_prev_char(self.edit_text,0,p)
                    self.set_edit_text( self.edit_text[:p] +
                    self.edit_text[self.edit_pos:] )
                    self.set_edit_pos(p)
                # then delete all characters until whitespace or the beginning of the node is found
                while (p != 0) and (self.edit_text[p-1] != ' '):
                    p = move_prev_char(self.edit_text,0,p)
                    self.set_edit_text( self.edit_text[:p] +
                    self.edit_text[self.edit_pos:] )
                    self.set_edit_pos(p)

        # urwid.Edit expects only maxcol
        (maxcol, maxrow) = size
        key = self.__super.keypress((maxcol,), key)
    
class PNBTreeWidget(urwid.WidgetWrap):
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
            PNBEdit(
            caption='',
            edit_text=self.contents
        ), 'edit',
        ), width=('relative', 100), left=self.indent_cols + 4,
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


class PNBUrwidNode(PNBNode):

    def destruct(self):
        ''' Clean up references to this node and its widget. '''
        # TODO: make this work for the last node in children?
        self._widget._node = None
        self._widget = None

    @property
    def widget(self):
        if self._widget is None:
            self._widget = PNBTreeWidget(self)
        return self._widget

    def regen_widget(self):
        self._widget = None
        self.widget.refresh_prefix()

    def refresh_percent_display(self):
        if self.percent != None:
            self.widget.refresh_prefix()

        for n in self.all_parents:
            if n.percent != None:
                n.widget.refresh_prefix()

class PNBTreeWalker(urwid.ListWalker):
    def __init__(self, start_from):
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
    def __init__(self, walker, browser):
        self.browser = browser
        self.mode = 'main'
        self.text_buffer = ''
        self.temp_node = None
        self.pressed_key = None
        self.__super.__init__(walker)

        # TODO: have these associated with the class itself, not each object
        #       (or even better, read them from a config file)
        self.mode_mapping = {
            'main': self.mode_main_keypress,
            'main-select': self.mode_main_select_keypress,
            'main-newnode': self.mode_main_newnode_keypress,
            'main-subnode': self.mode_main_subnode_keypress,
            'edit': self.mode_edit_keypress,
            'confirm-delete': self.mode_confirm_delete_keypress,
            'vim-cmd': self.mode_vim_cmd_keypress,
        }

        self.main_mode_key_mappings = {
            'esc': self.enter_vim_mode,
            'up': self.move_focus_to_prev_sib,
            'down': self.move_focus_to_next_sib,
            'left': self.move_focus_to_parent,
            'right': self.move_focus_to_first_child,
            'home': self.move_focus_to_first_sib,
            'end': self.move_focus_to_last_sib,
            'page up': self.move_focus_to_first_sib,
            'page down': self.move_focus_to_last_sib,
            '+': self.set_sticky_expand,
            '-': self.unset_sticky_expand,
            'ctrl t': self.toggle_todo,
            'ctrl d': self.toggle_done,
            'f2': self.save_to_disk,
            'enter': self.start_editing,
            'delete': self.delete_node,
            'ctrl e': self.debug_node,
            'ctrl g': self.try_to_delete_node,
            'ctrl f': self.mark_node,
            'ctrl r': self.debug_marked_node,

            'shift up': self.move_node_to_prev_sib,
            'shift down': self.move_node_to_next_sib,
            'shift left': self.move_node_under_grandparent,
            'shift right': self.move_node_under_prev_sib,
            '>': self.move_node_and_below_under_prev_sib,
            '<': self.move_node_and_below_under_grandparent,
            #'shift home': self.move_node_to_first_sib,
            #'shift end': self.move_node_to_last_sib,
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

        if key in self.main_mode_key_mappings:
            func = self.main_mode_key_mappings[key]
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
            self.temp_node.is_temp = False
            self.temp_node = None
            self.text_buffer = ''
            self.mode = 'main'
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
        #       correct place relative to the selected node?
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
                        pnblog('lawl', target_node)
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

    def save_to_disk(self):
        widget, node = self.body.get_focus()

        xmltree = convert_tree_to_xml(node.root)
        # TODO: move to a config file
        xmltree.write('/home/glenn/.hnbbak')
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
