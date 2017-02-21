import os
#TODO: make this not suck
prefix_width = 4
log_file = "/tmp/outfile.out"
# TODO: more system/user agnostic defaults
home_dir = os.getenv('HOME')
tree_file = home_dir + '/.pnb'
email_addr = 'doodoo@mailinator.com'
email_cmd = 'msmtp -t'
continuation_prefix = ' ' * prefix_width

edit_node_key_remappings = {
  'up': 'home',
  'down': 'end',
  'ctrl a': 'home',
  'ctrl e': 'end',
}

per_mode_mappings = {
  'main': {
    'esc': ['enter_vim_mode'],
    'up': ['move_focus_to_prev_sib'],
    'down': ['move_focus_to_next_sib'],
    'left': ['move_focus_to_parent'],
    'right': ['move_focus_to_first_child_or_create'],
    'home': ['move_focus_to_first_sib'],
    'end': ['move_focus_to_last_sib'],
    'page up': ['move_focus_to_first_sib'],
    'page down': ['move_focus_to_last_sib'],
    '+': ['set_sticky_expand'],
    '-': ['unset_sticky_expand'],
    'ctrl t': ['toggle_todo'],
    'ctrl d': ['toggle_done'],
    'f2': ['save_tree'],
    'enter': ['start_editing'],
    'delete': ['delete_node'],
    'ctrl e': ['debug_node'],
    'ctrl g': ['try_to_delete_node'],
    'ctrl f': ['mark_node'],
    'ctrl r': ['debug_marked_node'],

    'meta =': ['email_subtree'],

    'shift up': ['move_node_to_prev_sib'],
    'shift down': ['move_node_to_next_sib'],
    'shift left': ['move_node_under_grandparent'],
    'shift right': ['move_node_under_prev_sib'],
    '>': ['move_node_and_below_under_prev_sib'],
    '<': ['move_node_and_below_under_grandparent'],
    #'shift home': ['move_node_to_first_sib'],
    #'shift end': ['move_node_to_last_sib'],
  },
  'vim': {
    'k': ['move_focus_to_prev_sib'],
    'j': ['move_focus_to_next_sib'],
    'h': ['move_focus_to_parent'],
    # TODO: have this not create new children?
    'l': ['move_focus_to_first_child'],
  }
}

# TODO: don't use eval, import intelligently
user_config_file = home_dir + '/.pnb.cfg'
user_config = open(user_config_file, 'r').read()
exec(user_config)
 
# vim: ts=2 et sw=2 sts=2
