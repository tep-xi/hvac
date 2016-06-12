import socket, struct

### BACnet objects ###
rooms = {
    '21': 15, '22': 14, '23': 17, '24': 16,
    '31': 10, '32': 11, '33': 12, '33': 13,
    '41':  7, '42':  6, '43':  8, '44':  9,
    '51':  2, '52':  1, '53':  3, '54':  4, '55':  5
}
attributes = {
    'on_off_setup':  0x01002711,
    'on_off_state':  0x00c02712,
    'room_temp':     0x00002719,
    'set_temp_cool': 0x00802728,
    'set_temp_heat': 0x00802729,
    'set_temp_auto': 0x0080272a
}
def mitsubishi_object(room, attribute):
    id = attributes[attribute] + (rooms[room] * 100)
    return b'\x0c' + struct.pack('!i', id)

### BACnet data ###
def encode_data(value):
    if value is None:
        return b''
    elif type(value) == bool:
        body = b'\x91' + b'\x01' if value else b'\x00'
    elif type(value) == float:
        body = b'\x44' + struct.pack('!f', value)
    return b'\x3e' + body + b'\x3f'
def decode_data(string):
    if len(string) == 0:
        return None
    assert string[:1] == b'\x3e' and string[-1:] == b'\x3f'
    if string[1:2] == b'\x91':
        return (string[2:3] != b'\x00')
    elif string[1:2] == b'\x44':
        return struct.unpack('!f', string[2:6])[0]

### BACnet protocol ###
def header(length):
    return (b'\x81\x0a' + struct.pack('!h', length) +
            b'\x01\x04\x02\x44\x00')
def build_message(object, data=None):
    request_type = b'\x0f' if len(data) > 0 else b'\x0c'
    message = request_type + object + b'\x19\x55' + data
    return header(len(message) + 9) + message
def communicate(message, server='bacnet.mit.edu', port=0xbac0):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message, (server, port))
    response, addr = sock.recvfrom(1024)
    sock.close()
    return response

def mitsu_comm(room, attribute, new_value=None):
    obj = mitsubishi_object(room, attribute)
    data = encode_data(new_value)
    message = build_message(obj, data)
    response = communicate(message)
    value = decode_data(response[16:])  # the big kludge
    return value

for room in ['23', '42']:
    temp = mitsu_comm(room, 'room_temp')
    set_temp = mitsu_comm(room, 'set_temp_cool')
    state = mitsu_comm(room, 'on_off_state')
    print('{}: temp {}, set to {}, state {}'.format(
        room, temp, set_temp, state))
