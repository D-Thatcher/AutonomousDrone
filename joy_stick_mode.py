
if __name__ != '__main__':
    raise Exception("joy stick mode is not designed to be imported")

import threading
import socket
import keyboard
import time
import os
import traceback


def check_root():
    if hasattr(os, "geteuid"):
        if not os.geteuid() == 0:
            print("This script needs to be run as root.")
            exit()

class KeyListener:
    def __init__(self):
        check_root()
        self.on = True
        self.verbose = False
        self.fps = 1/24
        self.listener_thread = None
        self.key_map = {}

    def exit_nice(self):
      self.on = False
      if self.listener_thread is not None:
        self.listener_thread.join()

    def key_event(self, e):
      if self.verbose:
          # if e.event_type == "up":
          #   print("Key up: " + str(e.name))
          # if e.event_type == "down":
          #   print("Key down: " + str(e.name))
          if e.name == "q":
            self.exit_nice()
            print("Quitting")

      if e.event_type == "down":
          if e.name in self.key_map:
            lo_cb = self.key_map[e.name]

            for cb in lo_cb:
                cb(e.name)


    def register_callback(self, key, callback):
        if not isinstance(key,str):
            raise TypeError('arg: "key" must be a '+str(type("")))

        if key in self.key_map:
            keys_so_far = self.key_map[key]
            keys_so_far.append(callback)
        else:
            self.key_map[key] = [callback]

    def start(self):
        self.listener_thread = threading.Thread(target=self._main)
        self.listener_thread.start()

    def _main(self):
        keyboard.hook(self.key_event)
        while self.on:
          time.sleep(self.fps)
        self.exit_nice()




host = ''
port = 9000
locaddr = (host,port)


# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

tello_address = ('192.168.10.1', 8889)

sock.bind(locaddr)

def recv():
    while True:
        data, server = sock.recvfrom(1518)
        print(data.decode(encoding="utf-8"))
        time.sleep(0.005)





#recvThread create
recvThread = threading.Thread(target=recv)
recvThread.start()

com_map = {
           'right': 'rc 80 0 0 0',
           'left': 'rc -80 0 0 0',
           'back': 'rc 0 -80 0 0',
           'forward': 'rc 0 80 0 0',
           'up': 'rc 0 0 80 0',
           'down': 'rc 0 0 -80 0',
           'space': 'rc 0 0 0 0',
            'c': 'command',
            't':'takeoff',
            'l':'land',
            'b':'battery?',

           }


def joy(e):
    print("hit " + str(e) + '\n')

    if e not in com_map:
        sock.close()
        raise ValueError(e+ " not in controller map")

    msg = com_map[e]
    # Send data
    print("sent " + msg + '\n')

    msg = msg.encode(encoding="utf-8")
    sock.sendto(msg, tello_address)



# def joy_up(e):
#     joy('up')
#
# def joy_down(e):
#     joy('up')

def joy_left(e):
    joy('left')


def joy_right(e):
    joy('right')


def joy_forward(e):
    joy('forward')


def joy_back(e):
    joy('back')

def joy_stabilize(e):
    joy('space')

def joy_land(e):
    joy('l')

def joy_takeoff(e):
    joy('t')

def joy_command(e):
    joy('c')

def joy_battery(e):
    joy('b')

kl = KeyListener()
kl.register_callback("left", joy_left)
kl.register_callback("right", joy_right)
kl.register_callback("up", joy_forward)
kl.register_callback("down", joy_back)
kl.register_callback("space", joy_stabilize)
kl.register_callback("l", joy_land)
kl.register_callback("t", joy_takeoff)
kl.register_callback("c", joy_command)
kl.register_callback("b", joy_battery)


# kl.verbose=True



kl.start()



