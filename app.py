#!/usr/bin/python

from bac import *
import flask, sys

app = flask.Flask(__name__)

max_heat_temp = 80
min_cool_temp = 70

# Simultaneous heating and cooling are prohibited within a group.
# This is due to the design of the refrigerant piping.
groups = [['21', '22'],
          ['23', '24'],
          ['31', '32'],
          ['33', '34'],
          ['41', '42'],
          ['43', '44'],
          ['51', '52'],
          ['53', '54', '55']]

@app.route('/')
def room_selector():
    return flask.render_template('index.html',
                                 rooms=sorted(rooms.keys()))

@app.route('/<room>', methods=['GET'])
def show_controls(room, msg=None):
    attrs = [['State', states, get_state(room)],
             ['Mode', modes[:3], get_mode(room)],
             ['Temperature', None, get_setpoint(room)],
             ['Fan speed', fan_speeds, get_fan_speed(room)],
             ['Air direction', air_directions, get_air_direction(room)]]
    return flask.render_template('room.html', room=room, attrs=attrs,
                                 msg=msg, temp=get_temperature(room))

@app.route('/<room>', methods=['POST'])
def set_controls(room):
    response = flask.request.form
    msg = 'Settings applied successfully.'
    set_state(room, response['State'])
    mode, temp = response['Mode'], float(response['Temperature'])
    set_mode(room, mode)
    if mode == 'cool':
        set_cool_setpoint(room, max(temp, min_cool_temp))
    elif mode == 'heat':
        set_heat_setpoint(room, min(temp, max_heat_temp))
    for group in groups:
        if room in group:
            for other_room in group:
                other_mode = get_mode(other_room)
                if (other_mode in ['heat', 'cool', 'auto'] and
                    mode in ['heat', 'cool'] and other_mode != mode):
                    set_mode(other_room, mode)
                    if get_state(other_room) == 'on':
                        msg += ('\n{} forced from {} to {}.'
                                .format(other_room, other_mode, mode))
    set_fan_speed(room, response['Fan speed'])
    set_air_direction(room, response['Air direction'])
    return show_controls(room, msg)

if __name__ == '__main__':
    host, port = sys.argv[1], sys.argv[2]
    app.run(host=host, port=port)
