#TODO: make this not suck
prefix_width = 4
log_file = "/tmp/outfile.out"
tree_file = '/home/glenn/.pnb'
continuation_prefix = ' ' * prefix_width

edit_node_key_remappings = {
    'up': 'home',
    'down': 'end',
    'ctrl a': 'home',
    'ctrl e': 'end',
}

import subprocess

per_mode_mappings = {
    'main': {
        'esc': ['enter_vim_mode'],
        'up': ['move_focus_to_prev_sib'],
        'down': ['move_focus_to_next_sib'],
        'left': ['move_focus_to_parent'],
        'right': ['move_focus_to_first_child'],
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

        'shift up': ['move_node_to_prev_sib'],
        'shift down': ['move_node_to_next_sib'],
        'shift left': ['move_node_under_grandparent'],
        'shift right': ['move_node_under_prev_sib'],
        '>': ['move_node_and_below_under_prev_sib'],
        '<': ['move_node_and_below_under_grandparent'],
        #'shift home': ['move_node_to_first_sib'],
        #'shift end': ['move_node_to_last_sib'],
    }
}
