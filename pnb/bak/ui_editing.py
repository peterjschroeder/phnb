from .input_pad import InputPad
class UINodeEditor:
  def edit(ui):
    # TODO: define this method
    #win = ui.gen_win_selected()
    win = ui.win_tree
    tbox = InputPad(win)
    tbox.edit()
    pnblog([tbox.gather()])
