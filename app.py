#!/usr/bin/python

from bac import *
import flask, sys

app = flask.Flask(__name__)

max_heat_temp = 75
min_cool_temp = 67

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

@app.route('/room/<room>', methods=['GET'])
def show_controls(room, msg=None):
    objts = [attr.state, attr.mode, attr.fan_speed,
             attr.set_temp_cool, attr.set_temp_heat, attr.room_temp]
    reqs = [(room, objt) for objt in objts]
    state, mode, fan, setcool, setheat, temp = do_gets(reqs)
    setpoint = { hvac_mode.cool: setcool
               , hvac_mode.heat: setheat
               }.get(mode, None)
    attrs = [ ['State', hvac_state, state]
            , ['Mode', list(hvac_mode)[:2], mode]
            , ['Setpoint', None, setpoint]
            , ['Fan speed', fan_speed, fan]
            ]
    return flask.render_template('room.html', room=room, attrs=attrs,
                                 msg=msg, temp=temp)

@app.route('/room/<room>', methods=['POST'])
def set_controls(room):
    response = flask.request.form
    msg = 'Settings applied successfully.'
    do_set(room, attr.state, hvac_state(int(response['State'])))
    mode = hvac_mode(int(response['Mode']))
    temp = float(response['Setpoint'])
    if mode == hvac_mode.cool:
        temp = max(temp, min_cool_temp)
    elif mode == hvac_mode.heat:
        temp = min(temp, max_heat_temp)
    set_mode(room, mode, temp)
    do_set(room, attr.fan_speed, fan_speed(int(response['Fan speed'])))
    for group in groups:
        if room in group:
            for other_room in group:
                other_mode = do_get(other_room, attr.mode)
                if other_mode != mode:
                    set_mode(room, mode)
                    msg += ('\n{} forced from {} to {}.'
                            .format(other_room, other_mode, mode))
    return show_controls(room, msg)

if __name__ == '__main__':
    host, port = sys.argv[1], sys.argv[2]
    app.run(host=host, port=port)
