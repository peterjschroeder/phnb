import urwid
import phnb.config as config
from urwid.util import move_prev_char, move_next_char

class PHNBEdit(urwid.Edit):
    # TODO: you can make this a list to have it be accessible everywhere, or a list to not recreate it on every write
    # TODO lowpri: figure out how to make text indent correctly during editing of long nodes
    paste_buffer = ""

    def keypress(self, size, key):
        if key in config.edit_node_key_remappings:
            key = config.edit_node_key_remappings[key]

        p = self.edit_pos
        if key == 'enter':
            self.tree_widget.stop_editing()
            return None

        # paste
        elif key=="ctrl y":
            for char in self.paste_buffer:
                p = move_next_char(self.edit_text, p, -1)
                self.set_edit_text(self.edit_text + char)
                self.set_edit_pos(p+1)

        # kill to beginning of line
        elif key=="ctrl u":
            if not self._delete_highlighted():
                if p == 0:
                    return key

                while (p != 0):
                    p = move_prev_char(self.edit_text, 0, p)
                    self.paste_buffer = self.edit_text[p:] + self.paste_buffer
                    self.set_edit_text(self.edit_text[:p] +
                                                         self.edit_text[self.edit_pos:])
                    self.set_edit_pos(p)

        # kill to beginning of word
        elif key=="ctrl w":
            if not self._delete_highlighted():
                if p == 0:
                    return key

                # first delete all whitespace
                while (p != 0) and (self.edit_text[p-1] == ' '):
                    p = move_prev_char(self.edit_text, 0, p)
                    self.paste_buffer = self.edit_text[p:] + self.paste_buffer
                    self.set_edit_text(self.edit_text[:p] +
                                                         self.edit_text[self.edit_pos:])
                    self.set_edit_pos(p)

                # then delete all characters until whitespace or the beginning of the node is found
                while (p != 0) and (self.edit_text[p-1] != ' '):
                    p = move_prev_char(self.edit_text, 0, p)
                    self.paste_buffer = self.edit_text[p:] + self.paste_buffer
                    self.set_edit_text(self.edit_text[:p] +
                                                         self.edit_text[self.edit_pos:])
                    self.set_edit_pos(p)

        (maxcol, maxrow) = size
        key = self.__super.keypress((maxcol,), key)

