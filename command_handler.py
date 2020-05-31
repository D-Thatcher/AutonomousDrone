from functools import partial
import pickle
import os
from util.ReverseCommandUtil import swap
import datetime
from FlightSimulator import FlightSimulator


def get_date():
    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d")
    return date + '-'+ str(now.hour) + '-'+ str(now.minute)+ '-'+str(now.second)

class CommandHandler:
    """
        args:

        command_poster_fn is a function that can send commands to the remote server
        x,y,z are the expected coordinates in space in centimeters
        angle_degree is the expected number of degrees counter-clockwise the remote object is from its starting position
    """

    def __init__(self, command_poster_fn, history=None, x=0,y=0,z=0,angle_degree=0):
        self.command_history = []
        self.landed = True
        self.initialized = False

        if history is not None:
            self.history = history
            self._load_history()
        else:
            self.history_location = 'history'

            if not os.path.exists(self.history_location):
                os.mkdir(self.history_location)

            self.history = 'history/flight_'+get_date()+'.flightlog'



        # Wrap an observer around the post function
        self.post_command = partial(self._store_history, fn=command_poster_fn)



        # Store the expected state of the remote object
        self.x = x
        self.y = y
        self.z = z
        self.angle_degree = angle_degree

    def initialize_sdk(self):
        # Initialize the SDK
        self.initialized = True
        self.post_command('Command')

    def track_back(self):
        cp = list(self.command_history)
        cp.reverse()
        for cmd in cp:
            swapped = swap(cmd)
            self.post_command(swapped)


    def _load_history(self):
        with open(self.history, 'rb') as f:
            self.command_history = pickle.load(f)


    def _store_history(self, x, fn):
        fn(x)


        if x == 'takeoff':
            self.landed = False
        elif x is 'land':
            self.landed = True


        self.command_history.append(x)


        with open(self.history,'wb') as f:
            pickle.dump(self.command_history, f)


    def take_off(self):
        self.post_command('takeoff')
        self.z+=100



    def land(self):
        self.post_command('land')
        self.z-=100


    def enable_video_stream(self):
        self.post_command('streamon')

    def disable_video_stream(self):
        self.post_command('streamoff')

    def kill_power_unsafely(self):
        self.post_command('emergency')

    def up(self, x):
        self._move(x,'up',self.up)
        self.z+=x

    def down(self, x):
        self._move(x,'down',self.down)
        self.z-=x


    def left(self, x):
        self._move(x,'left',self.left)
        self.x-=x


    def right(self, x):
        self._move(x,'right',self.right)
        self.x+=x


    def forward(self, x):
        self._move(x,'forward',self.forward)
        self.y+=x


    def back(self, x):
        self._move(x,'up',self.back)
        self.y-=x

    def rotate_clockwise(self, x):
        self._move(x,'cw', self.rotate_clockwise, min_x=1, max_x=360)
        self.angle_degree -= x
        self.angle_degree = (self.angle_degree - x) % 360

    def rotate_counter_clockwise(self, x):
        self._move(x,'ccw', self.rotate_counter_clockwise, min_x=1, max_x=360)
        self.angle_degree = (self.angle_degree + x) % 360

    def _move(self, x, cmd_prefix, curr_func, expected_type=int, min_x=20,max_x=500):
        if not isinstance(x, expected_type):
            raise TypeError('x = '+str(x)+ " argument is not a " +  str(expected_type) + ' ' + str(curr_func) + ' type:  '+str(type(x)))

        # is x a float? @TODO
        if not ((x>=min_x) and (x<=max_x)):
            raise ValueError(str(x)+ " argument is out of bounds in " + str(curr_func))

        self.post_command(cmd_prefix+' '+str(x))







