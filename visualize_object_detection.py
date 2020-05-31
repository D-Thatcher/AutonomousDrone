import numpy as np
import time
import tensorflow as tf
import cv2
import os

from TensorFlowObjectDetectionUtil import label_map_util
from TensorFlowObjectDetectionUtil import visualization_utils as vis_util


NUM_CLASSES = 80
MINIMUM_CONFIDENCE = 0.75
height = 720
width = 1280

queue_filter = True


PATH_TO_LABELS='labelmaps/label_map.pbtxt'
PATH_TO_CKPT = 'faster_rcnn_inception_v2_coco_2018_01_28.tar/faster_rcnn_inception_v2_coco_2018_01_28/frozen_inference_graph.pb'

label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(
    label_map,
    max_num_classes=NUM_CLASSES,
    use_display_name=True)
CATEGORY_INDEX = label_map_util.create_category_index(categories)

def get_frozen_graph(graph_file):
    """Read Frozen Graph file from disk."""
    with tf.Graph().as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(graph_file, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)

    return od_graph_def

trt_graph = get_frozen_graph(PATH_TO_CKPT)



pth = r"person_increasing.mp4"
assert os.path.exists(pth)
cap = cv2.VideoCapture(pth)
# Running the tensorflow session
with tf.Session() as sess:
    tf.import_graph_def(trt_graph, name= '')
    image_tensor = sess.graph.get_tensor_by_name('image_tensor:0')
    detection_boxes = sess.graph.get_tensor_by_name('detection_boxes:0')
    detection_scores = sess.graph.get_tensor_by_name('detection_scores:0')
    detection_classes = sess.graph.get_tensor_by_name('detection_classes:0')
    num = sess.graph.get_tensor_by_name('num_detections:0')

    while True:
        t = time.time()
        ret, img_temp = cap.read()
        frame = cv2.cvtColor(img_temp, cv2.COLOR_BGR2RGB)
        image_np_expanded = np.expand_dims(frame, axis=0)
        (boxes, scores, classes, num_detections) = sess.run(
                          [detection_boxes, detection_scores, detection_classes,num],
                          feed_dict={image_tensor: image_np_expanded})

        boxes = boxes[scores >MINIMUM_CONFIDENCE]
        classes = classes[scores >MINIMUM_CONFIDENCE]
        scores = scores[scores >MINIMUM_CONFIDENCE]




        vis_util.visualize_boxes_and_labels_on_image_array(
            img_temp,
            boxes,
            classes.astype(np.int32),
            scores,
            CATEGORY_INDEX,
            use_normalized_coordinates=True
        )

        cv2.imshow('image',img_temp)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break

        print("FPS:" + str(1/(time.time()-t)))

cap.release()
cv2.destroyAllWindows()

