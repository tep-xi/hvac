#!/usr/bin/python

import sys
from bac import *

if len(sys.argv) != 4:
    print('Usage:   {} cool_or_heat max_heat_temp min_cool_temp'.format(sys.argv[0]))
    print('Example: {} cool 80 70'.format(sys.argv[0]))
    exit()

pref_mode = sys.argv[1]
assert pref_mode in ['heat', 'cool']
max_heat_temp = int(sys.argv[2])
min_cool_temp = int(sys.argv[3])

groups = [['21', '22'],
          ['23', '24'],
          ['31', '32'],
          ['33', '34'],
          ['41', '42'],
          ['43', '44'],
          ['51', '52'],
          ['53', '54', '55']]

for group in groups:
    modes = [get_mode(room) for room in group]
    states = [get_state(room) for room in group]
    on_modes = [m for m, s in zip(modes, states) if s == 'on']
    new_mode = pref_mode
    if ((len(on_modes) > 0) and
        (on_modes[1:] == on_modes[:-1]) and
        (on_modes[0] != 'auto')):
        new_mode = on_modes[0]
    for room, mode, state in zip(group, modes, states):
        print("processing {} (state {})".format(room, state))
        if mode != new_mode:
            set_mode(room, new_mode)
            print('{} switched from {} to {}'
                  .format(room, mode, pref_mode))
        if get_cool_setpoint(room) < min_cool_temp:
            set_cool_setpoint(room, min_cool_temp)
            print('{} cooling setpoint raised to {}'
                  .format(room, min_cool_temp))
        if get_heat_setpoint(room) > max_heat_temp:
            set_heat_setpoint(room, max_heat_temp)
            print('{} heating setpoint lowered to {}'
                  .format(room, max_heat_temp))
