# NOTE: these are all Main mode selection movements - there are similar paradigms, so you may want to make these more extensible. just start here.
class UIMovement:
  @classmethod
  def left(ui):
    node = ui.selected
    if node.parent != ui.root:
      ui.selected = node.parent
      # TODO: move cursor position
      # TODO: collapse, if dong is not expanded


  @classmethod
  def right(ui):
    node = ui.selected
    # TODO: check node collapse state
    ui.selected = node.first_child

  @classmethod
  def up(ui):
    node = ui.selected
    sibs = node.parent.children
    selfindex = sibs.index(node)

    # Don't try to move up if this is the top node
    movement = (selfindex == 0) and 0 or -1
    ui.selected = sibs[selfindex + movement]

  @classmethod
  def down(ui):
    node = ui.selected
    sibs = node.parent.children
    selfindex = sibs.index(node)

    # Don't try to move down if this is the bottom node
    movement = (selfindex == (len(sibs) - 1)) and 0 or 1
    ui.selected = sibs[selfindex + movement]

    # JFDKLSJ you need a function that determines the physical screen height of a node
    # len(node.contents) (screen width - left margin size)

  @classmethod
  def top(ui):
    node = ui.selected
    return node.parent.first_child

  @classmethod
  def bottom(ui):
    node = ui.selected
    return node.parent.last_child

  def cripped_draw_node(ui, node):

    _, w = ui.win_tree.getmaxyx()
    # IMPORTANT: how to draw node
    ##ui.win_tree.addstr(y + i, 0, left_space + chunk)
