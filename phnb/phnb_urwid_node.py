from phnb.phnb_tree_widget import PHNBTreeWidget
from phnb.phnb_node import PHNBNode

class PHNBUrwidNode(PHNBNode):
    def destruct(self):
        ''' Clean up references to this node and its widget. '''
        # TODO: make this work for the last node in children?
        self._widget._node = None
        self._widget = None

    @property
    def widget(self):
        if self._widget is None:
            self._widget = PHNBTreeWidget(self)
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

 
# vim: set ts=2 et sw=2 sts=2
