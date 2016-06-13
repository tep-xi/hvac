#!/usr/bin/python

from bac import *

properties = ['state', 'mode', 'setpt', 'temp', 'fan', 'dir']
getters = [get_state, get_mode, get_setpoint,
           get_temperature, get_fan_speed, get_air_direction]
setters = [set_state, set_mode, set_setpoint,
           set_setpoint, set_fan_speed, set_air_direction]

while True:
    try:
        cmd = input('> ').split()
        if len(cmd) == 0:
            continue
        elif cmd[0] == 'summary':
            if len(cmd) == 1:
                format_str = '{:<4}' + ' {:<6}' * len(properties)
                print(format_str.format('', *properties))
                for room in sorted(rooms.keys()):
                    print(format_str.format(
                        room, *[getter(room) for getter in getters]))
            else:
                print('Usage: summary')
        elif cmd[0] == 'get':
            if len(cmd) == 2:
                for prop, getter in zip(properties, getters):
                    print('{:<6} {}'.format(prop, getter(cmd[1])))
            elif len(cmd) == 3 and cmd[2] in properties:
                print(getters[properties.index(cmd[2])](cmd[1]))
            else:
                print('Usage: get room [prop]')
        elif cmd[0] == 'set':
            if len(cmd) == 4 and cmd[2] in properties:
                setters[properties.index(cmd[2])](cmd[1], cmd[3])
            else:
                print('Usage: set room prop value')
        elif cmd[0] == 'exit':
            exit()
        else:
            print('Commands: summary get set exit')
            print('Rooms: {}'.format(' '.join(sorted(rooms.keys()))))
            print('Properties: {}'.format(' '.join(properties)))
            print('Values (state): {}'.format(' '.join(states)))
            print('Values (mode): {}'.format(' '.join(modes)))
            print('Values (fan): {}'.format(' '.join(fan_speeds)))
            print('Values (dir): {}'.format(' '.join(air_directions)))
            print('setpt, temp in degrees F')
    except EOFError:
        exit()
    except KeyboardInterrupt:
        exit()
    except:
        print("Error.")
        continue
