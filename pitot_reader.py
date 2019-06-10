#! /usr/bin/python
# -*- coding: utf-8 -*-

# Example line received
# 123305844, 052319, 0000.00, 0000.00, +00.00, +00.00, +00003, 101277, 0101277, 16

import serial, threading, time, socket, struct

# Serial read config 
PORT = "/dev/ttyUSB0"
BAUD = 115200
STOP_SERIAL = False

line = ['000000000', '000000', '0', '0', '0', '0', '0', '0', '0', '0']

# UDP sender config
UDP_IP="127.0.0.1"
UDP_PORT=5005

class Pitot:
    def __init__(self):
        self.time, self.date = 0, 0
        self.true_airspeed = 0
        self.angle_attack, self.angle_sideslip = 0, 0
        self.press_alt, self.static_press, self.total_press = 0, 0, 0
        self.thermo_temp = 0
        self.checksum = 0
        self.msg2send = 0

    # Prepare data struct to be sent (64B - {8 11 7 7 6 6 6 6 7})
    def pack_data(self):
        self.msg2send = struct.pack('{0}s{1}s{2}s{3}s{4}s{5}s{6}s{7}s{8}s'.format(len(self.date), len(self.time), len(self.true_airspeed), len(self.angle_attack), len(self.angle_sideslip), len(self.press_alt), len(self.static_press), len(self.total_press), len(self.thermo_temp)), self.date, self.time,
                                    self.true_airspeed, self.angle_attack, self.angle_sideslip, self.press_alt, self.static_press, self.total_press,self.thermo_temp)

    # Just for check received data
    def print_all(self):
        # Checksum not printed
        print self.date+" "+self.time+" AirSpeed:"+self.true_airspeed+" Angles:"+self.angle_attack+" "+self.angle_sideslip+" Pressures:"+self.press_alt+" "+self.static_press+" "+self.total_press+" TC:"+self.thermo_temp

def serial_read():
    global line
    con = serial.Serial(
        port=PORT,
        baudrate=BAUD,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS
    )
    con.flushInput()
    try:
        while True:
            line = con.readline().split(", ")
    except STOP_SERIAL==True:
        print "Communication stopped"

if __name__ == "__main__":
    pitot = Pitot()

    serial_com = threading.Thread(target=serial_read, name='Serial')
    serial_com.setDaemon(True)
    serial_com.start()

    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

    try:
        while True:  
            pitot.time = line[0][0:2]+':'+line[0][2:4]+':'+line[0][4:6]+':'+line[0][6:8]
            pitot.date = line[1][2:4]+'/'+line[1][0:2]+'/'+line[1][4:6]
            pitot.true_airspeed = line[2]
            pitot.angle_attack, pitot.angle_sideslip = line[3], line[4]
            pitot.press_alt, pitot.static_press, pitot.total_press = line[5], line[6], line[7]
            pitot.thermo_temp = line[8]
            pitot.checksum = line[9]

            pitot.pack_data()
            sock.sendto(pitot.msg2send,(UDP_IP, UDP_PORT))
            pitot.print_all()

            time.sleep(0.5)

    except KeyboardInterrupt:
        STOP_SERIAL=True
        print('interrupted!')
