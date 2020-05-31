


# Autonomous Drone Controller

* Flight Command History Logs (Can also be used to reproduce routes)
* Flight Video Stream Logs
* Joystick Mode (maps keyboard presses to commands)
* H264 video stream decoder included (libh264) (provided by Ryze)


If the TensorFlow wheel provided fails to install, try 
`python -m pip install "tensorflow-1.10.0-cp27-cp27m-win_amd64.whl`
On Windows 10 it seems this version of TensorFlow and Python (2.7) work best with the H264 library. I've included this wheel in the repository

## Object Detection
Real-time inference is conducted on the machine connected to the Drone over the network. In this case, we used a Faster RCNN model trained on the Open Images dataset to generate bounding boxes and class names of relevant objects. These are then used in the feedback algorithm to determine the appropriate response by the Drone


## Object Tracking
My implementation of an Object Tracking algorithm is included that finds the minimum bounding box center distance between frames of the same class (using a KD tree). If you want to experiment with using Object Tracking in the feedback loop, see `ObjectDetector.py` and set `self.visualize_object_tracking=True`
To understand what algorithm is being used to track, see `ObjectTrackingUtil.py`

### Points of Interest
* A lot of different types of drones communicate over the same protocol (and socket sometimes too!). It is important to employ security measures for your device, such as creating a password for your drone's network, connecting over a secure socket layer, blocking unused ports etc