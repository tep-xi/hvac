import socket, struct
from enum import Enum

rooms = {
    '21': 15, '22': 14, '23': 17, '24': 16,
    '31': 10, '32': 11, '33': 12, '34': 13,
    '41':  7, '42':  6, '43':  8, '44':  9,
    '51':  2, '52':  1, '53':  3, '54':  4, '55':  5
}

class MyEnum(Enum):
    def __str__(self):
        return self.name[:1].upper() + self.name[1:]

class hvac_state(MyEnum):
    off = 0
    on = 1

class hvac_mode(MyEnum):
    cool = 1
    heat = 2
    fan = 3
    auto = 4
    dry = 5
    setback = 6

class fan_speed(MyEnum):
    low = 1
    high = 2
    mid2 = 3
    mid1 = 4

class air_direction(MyEnum):
    horiz = 1
    down60 = 2
    down80 = 3
    down100 = 4
    swing = 5

class attr(Enum):
    state         = (0x00c02712, 0x01002711, hvac_state)
    mode          = (0x03402716, 0x03802715, hvac_mode)
    fan_speed     = (0x03402718, 0x03802717, fan_speed)
    air_direction = (0x03402727, 0x03802726, air_direction)
    set_temp_cool = (0x00802728, 0x00802728)
    set_temp_heat = (0x00802729, 0x00802729)
    set_temp_auto = (0x0080272a, 0x0080272a)
    room_temp     =  0x00002719
    error_code    =  0x03402714
    def __init__(self, get_magic, set_magic=None, interpret=(lambda x: x)):
        self.get_magic = get_magic
        if set_magic is not None:
            self.set_magic = set_magic
        self.interpret = interpret

def do_gets(reqs):
    objs = [mitsubishi_object(room, objt.get_magic) for room, objt in reqs]
    get = build_get(objs)
    msg = build_message(get)
    res = communicate(msg)
    ret = []
    for (room, objt), obj in zip(reqs, objs):
        i = res.index(obj) + len(obj)
        j = res.index(b'\x4e', i) + 1
        k = res.index(b'\x4f', j)
        data = decode_data(res[j:k])
        ret += [objt.interpret(data)]
    return ret

def do_get(room, objt):
    return do_gets([(room, objt)])[0]

def do_set(room, objt, val):
    obj = mitsubishi_object(room, objt.set_magic)
    msg = build_message(build_set(obj, val))
    communicate(msg)

modeset = { hvac_mode.cool: (air_direction.horiz, attr.set_temp_cool)
          , hvac_mode.heat: (air_direction.down100, attr.set_temp_heat)
          , hvac_mode.auto: (None, attr.set_temp_auto)
          }
def set_mode(room, mode, temp=None):
    do_set(room, attr.mode, mode)
    if mode in modeset:
        ad, setter = modeset[mode]
        if ad is not None:
            do_set(room, attr.air_direction, ad)
        if temp is not None:
            do_set(room, setter, temp)


def communicate(message, server='bacnet.mit.edu', port=0xbac0):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message, (server, port))
    sock.settimeout(0.5)
    response, addr = sock.recvfrom(1024)
    sock.close()
    return response

def header(length):
    return b'\x81\x0a' + struct.pack('!h', length) + b'\x01\x04\x00\x05\x22'
def build_message(contents):
    return header(len(contents) + 9) + contents

def build_get(objs):
    return b'\x0e' + b''.join(obj + b'\x1e\x09\x55\x1f' for obj in objs)
def build_set(obj, data):
    return b'\x0f' + obj + b'\x19\x55\x3e' + encode_data(data) + b'\x3f'

def encode_data(value):
    if value is None:
        return b''
    else:
        if isinstance(value, Enum):
            value = value.value
        if type(value) == bool:
            return b'\x91' + (b'\x01' if value else b'\x00')
        elif type(value) == float:
            return b'\x44' + struct.pack('!f', value)
        elif type(value) == int:
            return b'\x21' + struct.pack('!b', value)
def decode_data(string):
    if len(string) == 0:
        return None
    if string[0] == 0x91:
        return (string[1] != 0)
    elif string[0] == 0x44:
        return struct.unpack('!f', string[1:5])[0]
    elif string[0] == 0x21:
        return string[1]

def mitsubishi_object(room, magic):
    ident = magic + (rooms[room] * 100)
    return b'\x0c' + struct.pack('!i', ident)
