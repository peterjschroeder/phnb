import urwid

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
