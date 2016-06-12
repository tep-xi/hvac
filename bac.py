import socket, struct

rooms = ['52', '51', '53', '54', '55',
         '42', '41', '43', '44',
         '31', '32', '33', '34',
         '22', '21', '24', '23']

bacnet_message = bytearray(b'\x81\x0a\x00\x11\x01\x04\x02\x44\x00\x0c\x0c\x00\x00\x00\x00\x19\x55')

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

for i in range(17):
    bacnet_message[-6:-2] = struct.pack('!i', 10109 + i*100)
    s.sendto(bacnet_message, ('18.102.224.51', 0xBAC0))
    data, addr = s.recvfrom(1024)
    print("temp in room {} is {}".format(
        rooms[i], struct.unpack('!f', data[18:22])[0]))
