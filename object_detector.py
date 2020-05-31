import numpy as np
import tensorflow as tf
import cv2
from TensorFlowObjectDetectionUtil import label_map_util
from TensorFlowObjectDetectionUtil import visualization_utils as vis_util
import os
import time
from util import ObjectTrackingUtil as util

class DetectorAPI:
    def __init__(self, path_to_ckpt, path_to_label_map):
        assert os.path.exists(path_to_ckpt), path_to_ckpt
        assert os.path.exists(path_to_label_map), path_to_label_map

        self.path_to_ckpt = path_to_ckpt

        if not os.path.exists('images'):
            os.mkdir('images')

        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(self.path_to_ckpt, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

        self.default_graph = self.detection_graph.as_default()
        self.sess = tf.Session(graph=self.detection_graph)

        # Definite input and output Tensors for detection_graph
        self.image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
        # Each box represents a part of the image where a particular object was detected.
        self.detection_boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
        # Each score represent how level of confidence for each of the objects.
        # Score is shown on the result image, together with the class label.
        self.detection_scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
        self.detection_classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
        self.num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')

        # Open images class labelmap
        NUM_CLASSES = 601

        self.MINIMUM_CONFIDENCE = 0.30

        self.idx_to_save = 0

        label_map = label_map_util.load_labelmap(path_to_label_map)
        categories = label_map_util.convert_label_map_to_categories(
            label_map,
            max_num_classes=NUM_CLASSES,
            use_display_name=True)
        self.CATEGORY_INDEX = label_map_util.create_category_index(categories)

        self.sz = (1280,720)
        self.cap = None
        self.old_boxes = None
        self.old_classes = None

        self.visualize_object_tracking = False

        self.lo_trail = []

    def preprocess_frame(self,frame):
        if frame is None:
            raise ValueError("None type frame received")
        return cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), self.sz)

    def set_capture(self, cap):
        self.cap = cap

    def main_stream_loop(self,pth):
        all_im = [os.path.join(pth,i) for i in os.listdir(pth)]
        try:
            for imp in all_im:
                img = cv2.imread(imp)
                odapi.processFrame(img)
        finally:
            self.close()


    def main_loop(self):
        assert self.cap is not None,"Must Set Capture Input"
        try:

            ret = 1
            ii = 0
            while ret:
                ret, img = self.cap.read()

                if ii%2 == 0:
                    odapi.processFrame(img)

                ii +=1
        except KeyboardInterrupt as e:
            print("Safely handled keyboard interrupt: Exiting nicely...")
        finally:
            odapi.close()
            cv2.destroyAllWindows()
            self.cap.release()

    def save_frame(self,frame):
        ret, frame_jpg = cv2.imencode('.jpg', frame)
        if ret:
            frame_name = "images/" + str(self.idx_to_save) + ".jpg"
            assert not os.path.exists(frame_name), "Tried to overwrite frame: "+frame_name
            with open(frame_name,'wb') as wf:
                wf.write(frame_jpg)

    def processFrame(self, img):
        t = time.time()
        img_preprocessed = self.preprocess_frame(img)

        (boxes, scores, classes, num_detections) =  self.sess.run(
            [self.detection_boxes, self.detection_scores, self.detection_classes,  self.num_detections],
            feed_dict={ self.image_tensor: np.expand_dims(img_preprocessed, axis=0)})


        img_temp = cv2.cvtColor(img_preprocessed, cv2.COLOR_RGB2BGR)

        # # Threshold by min confidence
        idc = scores > self.MINIMUM_CONFIDENCE
        boxes = boxes[idc]
        classes = classes[idc]
        scores = scores[idc]

        # Object track based on classes first if possible, then by distance to center

        if self.visualize_object_tracking and self.old_boxes is not None and self.old_classes is not None:
            # Get a pair of maps of the class to area & change in area
            area, change_in_area = util.draw_line_between_shortest(img_temp, self.old_boxes, boxes, self.old_classes, classes, self.lo_trail)
        self.old_boxes = boxes
        self.old_classes = classes

        vis_util.visualize_boxes_and_labels_on_image_array(
            img_temp,
            boxes,
            classes.astype(np.int32),
            scores,
            self.CATEGORY_INDEX,
            use_normalized_coordinates=True
        )
        #print("FPS is: " + str(1 / (time.time() - t)))


        cv2.imshow('image', img_temp)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            raise KeyboardInterrupt("Exited by q")



    def close(self):
        self.sess.close()



if __name__ == "__main__":

    # Open Images
    model_path=r"faster_rcnn_inception_resnet_v2_atrous_oid_v4_2018_12_12\frozen_inference_graph.pb"
    labelmap_path = r'faster_rcnn_inception_resnet_v2_atrous_oid_v4_2018_12_12\open_images\label_map_v4.pbtxt'


    odapi = DetectorAPI(path_to_ckpt=model_path,path_to_label_map=labelmap_path)
    pth =r"person_increasing.mp4"
    odapi.set_capture(cv2.VideoCapture(pth))
    odapi.main_loop()


