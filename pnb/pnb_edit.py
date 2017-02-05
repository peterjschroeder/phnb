import urwid
import pnb.config as config

class PNBEdit(urwid.Edit):
    # TODO: figure out how to make text indent correctly during editing of long nodes
    # TODO: make newlines lead to new nodes during edit (or not, not crucial)
    def keypress(self, size, key):
        if key in config.edit_node_key_remappings:
            key = config.edit_node_key_remappings[key]

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

