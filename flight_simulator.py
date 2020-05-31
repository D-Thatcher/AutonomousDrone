

import time



class FlightSimulator:
    def __init__(self):
        self.cm = None
        self.latency = 0.1

    def set_commander(self,commander):
        self.cm = commander

    def is_statelike(self,cmd):
        return cmd[-1]=='?'

    def check_state(self,cmd):
        assert self.cm is not None, "Must set commander before flying"
        assert self.cm.initialized, "Must initialize SDK before starting"
        assert (self.cm.z > 0) or self.cm.landed, "Flying below takeoff pad?"

        if self.cm.landed:
            assert self.is_statelike(cmd) or cmd == 'takeoff' or cmd == 'Command', "LANDED but sent command: "+  cmd


    def post_command(self,cmd):
        print('Posting command '+str(cmd))
        time.sleep(self.latency)
        self.check_state(cmd)