import socket
import threading
import time
import numpy as np
import libh264decoder
import cv2
import os
from object_detector import DetectorAPI
#"C:\ProgramData\Miniconda2\Scripts\pip.exe" install https://storage.googleapis.com/tensorflow/linux/cpu/tensorflow-2.0.0-cp27-none-linux_x86_64.whl



class AutonomousFlight:

    def __init__(self, local_ip='', local_port=9000, drone_ip='192.168.10.1',
                 drone_port=8889):
        """
        Binds to the local IP/port and puts the Tello into command mode.

        :param local_ip (str): Local IP address to bind.
        :param local_port (int): Local port to bind.
        :param imperial (bool): If True, speed is MPH and distance is feet.
                             If False, speed is KPH and distance is meters.
        :param command_timeout (int|float): Number of seconds to wait for a response to a command.
        :param drone_ip (str): Tello IP.
        :param drone_port (int): Tello port.
        """

        if not os.path.exists('images'):
            os.mkdir('images')

        # Command Send & Receive Queue
        self.max_len = 5
        self.rec_q = []

        #

        self.decoder = libh264decoder.H264Decoder()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket for sending cmd
        self.socket_video = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket for receiving video stream
        self.tello_address = (drone_ip, drone_port)

        self.socket.bind((local_ip, local_port))

        # thread for receiving cmd ack
        self.receive_thread = threading.Thread(target=self._receive_thread)
        self.receive_thread.daemon = True
        self.receive_thread.start()



        # Load up the inference graph
        model_path = 'faster_rcnn_inception_v2_coco_2018_01_28.tar/faster_rcnn_inception_v2_coco_2018_01_28/frozen_inference_graph.pb'
        labelmap_path = 'lblmap.pbtxt'
        self.odapi = DetectorAPI(path_to_ckpt=model_path, path_to_label_map=labelmap_path)

        self.local_video_port = 11111  # port for receiving video stream
        self.socket_video.bind((local_ip, self.local_video_port))

        # thread for receiving video
        self.receive_video_thread = threading.Thread(target=self._receive_video_thread)
        self.receive_video_thread.daemon = True

        self.receive_video_thread.start()


        # Post command every 5 sec
        self.send_5_sec_com = threading.Thread(target=self._command_thread)
        self.send_5_sec_com.start()

        # to receive video -- send cmd: command, streamon
        self.send_command('command')
        print('sent: command')
        self.send_command('streamon')
        print('sent: streamon')



    def __del__(self):
        """Closes the local socket."""

        self.socket.close()
        self.socket_video.close()

    def main_loop(self):

        while True:
            time.sleep(0.1)
            pass

    # def read_response(self):
    #     if len(self.rec_q) < 1:
    #         return None
    #     else:
    #         return self.rec_q.pop()


    def _receive_thread(self):
        """Listen to responses from the Tello.

        Runs as a thread, sets response to whatever the Drone last returned.

        """
        while True:
            try:
                response, ip = self.socket.recvfrom(3000)

                if response is not None:
                    response_decoded = response.decode('utf-8')
                    print('message: %s' % response_decoded)

                    # if len(self.rec_q) >= self.max_len:
                    #     ppd = self.rec_q.pop()
                    #     #print('unread message left receive queue: %s' % ppd)
                    #
                    # self.rec_q.insert(0, response_decoded)


            except socket.error as exc:
                print("Caught exception socket.error in Receive thread : %s" % exc)
                time.sleep(1)
                # Dont break

    def _command_thread(self):
        """
        Posts 'command' to Tello every n seconds.
        Runs as a seperate thread
        """
        N = 5.0
        while True:
            try:
                self.send_command('command')
                time.sleep(N)

            except socket.error as exc:
                print("Caught exception socket.error in Command thread: %s" % exc)



    def _receive_video_thread(self):
        """
        Listens for video streaming (raw h264) from the Tello.

        Runs as a thread, sets frame to the most recent frame Tello captured.

        """
        ii=0
        packet_data = ""
        time.sleep(4)
        while True:
            try:
                res_string, ip = self.socket_video.recvfrom(2048)
                packet_data += res_string
                # end of frame
                if len(res_string) != 1460 and len(res_string)!=0:

                    for frame in self._h264_decode(packet_data):
                        #self.state?
                        # Psas a BGR image!! @TODO BGR PASSED?
                        area, change_in_area = self.odapi.processFrame(frame, ii)
                        ii += 1
                    packet_data = ""

            except socket.error as exc:
                print("Caught exception socket.error in Video thread : %s" % exc)



    def _h264_decode(self, packet_data):
        """
        decode raw h264 format data from Tello

        :param packet_data: raw h264 data array

        :return: a list of decoded frame
        """
        res_frame_list = []
        frames = self.decoder.decode(packet_data)
        for framedata in frames:
            (frame, w, h, ls) = framedata
            if frame is not None:
                # print 'frame size %i bytes, w %i, h %i, linesize %i' % (len(frame), w, h, ls)

                frame = np.fromstring(frame, dtype=np.ubyte, count=len(frame), sep='')
                frame = (frame.reshape((h, ls / 3, 3)))
                frame = frame[:, :w, :]
                res_frame_list.append(frame)

        return res_frame_list


    def send_command(self, command):
        self.socket.sendto(command.encode('utf-8'), self.tello_address)











if __name__ == "__main__":
    t2 = AutonomousFlight()
    t2.main_loop()
