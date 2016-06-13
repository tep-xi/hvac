# Written by dlaw@mit.edu in 2016.

import socket, struct

### BACnet protocol ###
def header(length):
    return (b'\x81\x0a' + struct.pack('!h', length) +
            b'\x01\x04\x02\x44\x00')
def build_message(object, data=b''):
    request_type = b'\x0f' if len(data) > 0 else b'\x0c'
    message = request_type + object + b'\x19\x55' + data
    return header(len(message) + 9) + message
def communicate(message, server='bacnet.mit.edu', port=0xbac0):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message, (server, port))
    response, addr = sock.recvfrom(1024)
    sock.close()
    return response

### BACnet data ###
def encode_data(value):
    if value is None:
        return b''
    elif type(value) == bool:
        body = b'\x91' + b'\x01' if value else b'\x00'
    elif type(value) == float:
        body = b'\x44' + struct.pack('!f', value)
    elif type(value) == int:
        body = b'\x21' + struct.pack('!b', value)
    return b'\x3e' + body + b'\x3f'
def decode_data(string):
    if len(string) == 0:
        return None
    assert string[:1] == b'\x3e' and string[-1:] == b'\x3f'
    if string[1:2] == b'\x91':
        return (string[2:3] != b'\x00')
    elif string[1:2] == b'\x44':
        return struct.unpack('!f', string[2:6])[0]
    elif string[1:2] == b'\x21':
        return struct.unpack('!b', string[2:3])[0]

### BACnet objects (Mitsubishi-specific) ###
rooms = {
    '21': 15, '22': 14, '23': 17, '24': 16,
    '31': 10, '32': 11, '33': 12, '33': 13,
    '41':  7, '42':  6, '43':  8, '44':  9,
    '51':  2, '52':  1, '53':  3, '54':  4, '55':  5
}
attributes = {
    'on_off_setup':        0x01002711,
    'on_off_state':        0x00c02712,
    'mode_setup':          0x03802715,
    'mode_state':          0x03402716,
    'fan_speed_setup':     0x03802717,
    'fan_speed_state':     0x03402718,
    'air_direction_setup': 0x03802726,
    'air_direction_state': 0x03402727,
    'room_temp':           0x00002719,
    'set_temp_cool':       0x00802728,
    'set_temp_heat':       0x00802729,
    'set_temp_auto':       0x0080272a,
    'error_code':          0x03402714
}
def mitsubishi_object(room, attribute):
    id = attributes[attribute] + (rooms[room] * 100)
    return b'\x0c' + struct.pack('!i', id)

### Main Mitsubishi communication function ###
def mitsu_comm(room, attribute, new_value=None):
    obj = mitsubishi_object(room, attribute)
    data = encode_data(new_value)
    message = build_message(obj, data)
    response = communicate(message)
    value = decode_data(response[16:])  # the big kludge
    return value

### Wrapper functions ###
def get_on_off(room):
    return mitsu_comm(room, 'on_off_state')
def set_on_off(room, value):
    mitsu_comm(room, 'on_off_setup', bool(value))
modes = [0, 'cool', 'heat', 'fan', 'auto', 'dry', 'setback']
def get_mode(room):
    return modes[mitsu_comm(room, 'mode_state')]
def set_mode(room, value):
    mitsu_comm(room, 'mode_setup', modes.index(value))
fan_speeds = [0, 'low', 'high', 'mid2', 'mid1']
def get_fan_speed(room):
    return fan_speeds[mitsu_comm(room, 'fan_speed_state')]
def set_fan_speed(room, value):
    mitsu_comm(room, 'fan_speed_setup', fan_speeds.index(value))
air_directions = [0, 'horiz', 'down60', 'down80', 'down100', 'swing']
def get_air_direction(room):
    return air_directions[mitsu_comm(room, 'air_direction_state')]
def set_air_direction(room, value):
    mitsu_comm(room, 'air_direction_setup', air_directions.index(value))
def get_heat_setpoint(room):
    return mitsu_comm(room, 'set_temp_heat')
def set_heat_setpoint(room, value):
    mitsu_comm(room, 'set_temp_heat', float(value))
def get_cool_setpoint(room):
    return mitsu_comm(room, 'set_temp_cool')
def set_cool_setpoint(room, value):
    mitsu_comm(room, 'set_temp_cool', float(value))
def get_auto_setpoint(room):
    return mitsu_comm(room, 'set_temp_auto')
def set_auto_setpoint(room, value):
    mitsu_comm(room, 'set_temp_auto', float(value))
def get_temperature(room):
    return mitsu_comm(room, 'room_temp')

### Indirect wrapper functions ###
def get_status(room):
    return get_mode(room) if get_on_off(room) else 'off'
def set_status(room, value):
    if value == 'off':
        set_on_off(room, False)
    else:
        set_on_off(room, True)
        set_mode(room, value)
def get_setpoint(room):
    mode = get_mode(room)
    if mode == 'cool':
        return get_cool_setpoint(room)
    elif mode == 'heat':
        return get_heat_setpoint(room)
    elif mode == 'auto':
        return get_auto_setpoint(room)
    else:
        return 'err'
def set_setpoint(room, value):
    mode = get_mode(room)
    if mode == 'cool':
        set_cool_setpoint(room, value)
    elif mode == 'heat':
        set_heat_setpoint(room, value)
    elif mode == 'auto':
        set_auto_setpoint(room, value)
